#!/usr/bin/env python3
"""Exploratory, reproducible four-objective evaluation of submitted NG-Stego Algorithm 2.

Optimizer = same exact Bernoulli KL gradient and model-sampled score Fisher as
r27_algorithm2_direct_v1.py, with regularization and Armijo safeguards.
Codebooks are independent from fixed RNG seeds; no codeword is the cover point.
Six codebooks: 3 detector-training and 3 held-out. 2 bits/sampled image.
Model is fixed MNIST-VAE Bernoulli decoder; no claims for natural images.

Environmental variables: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1.
Run: python pareto_algorithm2_v1.py [--n 100 --bootstrap 150]
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
import time,json,csv,hashlib,argparse,sys
from pathlib import Path
from dataclasses import dataclass
import numpy as np,torch
from scipy.special import logsumexp
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sklearn.metrics import roc_auc_score
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'Version_1.0'),str(ROOT/'research_evidence'/'algorithm2_direct_validation')]
import r27_algorithm2_direct_v1 as algo
algo.b.DATA=ROOT/'data'
SEED=20261031
Z0=np.zeros(2,dtype=float)
COVERS=6
SPLIT=3
METHODS={
 'FisherMC_N64_T40':('Algorithm 2: MC Fisher',64,40,1e-3),
 'FisherMC_N256_T80':('Algorithm 2: MC Fisher',256,80,1e-3),
 'FisherMC_N512_T120':('Algorithm 2: MC Fisher',512,120,1e-3),
 'FisherMC_N256_T120_D01':('Algorithm 2: MC Fisher',256,120,1e-2),
 'Euclidean_T40':('Euclidean gradient descent',0,40,1e-3),
 'Euclidean_T80':('Euclidean gradient descent',0,80,1e-3),
 'Euclidean_T120':('Euclidean gradient descent',0,120,1e-3),
 'ExactFisher_T80':('Natural gradient: exact Fisher',0,80,1e-3),
}

def codebook(seed):
    rng=np.random.default_rng(seed); pts=[]
    for _ in range(4):
        for attempt in range(10000):
            angle=rng.uniform(0,2*np.pi);radius=rng.uniform(.40,1.15)
            z=np.array([radius*np.cos(angle),radius*np.sin(angle)])
            if all(np.linalg.norm(z-p)>.28 for p in pts):
                pts.append(z);break
        else:raise RuntimeError('Failure to sample separated codewords')
    return np.stack(pts)

def loglik(x,p):
    pp=np.clip(np.asarray(p),1e-7,1-1e-7)
    return np.asarray(x,dtype=float)@np.log(pp)+(1-np.asarray(x,dtype=float))@np.log1p(-pp)

def mix_likelihood_score(x,pc,p0):
    ll=np.stack([loglik(x,p)-loglik(x,p0) for p in pc],axis=1)
    return logsumexp(ll,axis=1)-np.log(len(pc))

def eval_set(m,p0,code,sols,idx,n,seed,public_encoder=True):
    """Use identical cover/sample uniforms across methods to reduce simulation variance."""
    rng=np.random.default_rng(seed)
    messages=np.tile(np.arange(4),int(np.ceil(n/4)))[:n]
    messages=rng.permutation(messages)
    ucover=rng.random((n,784));ustego=rng.random((n,784))
    cover=(ucover<p0[None,:]).astype(np.uint8)
    probs=np.stack([algo.b.decoder_probs(m,s) for s in sols])
    stego=(ustego<probs[messages]).astype(np.uint8)
    # The original latent-codeword decoder accesses only a PUBLIC VAE and the shared codebook.
    with torch.no_grad():
        zz,_=m.encode(torch.tensor(stego,dtype=torch.float32))
    decoded=np.argmin(np.square(zz.numpy()[:,None,:]-code[None,:,:]).sum(axis=2),axis=1)
    # Privileged known-model ML decoder uses final optimized parameters (additional diagnostic only).
    mm=np.stack([loglik(stego,p) for p in probs],axis=1)
    decoded_ml=mm.argmax(axis=1)
    # Fixed 1% independent pixel flip; same flip mask across methods.
    changed=(rng.random(stego.shape)<.01)
    noisy=(stego.astype(bool)^changed).astype(np.uint8)
    with torch.no_grad():nz,_=m.encode(torch.tensor(noisy,dtype=torch.float32))
    nd=np.argmin(np.square(nz.numpy()[:,None,:]-code[None,:,:]).sum(axis=2),axis=1)
    return {'covers':cover,'stegos':stego,'messages':messages,'public_correct':int((decoded==messages).sum()),
            'public_flip_correct':int((nd==messages).sum()),'oracle_decode_correct':int((decoded_ml==messages).sum()),
            'target_probs':probs,
            'oracle_scores':mix_likelihood_score(np.concatenate([cover,stego]),probs,p0)}

def features(m,x,F):
    with torch.no_grad(): z,_=m.encode(torch.tensor(x,dtype=torch.float32))
    zz=z.numpy(); return np.c_[zz,np.einsum('ni,ij,nj->n',zz,F,zz)]

def bootstrap_auc(y,s,rng,reps):
    n=int((y==0).sum());ni=np.where(y==0)[0];pi=np.where(y==1)[0]
    vals=[]
    for _ in range(reps):
        sub=np.r_[rng.choice(ni,size=n,replace=True),rng.choice(pi,size=len(pi),replace=True)]
        vals.append(roc_auc_score(y[sub],s[sub]))
    return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]

def dominate(a,b,keys):
    return all(a[k]<=b[k]+1e-12 for k in keys) and any(a[k]<b[k]-1e-12 for k in keys)

def main(n=100,bootstrap=150,suite='standard'):
    global METHODS
    if suite == 'earlystop':
        METHODS={
          'NoShift_T0':('Euclidean gradient descent',0,0,1e-3),
          **{f'FisherMC_N256_T{T}':('Algorithm 2: MC Fisher',256,T,1e-3) for T in [1,3,10,20,40,80]},
          **{f'Euclidean_T{T}':('Euclidean gradient descent',0,T,1e-3) for T in [1,3,10,20,40,80]},
        }
    tag = '_earlystop' if suite=='earlystop' else ''

    torch.set_num_threads(1)
    m=algo.b.load_model();p0=algo.b.decoder_probs(m,Z0)
    F0=algo.b.fisher_metric(m,Z0)
    codebooks=[codebook(SEED+19991*j+17) for j in range(COVERS)]
    assert all(min(np.linalg.norm(z-Z0) for z in c)>.399 for c in codebooks)
    sha=hashlib.sha256((ROOT/'data'/'s5_vae_mnist.pt').read_bytes()).hexdigest()
    tstart=time.perf_counter()
    artifact={'protocol':{'seed':SEED,'model':'Bernoulli 784 x latent 2 VAE','checkpoint_sha256':sha,
       'n_cover_and_stego_per_codebook':n,'suite':suite,'train_codebooks':list(range(SPLIT)),'heldout_codebooks':list(range(SPLIT,COVERS)),
       'optimizer':'model-sampled score outer-product Fisher; Bernoulli exact KL gradient; damping; Armijo safeguarded',
       'message_bits':2,'codebooks':[c.tolist() for c in codebooks],
       'detector':'standardized RBF SVC fixed C=1, gamma=scale, method-specific training on codebooks 0-2, evaluation on 3-5',
       'control':'same sampled uniform matrices and same message permutation per codebook across methods',
       'caution':'Exploratory; independent test codebooks but same fixed decoder; synthetic latent codebooks; no MNIST class means; no native iMEC/Discop; no natural images; no guarantee of generalization'},
       'optimization_runs':{},'method_results':{},'elapsed_seconds':None}
    summary=[]
    for meth_id,(kind,N,I,damping) in METHODS.items():
        sols=[]; runs=[]; rows=[]
        for cbidx,code in enumerate(codebooks):
            zz=[];rr=[]
            for msg,target in enumerate(code):
                r=algo.optimization(m,Z0,target,kind,np.random.default_rng(SEED+cbidx*2047+msg*29+123),N=N or 64,max_iter=I,tol=1e-5,damping=damping)
                zz.append(np.array(r['z']));rr.append(r)
                assert r['monotone'] and r['terminal_kl']<=r['initial_kl']+1e-7
            sols.append(np.array(zz));runs.append(rr)
        artifact['optimization_runs'][meth_id]=runs
        for cbidx,code in enumerate(codebooks):
            ev=eval_set(m,p0,code,sols[cbidx],cbidx,n,SEED+99999+cbidx*149)
            data=np.vstack([ev['covers'],ev['stegos']]); y=np.r_[np.zeros(n,dtype=int),np.ones(n,dtype=int)]
            q=ev['target_probs']
            kl=np.array([np.sum(p*np.log(p/p0)+(1-p)*np.log((1-p)/(1-p0))) for p in q])
            mse=float(np.mean((q-p0[None,:])**2))
            # Pinsker + mixture convexity gives valid (possibly loose) TV upper bound.
            tv_bound=float(min(1,np.sqrt(np.maximum(kl,0)/2).mean()))
            rows.append({'codebook':cbidx,'split':'train' if cbidx<SPLIT else 'heldout',
                         'pixels':data,'latent':features(m,data,F0),'labels':y,'oracle_scores':ev['oracle_scores'],
                         'decode':ev['public_correct'],'flip_decode':ev['public_flip_correct'],'ml_decode':ev['oracle_decode_correct'],
                         'kl_cover_avg':float(kl.mean()),'mse_p':mse,'tv_bound':tv_bound,
                         'opt_seconds':float(sum(x['seconds'] for x in runs[cbidx])),
                         'iterations':sum(x['iterations'] for x in runs[cbidx]),
                         'MC_samples':sum(x['monte_carlo_draws'] for x in runs[cbidx]),
                         'converged_targets':sum(int(x['converged']) for x in runs[cbidx])})
        train=[r for r in rows if r['split']=='train'];heldout=[r for r in rows if r['split']=='heldout']
        results={'per_codebook':[]}
        for detector_name in ['pixels','latent']:
            tx=np.vstack([r[detector_name] for r in train]); ty=np.concatenate([r['labels'] for r in train])
            # Fit detector only on train codebooks.
            det=make_pipeline(StandardScaler(),SVC(kernel='rbf',C=1,gamma='scale'))
            det.fit(tx,ty)
            for r in heldout:
                r['score_'+detector_name]=det.decision_function(r[detector_name])
        for r in rows:
            scalar={k:r[k] for k in ('codebook','split','decode','flip_decode','ml_decode','kl_cover_avg','mse_p','tv_bound','opt_seconds','iterations','MC_samples','converged_targets')}
            scalar['oracle_auc']=float(roc_auc_score(r['labels'],r['oracle_scores']))
            if r['split']=='heldout':
                for det in ['pixels','latent']:
                    s=r['score_'+det]
                    scalar[det+'_auc']=float(roc_auc_score(r['labels'],s))
                    scalar[det+'_ci95']=bootstrap_auc(r['labels'],s,np.random.default_rng(SEED+hashlib.sha256((meth_id+str(r['codebook'])+det).encode()).digest()[0]),bootstrap)
            results['per_codebook'].append(scalar)
        h=[r for r in results['per_codebook'] if r['split']=='heldout']
        metrics={'method':meth_id,'n_heldout_test_messages':n*len(h),'public_decode_rate':sum(r['decode'] for r in h)/(n*len(h)),
          'noisy_flip1pct_decode_rate':sum(r['flip_decode'] for r in h)/(n*len(h)),
          'privileged_ML_decode_rate':sum(r['ml_decode'] for r in h)/(n*len(h)),
          'pixel_AUC_mean':float(np.mean([r['pixels_auc'] for r in h])),
          'latent_AUC_mean':float(np.mean([r['latent_auc'] for r in h])),
          'oracle_AUC_mean':float(np.mean([r['oracle_auc'] for r in h])),
          'cover_KL_nats_mean':float(np.mean([r['kl_cover_avg'] for r in h])),
          'probability_MSE_mean':float(np.mean([r['mse_p'] for r in h])),
          'TV_upper_bound_mean':float(np.mean([r['tv_bound'] for r in h])),
          'optimizer_seconds_per_codeword':float(np.mean([r['opt_seconds'] for r in h])/4),
          'MC_samples_per_codebook':float(np.mean([r['MC_samples'] for r in h])),
          'converged_targets':int(sum(r['converged_targets'] for r in h)),
          'total_targets':4*len(h)}
        # AUC without inversion is not a valid objective: adversary may reverse scores.
        metrics['detector_advantage']=max(abs(metrics['pixel_AUC_mean']-.5),abs(metrics['latent_AUC_mean']-.5),abs(metrics['oracle_AUC_mean']-.5))
        metrics['decode_error']=1-metrics['public_decode_rate']
        artifact['method_results'][meth_id]={'summary':metrics,'per_codebook':results['per_codebook']}
        summary.append(metrics)
        (ROOT/('partial_pareto_results'+tag+'.json')).write_text(json.dumps(artifact,indent=2))
        print(meth_id,'heldout_decode',round(metrics['public_decode_rate'],3),'detectorAUC',tuple(round(metrics[k],3) for k in ['pixel_AUC_mean','latent_AUC_mean','oracle_AUC_mean']), 'converged',metrics['converged_targets'],'time',round(time.perf_counter()-tstart,1),flush=True)
    objectives=['decode_error','detector_advantage','probability_MSE_mean','optimizer_seconds_per_codeword']
    for a in summary:a['pareto_nondominated']=not any(dominate(b,a,objectives) for b in summary if b is not a)
    artifact['pareto_objectives']={x:'minimize' for x in objectives}
    artifact['summary']=summary
    artifact['elapsed_seconds']=time.perf_counter()-tstart
    (ROOT/('pareto_algorithm2_results'+tag+'.json')).write_text(json.dumps(artifact,indent=2))
    with (ROOT/('pareto_algorithm2_summary'+tag+'.csv')).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    return artifact
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--n',type=int,default=100);p.add_argument('--bootstrap',type=int,default=150);p.add_argument('--suite',choices=['standard','earlystop'],default='standard');args=p.parse_args()
    main(n=args.n,bootstrap=args.bootstrap,suite=args.suite)