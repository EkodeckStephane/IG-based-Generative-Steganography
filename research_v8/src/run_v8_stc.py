import ctypes, glob, hashlib, json, math, os, time
from pathlib import Path
import numpy as np
from PIL import Image

SO=glob.glob('/mnt/data/pySTC_src/pystc/stc_extension*.so')[0]
lib=ctypes.CDLL(SO)
U32=ctypes.c_uint; IP=ctypes.POINTER(ctypes.c_int); FP=ctypes.POINTER(ctypes.c_float); UP=ctypes.POINTER(ctypes.c_ubyte)
lib.stc_hide.argtypes=[U32,IP,FP,U32,UP,IP]; lib.stc_hide.restype=ctypes.c_int
lib.stc_unhide.argtypes=[U32,IP,U32,UP]; lib.stc_unhide.restype=ctypes.c_int
GRID=np.arange(1,509,3,dtype=np.int32)
CUTS=np.array([16,55,159,439,1271,3916,14108],dtype=np.int64)
DES=json.load(open('/mnt/data/Repare_framework_stage/v7_frozen_designs.json'))
TARGET={'0.0002':0.4789010282,'0.0008':0.6480707028}

def carrier_data(a):
    rr=GRID[:,None]; cc=GRID[None,:]
    center=a[rr,cc].astype(np.int32)
    ok=(center>0)&(center<255)
    vals=[a[rr-1,cc-1].astype(np.int64),a[rr-1,cc].astype(np.int64),a[rr-1,cc+1].astype(np.int64),a[rr,cc-1].astype(np.int64),a[rr,cc+1].astype(np.int64),a[rr+1,cc-1].astype(np.int64),a[rr+1,cc].astype(np.int64),a[rr+1,cc+1].astype(np.int64)]
    s=sum(vals); ss=sum(v*v for v in vals); vnum=8*ss-s*s
    strata=np.searchsorted(CUTS,vnum,side='right').astype(np.int8)
    flat=np.flatnonzero(ok.ravel())
    return center.ravel()[flat].copy(), strata.ravel()[flat].copy(), flat

def seed64(tag): return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8],'big')
def bits_for(eps,name,m): return np.random.default_rng(seed64(f'V8|{eps}|{name}')).integers(0,2,m,dtype=np.uint8)

def embed_image(path,eps,method,save=None):
    t=time.time(); a=np.asarray(Image.open(path),dtype=np.uint8); cover,strata,flat=carrier_data(a)
    n=len(cover); m=int(math.floor(TARGET[eps]*n)); msg=bits_for(eps,Path(path).name,m)
    rho=np.asarray(DES['epsilons'][eps][method]['rho'],dtype=np.float32)
    costs=np.empty(3*n,dtype=np.float32); costs[0::3]=rho[strata]; costs[1::3]=0.; costs[2::3]=rho[strata]
    stego=np.empty(n,dtype=np.int32)
    rc=lib.stc_hide(n,cover.ctypes.data_as(IP),costs.ctypes.data_as(FP),m,msg.ctypes.data_as(UP),stego.ctypes.data_as(IP))
    out=np.empty(m,dtype=np.uint8); rc2=lib.stc_unhide(n,stego.ctypes.data_as(IP),m,out.ctypes.data_as(UP))
    err=int(np.count_nonzero(msg!=out)); delta=stego-cover
    valid=bool(np.all((delta>=-1)&(delta<=1)) and np.all((stego>=0)&(stego<=255)))
    changes=int(np.count_nonzero(delta)); distortion=float(np.sum(np.where(delta==0,0.,rho[strata])))
    sc=np.bincount(strata,minlength=8); ch=np.bincount(strata[delta!=0],minlength=8)
    mse=changes/(512*512); psnr=float('inf') if changes==0 else 10*np.log10(255**2/mse)
    if save:
        b=a.copy(); centers=b[np.ix_(GRID,GRID)].reshape(-1); centers[flat]=stego.astype(np.uint8); b[np.ix_(GRID,GRID)]=centers.reshape(len(GRID),len(GRID)); Image.fromarray(b).save(save)
    return dict(image=Path(path).name,epsilon=eps,method=method,n_eligible=n,message_bits=m,rc=rc,rc_extract=rc2,bit_errors=err,success=bool(err==0 and valid),changes=changes,change_frac=changes/n,distortion_cost=distortion,psnr_db=psnr,strata_n=sc.tolist(),strata_changes=ch.tolist(),elapsed_s=time.time()-t)

if __name__=='__main__':
 import sys
 print(json.dumps(embed_image(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else None),indent=2))

def evaluate_saved(cover_path, stego_path, eps, method):
    t=time.time(); a=np.asarray(Image.open(cover_path),dtype=np.uint8); b=np.asarray(Image.open(stego_path),dtype=np.uint8)
    cover,strata,flat=carrier_data(a); n=len(cover); m=int(math.floor(TARGET[eps]*n)); msg=bits_for(eps,Path(cover_path).name,m)
    centers=b[np.ix_(GRID,GRID)].reshape(-1); stego=centers[flat].astype(np.int32)
    out=np.empty(m,dtype=np.uint8); rc2=lib.stc_unhide(n,stego.ctypes.data_as(IP),m,out.ctypes.data_as(UP))
    err=int(np.count_nonzero(msg!=out)); delta=stego-cover
    valid=bool(np.all((delta>=-1)&(delta<=1)) and np.all((stego>=0)&(stego<=255)))
    changes=int(np.count_nonzero(delta)); rho=np.asarray(DES['epsilons'][eps][method]['rho'],dtype=np.float32)
    distortion=float(np.sum(rho[strata][delta!=0])); sc=np.bincount(strata,minlength=8); ch=np.bincount(strata[delta!=0],minlength=8)
    mse=changes/(512*512); psnr=float('inf') if changes==0 else 10*np.log10(255**2/mse)
    return dict(image=Path(cover_path).name,epsilon=eps,method=method,n_eligible=n,message_bits=m,rc_extract=rc2,bit_errors=err,success=bool(err==0 and valid),changes=changes,change_frac=changes/n,distortion_cost=distortion,psnr_db=psnr,strata_n=sc.tolist(),strata_changes=ch.tolist(),elapsed_s=time.time()-t,reused=True)
