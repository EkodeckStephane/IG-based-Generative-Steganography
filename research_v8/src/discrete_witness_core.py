"""Discrete-Gaussian witness core for quantized residual steganography.

Cover pmf: p_sigma(k) proportional exp(-k^2/(2 sigma^2)), k in Z.
Embedding: q(k)=(1-2b)p(k)+b p(k-1)+b p(k+1).
Security: exact discrete D_KL(p||q), Cachin orientation.
Source nuisance eta=log sigma. Fisher I_eta=Var_p(k^2)/sigma^4.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.optimize import minimize
from image_witness_core import ideal_rate_bpp, ellipse_boundary_2d

K_DEFAULT=64

def _discrete_gaussian_extended(sigmas, K=K_DEFAULT):
    s=np.asarray(sigmas,float)
    if np.any(s<=0): raise ValueError('sigma must be positive')
    k=np.arange(-K-1,K+2,dtype=float)
    lw=-(k*k)/(2.0*s[...,None]**2)
    lw=lw-np.max(lw,axis=-1,keepdims=True)
    w=np.exp(lw)
    pext=w/np.sum(w,axis=-1,keepdims=True)
    return k,pext

def exact_discrete_cachin_kl_vec(sigmas,betas,K=K_DEFAULT):
    s=np.asarray(sigmas,float); b=np.asarray(betas,float)
    if np.any(b<0) or np.any(b>=0.5): raise ValueError('beta invalid')
    s,b=np.broadcast_arrays(s,b)
    _,pext=_discrete_gaussian_extended(s,K=K)
    p=pext[...,1:-1]
    q=(1-2*b)[...,None]*p+b[...,None]*pext[...,:-2]+b[...,None]*pext[...,2:]
    # tails outside [-K,K] are far below double precision at declared sigma range.
    out=np.zeros_like(p)
    mask=p>0
    qsafe=np.maximum(q, np.finfo(float).tiny)
    out[mask]=p[mask]*np.log(p[mask]/qsafe[mask])
    return np.maximum(np.sum(out,axis=-1), 0.0)

def exact_discrete_cachin_kl(sigma,beta,K=K_DEFAULT):
    return float(exact_discrete_cachin_kl_vec(np.asarray(sigma),np.asarray(beta),K=K))

def source_fisher_logsigma_discrete(sigmas,K=K_DEFAULT):
    s=np.asarray(sigmas,float)
    k,pext=_discrete_gaussian_extended(s,K=K)
    k2=k*k
    m2=np.sum(pext*k2,axis=-1)
    m4=np.sum(pext*(k2*k2),axis=-1)
    return (m4-m2*m2)/(s**4)

def normalized_source_fisher_metric_discrete(sigmas,counts,modes,K=K_DEFAULT):
    s=np.asarray(sigmas,float); c=np.asarray(counts,float); A=np.asarray(modes,float)
    I=source_fisher_logsigma_discrete(s,K=K)
    return (A.T @ ((c*I)[:,None]*A))/c.sum()

def nominal_discrete_risk(sigmas,counts,betas,eta_shift=None,K=K_DEFAULT):
    s=np.asarray(sigmas,float); c=np.asarray(counts,float); b=np.asarray(betas,float)
    if eta_shift is None: eta_shift=np.zeros_like(s)
    sp=s*np.exp(np.asarray(eta_shift,float))
    vals=exact_discrete_cachin_kl_vec(sp,b,K=K)
    return float(np.dot(c,vals)/c.sum())

def robust_discrete_risk_2d_fast(sigmas,counts,betas,modes,radius,nphi=240,radial_levels=(1.0,),K=K_DEFAULT):
    s=np.asarray(sigmas,float); c=np.asarray(counts,float); b=np.asarray(betas,float); A=np.asarray(modes,float)
    G=normalized_source_fisher_metric_discrete(s,c,A,K=K)
    cand=[]
    for f in radial_levels:
        if f==0: cand.append(np.zeros((1,2)))
        else: cand.append(ellipse_boundary_2d(G,radius*float(f),nphi=nphi))
    d=np.vstack(cand); eta=d@A.T
    sp=s[None,:]*np.exp(eta); bm=np.broadcast_to(b[None,:],sp.shape)
    kl=exact_discrete_cachin_kl_vec(sp,bm,K=K)
    risks=(kl@c)/c.sum(); j=int(np.argmax(risks))
    return float(risks[j]),d[j],eta[j]

def optimize_nominal_discrete(sigmas,counts,epsilon,beta_max=.2,K=K_DEFAULT):
    g=len(sigmas); x0=np.full(g,.01)
    con={'type':'ineq','fun':lambda b:epsilon-nominal_discrete_risk(sigmas,counts,b,K=K)}
    res=minimize(lambda b:-ideal_rate_bpp(counts,b),x0,bounds=[(1e-9,beta_max)]*g,constraints=con,method='SLSQP',options={'ftol':1e-12,'maxiter':900})
    if not res.success: raise RuntimeError(res.message)
    return res.x

def uniform_shrink_discrete(nominal,sigmas,counts,modes,epsilon,radius,nphi=720,K=K_DEFAULT):
    if radius==0:return np.asarray(nominal,float).copy(),1.0
    nom=np.asarray(nominal,float); lo,hi=0.0,1.0
    for _ in range(45):
        mid=(lo+hi)/2
        rr=robust_discrete_risk_2d_fast(sigmas,counts,mid*nom,modes,radius,nphi=nphi,K=K)[0]
        if rr<=epsilon:lo=mid
        else:hi=mid
    return lo*nom,lo

def optimize_robust_discrete_multistart(sigmas,counts,modes,epsilon,radius,nominal,shrink,beta_max=.2,nphi=240,K=K_DEFAULT):
    if radius==0:return np.asarray(nominal,float).copy()
    g=len(sigmas); ramp=np.linspace(-.18,.18,g)
    starts=[np.full(g,.004),np.asarray(shrink,float),.75*np.asarray(nominal,float),np.clip(shrink*(1+ramp),1e-9,beta_max),np.clip(shrink*(1-ramp),1e-9,beta_max)]
    best=None
    for x0 in starts:
        con={'type':'ineq','fun':lambda b:epsilon-robust_discrete_risk_2d_fast(sigmas,counts,b,modes,radius,nphi=nphi,K=K)[0]}
        res=minimize(lambda b:-ideal_rate_bpp(counts,b),x0,bounds=[(1e-9,beta_max)]*g,constraints=con,method='SLSQP',options={'ftol':2e-10,'maxiter':900})
        if res.success:
            rr=robust_discrete_risk_2d_fast(sigmas,counts,res.x,modes,radius,nphi=720,radial_levels=(0,.5,1),K=K)[0]
            if rr<=epsilon+max(2e-8,1e-4*epsilon) and (best is None or res.fun<best.fun):best=res
    if best is None:raise RuntimeError('no feasible robust discrete solution')
    return best.x

def embedding_fisher_beta0_discrete(sigmas,K=K_DEFAULT):
    """Exact Fisher information wrt symmetric +/-1 embedding beta at beta=0."""
    s=np.asarray(sigmas,float)
    _,pext=_discrete_gaussian_extended(s,K=K)
    p=pext[...,1:-1]
    dp=pext[...,:-2]+pext[...,2:]-2.0*p
    mask=p>0
    val=np.zeros_like(p)
    val[mask]=(dp[mask]*dp[mask])/p[mask]
    return np.sum(val,axis=-1)

def nominal_local_discrete_fisher_risk(sigmas,counts,betas,K=K_DEFAULT):
    s=np.asarray(sigmas,float); c=np.asarray(counts,float); b=np.asarray(betas,float)
    I=embedding_fisher_beta0_discrete(s,K=K)
    return float(np.dot(c,0.5*I*b*b)/c.sum())

def optimize_local_discrete_fisher(sigmas,counts,epsilon,beta_max=.2,K=K_DEFAULT):
    g=len(sigmas); x0=np.full(g,.01)
    con={'type':'ineq','fun':lambda b:epsilon-nominal_local_discrete_fisher_risk(sigmas,counts,b,K=K)}
    res=minimize(lambda b:-ideal_rate_bpp(counts,b),x0,bounds=[(1e-9,beta_max)]*g,constraints=con,method='SLSQP',options={'ftol':1e-12,'maxiter':900})
    if not res.success: raise RuntimeError(res.message)
    return res.x

class DiscreteRobustOracle:
    """Precomputed finite-grid robust risk oracle with exact beta gradient.

    For each source perturbation and stratum, q = p + beta*d where
    d=p(k-1)+p(k+1)-2p(k). The finite-grid max risk gradient is the gradient
    of the active direction (a valid subgradient if ties occur).
    """
    def __init__(self,sigmas,counts,modes,radius,nphi=360,radial_levels=(1.0,),K=K_DEFAULT):
        self.sigmas=np.asarray(sigmas,float); self.counts=np.asarray(counts,float); self.w=self.counts/self.counts.sum(); self.A=np.asarray(modes,float); self.K=K
        G=normalized_source_fisher_metric_discrete(self.sigmas,self.counts,self.A,K=K)
        cand=[]
        for f in radial_levels:
            if f==0:cand.append(np.zeros((1,2)))
            else:cand.append(ellipse_boundary_2d(G,radius*float(f),nphi=nphi))
        self.deltas=np.vstack(cand)
        eta=self.deltas@self.A.T
        sp=self.sigmas[None,:]*np.exp(eta)
        # precompute p and d for all [M,G,K]
        _,pext=_discrete_gaussian_extended(sp,K=K)
        self.p=pext[...,1:-1]
        self.dp=pext[...,:-2]+pext[...,2:]-2.0*self.p
    def risks_and_grads(self,betas):
        b=np.asarray(betas,float)
        q=self.p+b[None,:,None]*self.dp
        q=np.maximum(q,np.finfo(float).tiny)
        term=np.zeros_like(self.p); mask=self.p>0
        term[mask]=self.p[mask]*np.log(self.p[mask]/q[mask])
        per=np.sum(term,axis=-1) # M,G
        risks=per@self.w
        # derivative wrt each beta_g for each direction
        grad_per=-np.sum(self.p*self.dp/q,axis=-1) # M,G
        grads=grad_per*self.w[None,:]
        return risks,grads
    def value_grad(self,betas):
        risks,grads=self.risks_and_grads(betas); j=int(np.argmax(risks)); return float(risks[j]),grads[j].copy(),j
    def value(self,betas): return self.value_grad(betas)[0]
    def grad(self,betas): return self.value_grad(betas)[1]

def ideal_rate_grad_bpp(counts,betas):
    c=np.asarray(counts,float); b=np.asarray(betas,float); w=c/c.sum()
    # derivative H3(beta) = 2 log2((1-2beta)/beta)
    return w*2.0*np.log2((1.0-2.0*b)/b)

def optimize_robust_discrete_oracle(sigmas,counts,modes,epsilon,radius,starts,beta_max=.2,nphi=360,K=K_DEFAULT,maxiter=500):
    if radius==0:
        return optimize_nominal_discrete(sigmas,counts,epsilon,beta_max=beta_max,K=K)
    oracle=DiscreteRobustOracle(sigmas,counts,modes,radius,nphi=nphi,radial_levels=(0,.5,1),K=K)
    best=None; stats=[]
    for x0 in starts:
        x0=np.clip(np.asarray(x0,float),1e-9,beta_max)
        con={'type':'ineq','fun':lambda b: epsilon-oracle.value(b),'jac':lambda b:-oracle.grad(b)}
        res=minimize(lambda b:-ideal_rate_bpp(counts,b),x0,jac=lambda b:-ideal_rate_grad_bpp(counts,b),bounds=[(1e-9,beta_max)]*len(x0),constraints=con,method='SLSQP',options={'ftol':1e-11,'maxiter':maxiter})
        stats.append((bool(res.success),int(res.nit),float(res.fun),str(res.message)))
        if res.success and oracle.value(res.x)<=epsilon+max(5e-9,5e-5*epsilon) and (best is None or res.fun<best.fun):best=res
    if best is None:raise RuntimeError('oracle optimization failed '+repr(stats))
    return best.x
