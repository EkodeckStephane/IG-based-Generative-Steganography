#!/usr/bin/env python3
"""Aggregate deep V8 results without hiding adverse detector outcomes."""
import argparse,json,math
from pathlib import Path
import numpy as np
from scipy.stats import t
from sklearn.metrics import roc_auc_score
SEEDS=(12345,23456,34567)

def ci_t(vals):
    a=np.asarray(vals,float); n=len(a); mean=float(a.mean())
    if n<2:return [mean,mean]
    h=float(t.ppf(.975,n-1)*a.std(ddof=1)/math.sqrt(n)); return [mean-h,mean+h]

def paired_diff(a,b,nboot=10000,seed=20260912):
    assert a['test_names']==b['test_names']; n=len(a['test_names']); rng=np.random.default_rng(seed); dpe=[];dauc=[]; y=np.r_[np.zeros(n),np.ones(n)]
    ae=np.asarray(a['cover_error']); af=np.asarray(a['stego_error']); be=np.asarray(b['cover_error']); bf=np.asarray(b['stego_error'])
    ac=np.asarray(a['cover_scores']);as_=np.asarray(a['stego_scores']);bc=np.asarray(b['cover_scores']);bs=np.asarray(b['stego_scores'])
    for _ in range(nboot):
        ix=rng.integers(0,n,n); dpe.append(.5*(ae[ix].mean()+af[ix].mean())-.5*(be[ix].mean()+bf[ix].mean()))
        dauc.append(roc_auc_score(y,np.r_[ac[ix],as_[ix]])-roc_auc_score(y,np.r_[bc[ix],bs[ix]]))
    return {'IG_minus_uniform_balanced_error_mean':float(np.mean(dpe)),'IG_minus_uniform_balanced_error_ci95':[float(np.quantile(dpe,.025)),float(np.quantile(dpe,.975))],
            'IG_minus_uniform_auc_mean':float(np.mean(dauc)),'IG_minus_uniform_auc_ci95':[float(np.quantile(dauc,.025)),float(np.quantile(dauc,.975))]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--deep-dir',required=True);ap.add_argument('--srm-json');ap.add_argument('--out',required=True);args=ap.parse_args(); root=Path(args.deep_dir)
    final={'deep':{},'srm_ec':None,'decision_inputs':{}}
    for model in ['srnet','siastegnet']:
        final['deep'][model]={}
        for eps in ['0.0002','0.0008']:
            cond={}
            for method in ['uniform_shrink','IG_matched']:
                rows=[]
                for seed in SEEDS:
                    p=root/f'{model}_{eps}_{method}_seed{seed}.json'
                    if p.exists(): rows.append(json.loads(p.read_text()))
                cond[method]={'completed_seeds':[r['seed'] for r in rows],'n_completed':len(rows)}
                if rows:
                    for metric in ['balanced_error','roc_auc','accuracy']:
                        vals=[r[metric] for r in rows];cond[method][metric]={'per_seed':dict(zip([str(r['seed']) for r in rows],vals)),'mean':float(np.mean(vals)),'std':float(np.std(vals,ddof=1)) if len(vals)>1 else 0.0,'t_ci95':ci_t(vals)}
            paired={}
            for seed in SEEDS:
                pu=root/f'{model}_{eps}_uniform_shrink_seed{seed}.json';pi=root/f'{model}_{eps}_IG_matched_seed{seed}.json'
                if pu.exists() and pi.exists(): paired[str(seed)]=paired_diff(json.loads(pi.read_text()),json.loads(pu.read_text()),seed=20260912+seed)
            final['deep'][model][eps]={'conditions':cond,'paired_IG_vs_uniform':paired}
    if args.srm_json and Path(args.srm_json).exists(): final['srm_ec']=json.loads(Path(args.srm_json).read_text())
    srnet_complete=all(final['deep']['srnet'][e]['conditions'][m]['n_completed']==3 for e in ['0.0002','0.0008'] for m in ['uniform_shrink','IG_matched'])
    sia_complete=all(final['deep']['siastegnet'][e]['conditions'][m]['n_completed']==3 for e in ['0.0002','0.0008'] for m in ['uniform_shrink','IG_matched'])
    final['decision_inputs']={'srm_complete':final['srm_ec'] is not None,'srnet_three_seed_complete':srnet_complete,'siastegnet_three_seed_complete':sia_complete,'minimum_deep_closure_available':srnet_complete or sia_complete,
      'note':'This aggregator does not auto-declare C6 PASS; final claim/code/data audit must inspect detector disadvantages and provenance.'}
    Path(args.out).write_text(json.dumps(final,indent=2));print(json.dumps(final['decision_inputs'],indent=2))
if __name__=='__main__':main()