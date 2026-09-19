import os,sys,json,time,traceback
from pathlib import Path
import pandas as pd
from multiprocessing import Pool
sys.path.insert(0,'/mnt/data/Repare_framework_stage')
from run_v8_stc import embed_image, evaluate_saved
BASE='/mnt/data/BOSSBase_parts/extracted/BOSSbase'
OUT='/mnt/data/Repare_framework_stage/V8_STC'
conds=[('0.0002','uniform_shrink'),('0.0002','IG_matched'),('0.0008','uniform_shrink'),('0.0008','IG_matched')]
df=pd.read_csv('/mnt/data/Repare_framework_stage/bossbase_split_manifest_v4.csv')
df=df[df['split'].isin(['fit','calibration'])].sort_values(['split','rank_hash','image']).reset_index(drop=True)

def work(args):
    name,split,eps,method=args
    try:
        od=Path(OUT)/eps/method/split; od.mkdir(parents=True,exist_ok=True)
        sp=str(od/name); cp=os.path.join(BASE,name)
        r=evaluate_saved(cp,sp,eps,method) if os.path.exists(sp) else embed_image(cp,eps,method,sp)
        r['split']=split
        return r
    except Exception as e:
        return {'image':name,'split':split,'epsilon':eps,'method':method,'success':False,'error':repr(e),'traceback':traceback.format_exc()}

def main(a,b):
    rows=df.iloc[a:b]
    tasks=[(r.image,r.split,e,m) for r in rows.itertuples() for e,m in conds]
    t=time.time()
    with Pool(processes=5) as p:
        res=list(p.imap_unordered(work,tasks,chunksize=4))
    Path(OUT).mkdir(parents=True,exist_ok=True)
    fn=Path(OUT)/f'results_{a:04d}_{b:04d}.json'
    json.dump(res,open(fn,'w'),indent=1)
    ok=sum(x.get('success',False) for x in res)
    errs=sum(x.get('bit_errors',0) for x in res if 'bit_errors' in x)
    print(json.dumps({'range':[a,b],'tasks':len(res),'success':ok,'bit_errors':errs,'elapsed_s':time.time()-t,'file':str(fn)}))

if __name__=='__main__':
    main(int(sys.argv[1]),int(sys.argv[2]))
