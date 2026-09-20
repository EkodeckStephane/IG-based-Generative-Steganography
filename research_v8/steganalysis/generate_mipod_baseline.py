#!/usr/bin/env python3
"""Generate canonical MiPOD baselines at the exact V8 message length per image.

This supersedes the earlier mean-bpp helper. Payload is read from persisted V8
raw records and therefore matches actual-message coding image-by-image.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np, pandas as pd
from PIL import Image
import conseal as cl

def seed32(tag): return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:4],'big')

def load_v8_raw(root,eps):
    by={}
    for p in sorted(Path(root).glob('results_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9].json')):
        for r in json.loads(p.read_text()):
            if str(r.get('epsilon'))!=str(eps): continue
            n=str(r['image']); d=by.setdefault(n,{}) ; d[str(r['method'])]=r
    if len(by)!=5000: raise RuntimeError(f'{eps}: expected 5000 image identities in raw V8 evidence, got {len(by)}')
    out={}; bad=set()
    for n,d in by.items():
        if not {'uniform_shrink','IG_matched'}.issubset(d): raise RuntimeError(f'{n}: missing V8 method record')
        if int(d['uniform_shrink']['message_bits'])!=int(d['IG_matched']['message_bits']): raise RuntimeError(f'{n}: V8 message lengths differ')
        out[n]=int(d['uniform_shrink']['message_bits'])
        if not d['uniform_shrink'].get('success',False) or not d['IG_matched'].get('success',False): bad.add(n)
    return out,bad

def resolve(root,name):
    p=Path(root)/name
    if p.exists(): return p
    hits=list(Path(root).rglob(name))
    if len(hits)!=1: raise FileNotFoundError(name)
    return hits[0]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--bossbase-root',required=True); ap.add_argument('--manifest',required=True); ap.add_argument('--v8-raw-root',required=True)
    ap.add_argument('--epsilon',required=True,choices=['0.0002','0.0008']); ap.add_argument('--out',required=True); args=ap.parse_args()
    bits,bad=load_v8_raw(args.v8_raw_root,args.epsilon); df=pd.read_csv(args.manifest); df=df[df['split'].isin(['fit','calibration']) & ~df['image'].astype(str).isin(bad)].copy(); records=[]
    for row in df.sort_values(['split','rank_hash','image']).itertuples():
        name=str(row.image); src=resolve(args.bossbase_root,name); x=np.asarray(Image.open(src),dtype=np.uint8); m=bits[name]; alpha=m/(512.0*512.0); seed=seed32(f'V8-MiPOD|{args.epsilon}|{name}')
        y=cl.mipod.simulate_single_channel(x0=x,alpha=alpha,seed=seed); dst=Path(args.out)/row.split/name; dst.parent.mkdir(parents=True,exist_ok=True); Image.fromarray(np.asarray(y,dtype=np.uint8)).save(dst)
        records.append({'image':name,'split':row.split,'epsilon':args.epsilon,'method':'MiPOD','message_bits_matched':m,'alpha_bpp':alpha,'seed':seed,'changes':int(np.count_nonzero(y!=x))})
    meta={'epsilon':args.epsilon,'n':len(records),'excluded_v8_failure_union':sorted(bad),'payload_rule':'message_bits_i/(512*512)','seed_rule':'SHA256(V8-MiPOD|epsilon|filename)[:32 bits]','records':records}
    p=Path(args.out)/'MIPOD_MATERIALIZATION.json';p.write_text(json.dumps(meta,indent=2));print(json.dumps({k:meta[k] for k in ['epsilon','n','excluded_v8_failure_union','payload_rule','seed_rule']},indent=2))
if __name__=='__main__':main()