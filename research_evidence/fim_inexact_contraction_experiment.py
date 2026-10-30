"""Independent quadratic-model sensitivity check. Not an NG-Stego experiment."""
import csv
from pathlib import Path
import numpy as np
rng=np.random.default_rng(20261030)
d=8
Q,_=np.linalg.qr(rng.standard_normal((d,d)))
F=Q@np.diag(np.geomspace(1,100,d))@Q.T
w,V=np.linalg.eigh(F);H=V@np.diag(np.sqrt(w))@V.T
rows=[]
for delta in (0,.05,.1,.2,.3,.4,.49,.55,.7):
 ratios=[]
 for _ in range(100):
  B=rng.standard_normal((d,d));B=(B+B.T)/2
  B=B/np.linalg.norm(B,ord=2)*delta if delta else B*0
  Fhat=H@(np.eye(d)+B)@H
  e=rng.standard_normal(d);en=e-np.linalg.solve(Fhat,F@e)
  ratios.append(float(np.sqrt((en@F@en)/(e@F@e))))
 rows.append((delta,max(ratios),np.mean(ratios),delta/(1-delta),100))
p=Path(__file__).with_name('fim_inexact_contraction_results.csv')
with p.open('w',newline='') as f:
 writer=csv.writer(f);writer.writerow(['delta','observed_max','observed_mean','theoretical_bound','trials']);writer.writerows(rows)
for r in rows: print(r)
assert all(r[1] <= r[3]+1e-9 for r in rows)

# Deterministic sharpness: Fhat=(1-delta)F, yielding exact ratio delta/(1-delta).
for delta in (0.05, 0.2, 0.4, 0.49, 0.7):
    Fhat = (1-delta)*F
    e = np.arange(1,d+1,dtype=float)
    en = e-np.linalg.solve(Fhat,F@e)
    observed = float(np.sqrt((en@F@en)/(e@F@e)))
    bound = delta/(1-delta)
    assert abs(observed-bound)<1e-10, (delta, observed, bound)
    print('deterministic sharpness:', delta, observed, bound)
