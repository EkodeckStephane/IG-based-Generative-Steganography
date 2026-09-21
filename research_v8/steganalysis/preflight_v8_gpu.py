#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import pandas as pd
from PIL import Image

EXPECTED_DESIGN_SHA='a95f764bf7a92e21e3203aecb44c99b14a881f40f2bba6a221fb895d03a2d33b'
EXPECTED_MANIFEST_SHA='d132a45c62dd6ea8c6f9a1a0aa088f56d84ad1ffe8bc11e5054f280d8f6ed631'
EXPECTED_SUMMARY={
 '0.0002|uniform_shrink':(5000,5000),
 '0.0002|IG_matched':(5000,5000),
 '0.0008|uniform_shrink':(5000,4998),
 '0.0008|IG_matched':(5000,4999)
}

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def ensure_manifest(repo: Path) -> Path:
 mf=repo/'research_v8/results/bossbase_split_manifest_v4.csv'
 gen=repo/'research_v8/steganalysis/generate_bossbase_split_manifest_v4.py'
 if (not mf.exists()) or sha(mf)!=EXPECTED_MANIFEST_SHA:
  subprocess.run([sys.executable,str(gen),'--out',str(mf)],check=True)
 got=sha(mf)
 if got!=EXPECTED_MANIFEST_SHA:
  raise RuntimeError(f'BOSSBase split manifest hash mismatch: {got}')
 return mf

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--repo',required=True)
 ap.add_argument('--bossbase',required=True)
 args=ap.parse_args()
 r=Path(args.repo);b=Path(args.bossbase);out={'checks':{}}

 design=r/'research_v8/results/v7_frozen_designs.json'
 out['checks']['design_sha256']=sha(design)
 assert out['checks']['design_sha256']==EXPECTED_DESIGN_SHA

 manifest=ensure_manifest(r)
 out['checks']['manifest_sha256']=sha(manifest)
 mf=pd.read_csv(manifest)
 cnt=mf['split'].value_counts().to_dict()
 out['checks']['manifest_counts']=cnt
 assert len(mf)==10000
 assert cnt.get('fit')==3500 and cnt.get('calibration')==1500 and cnt.get('holdout')==5000

 files=sorted(b.rglob('*.pgm'))
 out['checks']['bossbase_pgm']=len(files)
 assert len(files)==10000
 for p in files[:20]+files[-20:]:
  assert Image.open(p).size==(512,512)

 summ=json.loads((r/'research_v8/results/V8_STC_RERUN/V8_STC_RERUN_SUMMARY.json').read_text())
 for k,(n,s) in EXPECTED_SUMMARY.items():
  assert summ['conditions'][k]['n']==n and summ['conditions'][k]['successes']==s
 out['checks']['v8_summary']='PASS'

 low=subprocess.run(
  [sys.executable,str(r/'research_v8/vendor/pystc_minimal/test_lowlevel.py')],
  cwd=r/'research_v8/vendor/pystc_minimal',
  capture_output=True,text=True
 )
 out['checks']['stc_lowlevel_rc']=low.returncode
 out['checks']['stc_lowlevel_tail']=(low.stdout+low.stderr)[-1500:]
 assert low.returncode==0

 try:
  import torch
  out['gpu']={'torch':torch.__version__,'cuda':torch.cuda.is_available(),
              'device':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
 except Exception as e:
  out['gpu']={'error':repr(e)}

 print(json.dumps(out,indent=2))
 (r/'research_v8/steganalysis/COLAB_PREFLIGHT_LAST.json').write_text(json.dumps(out,indent=2))

if __name__=='__main__':
 main()
