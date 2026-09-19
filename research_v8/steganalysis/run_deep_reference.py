#!/usr/bin/env python3
"""Frozen V8 Tier-B/Tier-C deep steganalysis driver.

SRNet: public PyTorch reproduction pinned in V8_STRONG_STEGANALYSIS_LOCK.md.
SiaStegNet: official SiaStg repository pinned in the same lock.
The calibration split is never used for checkpoint selection.
"""
import argparse, copy, importlib, json, math, os, random, sys, time, types
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import roc_auc_score
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

SEEDS=(12345,23456,34567)

def manifest_cols(df):
    n=next(c for c in ['image','filename','file','name'] if c in df.columns)
    s=next(c for c in ['split','partition'] if c in df.columns)
    return n,s

def failure_union(summary, eps):
    obj=json.loads(Path(summary).read_text())
    fs=obj.get('failures',obj.get('failure_cases',[]))
    return {str(x['image']) for x in fs if str(x.get('epsilon'))==str(eps)}

def frozen_names(manifest,summary,eps):
    df=pd.read_csv(manifest); n,s=manifest_cols(df)
    df=df[df[s].isin(['fit','calibration'])].copy()
    bad=failure_union(summary,eps)
    if bad: df=df[~df[n].astype(str).isin(bad)]
    return ([str(x) for x in df[df[s]=='fit'][n]],
            [str(x) for x in df[df[s]=='calibration'][n]],
            sorted(bad))

def resolve(root,name):
    p=Path(root)/name
    if p.exists(): return p
    hits=list(Path(root).rglob(name))
    if len(hits)!=1: raise FileNotFoundError(f'{name}: {len(hits)} matches under {root}')
    return hits[0]

class PairDataset(Dataset):
    def __init__(self,names,cover_root,stego_root):
        self.names=list(names); self.cover_root=Path(cover_root); self.stego_root=Path(stego_root)
    def __len__(self): return len(self.names)
    def __getitem__(self,i):
        name=self.names[i]
        c=np.asarray(Image.open(resolve(self.cover_root,name)),dtype=np.float32)
        s=np.asarray(Image.open(resolve(self.stego_root,name)),dtype=np.float32)
        if c.ndim!=2 or s.ndim!=2 or c.shape!=s.shape:
            raise ValueError(f'{name}: expected paired grayscale images')
        return torch.from_numpy(c[None]),torch.from_numpy(s[None]),name

def deterministic_setup(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark=False
    torch.backends.cudnn.deterministic=True

def d4_pair(c,s,rng):
    k=rng.randrange(4)
    if k:
        c=torch.rot90(c,k,(-2,-1)); s=torch.rot90(s,k,(-2,-1))
    if rng.randrange(2):
        c=torch.flip(c,(-1,)); s=torch.flip(s,(-1,))
    return c,s

def batch_aug(c,s,rng):
    cc=[]; ss=[]
    for i in range(c.shape[0]):
        a,b=d4_pair(c[i],s[i],rng); cc.append(a); ss.append(b)
    return torch.stack(cc),torch.stack(ss)

def load_srnet(repo_path):
    rp=Path(repo_path).resolve()
    cfg=types.ModuleType('config'); cfg.stego_img_channel=1; cfg.stego_img_height=512
    sys.modules['config']=cfg
    if str(rp) not in sys.path: sys.path.insert(0,str(rp))
    mod=importlib.import_module('models.SRNet')
    return mod.Model

def load_sia(repo_path):
    rp=Path(repo_path).resolve()
    if str(rp) not in sys.path: sys.path.insert(0,str(rp))
    models=importlib.import_module('src.models')
    return models.KeNet,models.ContrastiveLoss

def logits_for(model_kind,model,x):
    if model_kind=='srnet':
        return model(x)
    w=x.shape[-1] & ~1
    x=x[...,:w]
    left=x[...,:w//2]; right=x[...,w//2:]
    out,f0,f1=model(left,right)
    return out,f0,f1

def train_one(model_kind,seed,train_names,cover_root,stego_root,external_root,out_dir,
              num_workers=0):
    deterministic_setup(seed)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    ds=PairDataset(train_names,cover_root,Path(stego_root)/'fit')
    if model_kind=='srnet':
        Model=load_srnet(Path(external_root)/'Deep-Steganalysis')
        model=Model().to(device)
        epochs=100; pair_batch=4
        optimizer=torch.optim.Adam(model.parameters(),lr=2e-4,weight_decay=1e-5)
        scheduler=torch.optim.lr_scheduler.StepLR(optimizer,step_size=30,gamma=0.5)
        ce=nn.CrossEntropyLoss()
    else:
        KeNet,ContrastiveLoss=load_sia(Path(external_root)/'SiaStegNet')
        model=KeNet().to(device)
        epochs=500; pair_batch=16
        optimizer=torch.optim.Adamax(model.parameters(),lr=1e-3,eps=1e-8,weight_decay=1e-4)
        scheduler=torch.optim.lr_scheduler.MultiStepLR(optimizer,milestones=[300,400],gamma=0.1)
        ce=nn.CrossEntropyLoss(); contrast=ContrastiveLoss(margin=1.0).to(device)
    best_loss=float('inf'); best_state=None; best_epoch=None; epoch_rows=[]; t0=time.time()
    for epoch in range(1,epochs+1):
        g=torch.Generator(); g.manual_seed(seed*100000+epoch)
        loader=DataLoader(ds,batch_size=pair_batch,shuffle=True,generator=g,
                          num_workers=num_workers,drop_last=False,pin_memory=torch.cuda.is_available())
        rng=random.Random(seed*1000000+epoch)
        model.train(); total=0.; count=0
        for c,s,_ in loader:
            c,s=batch_aug(c,s,rng)
            if model_kind=='srnet':
                c=c/255.; s=s/255.
            x=torch.cat([c,s],0).to(device,non_blocking=True)
            y=torch.cat([torch.zeros(len(c),dtype=torch.long),
                         torch.ones(len(s),dtype=torch.long)],0).to(device)
            optimizer.zero_grad(set_to_none=True)
            if model_kind=='srnet':
                logits=model(x); loss=ce(logits,y)
            else:
                logits,f0,f1=logits_for(model_kind,model,x)
                loss=ce(logits,y)+0.1*contrast(f0,f1,y)
            loss.backward(); optimizer.step()
            total+=float(loss.detach())*len(y); count+=len(y)
        train_loss=total/max(count,1)
        scheduler.step()
        epoch_rows.append({'epoch':epoch,'training_objective':train_loss,
                           'lr':float(optimizer.param_groups[0]['lr'])})
        if train_loss<best_loss:
            best_loss=train_loss; best_epoch=epoch
            best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
    out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True)
    ckpt=out_dir/f'{model_kind}_seed{seed}_checkpoint.pt'
    torch.save({'state_dict':best_state,'epoch':best_epoch,'training_objective':best_loss,
                'seed':seed,'model':model_kind},ckpt)
    model.load_state_dict(best_state)
    return model,device,epochs,best_epoch,best_loss,time.time()-t0,epoch_rows,str(ckpt)

@torch.no_grad()
def test_one(model_kind,model,device,test_names,cover_root,stego_root,batch_size=8,num_workers=0):
    ds=PairDataset(test_names,cover_root,Path(stego_root)/'calibration')
    loader=DataLoader(ds,batch_size=batch_size,shuffle=False,num_workers=num_workers)
    model.eval(); cover_scores=[]; stego_scores=[]; cover_pred=[]; stego_pred=[]
    for c,s,_ in loader:
        if model_kind=='srnet':
            c=c/255.; s=s/255.
        for x,target_scores,target_pred in [(c,cover_scores,cover_pred),(s,stego_scores,stego_pred)]:
            x=x.to(device)
            if model_kind=='srnet': logits=model(x)
            else: logits=logits_for(model_kind,model,x)[0]
            prob=torch.softmax(logits,1)[:,1]
            pred=torch.argmax(logits,1)
            target_scores.extend(prob.cpu().tolist())
            target_pred.extend(pred.cpu().tolist())
    cs=np.asarray(cover_scores); ss=np.asarray(stego_scores)
    cp=np.asarray(cover_pred); sp=np.asarray(stego_pred)
    fp=(cp==1).astype(float); fn=(sp==0).astype(float)
    pe=float(.5*(fp.mean()+fn.mean()))
    auc=float(roc_auc_score(np.r_[np.zeros(len(cs)),np.ones(len(ss))],np.r_[cs,ss]))
    return {
      'balanced_error':pe,'roc_auc':auc,'accuracy':1-pe,
      'false_positive_rate':float(fp.mean()),'false_negative_rate':float(fn.mean()),
      'cover_scores':cs.tolist(),'stego_scores':ss.tolist(),
      'cover_error':fp.tolist(),'stego_error':fn.tolist(),
      'test_names':list(test_names)
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',required=True,choices=['srnet','siastegnet'])
    ap.add_argument('--seed',required=True,type=int,choices=SEEDS)
    ap.add_argument('--epsilon',required=True,choices=['0.0002','0.0008'])
    ap.add_argument('--method',required=True,choices=['uniform_shrink','IG_matched'])
    ap.add_argument('--cover-root',required=True)
    ap.add_argument('--stego-root',required=True,help='.../<epsilon>/<method>, containing fit and calibration')
    ap.add_argument('--manifest',default='research_v8/results/bossbase_split_manifest_v4.csv')
    ap.add_argument('--summary',default='research_v8/results/V8_STC_RERUN/V8_STC_RERUN_SUMMARY.json')
    ap.add_argument('--external-root',default='research_v8/steganalysis/external_refs')
    ap.add_argument('--out-dir',required=True)
    ap.add_argument('--num-workers',type=int,default=0)
    args=ap.parse_args()
    tr,te,bad=frozen_names(args.manifest,args.summary,args.epsilon)
    model,device,epochs,best_epoch,best_loss,seconds,rows,ckpt=train_one(
        args.model,args.seed,tr,args.cover_root,args.stego_root,args.external_root,args.out_dir,args.num_workers)
    metrics=test_one(args.model,model,device,te,args.cover_root,args.stego_root,
                     batch_size=(4 if args.model=='srnet' else 16),num_workers=args.num_workers)
    result={
      'detector':args.model,'seed':args.seed,'epsilon':args.epsilon,'method':args.method,
      'n_train_pairs':len(tr),'n_test_pairs':len(te),'excluded_failure_union':bad,
      'epochs_fixed_before_test':epochs,'checkpoint_rule':'minimum training objective; calibration labels unused',
      'selected_epoch':best_epoch,'selected_training_objective':best_loss,
      'training_seconds':seconds,'device':str(device),
      'torch_version':torch.__version__,
      'cuda_device':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
      'checkpoint':ckpt,'epoch_log':rows,**metrics
    }
    out=Path(args.out_dir)/f"{args.model}_{args.epsilon}_{args.method}_seed{args.seed}.json"
    out.write_text(json.dumps(result,indent=2))
    print(json.dumps({k:result[k] for k in ['detector','seed','epsilon','method','n_train_pairs','n_test_pairs','selected_epoch','training_seconds','device','balanced_error','roc_auc','accuracy']},indent=2))

if __name__=='__main__':
    main()
