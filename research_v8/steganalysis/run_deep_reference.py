#!/usr/bin/env python3
"""Reconciled V8 deep-steganalysis driver with internal validation and resume.

Final test (`calibration`) is evaluated exactly once after the checkpoint is
selected on a deterministic validation subset drawn from `fit`.
"""
import argparse, hashlib, importlib, json, math, os, random, sys, time, types
from pathlib import Path
import numpy as np, pandas as pd
from PIL import Image
from sklearn.metrics import roc_auc_score, balanced_accuracy_score
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

SEEDS=(12345,23456,34567)

def failure_union(summary,eps):
    obj=json.loads(Path(summary).read_text()); fs=obj.get('failures',obj.get('failure_cases',[]))
    return {str(x['image']) for x in fs if str(x.get('epsilon'))==str(eps)}

def frozen_split(manifest,summary,eps):
    df=pd.read_csv(manifest)
    if not {'image','split'}.issubset(df.columns): raise ValueError('manifest requires image, split')
    df=df[df['split'].isin(['fit','calibration'])].copy(); bad=failure_union(summary,eps)
    df=df[~df['image'].astype(str).isin(bad)].copy()
    fit=[str(x) for x in df[df['split']=='fit']['image']]
    test=[str(x) for x in df[df['split']=='calibration']['image']]
    ranked=sorted(fit,key=lambda n:(hashlib.sha256(f'V8-DET-VAL|{n}'.encode()).hexdigest(),n))
    val=ranked[:500]; train=ranked[500:]
    assert not (set(train)&set(val) or set(train)&set(test) or set(val)&set(test))
    return train,val,test,sorted(bad)

def resolve(root,name):
    p=Path(root)/name
    if p.exists(): return p
    hits=list(Path(root).rglob(name))
    if len(hits)!=1: raise FileNotFoundError(f'{name}: {len(hits)} matches under {root}')
    return hits[0]

class PairDataset(Dataset):
    def __init__(self,names,cover_root,stego_root): self.names=list(names); self.cover_root=Path(cover_root); self.stego_root=Path(stego_root)
    def __len__(self): return len(self.names)
    def __getitem__(self,i):
        n=self.names[i]; c=np.asarray(Image.open(resolve(self.cover_root,n)),dtype=np.float32); s=np.asarray(Image.open(resolve(self.stego_root,n)),dtype=np.float32)
        if c.shape!=(512,512) or s.shape!=(512,512): raise ValueError(f'{n}: expected 512x512')
        return torch.from_numpy(c[None]),torch.from_numpy(s[None]),n

def deterministic_setup(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark=False; torch.backends.cudnn.deterministic=True

def d4_pair(c,s,rng):
    k=rng.randrange(4)
    if k: c=torch.rot90(c,k,(-2,-1)); s=torch.rot90(s,k,(-2,-1))
    if rng.randrange(2): c=torch.flip(c,(-1,)); s=torch.flip(s,(-1,))
    return c,s

def batch_aug(c,s,rng):
    out=[d4_pair(c[i],s[i],rng) for i in range(c.shape[0])]
    return torch.stack([x[0] for x in out]),torch.stack([x[1] for x in out])

def load_srnet(repo_path):
    rp=Path(repo_path).resolve(); cfg=types.ModuleType('config'); cfg.stego_img_channel=1; cfg.stego_img_height=512; sys.modules['config']=cfg
    if str(rp) not in sys.path: sys.path.insert(0,str(rp))
    return importlib.import_module('models.SRNet').Model

def load_sia(repo_path):
    rp=Path(repo_path).resolve()
    if str(rp) not in sys.path: sys.path.insert(0,str(rp))
    m=importlib.import_module('src.models'); return m.KeNet,m.ContrastiveLoss

def forward_model(kind,model,x):
    if kind=='srnet': return model(x),None,None
    w=x.shape[-1]&~1; x=x[...,:w]; return model(x[...,:w//2],x[...,w//2:])

def make_model(kind,ext,device):
    if kind=='srnet':
        M=load_srnet(Path(ext)/'Deep-Steganalysis'); model=M().to(device); epochs=100; pair_batch=4
        opt=torch.optim.Adam(model.parameters(),lr=2e-4,weight_decay=1e-5); sched=torch.optim.lr_scheduler.StepLR(opt,30,.5); contrast=None
    else:
        M,C=load_sia(Path(ext)/'SiaStegNet'); model=M().to(device); epochs=500; pair_batch=16
        opt=torch.optim.Adamax(model.parameters(),lr=1e-3,eps=1e-8,weight_decay=1e-4); sched=torch.optim.lr_scheduler.MultiStepLR(opt,[300,400],.1); contrast=C(margin=1.0).to(device)
    return model,epochs,pair_batch,opt,sched,contrast

def loader_for(names,cover_root,stego_root,batch,shuffle,seed,num_workers):
    ds=PairDataset(names,cover_root,stego_root); g=torch.Generator(); g.manual_seed(seed)
    return DataLoader(ds,batch_size=batch,shuffle=shuffle,generator=g if shuffle else None,num_workers=num_workers,drop_last=False,pin_memory=torch.cuda.is_available())

def train_epoch(kind,model,loader,opt,ce,contrast,device,rng):
    model.train(); total=0.; n=0
    for c,s,_ in loader:
        c,s=batch_aug(c,s,rng)
        if kind=='srnet': c=c/255.; s=s/255.
        x=torch.cat([c,s],0).to(device,non_blocking=True); y=torch.cat([torch.zeros(len(c),dtype=torch.long),torch.ones(len(s),dtype=torch.long)],0).to(device)
        opt.zero_grad(set_to_none=True); logits,f0,f1=forward_model(kind,model,x); loss=ce(logits,y)
        if kind!='srnet': loss=loss+0.1*contrast(f0,f1,y)
        loss.backward(); opt.step(); total+=float(loss.detach())*len(y); n+=len(y)
    return total/max(n,1)

@torch.no_grad()
def evaluate(kind,model,names,cover_root,stego_root,batch,device,num_workers,with_names=False):
    loader=loader_for(names,cover_root,stego_root,batch,False,0,num_workers); model.eval(); cs=[];ss=[];cp=[];sp=[]; order=[]; ce=nn.CrossEntropyLoss(reduction='sum'); loss=0.; count=0
    for c,s,ns in loader:
        if kind=='srnet': c=c/255.; s=s/255.
        for x,label,scores,preds in [(c,0,cs,cp),(s,1,ss,sp)]:
            x=x.to(device); logits,_,_=forward_model(kind,model,x); y=torch.full((len(x),),label,dtype=torch.long,device=device)
            loss+=float(ce(logits,y)); count+=len(x); scores.extend(torch.softmax(logits,1)[:,1].cpu().tolist()); preds.extend(torch.argmax(logits,1).cpu().tolist())
        order.extend(list(ns))
    cs=np.asarray(cs);ss=np.asarray(ss);cp=np.asarray(cp);sp=np.asarray(sp); fp=(cp==1).astype(float);fn=(sp==0).astype(float)
    y=np.r_[np.zeros(len(cs)),np.ones(len(ss))]; score=np.r_[cs,ss]
    out={'loss':loss/max(count,1),'balanced_error':float(.5*(fp.mean()+fn.mean())),'balanced_accuracy':float(1-.5*(fp.mean()+fn.mean())),'accuracy':float(1-.5*(fp.mean()+fn.mean())),
         'roc_auc':float(roc_auc_score(y,score)),'false_positive_rate':float(fp.mean()),'false_negative_rate':float(fn.mean())}
    if with_names: out.update(test_names=order,cover_scores=cs.tolist(),stego_scores=ss.tolist(),cover_error=fp.tolist(),stego_error=fn.tolist())
    return out

def sha256(path):
    h=hashlib.sha256();
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--model',required=True,choices=['srnet','siastegnet']); ap.add_argument('--seed',required=True,type=int,choices=SEEDS)
    ap.add_argument('--epsilon',required=True,choices=['0.0002','0.0008']); ap.add_argument('--method',required=True,choices=['uniform_shrink','IG_matched'])
    ap.add_argument('--cover-root',required=True); ap.add_argument('--stego-root',required=True); ap.add_argument('--manifest',required=True); ap.add_argument('--summary',required=True)
    ap.add_argument('--external-root',required=True); ap.add_argument('--out-dir',required=True); ap.add_argument('--num-workers',type=int,default=2); ap.add_argument('--repo-commit',default='UNKNOWN')
    args=ap.parse_args(); deterministic_setup(args.seed)
    if not torch.cuda.is_available(): raise RuntimeError('GPU campaign requires CUDA; CPU execution cannot close C6')
    device=torch.device('cuda'); train,val,test,bad=frozen_split(args.manifest,args.summary,args.epsilon)
    expected=(3000,500,1500) if args.epsilon=='0.0002' else (2998,500,1499)
    if (len(train),len(val),len(test))!=expected: raise RuntimeError(f'split mismatch {(len(train),len(val),len(test))} != {expected}')
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True); tag=f'{args.model}_{args.epsilon}_{args.method}_seed{args.seed}'
    latest=out/f'{tag}_latest.pt'; best=out/f'{tag}_best.pt'; final_json=out/f'{tag}.json'
    if final_json.exists(): print(final_json.read_text()); return
    model,epochs,pair_batch,opt,sched,contrast=make_model(args.model,args.external_root,device); ce=nn.CrossEntropyLoss(); start_epoch=1; history=[]; best_key=None; best_epoch=None
    if latest.exists():
        ck=torch.load(latest,map_location=device); model.load_state_dict(ck['state_dict']); opt.load_state_dict(ck['optimizer']); sched.load_state_dict(ck['scheduler']); start_epoch=ck['epoch']+1; history=ck['history']; best_key=tuple(ck['best_key']) if ck['best_key'] else None; best_epoch=ck['best_epoch']
    t0=time.time()
    for epoch in range(start_epoch,epochs+1):
        loader=loader_for(train,args.cover_root,Path(args.stego_root)/'fit',pair_batch,True,args.seed*100000+epoch,args.num_workers); rng=random.Random(args.seed*1000000+epoch)
        trloss=train_epoch(args.model,model,loader,opt,ce,contrast,device,rng); sched.step()
        vm=evaluate(args.model,model,val,args.cover_root,Path(args.stego_root)/'fit',pair_batch,device,args.num_workers)
        row={'epoch':epoch,'training_objective':trloss,'lr':float(opt.param_groups[0]['lr']),'validation':vm}; history.append(row)
        key=(vm['balanced_accuracy'],-vm['loss'],-epoch)
        if best_key is None or key>best_key:
            best_key=key; best_epoch=epoch; torch.save({'state_dict':model.state_dict(),'epoch':epoch,'validation':vm},best)
        torch.save({'state_dict':model.state_dict(),'optimizer':opt.state_dict(),'scheduler':sched.state_dict(),'epoch':epoch,'history':history,'best_key':best_key,'best_epoch':best_epoch},latest)
        print(json.dumps({'tag':tag,'epoch':epoch,'train_loss':trloss,'val_bal_acc':vm['balanced_accuracy'],'val_auc':vm['roc_auc'],'best_epoch':best_epoch}))
    ck=torch.load(best,map_location=device); model.load_state_dict(ck['state_dict']); tm=evaluate(args.model,model,test,args.cover_root,Path(args.stego_root)/'calibration',pair_batch,device,args.num_workers,True)
    result={'detector':args.model,'seed':args.seed,'epsilon':args.epsilon,'method':args.method,'repo_commit':args.repo_commit,
            'external_commits':{'SRNet':'1a5b8f88ce3c928e44ca22ad66010d23cd4a1262','SiaStegNet':'592d9e13f39f287d9c675f1b89272bcfb6a9627c'},
            'excluded_failure_union':bad,'n_train_pairs':len(train),'n_validation_pairs':len(val),'n_test_pairs':len(test),
            'train_names':train,'validation_names':val,'test_names':test,'epochs_fixed_before_test':epochs,
            'checkpoint_rule':'max validation balanced accuracy; tie lower validation loss; tie earlier epoch; calibration test once',
            'selected_epoch':best_epoch,'selected_validation':ck['validation'],'epoch_log':history,'device':str(device),'torch_version':torch.__version__,
            'cuda_device':torch.cuda.get_device_name(0),'training_seconds_this_invocation':time.time()-t0,'checkpoint':str(best),'checkpoint_sha256':sha256(best),**tm}
    final_json.write_text(json.dumps(result,indent=2))
    print(json.dumps({k:result[k] for k in ['detector','seed','epsilon','method','selected_epoch','n_train_pairs','n_validation_pairs','n_test_pairs','balanced_error','roc_auc','accuracy'] if k in result},indent=2))
if __name__=='__main__': main()