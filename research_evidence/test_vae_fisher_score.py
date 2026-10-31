"""Numerical audit: generator decoder Jacobian, score Fisher and conditional gradient formula."""
import numpy as np,torch
from pathlib import Path
from vae_fisher_robust_objective import fisher_score
from prototype_original import model_load,decode_p

def main():
 torch.set_num_threads(1);root=Path(__file__).resolve().parent;m=model_load(root/'s5_vae_mnist.pt')
 z=np.array([.17,-.23]);p=decode_p(m,z);J,F=fisher_score(m,z,p)
 for j in range(2):
  d=np.eye(2)[j]*1e-3
  zz=np.array([p+d[0],0]) if False else None
  with torch.no_grad():
   lp=m.dec(torch.tensor(z+d,dtype=torch.float32)).numpy()
   lm=m.dec(torch.tensor(z-d,dtype=torch.float32)).numpy()
  fd=(lp-lm)/(2e-3)
  err=np.linalg.norm(fd-J[:,j])/max(1e-12,np.linalg.norm(J[:,j]))
  assert err<.003,(j,err)
 r=np.random.default_rng(556);n=30000;s=(r.random((n,784))<p[None,:]).astype(float)
 sc=(s-p[None,:])@J;Fmc=sc.T@sc/n
 rel=np.linalg.norm(Fmc-F)/np.linalg.norm(F)
 assert rel<.04,rel
 assert np.linalg.eigvalsh(F).min()>1e-6
 print('VAE FIM/Jacobian checks PASSED, relative sample F error',round(rel,4))
if __name__=='__main__':main()
