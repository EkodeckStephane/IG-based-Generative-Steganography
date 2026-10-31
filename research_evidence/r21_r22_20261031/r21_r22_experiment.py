#!/usr/bin/env python3
"""Reproducible R2.1 / R2.2: real trained Bernoulli VAE, exact Fisher, MC estimates,
operational codebook packing diagnostic. This experiment is separate from original S5.
Run: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python r21_r22_experiment.py --checkpoint /path/to/s5_vae_mnist.pt
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse, hashlib, json, csv
from pathlib import Path
import numpy as np, torch
from scipy.special import expit, logsumexp
from scipy.stats import beta as beta_dist
from sklearn.metrics import roc_auc_score

SEED=20261031
class VAE(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.latent_dim=2
        self.enc=torch.nn.Sequential(torch.nn.Linear(784,128),torch.nn.ReLU(),torch.nn.Linear(128,64),torch.nn.ReLU())
        self.fc_mu=torch.nn.Linear(64,2); self.fc_logvar=torch.nn.Linear(64,2)
        self.dec=torch.nn.Sequential(torch.nn.Linear(2,64),torch.nn.ReLU(),torch.nn.Linear(64,128),torch.nn.ReLU(),torch.nn.Linear(128,784))
    def encode(self,x):
        h=self.enc(x.reshape(-1,784));return self.fc_mu(h),self.fc_logvar(h)

def load(path):
    torch.set_num_threads(1)
    model=VAE().double();state=torch.load(path,map_location='cpu',weights_only=True)
    model.load_state_dict(state);model.eval()
    return model

def logits_and_J(m,z):
    z=np.asarray(z,dtype=float)
    W=[m.dec[j].weight.detach().cpu().numpy() for j in (0,2,4)]
    b=[m.dec[j].bias.detach().cpu().numpy() for j in (0,2,4)]
    a=W[0]@z+b[0];v=W[1]@np.maximum(a,0)+b[1]
    logits=W[2]@np.maximum(v,0)+b[2]
    J=W[2]@((W[1]*(v>0)[:,None])@(W[0]*(a>0)[:,None]))
    return logits,J

def pfj(m,z):
    l,j=logits_and_J(m,z);p=expit(l)
    return p,j,j.T@((p*(1-p))[:,None]*j)

def fhat(m,z,n,rng):
    p,J,F=pfj(m,z)
    # one sample from the model per pixel; score of latent Bernoulli distribution
    X=(rng.random((n,p.size))<p[None,:]).astype(float)
    scores=(X-p[None,:])@J
    return scores.T@scores/n

def norm_error(F,G):
    lam,V=np.linalg.eigh(F)
    if min(lam)<=0:raise ValueError('Singular Fisher')
    Finv2=(V/np.sqrt(lam))@V.T
    return float(np.linalg.norm(Finv2@(G-F)@Finv2,ord=2))

def kl_grad(m,z,target):
    l,J=logits_and_J(m,z);t,_=logits_and_J(m,target)
    p=expit(l);w=p*(1-p)
    kl=float(np.sum(np.logaddexp(0,t)-np.logaddexp(0,l)+p*(l-t)))
    return kl,J.T@(w*(l-t)),J.T@(w[:,None]*J)

def sample_p(p,n,rng):
    return (rng.random((n,len(p)))<p).astype(np.uint8)

def ll(x,p):
    q=np.clip(p,1e-12,1-1e-12)
    return x@np.log(q)+(1-x)@np.log1p(-q)

def clopper_lower_upper(k,n,conf=.95):
    a=1-conf
    lo=beta_dist.ppf(a/2,k,n-k+1) if k>0 else 0
    hi=beta_dist.ppf(1-a/2,k+1,n-k) if k<n else 1
    return float(lo),float(hi)

def h2(x):
    if x<=0 or x>=1:return 0.
    return -x*np.log2(x)-(1-x)*np.log2(1-x)

def test_r21(m,out,rng):
    centers=np.array([[0,0],[.25,-.12],[-.35,.23],[.65,.4],[-.4,-.65],[.8,-.2]])
    rows=[];local=[]
    for cidx,z in enumerate(centers):
        _,J,F=pfj(m,z)
        eig=np.linalg.eigvalsh(F)
        if eig[0]<=0:continue
        for n in [32,128,512,2048]:
            for r in range(8):
                H=fhat(m,z,n,np.random.default_rng(SEED+cidx*9901+n*91+r))
                d=norm_error(F,H)
                local.append({'center':cidx,'n_scores':n,'trial':r,'relative_delta':d,'lambda_min_F':eig[0],'lambda_max_F':eig[-1],'contract_sufficient_delta_lt_half':int(d<.5)})
        # finite displacement around target, test one local GN update with each approximation
        target=z+np.array([.007,-.006]);start=target+np.array([.008,.004])
        before,g,Fs=kl_grad(m,start,target)
        delta0=float(np.linalg.norm(start-target))
        for name,N in [('exact',0),('MC_128',128),('MC_512',512),('MC_2048',2048)]:
            if N:H=fhat(m,start,N,np.random.default_rng(SEED+99999+cidx*11+N))
            else:H=Fs
            dd=norm_error(Fs,H)
            step=np.linalg.solve(H+1e-9*np.eye(2),g)
            z_new=start-step
            after=kl_grad(m,z_new,target)[0]
            # target norm, not a geodesic claim, and a nonlinear KL objective.
            local.append({'center':cidx,'kind':name,'n_scores':N,'Fhat_delta':dd,'kl_before':before,'kl_after':after,'kl_decreased':int(after<=before),
                         'initial_euclidean_error':delta0,'final_euclidean_error':float(np.linalg.norm(z_new-target))})
    with (out/'r21_sampled_fisher_trials.csv').open('w',newline='') as f:
        fields=['center','n_scores','trial','relative_delta','lambda_min_F','lambda_max_F','contract_sufficient_delta_lt_half']
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(x for x in local if 'trial' in x)
    with (out/'r21_local_optimizer_trials.csv').open('w',newline='') as f:
        fields=['center','kind','n_scores','Fhat_delta','kl_before','kl_after','kl_decreased','initial_euclidean_error','final_euclidean_error']
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(x for x in local if 'kind' in x)
    summary={}
    for n in [32,128,512,2048]:
        a=[x['relative_delta'] for x in local if x.get('trial') is not None and x['n_scores']==n]
        summary[str(n)]={'median_relative_F_error':float(np.median(a)),'q95_relative_F_error':float(np.quantile(a,.95)),
                         'fraction_delta_lt_half':float(np.mean(np.array(a)<.5)),'n_trials':len(a)}
    return {'fisher_estimation_by_sample_size':summary,'one_step_KL_decrease_rate':{
           name:float(np.mean([x['kl_decreased'] for x in local if x.get('kind')==name])) for name in ['exact','MC_128','MC_512','MC_2048']},
           'ReLU_warning':'Fisher metric may jump at activation boundaries; smooth C1 metric theorems do NOT apply globally to this pretrained ReLU decoder.'}

def test_relu_jump(m):
    W=m.dec[0].weight.detach().numpy();b=m.dec[0].bias.detach().numpy()
    z0=np.zeros(2);results=[]
    # Find first-layer ReLU kink nearest to z0 where other activation boundaries may also be present
    for i in np.argsort(np.abs(b)/np.linalg.norm(W,axis=1))[:10]:
        n=W[i]/np.linalg.norm(W[i]);z=-b[i]/np.linalg.norm(W[i])*n
        Fminus=pfj(m,z-1e-6*n)[2];Fplus=pfj(m,z+1e-6*n)[2]
        rel=float(np.linalg.norm(Fplus-Fminus)/max(np.linalg.norm(Fminus),1e-12))
        results.append({'first_layer_unit':int(i),'kink_z':z.tolist(),'jump_relative_1e_minus6':rel})
    return results

def test_r22(m,out):
    z0=np.zeros(2);p0,_,F0=pfj(m,z0)
    w,V=np.linalg.eigh(F0);L=np.linalg.cholesky(F0);res=[]
    # distinct codebooks from independent rotations; local Fisher metric used only for *nominal* separation
    n=256
    for k in [1,2,3,4]:
        M=2**k
        for radius in [3.,6.,9.,12.]:
            for seed_i in range(4):
                rng=np.random.default_rng(SEED+10000*k+100*int(radius)+seed_i)
                phase=rng.uniform(0,2*np.pi)
                theta=phase+2*np.pi*np.arange(M)/M
                whitened=radius*np.column_stack([np.cos(theta),np.sin(theta)])
                # (L.T)^-1 sends Euclidean whitened coordinates to F0-norm coordinates
                code=z0+np.linalg.solve(L.T,whitened.T).T
                probs=np.stack([pfj(m,z)[0] for z in code]);message=rng.integers(0,M,size=n)
                X=(rng.random((n,784))<probs[message]).astype(np.uint8)
                llmat=np.stack([ll(X,p) for p in probs],axis=1)
                estimate=llmat.argmax(axis=1)
                error=int(np.sum(estimate!=message));pe=error/n
                with torch.no_grad():
                    latent=m.encode(torch.from_numpy(X.astype(np.float64)))[0].numpy()
                public_est=np.square(latent[:,None,:]-code[None,:,:]).sum(axis=2).argmin(axis=1)
                public_error=int(np.sum(public_est!=message))
                klcode=float(np.mean([np.sum(p*np.log(np.maximum(p,1e-12)/np.maximum(p0,1e-12))+
                             (1-p)*np.log(np.maximum(1-p,1e-12)/np.maximum(1-p0,1e-12))) for p in probs]))
                # Population optimal cover-v-mixture score; evaluated on independent cover & stego images
                cover=sample_p(p0,n,np.random.default_rng(SEED+200000+seed_i+100*k+int(radius)))
                mscore=lambda xx:logsumexp(np.stack([ll(xx,p) for p in probs],axis=1),axis=1)-np.log(M)-ll(xx,p0)
                scores=np.r_[mscore(cover),mscore(X)]
                auc=float(roc_auc_score(np.r_[np.zeros(n),np.ones(n)],scores))
                BC=[];ds=[]
                for i in range(M):
                    for j in range(i+1,M):
                        pi,pj=probs[i],probs[j]
                        BC.append(float(np.exp(np.log(np.sqrt(pi*pj)+np.sqrt((1-pi)*(1-pj))).sum())))
                        diff=code[i]-code[j];ds.append(float(np.sqrt(diff@F0@diff)))
                # Bhattacharyya union bound on ML message error, may be vacuous.
                union=min(1.,2*sum(BC)/M)
                pe_upper=clopper_lower_upper(error,n)[1]
                res.append({'bits':k,'n_codewords':M,'nominal_radius_fisher':radius,'codebook_seed':seed_i,
                            'n_messages':n,'ML_errors':error,'ML_error_rate':pe,'ML_error_upper_95':pe_upper,
                            'public_VAE_errors':public_error,'public_VAE_error_rate':public_error/n,
                            'nominal_min_separation_F0':min(ds),'min_Bhattacharyya_pairwise':min(BC),
                            'ML_pairwise_Bhattacharyya_union_bound':union,'KL_cover_codeword_mean':klcode,
                            'cover_stego_oracle_AUC':auc,
                            'Pinsker_TV_upper_bound':min(1.,float(np.sqrt(max(klcode,0)/2))),
                            'fano_I_lower_bound_bits':max(0.,k-h2(pe)-pe*np.log2(max(1,M-1)))})
    with (out/'r22_operational_payload_trials.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(res[0]));w.writeheader();w.writerows(res)
    agg=[]
    for k in [1,2,3,4]:
        for r in [3.,6.,9.,12.]:
            sub=[x for x in res if x['bits']==k and x['nominal_radius_fisher']==r]
            agg.append({'bits':k,'fisher_radius':r,'codebooks':len(sub),
                        'ML_error_mean':float(np.mean([x['ML_error_rate'] for x in sub])),
                        'public_error_mean':float(np.mean([x['public_VAE_error_rate'] for x in sub])),
                        'oracle_AUC_mean':float(np.mean([x['cover_stego_oracle_AUC'] for x in sub])),
                        'min_sep_mean':float(np.mean([x['nominal_min_separation_F0'] for x in sub])),
                        'KL_mean':float(np.mean([x['KL_cover_codeword_mean'] for x in sub]))})
    with (out/'r22_aggregate.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(agg[0]));w.writeheader();w.writerows(agg)
    return {'per_setting':agg,'n_codebooks_total':len(res),'n_messages_total':len(res)*n,
            'model_qualification':'True Bernoulli decoder conditional samples; synthetic latent codebooks; no message processing by original Algorithm 2; oracle model-known test and model likelihood decoder are privileged.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',type=Path,required=True);ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    m=load(args.checkpoint);pathsha=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest()
    assert pathsha=='e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61',f'Unexpected checkpoint {pathsha}'
    r21=test_r21(m,args.out,np.random.default_rng(SEED)); print('R21:',r21,flush=True)
    jumps=test_relu_jump(m);print('ReLU jumps',jumps[:3],flush=True)
    r22=test_r22(m,args.out);print('R22 complete',r22['n_messages_total'],flush=True)
    report={'seed':SEED,'checkpoint_sha256':pathsha,'protocol':'One 2-D MNIST Bernoulli VAE; R21 six latent centers, 8 MC samples per N; R22 four independent circular codebooks per k,radius; 256 samples per configuration. No original algorithm 2 optimization in R22.',
            'r21':r21,'relu_kink_examples':jumps,'r22':r22}
    (args.out/'experiment_results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__':main()