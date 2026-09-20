#!/usr/bin/env python3
"""Materialize one frozen V8 STC condition for deep-detector training.

The scientific embedding logic is identical to V8. This script limits output to
one (epsilon, method) condition so Colab does not need to store all 20,000
stegos simultaneously.
"""
import argparse, ctypes, hashlib, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image

GRID=np.arange(1,509,3,dtype=np.int32)
CUTS=np.array([16,55,159,439,1271,3916,14108],dtype=np.int64)
TARGET={'0.0002':0.4789010282,'0.0008':0.6480707028}

def seed64(tag): return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8],'big')
def bits_for(eps,name,m): return np.random.default_rng(seed64(f'V8|{eps}|{name}')).integers(0,2,m,dtype=np.uint8)

def carrier_data(a):
    rr=GRID[:,None]; cc=GRID[None,:]
    center=a[rr,cc].astype(np.int32)
    ok=(center>0)&(center<255)
    vals=[a[rr-1,cc-1].astype(np.int64),a[rr-1,cc].astype(np.int64),a[rr-1,cc+1].astype(np.int64),
          a[rr,cc-1].astype(np.int64),a[rr,cc+1].astype(np.int64),a[rr+1,cc-1].astype(np.int64),
          a[rr+1,cc].astype(np.int64),a[rr+1,cc+1].astype(np.int64)]
    s=sum(vals); ss=sum(v*v for v in vals); vnum=8*ss-s*s
    strata=np.searchsorted(CUTS,vnum,side='right').astype(np.int8)
    flat=np.flatnonzero(ok.ravel())
    return center.ravel()[flat].copy(), strata.ravel()[flat].copy(), flat

def build_extension(vendor):
    so=sorted((vendor/'pystc').glob('stc_extension*.so'))
    if not so:
        subprocess.run([sys.executable,'setup.py','build_ext','--inplace'],cwd=vendor,check=True)
        so=sorted((vendor/'pystc').glob('stc_extension*.so'))
    if not so: raise RuntimeError('STC extension build produced no shared object')
    return so[0]

def load_lib(so):
    lib=ctypes.CDLL(str(so)); U32=ctypes.c_uint
    IP=ctypes.POINTER(ctypes.c_int); FP=ctypes.POINTER(ctypes.c_float); UP=ctypes.POINTER(ctypes.c_ubyte)
    lib.stc_hide.argtypes=[U32,IP,FP,U32,UP,IP]; lib.stc_hide.restype=ctypes.c_int
    lib.stc_unhide.argtypes=[U32,IP,U32,UP]; lib.stc_unhide.restype=ctypes.c_int
    return lib,IP,FP,UP

def resolve(root,name):
    p=Path(root)/name
    if p.exists(): return p
    hits=list(Path(root).rglob(name))
    if len(hits)!=1: raise FileNotFoundError(f'{name}: {len(hits)} matches under {root}')
    return hits[0]

def embed(src,eps,method,rho,lib,IP,FP,UP,dst):
    a=np.asarray(Image.open(src),dtype=np.uint8)
    if a.shape!=(512,512): raise ValueError(f'{src}: expected 512x512, got {a.shape}')
    cover,strata,flat=carrier_data(a); n=len(cover); m=int(math.floor(TARGET[eps]*n))
    msg=bits_for(eps,Path(src).name,m)
    costs=np.empty(3*n,dtype=np.float32); costs[0::3]=rho[strata]; costs[1::3]=0.; costs[2::3]=rho[strata]
    stego=np.empty(n,dtype=np.int32)
    rc=lib.stc_hide(n,cover.ctypes.data_as(IP),costs.ctypes.data_as(FP),m,msg.ctypes.data_as(UP),stego.ctypes.data_as(IP))
    extracted=np.empty(m,dtype=np.uint8)
    rc2=lib.stc_unhide(n,stego.ctypes.data_as(IP),m,extracted.ctypes.data_as(UP))
    err=int(np.count_nonzero(msg!=extracted)); delta=stego-cover
    valid=bool(np.all((delta>=-1)&(delta<=1)) and np.all((stego>=0)&(stego<=255)))
    success=bool(err==0 and valid)
    dst.parent.mkdir(parents=True,exist_ok=True)
    b=a.copy(); centers=b[np.ix_(GRID,GRID)].reshape(-1); centers[flat]=stego.astype(np.uint8)
    b[np.ix_(GRID,GRID)]=centers.reshape(len(GRID),len(GRID)); Image.fromarray(b).save(dst)
    return dict(image=Path(src).name,n_eligible=n,message_bits=m,rc=int(rc),rc_extract=int(rc2),
                bit_errors=err,success=success,changes=int(np.count_nonzero(delta)))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bossbase-root',required=True,type=Path)
    ap.add_argument('--manifest',required=True,type=Path)
    ap.add_argument('--designs',required=True,type=Path)
    ap.add_argument('--vendor',required=True,type=Path)
    ap.add_argument('--epsilon',required=True,choices=['0.0002','0.0008'])
    ap.add_argument('--method',required=True,choices=['uniform_shrink','IG_matched'])
    ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args()
    df=pd.read_csv(args.manifest)
    if not {'image','split','rank_hash'}.issubset(df.columns): raise ValueError('unexpected manifest columns')
    df=df[df['split'].isin(['fit','calibration'])].sort_values(['split','rank_hash','image']).reset_index(drop=True)
    designs=json.loads(args.designs.read_text()); rho=np.asarray(designs['epsilons'][args.epsilon][args.method]['rho'],dtype=np.float32)
    so=build_extension(args.vendor); lib,IP,FP,UP=load_lib(so)
    records=[]
    for row in df.itertuples():
        src=resolve(args.bossbase_root,row.image); dst=args.out/row.split/row.image
        rec=embed(src,args.epsilon,args.method,rho,lib,IP,FP,UP,dst); rec['split']=row.split; records.append(rec)
    meta={'epsilon':args.epsilon,'method':args.method,'records':records,
          'n':len(records),'successes':sum(r['success'] for r in records),
          'failures':[r for r in records if not r['success']],'stc_so':str(so)}
    (args.out/'MATERIALIZATION.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps({k:meta[k] for k in ['epsilon','method','n','successes','failures','stc_so']},indent=2))
if __name__=='__main__': main()