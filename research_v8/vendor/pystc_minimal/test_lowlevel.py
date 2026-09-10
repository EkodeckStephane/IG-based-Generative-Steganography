import ctypes, glob, numpy as np
so=glob.glob('/mnt/data/pySTC_src/pystc/stc_extension*.so')[0]
lib=ctypes.CDLL(so)
u32=ctypes.c_uint; I=ctypes.POINTER(ctypes.c_int); F=ctypes.POINTER(ctypes.c_float); U=ctypes.POINTER(ctypes.c_ubyte)
lib.stc_hide.argtypes=[u32,I,F,u32,U,I]; lib.stc_hide.restype=ctypes.c_int
lib.stc_unhide.argtypes=[u32,I,u32,U]; lib.stc_unhide.restype=ctypes.c_int
rng=np.random.default_rng(123)
for n,rate in [(20000,0.30),(20000,0.48),(20000,0.64)]:
    cover=rng.integers(1,255,n,dtype=np.int32)
    rho=np.full(n,2.0,dtype=np.float32)
    costs=np.empty(3*n,dtype=np.float32); costs[0::3]=rho;costs[1::3]=0;costs[2::3]=rho
    m=int(n*rate); msg=rng.integers(0,2,m,dtype=np.uint8); stego=np.empty(n,dtype=np.int32)
    rc=lib.stc_hide(n,cover.ctypes.data_as(I),costs.ctypes.data_as(F),m,msg.ctypes.data_as(U),stego.ctypes.data_as(I))
    out=np.empty(m,dtype=np.uint8); rc2=lib.stc_unhide(n,stego.ctypes.data_as(I),m,out.ctypes.data_as(U))
    print(n,rate,'rc',rc,rc2,'ber',np.mean(msg!=out),'changes',np.mean(stego!=cover),'minmax',stego.min(),stego.max())
