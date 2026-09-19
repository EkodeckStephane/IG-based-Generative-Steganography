#!/usr/bin/env python3
"""Portable reproduction of the frozen V8 STC stego materialization.

Scientific logic is intentionally the same as research_v8/src/run_v8_stc.py.
Only filesystem paths are parameterized.
"""
import argparse, ctypes, glob, hashlib, json, math, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

GRID=np.arange(1,509,3,dtype=np.int32)
CUTS=np.array([16,55,159,439,1271,3916,14108],dtype=np.int64)
TARGET={'0.0002':0.4789010282,'0.0008':0.6480707028}
CONDITIONS=[('0.0002','uniform_shrink'),('0.0002','IG_matched'),
            ('0.0008','uniform_shrink'),('0.0008','IG_matched')]

def seed64(tag):
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8],'big')

def carrier_data(a):
    rr=GRID[:,None]; cc=GRID[None,:]
    center=a[rr,cc].astype(np.int32)
    ok=(center>0)&(center<255)
    vals=[a[rr-1,cc-1].astype(np.int64),a[rr-1,cc].astype(np.int64),
          a[rr-1,cc+1].astype(np.int64),a[rr,cc-1].astype(np.int64),
          a[rr,cc+1].astype(np.int64),a[rr+1,cc-1].astype(np.int64),
          a[rr+1,cc].astype(np.int64),a[rr+1,cc+1].astype(np.int64)]
    s=sum(vals); ss=sum(v*v for v in vals); vnum=8*ss-s*s
    strata=np.searchsorted(CUTS,vnum,side='right').astype(np.int8)
    flat=np.flatnonzero(ok.ravel())
    return center.ravel()[flat].copy(), strata.ravel()[flat].copy(), flat

def bits_for(eps,name,m):
    return np.random.default_rng(seed64(f'V8|{eps}|{name}')).integers(0,2,m,dtype=np.uint8)

def build_extension(vendor):
    so=sorted((vendor/'pystc').glob('stc_extension*.so'))
    if not so:
        subprocess.run([sys.executable,'setup.py','build_ext','--inplace'],cwd=vendor,check=True)
        so=sorted((vendor/'pystc').glob('stc_extension*.so'))
    if not so:
        raise RuntimeError('STC extension build produced no shared object')
    return so[0]

def load_lib(so):
    lib=ctypes.CDLL(str(so))
    U32=ctypes.c_uint; IP=ctypes.POINTER(ctypes.c_int)
    FP=ctypes.POINTER(ctypes.c_float); UP=ctypes.POINTER(ctypes.c_ubyte)
    lib.stc_hide.argtypes=[U32,IP,FP,U32,UP,IP]; lib.stc_hide.restype=ctypes.c_int
    lib.stc_unhide.argtypes=[U32,IP,U32,UP]; lib.stc_unhide.restype=ctypes.c_int
    return lib,IP,FP,UP

def embed(path,eps,method,designs,lib,IP,FP,UP,out_path):
    a=np.asarray(Image.open(path),dtype=np.uint8)
    if a.shape!=(512,512):
        raise ValueError(f'{path}: expected 512x512, got {a.shape}')
    cover,strata,flat=carrier_data(a); n=len(cover)
    m=int(math.floor(TARGET[eps]*n)); msg=bits_for(eps,Path(path).name,m)
    rho=np.asarray(designs['epsilons'][eps][method]['rho'],dtype=np.float32)
    costs=np.empty(3*n,dtype=np.float32)
    costs[0::3]=rho[strata]; costs[1::3]=0.; costs[2::3]=rho[strata]
    stego=np.empty(n,dtype=np.int32)
    rc=lib.stc_hide(n,cover.ctypes.data_as(IP),costs.ctypes.data_as(FP),
                    m,msg.ctypes.data_as(UP),stego.ctypes.data_as(IP))
    extracted=np.empty(m,dtype=np.uint8)
    rc2=lib.stc_unhide(n,stego.ctypes.data_as(IP),m,extracted.ctypes.data_as(UP))
    err=int(np.count_nonzero(msg!=extracted)); delta=stego-cover
    valid=bool(np.all((delta>=-1)&(delta<=1)) and np.all((stego>=0)&(stego<=255)))
    success=bool(err==0 and valid)
    out_path.parent.mkdir(parents=True,exist_ok=True)
    b=a.copy(); centers=b[np.ix_(GRID,GRID)].reshape(-1)
    centers[flat]=stego.astype(np.uint8)
    b[np.ix_(GRID,GRID)]=centers.reshape(len(GRID),len(GRID))
    Image.fromarray(b).save(out_path)
    return dict(image=Path(path).name,epsilon=eps,method=method,n_eligible=n,
                message_bits=m,rc=rc,rc_extract=rc2,bit_errors=err,success=success,
                changes=int(np.count_nonzero(delta)))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bossbase-root',required=True,type=Path)
    ap.add_argument('--manifest',default=Path('research_v8/results/bossbase_split_manifest_v4.csv'),type=Path)
    ap.add_argument('--designs',default=Path('research_v8/results/v7_frozen_designs_reconstructed.json'),type=Path)
    ap.add_argument('--vendor',default=Path('research_v8/vendor/pystc_minimal'),type=Path)
    ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args()
    import pandas as pd
    df=pd.read_csv(args.manifest)
    # tolerate historical manifest column names
    name_col=next(c for c in ['image','filename','file','name'] if c in df.columns)
    split_col=next(c for c in ['split','partition'] if c in df.columns)
    df=df[df[split_col].isin(['fit','calibration'])].copy()
    designs=json.loads(args.designs.read_text())
    so=build_extension(args.vendor); lib,IP,FP,UP=load_lib(so)
    records=[]
    for _,row in df.sort_values([split_col,name_col]).iterrows():
        name=str(row[name_col]); split=str(row[split_col])
        cover=args.bossbase_root/name
        if not cover.exists():
            hits=list(args.bossbase_root.rglob(name))
            if len(hits)!=1: raise FileNotFoundError(name)
            cover=hits[0]
        for eps,method in CONDITIONS:
            dst=args.out/eps/method/split/name
            rec=embed(cover,eps,method,designs,lib,IP,FP,UP,dst)
            rec['split']=split; records.append(rec)
    (args.out/'V8_STEGO_MATERIALIZATION.json').write_text(json.dumps(records,indent=2))
    failures=[r for r in records if not r['success']]
    print(json.dumps({'records':len(records),'failures':failures,'stc_so':str(so)},indent=2))

if __name__=='__main__':
    main()
