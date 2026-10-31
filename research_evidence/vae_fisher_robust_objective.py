"""Direct robust-utility conditional-score gradient on Bernoulli VAE.
Small pre-specified pilot, NOT original NG-Stego Algorithm 2 and no steganalysis.
Objective J(z)=1/4 sum_b E_{P_z(.|b)}[attack-decoder-success].
Gradient estimated via within-class covariance of utility and VAE score.
"""
from pathlib import Path
import sys,json,hashlib,time
import numpy as np
import torch
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from prototype_original import model_load,decode_p,bernoulli_kl
from operational_fisher_robust_7features import calibrate,bins,transforms
SD=20261031;CH=['jpeg_50','resize_14','shift_1','flip_0.01'];NTRAIN=3200;NTEST=2400

def sample(seed,p,n):return (np.random.default_rng(seed).random((n,784))<p).astype(np.float32)

def fisher_score(model,z,p):
 zz=torch.tensor(z,dtype=torch.float32,requires_grad=True)
 J=torch.autograd.functional.jacobian(lambda t:model.dec(t),zz,vectorize=True).detach().numpy().astype(float)
 F=J.T@((p*(1-p))[:,None]*J)
 return J,F

def utility_gradient(model,z,p,c,seed):
 x=sample(seed,p,NTRAIN);b=bins(x,c);J,F=fisher_score(model,z,p)
 score=(x.astype(float)-p[None,:])@J
 u=np.zeros(len(x),float)
 for j,ch in enumerate(CH):
  alt=transforms(x,ch,np.random.default_rng(seed+j*103+1))
  u+=(bins(alt,c)==b)/len(CH)
 grad=np.zeros(2)
 for bb in range(4):
  ii=b==bb
  if ii.sum()<70:raise RuntimeError('Bin occupancy too small')
  sc=score[ii];us=u[ii]
  grad+=(sc*us[:,None]).mean(axis=0)-sc.mean(axis=0)*us.mean()
 return grad/4,F,float(u.mean())

def choose_step(model,z0,p0,d,budget=.02):
 d=d/np.sqrt(d@d)
 lo=0.;hi=.05
 for _ in range(35):
  if bernoulli_kl(decode_p(model,z0+hi*d),p0)>budget:break
  hi*=2
 else:raise RuntimeError('Could not bracket KL')
 for _ in range(35):
  md=(lo+hi)*.5
  if bernoulli_kl(decode_p(model,z0+md*d),p0)<=budget:lo=md
  else:hi=md
 return z0+lo*d

def eval_conditional(model,z,cal,seed):
 p=decode_p(model,z);x=sample(seed,p,NTEST);b=bins(x,cal)
 q=np.bincount(b,minlength=4)/NTEST
 w=1/(4*q[b]);assert abs(w.mean()-1)<1e-9
 acc={}
 for j,ch in enumerate(CH):
  y=transforms(x,ch,np.random.default_rng(seed+j*103+1))
  acc[ch]=float(np.mean(w*(bins(y,cal)==b)))
 return {'mean':float(np.mean(list(acc.values()))),'acc':acc,'TV_bin_est':float(.5*np.sum(abs(q-.25)))}

def run():
 torch.set_num_threads(1);m=model_load(ROOT/'s5_vae_mnist.pt')
 centers=np.random.default_rng(SD+771).uniform(-.65,.65,size=(8,2))
 out={'status':'VAE generator-Fisher robust-objective pilot, NOT original Algorithm 2 and no detector','seed':SD,
      'centers':[],'train':NTRAIN,'eval':NTEST,'channels':CH,'KL_cap':.02,
      'checkpoint_sha256':hashlib.sha256((ROOT/'s5_vae_mnist.pt').read_bytes()).hexdigest()}
 for k,z0 in enumerate(centers):
  p0=decode_p(m,z0);cal=calibrate(sample(SD+k*711+1,p0,1800))
  grad,F,J0=utility_gradient(m,z0,p0,cal,SD+k*711+7)
  if np.linalg.norm(grad)<1e-10:raise RuntimeError('no gradient')
  ds={'matched':z0,'fisher':np.linalg.solve(F+1e-6*np.eye(2),grad),'euclidean':grad}
  results={}
  for j,sty in enumerate(['matched','fisher','euclidean']):
   z=z0 if sty=='matched' else choose_step(m,z0,p0,ds[sty])
   r=eval_conditional(m,z,cal,SD+k*711+500)
   r.update({'z':z.tolist(),'KL':bernoulli_kl(decode_p(m,z),p0)})
   results[sty]=r
  out['centers'].append({'z0':z0.tolist(),'grad':grad.tolist(),'F':F.tolist(),'Jtrain':J0,'methods':results})
  print(k, 'F',round(results['fisher']['mean'],5),'E',round(results['euclidean']['mean'],5),'M',round(results['matched']['mean'],5),flush=True)
 diff=np.array([v['methods']['fisher']['mean']-v['methods']['euclidean']['mean'] for v in out['centers']])
 out['comparison']={'mean':float(diff.mean()),'wins':int((diff>0).sum()),'diffs':diff.tolist()}
 (ROOT/'vae_fisher_robust_objective_results.json').write_text(json.dumps(out,indent=2))
 print('RESULT',out['comparison'])
if __name__=='__main__':run()
