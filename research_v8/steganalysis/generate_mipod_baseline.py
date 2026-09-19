#!/usr/bin/env python3
"""Generate mandatory MiPOD matched-rate baselines for the frozen V8 split."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np, pandas as pd
from PIL import Image
import conseal as cl

RATES={'0.0002':0.0521699935913086,'0.0008':0.07059953002929688}

def seed32(tag):
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:4],'big')

def cols(df):
    n=next(c for c in ['image','filename','file','name'] if c in df.columns)
    s=next(c for c in ['split','partition'] if c in df.columns)
    return n,s

def failure_union(summary, eps):
    obj=json.loads(Path(summary).read_text())
    fs=obj.get('failures',obj.get('failure_cases',[]))
    return {str(x['image']) for x in fs if str(x.get('epsilon'))==str(eps)}

def resolve(root,name):
    p=Path(root)/name
    if p.exists(): return p
    hits=list(Path(root).rglob(name))
    if len(hits)!=1: raise FileNotFoundError(name)
    return hits[0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bossbase-root',required=True)
    ap.add_argument('--manifest',default='research_v8/results/bossbase_split_manifest_v4.csv')
    ap.add_argument('--summary',default='research_v8/results/V8_STC_RERUN/V8_STC_RERUN_SUMMARY.json')
    ap.add_argument('--epsilon',required=True,choices=['0.0002','0.0008'])
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    df=pd.read_csv(args.manifest); n,s=cols(df)
    df=df[df[s].isin(['fit','calibration'])].copy()
    bad=failure_union(args.summary,args.epsilon)
    if bad: df=df[~df[n].astype(str).isin(bad)]
    alpha=RATES[args.epsilon]; records=[]
    for _,row in df.sort_values([s,n]).iterrows():
        name=str(row[n]); split=str(row[s])
        src=resolve(args.bossbase_root,name)
        x=np.array(Image.open(src))
        seed=seed32(f'MiPOD|{alpha:.15g}|{name}')
        y=cl.mipod.simulate_single_channel(x0=x,alpha=alpha,seed=seed)
        dst=Path(args.out)/args.epsilon/'MiPOD'/split/name
        dst.parent.mkdir(parents=True,exist_ok=True)
        Image.fromarray(np.asarray(y,dtype=np.uint8)).save(dst)
        records.append({'image':name,'split':split,'epsilon':args.epsilon,
                        'method':'MiPOD','alpha_bpp':alpha,'seed':seed,
                        'changes':int(np.count_nonzero(np.asarray(y)!=x))})
    out=Path(args.out)/args.epsilon/'MiPOD'/'MIPOD_MATERIALIZATION.json'
    out.write_text(json.dumps(records,indent=2))
    print(json.dumps({'epsilon':args.epsilon,'alpha_bpp':alpha,'n':len(records),'excluded_v8_failure_union':sorted(bad)},indent=2))

if __name__=='__main__':
    main()
