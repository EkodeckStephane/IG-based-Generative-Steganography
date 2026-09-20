from pathlib import Path
import json, hashlib, time
import numpy as np
from scipy.optimize import brentq, minimize
from numba import njit, prange
from discrete_witness_core import DiscreteRobustOracle, ideal_rate_bpp, ideal_rate_grad_bpp

OUT=Path('/mnt/data/Repare_framework_stage')
fit=json.loads((OUT/'bossbase_fit_model_v4.json').read_text())
cal=json.loads((OUT/'bossbase_calibration_v4.json').read_text())
sig=np.array(fit['fitted_sigma'],float); cnt=np.array(fit['counts'],float); w=cnt/cnt.sum()
z=np.array(cal['mode_z'],float); A=np.c_[np.ones(8),z]
rstar=float(cal['r_star_q95']); EPS=[2e-4,8e-4]; RAD=[.5*rstar,rstar,1.5*rstar]; K=255

@njit(cache=True, parallel=True)
def batch_maxrisk_numba(p, sratio, w, B):
    nb=B.shape[0]; M=p.shape[0]; G=p.shape[1]; KK=p.shape[2]
    out=np.empty(nb, dtype=np.float64)
    for bi in prange(nb):
        mr=-1.0
        for m in range(M):
            r=0.0
            for g in range(G):
                bg=B[bi,g]
                t=0.0
                for k in range(KK):
                    pk=p[m,g,k]
                    if pk>0.0:
                        t -= pk*np.log1p(bg*sratio[m,g,k])
                r += w[g]*t
            if r>mr: mr=r
        out[bi]=mr
    return out

@njit(cache=True, parallel=True)
def all_risk_grad_numba(p, sratio, w, b):
    M=p.shape[0]; G=p.shape[1]; KK=p.shape[2]
    risks=np.empty(M,dtype=np.float64); grads=np.empty((M,G),dtype=np.float64)
    for m in prange(M):
        r=0.0
        for g in range(G):
            bg=b[g]; t=0.0; dg=0.0
            for k in range(KK):
                pk=p[m,g,k]
                if pk>0.0:
                    sr=sratio[m,g,k]; den=1.0+bg*sr
                    t -= pk*np.log(den)
                    dg -= pk*sr/den
            r += w[g]*t
            grads[m,g]=w[g]*dg
        risks[m]=r
    return risks,grads

def prep_oracle(radius,nphi,levels=(0,1)):
    o=DiscreteRobustOracle(sig,cnt,A,radius,nphi=nphi,radial_levels=levels,K=K)
    sr=np.divide(o.dp,o.p,out=np.zeros_like(o.dp),where=o.p>0)
    return np.ascontiguousarray(o.p), np.ascontiguousarray(sr)

# compile on tiny slices
_tmpo=DiscreteRobustOracle(sig,cnt,A,0,nphi=4,radial_levels=(0,),K=K)
_tmps=np.divide(_tmpo.dp,_tmpo.p,out=np.zeros_like(_tmpo.dp),where=_tmpo.p>0)
batch_maxrisk_numba(_tmpo.p,_tmps,w,np.full((1,8),.01))
all_risk_grad_numba(_tmpo.p,_tmps,w,np.full(8,.01))

pn,srn=prep_oracle(0,4,(0,))
def nominal(b): return float(batch_maxrisk_numba(pn,srn,w,np.asarray(b,float)[None,:])[0])
def nominal_v(B): return batch_maxrisk_numba(pn,srn,w,np.asarray(B,float))
def nominal_grad(b):
    rr,gg=all_risk_grad_numba(pn,srn,w,np.asarray(b,float)); return gg[0]

def gen_designs(eps,seed):
    rng=np.random.default_rng(seed); D=[]; attempts=0
    while len(D)<128:
        attempts+=1; d=np.exp(rng.normal(0,.9,8)); d/=d.max(); hi=.2
        if nominal(hi*d)<eps: continue
        lam=brentq(lambda x:nominal(x*d)-eps,0,hi,xtol=1e-14,rtol=1e-14); D.append(lam*d)
    return np.array(D),attempts

def opt_nom(eps):
    best=None
    for a in [.005,.02,.05]:
        x0=np.full(8,a); con={'type':'ineq','fun':lambda b:eps-nominal(b),'jac':lambda b:-nominal_grad(b)}
        res=minimize(lambda b:-ideal_rate_bpp(cnt,b),x0,jac=lambda b:-ideal_rate_grad_bpp(cnt,b),bounds=[(1e-9,.2)]*8,constraints=con,method='SLSQP',options={'ftol':1e-12,'maxiter':1000})
        if res.success and nominal(res.x)<=eps+max(5e-9,5e-5*eps) and (best is None or res.fun<best.fun): best=res
    if best is None: raise RuntimeError('nominal optimizer failed')
    return best.x

class FastOracle:
    def __init__(self,radius,nphi,levels=(0,1)):
        self.p,self.sr=prep_oracle(radius,nphi,levels)
    def batch(self,B): return batch_maxrisk_numba(self.p,self.sr,w,np.asarray(B,float))
    def vg(self,b):
        rr,gg=all_risk_grad_numba(self.p,self.sr,w,np.asarray(b,float)); j=int(np.argmax(rr)); return float(rr[j]),gg[j]
    def value(self,b): return self.vg(b)[0]
    def grad(self,b): return self.vg(b)[1]

def uniform_shrink(nom,eps,o):
    lo,hi=0.,1.
    for _ in range(50):
        m=(lo+hi)/2
        if o.value(m*nom)<=eps: lo=m
        else: hi=m
    return lo*nom,lo

def opt_rob(nom,shr,eps,o):
    ramp=np.linspace(-.2,.2,8); starts=[shr,.75*nom,np.clip(shr*(1+ramp),1e-9,.2),np.clip(shr*(1-ramp),1e-9,.2)]; best=None; stats=[]
    for x0 in starts:
        con={'type':'ineq','fun':lambda b:eps-o.value(b),'jac':lambda b:-o.grad(b)}
        res=minimize(lambda b:-ideal_rate_bpp(cnt,b),x0,jac=lambda b:-ideal_rate_grad_bpp(cnt,b),bounds=[(1e-9,.2)]*8,constraints=con,method='SLSQP',options={'ftol':1e-11,'maxiter':800})
        stats.append([bool(res.success),int(res.nit),float(res.fun),str(res.message)])
        if res.success and o.value(res.x)<=eps+max(5e-9,5e-5*eps) and (best is None or res.fun<best.fun): best=res
    if best is None: raise RuntimeError('robust optimizer failed '+repr(stats))
    return best.x,stats

def nonscalar(b,ref):
    s=np.sum(w*b*ref)/np.sum(w*ref*ref); residual=np.sqrt(np.sum(w*(b-s*ref)**2))/max(np.sqrt(np.sum(w*b*b)),1e-15); return float(residual),float(s)

def run_eps(ei,eps):
    t=time.time(); D,attempts=gen_designs(eps,20260911+100*ei); nr=nominal_v(D); rrs={}; oracles={}
    for r in RAD:
        o=FastOracle(r,720,(0,1)); oracles[r]=o; rrs[str(r)]=o.batch(D)
    rr=rrs[str(rstar)]; inf=rr/eps; qs=np.quantile(inf,[.1,.5,.9]); inds=set(range(0,128,10)); inds.update([int(np.argmin(inf)),int(np.argmax(inf))]); inds.update(int(np.argmin(abs(inf-q))) for q in qs); inds=sorted(inds)
    ohi=FastOracle(rstar,2880,(0,1)); hv=ohi.batch(D[inds]); rel=np.abs(hv-rr[inds])/np.maximum(hv,1e-300); maxrel=float(rel.max())
    if maxrel>5e-4:
        rr=ohi.batch(D); rrs[str(rstar)]=rr; inf=rr/eps
    nom=opt_nom(eps); olo=oracles[rstar]; shr,scale=uniform_shrink(nom,eps,olo); rob,stats=opt_rob(nom,shr,eps,olo)
    hi_nom=float(ohi.batch([nom])[0]); hi_shr=float(ohi.batch([shr])[0]); hi_rob=float(ohi.batch([rob])[0]); ns,sc=nonscalar(rob,nom)
    ed={'seed':20260911+100*ei,'attempts':attempts,'iso_designs':D.tolist(),'nominal_risk_max_abs_error':float(np.max(np.abs(nr-eps))),'radii':{},'rstar_cert_max_relative_discrepancy':maxrel,
        'nominal_optimizer':{'beta':nom.tolist(),'rate':float(ideal_rate_bpp(cnt,nom)),'nominal_risk':nominal(nom),'robust_risk_2880':hi_nom},
        'uniform_shrink':{'beta':shr.tolist(),'scale':scale,'rate':float(ideal_rate_bpp(cnt,shr)),'robust_risk_2880':hi_shr},
        'robust_optimizer':{'beta':rob.tolist(),'rate':float(ideal_rate_bpp(cnt,rob)),'nominal_risk':nominal(rob),'robust_risk_2880':hi_rob,'nonscalar_residual':ns,'best_scalar_vs_nominal':sc,'optimizer_stats':stats},
        'rate_gain_vs_shrink_pct':float(100*(ideal_rate_bpp(cnt,rob)/ideal_rate_bpp(cnt,shr)-1))}
    for r in RAD:
        x=rrs[str(r)]/eps; q10,med,q90=np.quantile(x,[.1,.5,.9]); ed['radii'][str(r)]={'q10':float(q10),'median':float(med),'q90':float(q90),'D80':float(q90-q10),'S80':float(q90/q10),'min':float(x.min()),'max':float(x.max())}
    ed['elapsed_s']=time.time()-t
    (OUT/f'bossbase_v4a_eps_{eps:.0e}.json').write_text(json.dumps(ed,indent=2))
    print('eps',eps,'D80@r*',ed['radii'][str(rstar)]['D80'],'gain',ed['rate_gain_vs_shrink_pct'],'nonscalar',ns,'robust/eps',hi_rob/eps,'elapsed',ed['elapsed_s'],flush=True)
    return ed

def main():
    t0=time.time(); result={'fit_sha256':hashlib.sha256((OUT/'bossbase_fit_model_v4.json').read_bytes()).hexdigest(),'calibration_sha256':hashlib.sha256((OUT/'bossbase_calibration_v4.json').read_bytes()).hexdigest(),'method_lock_sha256':hashlib.sha256((OUT/'BOSSBASE_METHOD_LOCK_V4A.md').read_bytes()).hexdigest(),'rstar':rstar,'epsilons':{},'K':K}
    for ei,e in enumerate(EPS): result['epsilons'][str(e)]=run_eps(ei,e)
    fitpass=bool(fit['diagnostic']['pass']); d80s=[result['epsilons'][str(e)]['radii'][str(rstar)]['D80'] for e in EPS]
    robok=all(result['epsilons'][str(e)]['robust_optimizer']['robust_risk_2880']<=e+max(5e-9,5e-5*e) for e in EPS)
    nons=all(result['epsilons'][str(e)]['robust_optimizer']['nonscalar_residual']>1e-3 for e in EPS)
    p={'parametric_fit_pass':fitpass,'rstar_positive_finite':bool(np.isfinite(rstar) and rstar>0),'D80_at_rstar':d80s,'D80_positive_both':all(x>0 for x in d80s),'D80_ge_0.05_at_least_one':sum(x>=.05 for x in d80s)>=1,'robust_budget_pass':robok,'robust_nonscalar_pass':nons}
    p['pass']=all(p[k] for k in ['parametric_fit_pass','rstar_positive_finite','D80_positive_both','D80_ge_0.05_at_least_one','robust_budget_pass','robust_nonscalar_pass'])
    result['pre_holdout_success']=p;result['elapsed_s']=time.time()-t0
    (OUT/'bossbase_v4a_pre_holdout_results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(p,indent=2)); print('elapsed',result['elapsed_s'])

if __name__=='__main__': main()