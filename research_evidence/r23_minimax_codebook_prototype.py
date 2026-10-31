"""Exploratory discriminator/codebook co-training on a fixed Bernoulli MNIST-VAE.
NEW VARIANT, NOT manuscript Algorithm 2. Uses biased straight-through Bernoulli.
Source provenance: R23/R27 research package, 2026-10-31.
"""
from pathlib import Path
import json,sys,os,hashlib
import numpy as np,torch
from torch import nn
from torch.nn import functional as F
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import roc_auc_score
from scipy.special import logsumexp
ROOT=Path(os.getenv('DSP_PROJECT_ROOT',str(Path(__file__).resolve().parents[1])))
sys.path.insert(0,str(ROOT/'Version_1.0'))
import benchmark_s5_comparison as b
HERE=Path(__file__).resolve().parent

def oracle(x,p0,pc):
    x=x.astype(float);p0=np.clip(p0,1e-7,1-1e-7)
    pc=np.clip(pc,1e-7,1-1e-7)
    q=x@np.log(pc).T+(1-x)@np.log1p(-pc).T
    c=x@np.log(p0)+(1-x)@np.log1p(-p0)
    return logsumexp(q,axis=1)-np.log(4)-c

def sample_gen(p0,pc,rng,n):
    cover=(rng.random((n,784))<p0).astype(np.float32)
    msg=rng.integers(4,size=n)
    stego=(rng.random((n,784))<pc[msg]).astype(np.float32)
    return cover,stego,msg

def evaluate(model,z,seed,n_train=200,n_test=2000):
    with torch.no_grad():pc=model.decode_prob(torch.tensor(z,dtype=torch.float32)).numpy()
    p0=b.decoder_probs(model,np.zeros(2));rng=np.random.default_rng(seed)
    cv,st,_=sample_gen(p0,pc,rng,n_train)
    ct,stt,mt=sample_gen(p0,pc,rng,n_test)
    clf=make_pipeline(StandardScaler(),SVC(C=2,kernel='rbf',gamma='scale'))
    clf.fit(np.vstack([cv,st]),np.r_[np.zeros(n_train),np.ones(n_train)])
    scores=clf.decision_function(np.vstack([ct,stt]))
    test=np.vstack([ct,stt]);labels=np.r_[np.zeros(n_test),np.ones(n_test)]
    auc=float(roc_auc_score(labels,scores))
    oracle_auc=float(roc_auc_score(labels,oracle(test,p0,pc)))
    q=np.clip(pc,1e-7,1-1e-7)
    ll=stt@np.log(q).T+(1-stt)@np.log1p(-q).T
    with torch.no_grad():mu,_=model.encode(torch.as_tensor(stt,dtype=torch.float32))
    return {'RBF_SVM_AUC':auc,'known_model_oracle_AUC':oracle_auc,
      'exact_ML_message_rate':float(np.mean(np.argmax(ll,axis=1)==mt)),
      'public_VAE_encoder_message_rate':float(np.mean(
        np.argmin(np.sum((mu.numpy()[:,None,:]-z[None,:,:])**2,axis=2),axis=1)==mt)),
      'MSE_stego_vs_cover_expectation':float(np.square(stt-p0).mean()),
      'n_train_each':n_train,'n_test_each':n_test}

def train(model,init,seed=301,adv_weight=1.,decode_weight=.25,steps=100):
    torch.manual_seed(seed)
    z=nn.Parameter(torch.tensor(init,dtype=torch.float32))
    critic=nn.Sequential(nn.Linear(784,64),nn.ReLU(),nn.Linear(64,1))
    copt=torch.optim.Adam(critic.parameters(),lr=3e-4,weight_decay=1e-3)
    zopt=torch.optim.Adam([z],lr=.015)
    p0=model.decode_prob(torch.zeros(1,2)).detach()
    track=[]
    for epoch in range(steps):
        for _ in range(3):
            copt.zero_grad()
            with torch.no_grad():
                pr=model.decode_prob(z)
                m=torch.randint(0,4,(128,))
                ste=torch.bernoulli(pr[m])
                cov=torch.bernoulli(p0.expand(128,-1))
            logits=torch.cat([critic(cov),critic(ste)],0).view(-1)
            labels=torch.cat([torch.zeros(128),torch.ones(128)])
            closs=F.binary_cross_entropy_with_logits(logits,labels)
            closs.backward();copt.step()
        for q in critic.parameters():q.requires_grad_(False)
        zopt.zero_grad()
        pr=model.decode_prob(z);m=torch.randint(0,4,(256,))
        hard=(torch.rand(256,784)<pr[m]).float()
        # Straight-through estimator is biased, NOT an exact gradient.
        ste=hard+pr[m]-pr[m].detach()
        adv=F.binary_cross_entropy_with_logits(critic(ste).view(-1),torch.zeros(256))
        q=pr.clamp(1e-6,1-1e-6)
        ll=ste@q.log().T+(1-ste)@torch.log1p(-q).T
        dec=F.cross_entropy(ll,m)
        dis=torch.cdist(z,z)+10*torch.eye(4)
        sep=torch.relu(.10-dis).square().mean()
        loss=adv_weight*adv+decode_weight*dec+4*sep
        loss.backward();torch.nn.utils.clip_grad_norm_([z],5.)
        zopt.step()
        with torch.no_grad():z.clamp_(-2,2)
        for q in critic.parameters():q.requires_grad_(True)
        if epoch%20==0 or epoch==steps-1:
            track.append({'step':epoch,'adv_loss':float(adv.detach()),
              'decode_loss':float(dec.detach()),'min_separation':float(
              (dis.detach()+10*torch.eye(4)).min()),'z':z.detach().numpy().tolist()})
    return z.detach().numpy(),track

def main():
    torch.set_num_threads(1)
    model=b.load_model();model.eval()
    for p in model.parameters():p.requires_grad_(False)
    angles=np.arange(4)*np.pi/2+np.pi/7
    init=np.column_stack((.2*np.cos(angles),.2*np.sin(angles))).astype(np.float32)
    result={'scope':'Fixed public VAE, one initialization, biased STE, not Algorithm 2',
      'seed':20261031,'init_codebook':init.tolist(),
      'checkpoint_sha256':hashlib.sha256((ROOT/'data/s5_vae_mnist.pt').read_bytes()).hexdigest(),'experiments':{}}
    for k,(beta,gamma) in enumerate(((0.,.25),(1.,.25),(3.,.25))):
        z,hist=train(model,init,seed=20261031+k,adv_weight=beta,decode_weight=gamma,steps=100)
        key=f'adversarial_weight_{beta}'
        result['experiments'][key]={'after_codebook':z.tolist(),'train_history':hist,
            'before':evaluate(model,init,100001+k),'after':evaluate(model,z,300001+k)}
    out=HERE/'r23_minimax_codebook_results.json';out.write_text(json.dumps(result,indent=2))
    print('Wrote',out)
if __name__=='__main__':main()
