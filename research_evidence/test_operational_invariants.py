"""Independent invariant tests for the finite-source diagnostic; no MNIST data needed."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np
from operational_fisher_robust_7features import probabilities,measures,gradient,find_feasible
from triplicate_exact_diagnostic import exactly_three

def run():
 rng=np.random.default_rng(45)
 n=8000;T=rng.normal(size=(n,3));b=np.tile(np.arange(4,dtype=np.uint8),n//4)
 rng.shuffle(b)
 quality={k:rng.random(n)<.77 for k in ['jpeg_50','blur_0.6','resize_14','shift_1','flip_0.001','flip_0.01']}
 theta=np.array([.05,-.04,.02]);p=probabilities(T,theta)
 assert np.isclose(p.sum(),1)
 q=np.bincount(b,weights=p,minlength=4)
 Q=p/(4*q[b])
 assert np.isclose(Q.sum(),1)
 assert np.isclose(.5*np.sum(np.abs(Q-p)),.5*np.sum(np.abs(q-.25)),atol=1e-12)
 # Exact reweighted objective gradient is covariance within message cells.
 g,F=gradient(T,b,quality)
 def objective(z):return measures(T,b,quality,z)['objective']
 for j in range(3):
  v=np.zeros(3);v[j]=1e-5
  fd=(objective(v)-objective(-v))/(2e-5)
  assert abs(fd-g[j])<1e-7,(fd,g[j])
 assert np.linalg.eigvalsh(F).min()>0
 d=np.linalg.solve(F,g)
 gd=d/np.sqrt(d@F@d)
 eu=g/np.sqrt(g@F@g)
 assert (g@gd)>=(g@eu)-1e-12
 # Exact 3-fold majority enumeration: perfect and random error limits.
 f=np.full(n,1/n)
 perfect=exactly_three(f,b,b)[0]
 assert abs(perfect-1)<1e-12
 shifted=np.bitwise_xor(b,1)
 assert exactly_three(f,b,shifted)[0]<1e-10
 # 100% per-symbol correctness implies zero decoding errors for all methods.
 print('All 7 invariant groups passed: normalized Q, TV identity, gradient FD, F SPD, steepest ascent, repetition extremes.')
if __name__=='__main__':run()
