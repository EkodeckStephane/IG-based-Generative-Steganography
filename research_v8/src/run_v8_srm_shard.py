#!/usr/bin/env python3
import argparse, ctypes, glob, hashlib, json, math, os, subprocess, tempfile, time
from pathlib import Path
from multiprocessing import Pool
import numpy as np
import pandas as pd
from PIL import Image
import conseal as cl

GRID=np.arange(1,509,3,dtype=np.int32)
CUTS=np.array([16,55,159,439,1271,3916,14108],dtype=np.int64)
TARGET={'0.0002':0.4789010282,'0.0008':0.6480707028}
VARIANTS=[
    'cover',
    'e2e4_uniform','e2e4_ig',
    'e8e4_uniform','e8e4_ig',
    'mipod_e2e4','mipod_e8e4',
]
SO=None; LIB=None; DES=None; SRM_EXE=None; BOSS_DIR=None

def seed32(tag):
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:4],'big')

def seed64(tag):
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8],'big')

def init_worker(so, designs, srm_exe, boss_dir):
    global SO,LIB,DES,SRM_EXE,BOSS_DIR
    SO=so; SRM_EXE=srm_exe; BOSS_DIR=boss_dir
    DES=json.load(open(designs))
    LIB=ctypes.CDLL(SO)
    U32=ctypes.c_uint; IP=ctypes.POINTER(ctypes.c_int); FP=ctypes.POINTER(ctypes.c_float); UP=ctypes.POINTER(ctypes.c_ubyte)
    LIB.stc_hide.argtypes=[U32,IP,FP,U32,UP,IP]; LIB.stc_hide.restype=ctypes.c_int
    LIB.stc_unhide.argtypes=[U32,IP,U32,UP]; LIB.stc_unhide.restype=ctypes.c_int

def carrier_data(a):
    rr=GRID[:,None]; cc=GRID[None,:]
    center=a[rr,cc].astype(np.int32)
    ok=(center>0)&(center<255)
    vals=[a[rr-1,cc-1].astype(np.int64),a[rr-1,cc].astype(np.int64),a[rr-1,cc+1].astype(np.int64),
          a[rr,cc-1].astype(np.int64),a[rr,cc+1].astype(np.int64),
          a[rr+1,cc-1].astype(np.int64),a[rr+1,cc].astype(np.int64),a[rr+1,cc+1].astype(np.int64)]
    s=sum(vals); ss=sum(v*v for v in vals); vnum=8*ss-s*s
    strata=np.searchsorted(CUTS,vnum,side='right').astype(np.int8)
    flat=np.flatnonzero(ok.ravel())
    return center.ravel()[flat].copy(), strata.ravel()[flat].copy(), flat

def bits_for(eps,name,m):
    return np.random.default_rng(seed64(f'V8|{eps}|{name}')).integers(0,2,m,dtype=np.uint8)

def stc_stego(a,name,eps,method):
    cover,strata,flat=carrier_data(a)
    n=len(cover); m=int(math.floor(TARGET[eps]*n)); msg=bits_for(eps,name,m)
    rho=np.asarray(DES['epsilons'][eps][method]['rho'],dtype=np.float32)
    costs=np.empty(3*n,dtype=np.float32)
    costs[0::3]=rho[strata]; costs[1::3]=0.; costs[2::3]=rho[strata]
    stego=np.empty(n,dtype=np.int32)
    U32=ctypes.c_uint; IP=ctypes.POINTER(ctypes.c_int); FP=ctypes.POINTER(ctypes.c_float); UP=ctypes.POINTER(ctypes.c_ubyte)
    rc=LIB.stc_hide(n,cover.ctypes.data_as(IP),costs.ctypes.data_as(FP),m,msg.ctypes.data_as(UP),stego.ctypes.data_as(IP))
    out=np.empty(m,dtype=np.uint8)
    rc2=LIB.stc_unhide(n,stego.ctypes.data_as(IP),m,out.ctypes.data_as(UP))
    err=int(np.count_nonzero(msg!=out)); delta=stego-cover
    valid=bool(np.all((delta>=-1)&(delta<=1)) and np.all((stego>=0)&(stego<=255)))
    b=a.copy(); centers=b[np.ix_(GRID,GRID)].reshape(-1); centers[flat]=stego.astype(np.uint8)
    b[np.ix_(GRID,GRID)]=centers.reshape(len(GRID),len(GRID))
    return b, dict(message_bits=m,n_eligible=n,rc=int(rc),rc_extract=int(rc2),bit_errors=err,success=bool(err==0 and valid))

def mipod_stego(a,name,eps):
    _,_,_=carrier_data(a)
    n=len(carrier_data(a)[0])
    m=int(math.floor(TARGET[eps]*n))
    alpha=m/(512.0*512.0)
    b=cl.mipod.simulate_single_channel(a,alpha=alpha,seed=seed32(f'V8-MiPOD|{eps}|{name}'))
    return b, dict(message_bits=m,alpha_bpp=alpha,success=True)

def extract_srm(a):
    with tempfile.TemporaryDirectory(prefix='v8srm_') as td:
        td=Path(td); ip=td/'image.pgm'; od=td/'features'; od.mkdir()
        Image.fromarray(a.astype(np.uint8)).save(ip)
        p=subprocess.run([SRM_EXE,'-i',str(ip),'-O',str(od)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
        if p.returncode != 0:
            raise RuntimeError(f'SRM failed rc={p.returncode}: {p.stderr[-1000:]}')
        files=sorted(od.glob('*.fea'))
        if len(files)!=106:
            raise RuntimeError(f'Expected 106 SRM submodels, got {len(files)}')
        chunks=[np.fromstring(f.read_text(),sep=' ',dtype=np.float32) for f in files]
        x=np.concatenate(chunks)
        if x.size != 34671:
            raise RuntimeError(f'Expected 34671 SRM dimensions, got {x.size}')
        return x, [f.stem for f in files], [int(z.size) for z in chunks]

def work(rec):
    idx,name,split=rec
    t=time.time()
    cp=Path(BOSS_DIR)/name
    a=np.asarray(Image.open(cp),dtype=np.uint8)
    rows=[]
    for variant in VARIANTS:
        if variant=='cover':
            b=a; meta={'success':True,'message_bits':0}
        elif variant=='e2e4_uniform':
            b,meta=stc_stego(a,name,'0.0002','uniform_shrink')
        elif variant=='e2e4_ig':
            b,meta=stc_stego(a,name,'0.0002','IG_matched')
        elif variant=='e8e4_uniform':
            b,meta=stc_stego(a,name,'0.0008','uniform_shrink')
        elif variant=='e8e4_ig':
            b,meta=stc_stego(a,name,'0.0008','IG_matched')
        elif variant=='mipod_e2e4':
            b,meta=mipod_stego(a,name,'0.0002')
        elif variant=='mipod_e8e4':
            b,meta=mipod_stego(a,name,'0.0008')
        x,submodels,dims=extract_srm(b)
        rows.append((variant,x,meta,submodels,dims))
    return dict(index=int(idx),image=name,split=split,rows=rows,elapsed_s=time.time()-t)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--boss-dir',required=True)
    ap.add_argument('--manifest',required=True)
    ap.add_argument('--designs',required=True)
    ap.add_argument('--stc-so',required=True)
    ap.add_argument('--srm-exe',required=True)
    ap.add_argument('--start',type=int,required=True)
    ap.add_argument('--end',type=int,required=True)
    ap.add_argument('--jobs',type=int,default=4)
    ap.add_argument('--out-dir',required=True)
    args=ap.parse_args()
    df=pd.read_csv(args.manifest)
    df=df[df['split'].isin(['fit','calibration'])].sort_values(['split','rank_hash','image']).reset_index(drop=True)
    sub=df.iloc[args.start:args.end]
    tasks=[(i,r.image,r.split) for i,r in sub.iterrows()]
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    t=time.time()
    with Pool(args.jobs,initializer=init_worker,initargs=(args.stc_so,args.designs,args.srm_exe,args.boss_dir)) as pool:
        results=list(pool.imap_unordered(work,tasks,chunksize=1))
    results.sort(key=lambda z:z['index'])
    for variant in VARIANTS:
        X=[]; names=[]; splits=[]; success=[]; message_bits=[]; extra=[]
        sm=None; dims=None
        for rr in results:
            row=next(x for x in rr['rows'] if x[0]==variant)
            _,vec,meta,s0,d0=row
            X.append(vec); names.append(rr['image']); splits.append(rr['split'])
            success.append(bool(meta.get('success',True))); message_bits.append(int(meta.get('message_bits',0))); extra.append(meta)
            if sm is None: sm=s0; dims=d0
            elif sm!=s0 or dims!=d0: raise RuntimeError('SRM submodel ordering changed')
        X=np.asarray(X,dtype=np.float32)
        np.savez_compressed(out/f'{variant}_{args.start:04d}_{args.end:04d}.npz',
            X=X,names=np.asarray(names),splits=np.asarray(splits),success=np.asarray(success,dtype=np.bool_),
            message_bits=np.asarray(message_bits,dtype=np.int32),
            submodels=np.asarray(sm),submodel_dims=np.asarray(dims,dtype=np.int32))
        json.dump(extra,open(out/f'{variant}_{args.start:04d}_{args.end:04d}_meta.json','w'),indent=1)
    summary={
        'range':[args.start,args.end],'n_images':len(results),'variants':VARIANTS,
        'feature_dim':34671,'submodels':106,'jobs':args.jobs,
        'elapsed_s':time.time()-t,
        'failures':[
          {'image':rr['image'],'variant':v,'meta':m}
          for rr in results for v,_,m,_,_ in rr['rows'] if not m.get('success',True)
        ]
    }
    json.dump(summary,open(out/f'summary_{args.start:04d}_{args.end:04d}.json','w'),indent=2)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':
    main()
