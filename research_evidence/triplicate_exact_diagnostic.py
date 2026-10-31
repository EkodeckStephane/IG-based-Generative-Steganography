#!/usr/bin/env python3
"""Independent post-hoc audit: exact triplicate majority success on finite MNIST
source under fixed-seed transformations. Estimates conditional error transition
probabilities and enumerates all 4^3 error vectors; no learned parameters.
"""
import sys,json,hashlib
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from operational_fisher_robust_7features import load,calibrate,bins,tilt_stats,transforms,q_dist
SD=20261031

def exactly_three(p,clean,altered):
    q=np.bincount(clean,weights=p,minlength=4)
    prob=np.zeros(4)
    for b in range(4):
        w=p[clean==b]/q[b]
        err=np.bitwise_xor(clean[clean==b],altered[clean==b])
        prob+=np.bincount(err,weights=w,minlength=4)/4
    assert abs(sum(prob)-1)<1e-8
    r=0.
    for a in range(4):
        for b in range(4):
            for c in range(4):
                hi=((a>>1)&1)+((b>>1)&1)+((c>>1)&1)
                lo=(a&1)+(b&1)+(c&1)
                if hi<=1 and lo<=1:r+=prob[a]*prob[b]*prob[c]
    return float(r),prob.tolist()

def main():
    tr=load(HERE/'mnist_train_real.gz');te=load(HERE/'mnist_test_real.gz')
    cal=calibrate(tr[5000:20000]);clean=bins(te,cal)
    T=tilt_stats(te);o=tilt_stats(tr[20000:40000]);T=(T-o.mean(axis=0))/o.std(axis=0)
    results={'source':'10k original MNIST fixed test pool','assumption':'three draws iid with fresh independent uniform OTP masks, conditional on same 2-bit payload','methods':{},'seed':SD}
    paths=['operational_fisher_2features_results.json','operational_fisher_7features_results.json']
    chans=['jpeg_50','blur_0.6','resize_14','shift_1','flip_0.001','flip_0.01']
    observed={}
    for j,ch in enumerate(chans):
        a=transforms(te,ch,np.random.default_rng(SD+100101+j*271))
        observed[ch]=bins(a,cal)
    for path in paths:
        d=json.loads((HERE/path).read_text());style='7features' if '7features' in path else '2features'
        fs=T if style=='7features' else T[:,:2] # below recompute proper 2feature scaling
        if style=='2features':
            from operational_fisher_robust_v2 import stats
            a=stats(tr[20000:40000]);fs=(stats(te)-a.mean(0))/a.std(0)
        runs={'matched':np.zeros(fs.shape[1])}
        for cap,rr in d['results'].items():
            for meth in ('fisher','euclidean'):runs[f'{meth}_TVcap{cap}']=np.array(rr[meth]['theta'])
        allres={}
        for name,theta in runs.items():
            p=np.exp(fs@theta-np.logaddexp.reduce(fs@theta))
            x={}
            for ch,bp in observed.items():
                tripl,err=exactly_three(p,clean,bp)
                x[ch]={'triple_exact_accuracy':tripl,'effective_bits_per_image':tripl*2/3,'xor_error_probabilities':err}
            allres[name]=x
        results['methods'][style]=allres
    (HERE/'triple_exact_results.json').write_text(json.dumps(results,indent=2))
    for method,rs in results['methods'].items():
        print(method)
        for name in ['matched','fisher_TVcap0.05','euclidean_TVcap0.05']:
            print(name,{ch:round(rs[name][ch]['triple_exact_accuracy'],5) for ch in chans})
if __name__=='__main__':main()
