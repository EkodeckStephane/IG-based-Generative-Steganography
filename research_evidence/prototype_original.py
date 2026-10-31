#!/usr/bin/env python3
"""Pre-submission research prototype: Fisher-constrained entropy-guided, keyed rejection sampling.
NOT the original NG-Stego Algorithm 2; hash-based rejection sampling is prior art.
Uses a fixed pretrained Bernoulli VAE and two-bit shared-key messages. No MNIST raw images.
"""
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from scipy.special import xlogy
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

HERE = Path(__file__).resolve().parent
D=784; B=4; MASK=(1 << 2)-1; SEED=20261031

class VAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc=nn.Sequential(nn.Linear(784,128),nn.ReLU(),nn.Linear(128,64),nn.ReLU())
        self.fc_mu=nn.Linear(64,2);self.fc_logvar=nn.Linear(64,2)
        self.dec=nn.Sequential(nn.Linear(2,64),nn.ReLU(),nn.Linear(64,128),nn.ReLU(),nn.Linear(128,784))
    def encode(self,x):
        h=self.enc(x.reshape(-1,784));return self.fc_mu(h),self.fc_logvar(h)
    def decode_prob(self,z):return torch.sigmoid(self.dec(z))

def model_load(checkpoint):
    torch.set_num_threads(1)
    model=VAE();model.load_state_dict(torch.load(checkpoint,map_location='cpu',weights_only=True));model.eval();return model

def decode_p(model,z):
    with torch.no_grad(): p=model.decode_prob(torch.tensor(z,dtype=torch.float32)).numpy().ravel()
    return np.clip(p.astype(float),1e-12,1-1e-12)

def metric_entropy_grad(model,z):
    zz=torch.tensor(z,dtype=torch.float32,requires_grad=True)
    # logits and Jacobian of 784 Bernoulli parameters
    logits=model.dec(zz); J=torch.autograd.functional.jacobian(lambda t:model.dec(t),zz,vectorize=True).detach().numpy().astype(float)
    p=torch.sigmoid(logits).detach().numpy().astype(float)
    p=np.clip(p,1e-12,1-1e-12)
    w=p*(1-p)
    F=J.T@(w[:,None]*J)
    g=J.T@(w*np.log((1-p)/p))
    return F,g

def entropy(p):return float(np.sum(-xlogy(p,p)-xlogy(1-p,1-p)))
def bernoulli_kl(p,q):
    return float(np.sum(xlogy(p,p/q)+xlogy(1-p,(1-p)/(1-q))))

def choose_latent(model,z0,style,kl_budget):
    p0=decode_p(model,z0);F,g=metric_entropy_grad(model,z0)
    if style=='matched':return z0.copy(),0.,entropy(p0),dict(g=g.tolist(),F=F.tolist())
    if style=='fisher': d=np.linalg.solve(F+1e-9*np.eye(2),g)
    elif style=='euclidean': d=g.copy()
    else:raise ValueError(style)
    fd=float(d@F@d)
    if fd<1e-18:raise RuntimeError('Degenerate Fisher entropy direction')
    d=d/np.sqrt(fd)
    # Fixed direction, KL-matched positive radius in z-space (not local Fisher approximation).
    low=0.; high=max(0.2,np.sqrt(2*kl_budget)*3)
    for _ in range(30):
        if bernoulli_kl(decode_p(model,z0+high*d),p0)>kl_budget:break
        high*=2.
    else:raise RuntimeError('KL budget not attained in search range')
    for _ in range(34):
        m=(low+high)/2
        if bernoulli_kl(decode_p(model,z0+m*d),p0)<=kl_budget:low=m
        else:high=m
    z=z0+low*d; p=decode_p(model,z)
    return z,bernoulli_kl(p,p0),entropy(p),dict(g=g.tolist(),F=F.tolist(),direction=d.tolist())

def hash_bits(x,H):
    a=np.asarray(x,dtype=np.uint8).reshape(-1,D)
    # 784 additions: uint16 avoids overflow, then mask parity.
    y=((a.astype(np.uint16)@H.T.astype(np.uint16))&1).astype(np.uint8)
    return ((y[:,0]<<1)|y[:,1]).astype(np.uint8)

def exact_hash_bins(p,H):
    # For independent Bernoulli pixels: E[(-1)^(a.H.X)] = product_j (1-2*p_j)^(a.H[:,j]).
    # Walsh inversion computes all 4 bin masses, no Monte Carlo estimation needed.
    phi=np.ones(4)
    for a in range(1,4):
        selector=(((a>>1)&1)*H[0]+((a&1)*H[1]))&1
        phi[a]=float(np.prod(1-2*p[selector.astype(bool)]))
    q=np.empty(4)
    for b in range(4):
        q[b]=sum(((-1)**((int(a&b).bit_count())%2))*phi[a] for a in range(4))/4.
    return q,phi

def sample_cover(rng,p,n):return (rng.random((n,D))<p).astype(np.uint8)

def encode_messages(rng,p,H,n,max_rounds=10000):
    msg=rng.integers(0,B,n,dtype=np.uint8)
    otp=rng.integers(0,B,n,dtype=np.uint8)
    requested=np.bitwise_xor(msg,otp)
    out=np.empty((n,D),np.uint8); attempts=np.zeros(n,np.int32)
    todo=np.arange(n,dtype=np.int64)
    # Each iteration is independent cover-channel draw; accepted sample conditional on hash=target.
    # Terminate on all hits (no silent reassignments and no truncation bias).
    while len(todo):
        samples=sample_cover(rng,p,len(todo))
        hv=hash_bits(samples,H);attempts[todo]+=1
        hit=hv==requested[todo];out[todo[hit]]=samples[hit]
        todo=todo[~hit]
        if attempts.max()>max_rounds:raise RuntimeError('Exceeded max rejection attempts')
    recovered=hash_bits(out,H)^otp
    assert np.array_equal(recovered,msg), 'Exact decode failed'
    return out,attempts,msg,otp

def oracle_logratio(x,p0,p1,H,q):
    x=np.asarray(x,dtype=np.float64)
    v=x@np.log(p1/p0)+(1-x)@np.log((1-p1)/(1-p0))
    h=hash_bits(x.astype(np.uint8),H)
    return v-np.log(B*q[h])

def feature_public_encoder(model,x,z0,F):
    with torch.no_grad(): mean,_=model.encode(torch.tensor(x,dtype=torch.float32))
    means=mean.numpy().astype(float)
    delta=means-z0[None,:]
    f=np.einsum('ni,ij,nj->n',delta,F,delta)
    return np.column_stack([means,f])

def compute_auc_ci(y,s,rng,rep=120):
    auc=float(roc_auc_score(y,s));pos=np.where(y==1)[0];neg=np.where(y==0)[0]
    boots=[]
    for _ in range(rep):
        ix=np.concatenate([rng.choice(pos,len(pos),replace=True),rng.choice(neg,len(neg),replace=True)])
        boots.append(roc_auc_score(y[ix],s[ix]))
    return [auc,float(np.quantile(boots,.025)),float(np.quantile(boots,.975))]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--n-train',type=int,default=240)
    parser.add_argument('--n-test',type=int,default=400);parser.add_argument('--budget',type=float,default=.02)
    parser.add_argument('--seed',type=int,default=SEED);parser.add_argument('--output',type=Path,default=HERE/'results.json')
    args=parser.parse_args();t0=time.perf_counter();rng=np.random.default_rng(args.seed)
    model=model_load(HERE/'s5_vae_mnist.pt');sha=hashlib.sha256((HERE/'s5_vae_mnist.pt').read_bytes()).hexdigest()
    centers=[np.array(x,dtype=float) for x in ((0,0),(.35,-.45),(-.45,.35),(.6,.4))]
    styles=('matched','fisher','euclidean')
    output={'seed':args.seed,'checkpoint_sha256':sha,'n_train_per_class':args.n_train,'n_test_per_class':args.n_test,'k_bits':2,'target_KL_nats':args.budget,'centers':[], 'protocol':'Independent Bernoulli decoder cover model; 2-universal random linear hash; independent OTP and cover-channel rejection. Matched baseline exactly uses cover p0. Fisher/Euclidean entropy-ascent steps KL-calibrated to same cover KL. Detectors train on 3 centers and test fourth. No media channel distortions.'}
    splits={};methodstats={}
    for j,z0 in enumerate(centers):
        H=rng.integers(0,2,(2,D),dtype=np.uint8)
        F,g=metric_entropy_grad(model,z0);p0=decode_p(model,z0);scope={'center':j,'z0':z0.tolist(),'cover_entropy_nats':entropy(p0),'hash_sha256':hashlib.sha256(H.tobytes()).hexdigest(),'hash_matrix_packed_hex':np.packbits(H,axis=1).tobytes().hex(),'flip_channel_recovery_probability':{str(t):float(sum((1-2*t)**int(np.count_nonzero((((a>>1)&1)*H[0]+(a&1)*H[1])&1)) for a in range(4))/4) for t in (0.,0.001,0.01)},'methods':{}}
        for style in styles:
            z,kl,ent,details=choose_latent(model,z0,style,args.budget)
            p=decode_p(model,z);q,phi=exact_hash_bins(p,H)
            if q.min()<=0:raise RuntimeError('unreachable bin')
            dist_tv=float(.5*np.sum(np.abs(q-.25)));bound=float(np.sqrt(kl/2)+dist_tv)
            # With secret fresh OTP the marginal is uniform across bins even for non-uniform plaintext.
            # Exact unconditional TV between output and p1 is 0.5 sum_b |q_b-1/B|.
            stats={'z':z.tolist(),'KL_to_cover_nats':kl,'generated_entropy_nats':ent,'entropy_gain_nats':ent-entropy(p0),'hash_bins_probabilities':q.tolist(),'hash_parity_moments':phi.tolist(),'exact_TV_hash_to_p_theta':dist_tv,'Pinsker_TV_cover_upper_bound':bound,'expected_draws_exact':float(np.mean(1/q)/B)}
            groups={}
            for split,n in (('train',args.n_train),('test',args.n_test)):
                cover=sample_cover(rng,p0,n)
                steg,attempts,ms,otp=encode_messages(rng,p,H,n)
                groups[split]=(cover,steg)
                stats[split]={'exact_decode':int(n),'draws_mean':float(attempts.mean()),'draws_median':float(np.median(attempts)),'draws_max':int(attempts.max()),'total_draws':int(attempts.sum()),'sha256_stego':hashlib.sha256(steg.tobytes()).hexdigest(),'message_counts':np.bincount(ms,minlength=4).tolist()}
                if split=='test':
                    combined=np.concatenate([cover,steg]);labels=np.r_[np.zeros(n,dtype=int),np.ones(n,dtype=int)]
                    scores=oracle_logratio(combined,p0,p,H,q)
                    stats['oracle_AUC_bootstrap_ci95']=compute_auc_ci(labels,scores,np.random.default_rng(args.seed+500+j*10+styles.index(style)))
            splits[(j,style)]=groups;scope['methods'][style]=stats
            print(f'{j} {style}: KL={kl:.5f} dH={stats["entropy_gain_nats"]:+.5f} exact_tv={dist_tv:.3e} bound={bound:.3f} draws={stats["test"]["draws_mean"]:.3f} oracle_AUC={stats["oracle_AUC_bootstrap_ci95"][0]:.3f}',flush=True)
        output['centers'].append(scope)
    # Leave-one-center-out adversarial test, trained only on other centers. Identical labels and groups per center.
    output['leave_center_out_detectors']={}
    for style in styles:
        per=[]
        for j,z0 in enumerate(centers):
            train=[]; yy=[]
            for i in range(len(centers)):
                if i==j:continue
                a,b=splits[(i,style)]['train'];train.extend([a,b]); yy.extend([np.zeros(len(a)),np.ones(len(b))])
            train=np.vstack(train);yy=np.concatenate(yy)
            c,s=splits[(j,style)]['test'];test=np.vstack([c,s]);y=np.r_[np.zeros(len(c)),np.ones(len(s))]
            F,_=metric_entropy_grad(model,z0)
            # Encoder's latent coordinates are model-defined and comparable across centers; Fisher feature
            # uses a center-specific public source parameter -> intentionally strong informed detector.
            train_lat=[]
            for i in range(len(centers)):
                if i==j:continue
                zc=centers[i];FF,_=metric_entropy_grad(model,zc)
                a,b=splits[(i,style)]['train']
                train_lat.extend([feature_public_encoder(model,a,zc,FF),feature_public_encoder(model,b,zc,FF)])
            train_lat=np.vstack(train_lat);test_lat=feature_public_encoder(model,test,z0,F)
            det={}
            for name,ax,bx in [('pixel_rbf_svm',train,test),('public_encoder_fisher_rbf_svm',train_lat,test_lat)]:
                est=make_pipeline(StandardScaler(),SVC(C=1.,kernel='rbf',gamma='scale',random_state=args.seed))
                est.fit(ax,yy)
                scores=est.decision_function(bx)
                det[name]=compute_auc_ci(y,scores,np.random.default_rng(args.seed+3000+j*17+len(name)))
            per.append({'heldout_center':j,'detectors':det})
            print('DETECT',style,j,{k:round(v[0],4) for k,v in det.items()},flush=True)
        output['leave_center_out_detectors'][style]=per
    output['wall_seconds']=float(time.perf_counter()-t0)
    args.output.write_text(json.dumps(output,indent=2,allow_nan=False))
    print('SAVED',args.output, 'seconds',round(output['wall_seconds'],2))
if __name__=='__main__':main()
