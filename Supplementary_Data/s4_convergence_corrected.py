"""Reproducible S4 convergence experiment, corrected Fisher metric.
For N(mu,sigma**2 I_2), Fisher is diag(1,1,4)/sigma**2.
The experiment computes exact hyperbolic geodesics and independently
computes reference energies and sequential Gaussian KL.
"""
import csv
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
LS=(16,32,64,128,256,512,1024)
def geodesic(a,b,t):
    dm=b[:2]-a[:2]; dh=np.linalg.norm(dm)/2
    z0,z1=a[2],b[2]
    if dh<1e-12:
        return np.column_stack((np.repeat(a[None,:2],len(t),axis=0),
                                z0*np.exp(t*np.log(z1/z0))))
    h=(dh*dh+z1*z1-z0*z0)/(2*dh)
    r=np.hypot(h,z0)
    p0=np.arctan2(z0,-h);p1=np.arctan2(z1,dh-h)
    q=np.log(np.tan(p0/2))*(1-t)+np.log(np.tan(p1/2))*t
    return np.column_stack((a[:2][None,:]+((h-r*np.tanh(q))/dh)[:,None]*dm[None,:],r/np.cosh(q)))
def kl(a,b):
    d=(a[:,2]-b[:,2])/b[:,2]
    ell=np.log1p(d)
    return np.expm1(2*ell)-2*ell+np.sum((a[:,:2]-b[:,:2])**2,axis=1)/(2*b[:,2]**2)
def energies(a,b):
    delta=b-a
    h2=np.sum(delta[:2]**2)/4
    distance=2*np.arcsinh(np.sqrt((h2+delta[2]**2)/(4*a[2]*b[2])))
    egeo=4*distance**2
    estr=(sum(delta[:2]**2)+4*delta[2]**2)/(a[2]*b[2])
    return egeo,estr
def main():
    rng=np.random.default_rng(123); rows=[];ratios=[]
    for i in range(50):
        a=np.array([rng.uniform(-3,3),rng.uniform(-3,3),rng.uniform(.5,2.5)])
        b=np.array([rng.uniform(-3,3),rng.uniform(-3,3),rng.uniform(.5,2.5)])
        eg,es=energies(a,b)
        for L in LS:
            t=np.linspace(0,1,L+1)
            pg=geodesic(a,b,t)
            ps=a[None,:]+t[:,None]*(b-a)[None,:]
            kg=float(np.sum(kl(pg[:-1],pg[1:])))
            ks=float(np.sum(kl(ps[:-1],ps[1:])))
            for typ,E,K in [('geo',eg,kg),('straight',es,ks)]:
                rows.append((i,L,typ,E,K,abs(2*L*K/E-1)))
            ratios.append((i,L,eg/es,kg/ks))
    for file,head,data in [
        ('s4_convergence_github.csv',['pair','L','path','energy','KL','relative_error'],rows),
        ('s4_ratios_github.csv',['pair','L','E_geo_over_straight','KL_geo_over_straight'],ratios)]:
        with (ROOT/file).open('w',newline='') as f:
            w=csv.writer(f);w.writerow(head);w.writerows(data)
    for L in LS:
        r=[x for x in rows if x[1]==L]
        q=[x for x in ratios if x[1]==L]
        print(L, np.mean([x[5] for x in r if x[2]=='geo']),
              np.mean([x[5] for x in r if x[2]=='straight']),
              np.mean([x[2] for x in q]),np.mean([x[3] for x in q]))
if __name__=='__main__':main()
