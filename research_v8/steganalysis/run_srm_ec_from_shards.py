#!/usr/bin/env python3
"""Train/evaluate SealWatch FLD ensembles from DDE-SRM feature shards.

Input shards are produced by `research_v8/src/run_v8_srm_shard.py` and contain
cover, four V8 conditions, and two image-specific-payload MiPOD baselines.
"""
import argparse, json, hashlib
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
import sealwatch as sw

SEED=12345; BOOT_SEED=20260910; BOOT_N=10000
VARIANTS={
 '0.0002':('e2e4_uniform','e2e4_ig','mipod_e2e4'),
 '0.0008':('e8e4_uniform','e8e4_ig','mipod_e8e4'),
}

def load_variant(root,variant):
    files=sorted(Path(root).glob(f'{variant}_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9].npz'))
    if not files: raise FileNotFoundError(f'no shards for {variant}')
    X=[]; names=[]; splits=[]; success=[]; bits=[]; seen=set(); sub=None; dims=None
    for f in files:
        z=np.load(f,allow_pickle=False); ns=[str(x) for x in z['names']]
        if seen.intersection(ns): raise RuntimeError(f'duplicate names in {variant}: {f}')
        seen.update(ns); X.append(z['X']); names.extend(ns); splits.extend([str(x) for x in z['splits']]); success.extend(z['success'].astype(bool).tolist()); bits.extend(z['message_bits'].astype(int).tolist())
        sm=[str(x) for x in z['submodels']]; dm=z['submodel_dims'].astype(int).tolist()
        if sub is None: sub, dims=sm,dm
        elif sub!=sm or dims!=dm: raise RuntimeError('SRM submodel ordering changed across shards')
    X=np.concatenate(X,axis=0)
    if X.shape!=(len(names),34671): raise RuntimeError(f'{variant}: unexpected shape {X.shape}')
    return {'X':X,'names':np.asarray(names),'splits':np.asarray(splits),'success':np.asarray(success,bool),'message_bits':np.asarray(bits,int),'submodels':sub,'dims':dims}

def reorder(d,order):
    idx={n:i for i,n in enumerate(d['names'])}; ii=np.asarray([idx[n] for n in order],int)
    return d['X'][ii],d['splits'][ii],d['success'][ii],d['message_bits'][ii]

def metrics(clf,Xc,Xs):
    cc=clf.predict_confidence(Xc); ss=clf.predict_confidence(Xs); pc=clf.predict(Xc); ps=clf.predict(Xs)
    fp=(pc>0).astype(float); fn=(ps<0).astype(float); pe=float(.5*(fp.mean()+fn.mean()))
    auc=float(roc_auc_score(np.r_[np.zeros(len(cc)),np.ones(len(ss))],np.r_[cc,ss]))
    return {'balanced_error':pe,'balanced_accuracy':1-pe,'accuracy':1-pe,'roc_auc':auc,'false_positive_rate':float(fp.mean()),'false_negative_rate':float(fn.mean()),
            'cover_confidence':cc,'stego_confidence':ss,'cover_error':fp,'stego_error':fn}

def boot_one(m):
    rng=np.random.default_rng(BOOT_SEED); n=len(m['cover_error']); pes=[]; aucs=[]; y=np.r_[np.zeros(n),np.ones(n)]
    for _ in range(BOOT_N):
        ix=rng.integers(0,n,n); pes.append(.5*(m['cover_error'][ix].mean()+m['stego_error'][ix].mean())); aucs.append(roc_auc_score(y,np.r_[m['cover_confidence'][ix],m['stego_confidence'][ix]]))
    return {'pe_ci95':[float(np.quantile(pes,.025)),float(np.quantile(pes,.975))], 'auc_ci95':[float(np.quantile(aucs,.025)),float(np.quantile(aucs,.975))]}

def boot_diff(a,b):
    rng=np.random.default_rng(BOOT_SEED+1); n=len(a['cover_error']); dpe=[];dauc=[]; y=np.r_[np.zeros(n),np.ones(n)]
    for _ in range(BOOT_N):
        ix=rng.integers(0,n,n)
        pea=.5*(a['cover_error'][ix].mean()+a['stego_error'][ix].mean()); peb=.5*(b['cover_error'][ix].mean()+b['stego_error'][ix].mean())
        aa=roc_auc_score(y,np.r_[a['cover_confidence'][ix],a['stego_confidence'][ix]]); ab=roc_auc_score(y,np.r_[b['cover_confidence'][ix],b['stego_confidence'][ix]])
        dpe.append(pea-peb); dauc.append(aa-ab)
    return {'IG_minus_uniform_balanced_error_ci95':[float(np.quantile(dpe,.025)),float(np.quantile(dpe,.975))],
            'IG_minus_uniform_auc_ci95':[float(np.quantile(dauc,.025)),float(np.quantile(dauc,.975))],
            'IG_minus_uniform_balanced_error_mean':float(np.mean(dpe)),'IG_minus_uniform_auc_mean':float(np.mean(dauc))}

def serial(m):
    return {k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in m.items()}

def train_condition(Xc_tr,Xs_tr,Xc_te,Xs_te):
    trainer=sw.ensemble_classifier.FldEnsembleTrainer(Xc=np.ascontiguousarray(Xc_tr),Xs=np.ascontiguousarray(Xs_tr),seed=SEED,verbose=1)
    clf,records=trainer.train(); m=metrics(clf,Xc_te,Xs_te); m['bootstrap']=boot_one(m); m['d_sub']=int(clf.d_sub);m['num_base_learners']=int(clf.num_base_learners);m['training_records']=records; return m

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--shard-dir',required=True); ap.add_argument('--out',required=True); ap.add_argument('--repo-commit',default='UNKNOWN'); args=ap.parse_args()
    cover=load_variant(args.shard_dir,'cover'); if_names=list(cover['names'])
    if len(if_names)!=5000 or len(set(if_names))!=5000: raise RuntimeError('expected exactly 5000 unique non-holdout images')
    out={'detector':'DDE-SRM34671 + SealWatch-FLD-Ensemble','repo_commit':args.repo_commit,'sealwatch_commit':'90af7175a70f9c7cf48072b011334add499805db','seed':SEED,'bootstrap_seed':BOOT_SEED,'bootstrap_n':BOOT_N,'epsilons':{}}
    for eps,(uvar,ivar,mvar) in VARIANTS.items():
        u=load_variant(args.shard_dir,uvar); i=load_variant(args.shard_dir,ivar); m=load_variant(args.shard_dir,mvar)
        # align every variant to cover ordering and assert same payload for V8 pair
        Xc,splits,_,_=reorder(cover,if_names); Xu,su,oku,bu=reorder(u,if_names); Xi,si,oki,bi=reorder(i,if_names); Xm,sm,okm,bm=reorder(m,if_names)
        if not (np.array_equal(splits,su) and np.array_equal(splits,si) and np.array_equal(splits,sm)): raise RuntimeError('split alignment failure')
        if not np.array_equal(bu,bi): raise RuntimeError('uniform/IG message lengths differ')
        common=oku&oki; expected=5000 if eps=='0.0002' else 4997
        if int(common.sum())!=expected: raise RuntimeError(f'{eps}: common-success {common.sum()} != {expected}')
        train=common&(splits=='fit'); test=common&(splits=='calibration'); expected_counts=(3500,1500) if eps=='0.0002' else (3498,1499)
        if (int(train.sum()),int(test.sum()))!=expected_counts: raise RuntimeError(f'{eps}: train/test count mismatch')
        Xct=np.ascontiguousarray(Xc[train]); Xce=np.ascontiguousarray(Xc[test]); names=np.asarray(if_names)[test].tolist()
        results={}
        for label,Xs in [('uniform_shrink',Xu),('IG_matched',Xi),('MiPOD',Xm)]:
            rr=train_condition(Xct,np.ascontiguousarray(Xs[train]),Xce,np.ascontiguousarray(Xs[test])); rr['n_train_pairs']=int(train.sum());rr['n_test_pairs']=int(test.sum());rr['test_names']=names
            results[label]=serial(rr)
        # paired IG vs uniform identity bootstrap
        a={k:np.asarray(results['IG_matched'][k]) for k in ['cover_confidence','stego_confidence','cover_error','stego_error']}
        b={k:np.asarray(results['uniform_shrink'][k]) for k in ['cover_confidence','stego_confidence','cover_error','stego_error']}
        out['epsilons'][eps]={'common_success_n':int(common.sum()),'train_pairs':int(train.sum()),'test_pairs':int(test.sum()),'conditions':results,'paired_IG_vs_uniform':boot_diff(a,b)}
        del u,i,m,Xu,Xi,Xm,Xct,Xce
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2)); print(json.dumps({e:{k:v for k,v in out['epsilons'][e].items() if k!='conditions'} for e in out['epsilons']},indent=2))
if __name__=='__main__': main()