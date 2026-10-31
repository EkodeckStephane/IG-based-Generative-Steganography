"""Standalone check: exact local Fisher-KL identity in a Bernoulli ReLU VAE.
Run: python verify_relu_cell_fisher_standalone.py /path/to/s5_vae_mnist.pt
Only a local undamped unit-step theorem; not a global Algorithm-2 convergence proof.
"""
import sys, json, hashlib
import numpy as np
import torch

class VAE(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.enc=torch.nn.Sequential(torch.nn.Linear(784,128),torch.nn.ReLU(),torch.nn.Linear(128,64),torch.nn.ReLU())
        self.fc_mu=torch.nn.Linear(64,2)
        self.fc_logvar=torch.nn.Linear(64,2)
        self.dec=torch.nn.Sequential(torch.nn.Linear(2,64),torch.nn.ReLU(),torch.nn.Linear(64,128),torch.nn.ReLU(),torch.nn.Linear(128,784))

def info(m,z):
    W=[m.dec[i].weight.detach().numpy().astype(float) for i in (0,2,4)]
    b=[m.dec[i].bias.detach().numpy().astype(float) for i in (0,2,4)]
    a1=W[0]@z+b[0];a2=W[1]@np.maximum(a1,0)+b[1]
    h=W[2]@np.maximum(a2,0)+b[2]
    J=W[2]@((W[1]*(a2>0)[:,None])@(W[0]*(a1>0)[:,None]))
    p=1/(1+np.exp(-np.clip(h,-50,50)))
    F=J.T@((p*(1-p))[:,None]*J)
    return h,J,p,F,np.r_[a1>0,a2>0]

def relative_delta(F,H):
    w,V=np.linalg.eigh(F)
    B=(V/np.sqrt(w))@V.T
    return float(np.linalg.norm(B@(H-F)@B,ord=2))

def main(path):
    torch.set_num_threads(1)
    ckpt=open(path,'rb').read()
    m=VAE();m.load_state_dict(torch.load(path,map_location='cpu',weights_only=True));m.eval()
    targets=np.array([[0,0],[.12,.22],[-.25,.31],[.56,-.38],[-.51,-.22],[.30,-.18]],float)
    records=[]
    for j,t in enumerate(targets):
        ht,Jt,pt,Ft,cell=info(m,t)
        direction=np.array([np.cos(j*1.48+.5),np.sin(j*1.48+.5)])
        r=.01
        while r>1e-10:
            z=t+r*direction
            if all(np.array_equal(info(m,t+f*(z-t))[4],cell) for f in np.linspace(0,1,81)):break
            r*=.5
        assert r>1e-10
        hz,J,p,F,_=info(m,z);e=z-t
        g=J.T@(p*(1-p)*(hz-ht))
        identity=float(np.linalg.norm(g-F@e)/max(np.linalg.norm(g),1e-14))
        exact=float(np.linalg.norm(z-np.linalg.solve(F,g)-t))
        trials=[]
        for n in [32,128,512,2048]:
            for rep in range(8):
                rng=np.random.default_rng(2026103109+2017*j+77*rep+n)
                X=(rng.random((n,len(p)))<p).astype(float)
                scores=(X-p)@J;H=scores.T@scores/n
                delta=relative_delta(F,H)
                e_plus=z-np.linalg.solve(H,g)-t
                norm=lambda v:float(np.sqrt(max(v@F@v,0)))
                ratio=norm(e_plus)/norm(e)
                valid=bool(delta<.5)
                trials.append(dict(N=n,rep=rep,delta=delta,ratio=ratio,condition_met=valid,bound_respected=(ratio<=delta/(1-delta)+1e-9) if valid else None))
        records.append(dict(target=t.tolist(),radius=r,relative_gradient_identity_error=identity,exact_step_euclidean_error=exact,trials=trials))
    out=dict(scope='local ReLU cell only, undamped full-step, KL(P_z || P_target)',checkpoint_sha256=hashlib.sha256(ckpt).hexdigest(),results=records)
    print(json.dumps(dict(checkpoint=out['checkpoint_sha256'],targets=len(records),identity_max=max(v['relative_gradient_identity_error'] for v in records),exact_step_error_max=max(v['exact_step_euclidean_error'] for v in records),n_condition_met=sum(w['condition_met'] for v in records for w in v['trials']),n_bound_failures=sum(w['bound_respected'] is False for v in records for w in v['trials'])),indent=2))
    return out

if __name__=='__main__': main(sys.argv[1])
