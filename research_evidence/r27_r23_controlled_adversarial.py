"""CONTROLLED R2.7/R2.3: fixed synthetic latent endpoints, independent generated splits.
This is not original MNIST class-means S5, Algorithm 2, or native iMEC/Discop pipelines.
Observations to learned detectors are pixels or public VAE encoder output, never private paths.
"""
import csv,json,hashlib,sys,time
from pathlib import Path
import numpy as np,torch
from scipy.special import logsumexp
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent))
import benchmark_s5_comparison as b
SEED=20261031;TRAIN=120;TEST=120;BOOT=300
METHODS=['Euclidean path','Fisher-NG path','Discop'];Z0=np.array([0.,0.]);Z1=np.array([1.5,.5])
def features(model,xx,F):
 with torch.no_grad(): z,_=model.encode(torch.as_tensor(xx,dtype=torch.float32))
 z=z.numpy();delta=z-Z0
 return np.column_stack([z,np.einsum('ni,ij,nj->n',delta,F,delta),np.linalg.norm(delta,axis=1)])
def predict(a,y,x):
 m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,C=.5,random_state=SEED));m.fit(a,y);return m.predict_proba(x)[:,1]
def auc(y,s,seed):
 rng=np.random.default_rng(seed);pos=np.where(y==1)[0];neg=np.where(y==0)[0];v=[]
 for _ in range(BOOT):
  ix=np.r_[rng.choice(pos,len(pos)),rng.choice(neg,len(neg))];v.append(roc_auc_score(y[ix],s[ix]))
 return [float(roc_auc_score(y,s)),*map(float,np.quantile(v,[.025,.975]))]
def oracle(x,p0,pc):
 q=np.clip(np.asarray(pc),1e-7,1-1e-7);x=np.asarray(x,dtype=np.float64)
 ll=x@np.log(q).T+(1-x)@np.log1p(-q).T
 return logsumexp(ll,axis=1)-np.log(len(q))-(x@np.log(p0)+(1-x)@np.log1p(-p0))
def main():
 torch.set_num_threads(1);m=b.load_model();p0=b.decoder_probs(m,Z0);F=b.fisher_metric(m,Z0)
 ng=b.ng_path(m,Z0,Z1,max_steps=150)
 codes={'Euclidean path':np.linspace(Z0,Z1,4),'Fisher-NG path':b.resample_path(ng,4,m)}
 mec=b.load_official_mec(b.DSP/'_imec_reference'/'src')
 out={'scope':'Synthetic z0/z1 on checkpoint; NOT original S5; NOT Algorithm 2; NOT native media iMEC/Discop; iMEC excluded due time budget','seed':SEED,'train_per_class':TRAIN,'test_per_class':TEST,'z0':Z0.tolist(),'z1':Z1.tolist(),'bootstrap':BOOT,'methods':{},'checkpoint_sha256':hashlib.sha256((b.DATA/'s5_vae_mnist.pt').read_bytes()).hexdigest()}
 for k,method in enumerate(METHODS):
  sets={};codes_test=[];times=[]
  for split,n,offset in [('train',TRAIN,0),('test',TEST,1000000)]:
   cover=np.stack([b.sample_cover(p0,SEED+offset+i) for i in range(n)]).astype(np.uint8)
   stego=[]
   for i in range(n):
    seed=SEED+offset+100000+10000*k+i
    msg=np.random.default_rng(seed+123).integers(0,2,2,dtype=np.uint8)
    if method=='iMEC': img,dec,enc,dec_time,_=b.imec_encode_decode(p0,msg,seed,mec)
    elif method=='Discop':img,dec,enc,dec_time,_=b.discop_encode_decode(p0,msg,seed)
    else: img,enc,dec,dec_time=b.generate_method_image(method,m,p0,msg,seed,mec,{method:codes[method]})
    stego.append(np.asarray(img,dtype=np.uint8).ravel())
    if split=='test':codes_test.append(bool(np.array_equal(msg,dec)))
    times.append([enc,dec_time])
   sets[split]=(cover,np.stack(stego))
  xtrain=np.vstack(sets['train']);xtest=np.vstack(sets['test'])
  ytrain=np.r_[np.zeros(TRAIN),np.ones(TRAIN)];ytest=np.r_[np.zeros(TEST),np.ones(TEST)]
  ztrain=features(m,xtrain,F);ztest=features(m,xtest,F)
  scores={'pixel_logistic':predict(xtrain,ytrain,xtest),'public_encoder_geometry':predict(ztrain,ytrain,ztest),'fusion':predict(np.column_stack([xtrain,ztrain]),ytrain,np.column_stack([xtest,ztest]))}
  if method in codes:scores['known_model_oracle']=oracle(xtest,p0,[b.decoder_probs(m,z) for z in codes[method]])
  det={name:auc(ytest,s,SEED+17*k+j) for j,(name,s) in enumerate(scores.items())}
  out['methods'][method]={'detector_auc_ci95':det,'decoded_test':sum(codes_test),'test_n':TEST,'encoding_ms_median':float(np.median(np.array(times)[:,0])*1000),'decoding_ms_median':float(np.median(np.array(times)[:,1])*1000),'stego_sample_mse_from_p0':float(np.square(sets['test'][1].astype(float)-p0[None,:]).mean())}
  print(method,out['methods'][method],flush=True)
 x0=np.stack([b.sample_cover(p0,SEED+3000000+i) for i in range(TEST)])
 p1=b.decoder_probs(m,Z1);x1=np.stack([b.sample_cover(p1,SEED+4000000+i) for i in range(TEST)])
 out['positive_control_oracle_auc']=float(roc_auc_score(np.r_[np.zeros(TEST),np.ones(TEST)],oracle(np.vstack([x0,x1]),p0,[p1])))
 (HERE/'r27_r23_controlled_adversarial_results.json').write_text(json.dumps(out,indent=2))
 with (HERE/'r27_r23_controlled_adversarial_results.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['method','detector','AUC','CI95_low','CI95_high','decoded_test','n_test','enc_ms_median','dec_ms_median','MSE'])
  for method,item in out['methods'].items():
   for det,v in item['detector_auc_ci95'].items():w.writerow([method,det,*v,item['decoded_test'],item['test_n'],item['encoding_ms_median'],item['decoding_ms_median'],item['stego_sample_mse_from_p0']])
 print('CONTROL',out['positive_control_oracle_auc'])
if __name__=='__main__':main()
