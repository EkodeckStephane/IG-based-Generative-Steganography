#!/usr/bin/env python3
"""Ablation of actual generator Fisher vs Euclidean entropy-ascent using a robust
message decoder on samples from the fixed Bernoulli VAE.
This is NOT the original Algorithm 2 or adversarial detector study."""
import sys,json,time,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from prototype_original import model_load,choose_latent,decode_p
sys.path.insert(0,str(ROOT))
from operational_fisher_robust_7features import calibrate,bins,transforms
SEED=20261031;CH=['jpeg_50','blur_0.6','resize_14','shift_1','flip_0.001','flip_0.01'];N=1000

def sample(rng,p,n):return (rng.random((n,784))<p).astype(np.float32)

def run():
 st=time.time();rng=np.random.default_rng(SEED);m=model_load(ROOT/'s5_vae_mnist.pt')
 zz=np.random.default_rng(SEED+7).uniform(-.65,.65,(12,2))
 out={'status':'bounded VAE generator-FIM test: synthetic Bernoulli samples, no detector, not Algorithm 2','seed':SEED,'centers':[],
      'ncal':900,'neval':N,'transformations':CH,
      'model_sha256':hashlib.sha256((ROOT/'s5_vae_mnist.pt').read_bytes()).hexdigest()}
 for j,z0 in enumerate(zz):
  item={'center':z0.tolist(),'methods':{}}
  for ii,method in enumerate(('matched','fisher','euclidean')):
   z,kl,H,meta=choose_latent(m,z0,method,.02);p=decode_p(m,z)
   cal=calibrate(sample(np.random.default_rng(SEED+j*511+ii*97+1),p,900))
   s=sample(np.random.default_rng(SEED+j*511+ii*97+2),p,N)
   bc=bins(s,cal);q=np.bincount(bc,minlength=4).astype(float)/N
   if min(q)<=0:raise ValueError('Empty symbol class')
   w=1/(4*q[bc]); assert np.isclose(w.mean(),1.,atol=1e-10)
   acc={};error={}
   for c,ch in enumerate(CH):
    alt=transforms(s,ch,np.random.default_rng(SEED+j*511+ii*97+c*13+3))
    got=bins(alt,cal);acc[ch]=float(np.mean(w*(got==bc)))
   item['methods'][method]={'z':z.tolist(),'KL':float(kl),'h':float(H),'q':q.tolist(),
      'tv_with_Ptheta_estimate':float(.5*abs(q-.25).sum()),'acc':acc,'avg_robust':float(np.mean(list(acc.values())))}
  out['centers'].append(item)
  print('center',j,'F',round(item['methods']['fisher']['avg_robust'],4),
        'E',round(item['methods']['euclidean']['avg_robust'],4),'M',round(item['methods']['matched']['avg_robust'],4),flush=True)
 differences=np.array([x['methods']['fisher']['avg_robust']-x['methods']['euclidean']['avg_robust'] for x in out['centers']])
 out['paired_difference']={'values':differences.tolist(),'mean':float(differences.mean()),'wins':int((differences>0).sum()),
                           'losses':int((differences<0).sum()),'median':float(np.median(differences))}
 out['elapsed_seconds']=time.time()-st
 (ROOT/'vae_generator_results.json').write_text(json.dumps(out,indent=2))
 print('DIFF',out['paired_difference'],'TIME',round(out['elapsed_seconds'],2))
if __name__=='__main__':run()
