"""Frozen theta evaluated on a separate 20k held-out original MNIST training subset.
No hyperparameters or partitions are reselected on this subset."""
import json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from operational_fisher_robust_7features import load,calibrate,bins,tilt_stats,stats,transforms,measures
SEED=20261031

def main():
 tr=load(HERE/'mnist_train_real.gz');c=calibrate(tr[5000:20000]);v=tr[40000:60000]
 b=bins(v,c);chs=['jpeg_50','blur_0.6','resize_14','shift_1','flip_0.001','flip_0.01']
 good={'clean':np.ones(len(v))}
 for j,ch in enumerate(chs):
  x=transforms(v,ch,np.random.default_rng(SEED+200201+j*271))
  good[ch]=(bins(x,c)==b).astype(float)
 out={'source':'train images 40k:60k, never used in calibration or optimizer fitting','n':len(v),'frozen':True,'models':{}}
 for which,name,fun in [('2features','operational_fisher_2features_results.json',stats),('7features','operational_fisher_7features_results.json',tilt_stats)]:
  data=json.loads((HERE/name).read_text());Z=fun(tr[20000:40000]);V=(fun(v)-Z.mean(0))/Z.std(0)
  rows={'matched':measures(V,b,good,np.zeros(V.shape[1]))}
  for cap,ex in data['results'].items():
   for meth in ('fisher','euclidean'):
    rows[f'{meth}_cap{cap}']=measures(V,b,good,np.array(ex[meth]['theta']))
  out['models'][which]=rows
  print(which,'matched',round(rows['matched']['objective'],6))
  for cap in data['caps_TV']:
   f=rows[f'fisher_cap{cap}'];e=rows[f'euclidean_cap{cap}']
   print('cap',cap,'F',round(f['objective'],6),'E',round(e['objective'],6),
         'diff',round(f['objective']-e['objective'],7),'TV(F,E)',round(f['TV'],4),round(e['TV'],4))
 (HERE/'external_validation_20k_results.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
