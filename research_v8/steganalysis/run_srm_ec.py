#!/usr/bin/env python3
"""Frozen V8 Tier-A: full SRM + FLD Ensemble with paired bootstrap."""
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
import sealwatch as sw

SEED=12345
BOOT_SEED=20260910
BOOT_N=10000

def cols(df):
    n=next(c for c in ['image','filename','file','name'] if c in df.columns)
    s=next(c for c in ['split','partition'] if c in df.columns)
    return n,s

def failure_union(summary, eps):
    obj=json.loads(Path(summary).read_text())
    fs=obj.get('failures',obj.get('failure_cases',[]))
    return {str(x['image']) for x in fs if str(x.get('epsilon'))==str(eps)}

def files_for(manifest, eps, summary):
    df=pd.read_csv(manifest); n,s=cols(df)
    df=df[df[s].isin(['fit','calibration'])].copy()
    bad=failure_union(summary,eps)
    if bad: df=df[~df[n].astype(str).isin(bad)]
    return [str(x) for x in df[df[s]=='fit'][n]], [str(x) for x in df[df[s]=='calibration'][n]]

def resolve(root,name):
    p=Path(root)/name
    if p.exists(): return p
    hits=list(Path(root).rglob(name))
    if len(hits)!=1: raise FileNotFoundError(f'{name}: {len(hits)} matches in {root}')
    return hits[0]

def feature(path):
    return sw.tools.flatten(sw.srm.extract_from_file(path)).astype(np.float32)

def matrix(root,names,cache):
    cache=Path(cache)
    if cache.exists():
        x=np.load(cache)
        if x.shape[0]!=len(names): raise ValueError(f'cache rows mismatch: {cache}')
        return x
    arr=np.stack([feature(resolve(root,n)) for n in names],axis=0)
    cache.parent.mkdir(parents=True,exist_ok=True); np.save(cache,arr)
    return arr

def metrics(clf,Xc,Xs):
    cc=clf.predict_confidence(Xc); ss=clf.predict_confidence(Xs)
    pc=clf.predict(Xc); ps=clf.predict(Xs)
    fp=(pc>0).astype(float); fn=(ps<0).astype(float)
    pe=float(0.5*(fp.mean()+fn.mean()))
    y=np.r_[np.zeros(len(cc)),np.ones(len(ss))]
    score=np.r_[cc,ss]
    auc=float(roc_auc_score(y,score))
    return pe,auc,fp,fn,cc,ss

def paired_boot(fp,fn,cc,ss):
    rng=np.random.default_rng(BOOT_SEED); n=len(fp)
    pe=[]; auc=[]
    y0=np.r_[np.zeros(n),np.ones(n)]
    for _ in range(BOOT_N):
        ix=rng.integers(0,n,n)
        pe.append(0.5*(fp[ix].mean()+fn[ix].mean()))
        scores=np.r_[cc[ix],ss[ix]]
        auc.append(roc_auc_score(y0,scores))
    return {
      'pe_ci95':[float(np.quantile(pe,.025)),float(np.quantile(pe,.975))],
      'auc_ci95':[float(np.quantile(auc,.025)),float(np.quantile(auc,.975))]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cover-root',required=True)
    ap.add_argument('--stego-root',required=True,help='root for one eps/method condition, containing fit/ and calibration/')
    ap.add_argument('--manifest',default='research_v8/results/bossbase_split_manifest_v4.csv')
    ap.add_argument('--summary',default='research_v8/results/V8_STC_RERUN/V8_STC_RERUN_SUMMARY.json')
    ap.add_argument('--epsilon',required=True,choices=['0.0002','0.0008'])
    ap.add_argument('--method',required=True,choices=['uniform_shrink','IG_matched'])
    ap.add_argument('--cache-dir',required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    tr,te=files_for(args.manifest,args.epsilon,args.summary)
    croot=Path(args.cover_root); sroot=Path(args.stego_root)
    cd=Path(args.cache_dir); tag=f"{args.epsilon}_{args.method}"
    Xc_tr=matrix(croot,tr,cd/f'cover_{args.epsilon}_fit.npy')
    Xc_te=matrix(croot,te,cd/f'cover_{args.epsilon}_calibration.npy')
    Xs_tr=matrix(sroot/'fit',tr,cd/f'stego_{tag}_fit.npy')
    Xs_te=matrix(sroot/'calibration',te,cd/f'stego_{tag}_calibration.npy')
    trainer=sw.ensemble_classifier.FldEnsembleTrainer(
        Xc=np.ascontiguousarray(Xc_tr),Xs=np.ascontiguousarray(Xs_tr),
        seed=SEED,verbose=1)
    clf,records=trainer.train()
    pe,auc,fp,fn,cc,ss=metrics(clf,Xc_te,Xs_te)
    out={
      'detector':'SRM34671+FLD-Ensemble','sealwatch_seed':SEED,
      'epsilon':args.epsilon,'method':args.method,
      'n_train_pairs':len(tr),'n_test_pairs':len(te),
      'balanced_error':pe,'roc_auc':auc,'accuracy':1-pe,
      'false_positive_rate':float(fp.mean()),'false_negative_rate':float(fn.mean()),
      'd_sub':int(clf.d_sub),'num_base_learners':int(clf.num_base_learners),
      'training_records':records,
      'bootstrap':paired_boot(fp,fn,cc,ss),
      'test_names':te,'cover_confidence':cc.tolist(),'stego_confidence':ss.tolist(),
      'cover_error':fp.tolist(),'stego_error':fn.tolist()
    }
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(out,indent=2))
    print(json.dumps({k:out[k] for k in ['epsilon','method','n_train_pairs','n_test_pairs','balanced_error','roc_auc','accuracy','d_sub','num_base_learners','bootstrap']},indent=2))

if __name__=='__main__':
    main()
