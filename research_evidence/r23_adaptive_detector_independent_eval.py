"""Three-seed independent post-training test for R2.3 adversarial codebooks.
New pixel and public-latent SVM are independently refitted for each variant.
Requires the full research bundle's VAE adapter/checkpoint and prior minimax JSON.
"""
import os,sys,json,math
from pathlib import Path
import numpy as np,torch
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
ROOT=Path(os.getenv('DSP_PROJECT_ROOT',str(Path(__file__).resolve().parents[1])))
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'Version_1.0'))
import benchmark_s5_comparison as b
from r23_minimax_codebook_prototype import sample_gen,oracle
INPUT=Path(os.getenv('R23_MINIMAX_RESULTS',str(HERE/'r23_minimax_codebook_results.json')))
def public_features(model,x,F):
    with torch.no_grad():mu,_=model.encode(torch.as_tensor(x,dtype=torch.float32))
    z=mu.numpy()
    return np.column_stack([z,np.einsum('ni,ij,nj->n',z,F,z),x.mean(1),x.std(1)])
def wilson(p,n):
    z=1.96;d=1+z*z/n;ctr=(p+z*z/(2*n))/d
    gap=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [float(max(0,ctr-gap)),float(min(1,ctr+gap))]
def test_one(model,p0,F,z,seed,Ntrain=400,Ntest=800):
    with torch.no_grad():pc=model.decode_prob(torch.tensor(z,dtype=torch.float32)).numpy()
    cv,ste,_=sample_gen(p0,pc,np.random.default_rng(seed),Ntrain)
    ct,stt,msg=sample_gen(p0,pc,np.random.default_rng(seed+100000),Ntest)
    tr=np.vstack([cv,ste]);te=np.vstack([ct,stt])
    ytr=np.r_[np.zeros(Ntrain),np.ones(Ntrain)]
    yte=np.r_[np.zeros(Ntest),np.ones(Ntest)]
    result={}
    for name,trainx,testx in [('pixels_RBF_SVM',tr,te),
      ('public_latent_RBF_SVM',public_features(model,tr,F),public_features(model,te,F))]:
        c=make_pipeline(StandardScaler(),SVC(C=2,kernel='rbf',gamma='scale'))
        c.fit(trainx,ytr)
        result[name]=float(roc_auc_score(yte,c.decision_function(testx)))
    result['known_model_oracle']=float(roc_auc_score(yte,oracle(te,p0,pc)))
    q=np.clip(pc,1e-7,1-1e-7)
    ll=stt@np.log(q).T+(1-stt)@np.log1p(-q).T
    result['ML_success']=int(np.sum(np.argmax(ll,axis=1)==msg))
    with torch.no_grad():mu,_=model.encode(torch.tensor(stt,dtype=torch.float32))
    estimate=np.argmin(np.sum((mu.numpy()[:,None,:]-z[None,:,:])**2,axis=2),axis=1)
    result['public_VAE_success']=int(np.sum(estimate==msg))
    result['N_test']=Ntest
    return result
def main():
    torch.set_num_threads(1)
    model=b.load_model();p0=b.decoder_probs(model,np.zeros(2));F0=b.fisher_metric(model,np.zeros(2))
    source=json.loads(INPUT.read_text())
    books={'untrained':source['init_codebook']}
    for k,v in source['experiments'].items():books[k]=v['after_codebook']
    seeds=[6101,6203,6309]
    output={'scope':'Independent 400+400 train, 800+800 test x3 seeds, one VAE and initial codebook, not Algorithm 2','rng_seeds':seeds,'variants':{}}
    for key,coords in books.items():
        z=np.asarray(coords,dtype=float)
        results=[test_one(model,p0,F0,z,s) for s in seeds]
        mean={x:float(np.mean([r[x] for r in results]))
          for x in ['pixels_RBF_SVM','public_latent_RBF_SVM','known_model_oracle']}
        count_ml=sum(r['ML_success'] for r in results)
        count_pub=sum(r['public_VAE_success'] for r in results)
        n=sum(r['N_test'] for r in results)
        output['variants'][key]={'codebook':coords,'runs':results,'mean_AUC':mean,
          'ML_accuracy':count_ml/n,'ML_Wilson_CI95':wilson(count_ml/n,n),
          'public_encoder_accuracy':count_pub/n,
          'public_encoder_Wilson_CI95':wilson(count_pub/n,n),
          'count_ml':count_ml,'count_public':count_pub,'count_test':n}
        print(key,mean,count_ml,count_pub,flush=True)
    out=HERE/'r23_adaptive_detector_independent_eval.json'
    out.write_text(json.dumps(output,indent=2));print('Wrote',out)
if __name__=='__main__':main()
