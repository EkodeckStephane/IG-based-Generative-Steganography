"""Standalone Algorithm 2 optimizer on the public Bernoulli MNIST-VAE checkpoint.
Requires numpy and torch. Run from repository root:
python research_evidence/r27_algorithm2_core_standalone.py
Exact KL gradient, model-sampled Monte Carlo Fisher (N=256), damping/line search.
Optimisation diagnostic ONLY; this does not evaluate adversarial detector performance.
"""
from pathlib import Path
import sys, hashlib, json
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'data'/'s5_vae_mnist.pt').exists(): ROOT=ROOT.parent
simdir=ROOT/'Supplementary_Data'
if not (simdir/'sim_s5_vae_mnist.py').exists(): simdir=ROOT/'Version_1.0'
sys.path.insert(0,str(simdir))
from sim_s5_vae_mnist import VAE

def decoder(model,z):
    d=model.dec
    weights=[d[i].weight.detach().cpu().numpy().astype(float) for i in (0,2,4)]
    biases=[d[i].bias.detach().cpu().numpy().astype(float) for i in (0,2,4)]
    a=weights[0]@z+biases[0];h=np.maximum(a,0)
    v=weights[1]@h+biases[1];h2=np.maximum(v,0)
    logits=weights[2]@h2+biases[2]
    jac=weights[2]@((weights[1]*(v>0)[:,None])@(weights[0]*(a>0)[:,None]))
    return logits,jac

def kl_grad_fisher(model,z,target):
    logits,J=decoder(model,z);t,_=decoder(model,target)
    p=1/(1+np.exp(-np.clip(logits,-50,50)));w=p*(1-p)
    kl=float(np.sum(np.logaddexp(0,t)-np.logaddexp(0,logits)+p*(logits-t)))
    grad=J.T@(w*(logits-t));F=J.T@(w[:,None]*J)
    return kl,grad,F,p,J

def optimize(model,target,method,seed,N=256,maxiter=100,tol=1e-5):
    z=np.array([0.,0.]);rng=np.random.default_rng(seed);history=[];draws=0
    for t in range(maxiter):
        loss,g,F,p,J=kl_grad_fisher(model,z,target);history.append(loss)
        if loss<tol:break
        if method=='MC Fisher':
            x=(rng.random((N,len(p)))<p[None,:]).astype(float)
            score=(x-p)@J;F=score.T@score/N;draws+=N
        if method=='Euclidean':direction=g
        else:direction=np.linalg.solve(F+1e-3*np.eye(2),g)
        if not np.isfinite(direction).all() or g@direction<=0:break
        alpha=1.
        for _ in range(28):
            new=z-alpha*direction;updated=kl_grad_fisher(model,new,target)[0]
            if updated<=loss-1e-4*alpha*(g@direction):break
            alpha*=.5
        else:break
        z=new
    final=kl_grad_fisher(model,z,target)[0]
    return dict(target=target.tolist(),final_z=z.tolist(),final_KL=final,iterations=len(history),
                converged=bool(final<=tol),sampled_scores=draws)

def main():
    torch.set_num_threads(1)
    path=ROOT/'data'/'s5_vae_mnist.pt';model=VAE()
    model.load_state_dict(torch.load(path,map_location='cpu',weights_only=True));model.eval()
    results={'checkpoint_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
             'scope':'Synthetic 2-bit target codebook. Algorithm 2 optimizer only, not MNIST class-mean S5 or security test.',
             'results':{}}
    z0=np.array([0.,0.]);z1=np.array([1.5,.5])
    for j,kind in enumerate(('MC Fisher','Exact Fisher','Euclidean')):
        results['results'][kind]=[optimize(model,z0+t*(z1-z0),kind,20261031+1000*j+i)
                                 for i,t in enumerate(np.linspace(0,1,4))]
    print(json.dumps(results,indent=2))
if __name__=='__main__':main()
