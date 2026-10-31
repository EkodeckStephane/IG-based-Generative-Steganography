"""Known-distribution white-box likelihood-ratio audit for a four-codeword Bernoulli VAE.
Requires the full R2.3/R2.7 research bundle, or its benchmark adapter, checkpoint and
multicodebook_results.json. Does not represent a deployable blind steganalyzer.
"""
import json,os,sys,hashlib
from pathlib import Path
import numpy as np
import torch
from scipy.special import logsumexp
from sklearn.metrics import roc_auc_score
ROOT=Path(os.environ.get('DSP_PROJECT_ROOT',str(Path(__file__).resolve().parents[1])))
sys.path.insert(0,str(ROOT/'Version_1.0'))
import benchmark_s5_comparison as b
INPUT=Path(os.environ.get('R27_MULTICODEBOOK_RESULTS',str(Path(__file__).with_name('multicodebook_results.json'))))
OUTPUT=Path(__file__).with_name('r23_oracle_detection_tradeoff_results.json')
SEED=314159
def oracle_scores(x,pcover,pcode):
    pcover=np.clip(pcover,1e-7,1-1e-7)
    pcode=np.clip(pcode,1e-7,1-1e-7)
    logq=x@np.log(pcode).T+(1-x)@np.log1p(-pcode).T
    logp=x@np.log(pcover)+(1-x)@np.log1p(-pcover)
    return logsumexp(logq,axis=1)-np.log(len(pcode))-logp
def ber_kl(p,q):
    return float(np.sum(p*np.log(p/q)+(1-p)*np.log((1-p)/(1-q))))
def assess(pcover,pcode,rng,n=2500):
    d=len(pcover)
    covers=(rng.random((n,d))<pcover).astype(float)
    ids=rng.integers(len(pcode),size=n)
    stegos=(rng.random((n,d))<pcode[ids]).astype(float)
    scores=oracle_scores(np.vstack([covers,stegos]),pcover,pcode)
    auc=float(roc_auc_score(np.r_[np.zeros(n),np.ones(n)],scores))
    loglikes=stegos@np.log(pcode).T+(1-stegos)@np.log1p(-pcode).T
    acc=float(np.mean(np.argmax(loglikes,axis=1)==ids))
    mean_component_kl=float(np.mean([ber_kl(p,pcover) for p in pcode]))
    return dict(oracle_auc=auc,optimal_ml_message_accuracy=acc,
        mean_component_KL_to_cover=mean_component_kl,
        mean_pixel_MSE_to_cover_expectation=float(np.square(stegos-pcover).mean()),
        n_cover=n,n_stego=n)
def main():
    torch.set_num_threads(1)
    model=b.load_model()
    p0=b.decoder_probs(model,np.zeros(2))
    previous=json.loads(INPUT.read_text())
    output=dict(source_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        checkpoint_sha256=hashlib.sha256((ROOT/'data/s5_vae_mnist.pt').read_bytes()).hexdigest(),
        scope='White-box known mixture oracle; separate diagnostic, not security guarantee.',
        books={},radii={})
    for j,(name,detail) in enumerate(previous['details'].items()):
        output['books'][name]={}
        for k,method in enumerate(('Algorithm 2: MC Fisher',
            'Natural gradient: exact Fisher','Euclidean gradient descent')):
            solutions=detail['solutions'][method]
            pc=np.stack([b.decoder_probs(model,np.array(row['z'])) for row in solutions])
            output['books'][name][method]=assess(p0,pc,np.random.default_rng(SEED+100*j+k))
    for radius in [.02,.05,.10,.20,.40,.80,1.20,1.60]:
        angles=np.arange(4)*np.pi/2+np.pi/7
        book=np.column_stack([radius*np.cos(angles),radius*np.sin(angles)])
        pc=np.stack([b.decoder_probs(model,z) for z in book])
        output['radii'][str(radius)]=assess(p0,pc,np.random.default_rng(SEED+1000+int(radius*100)))
    OUTPUT.write_text(json.dumps(output,indent=2))
    print('Wrote',OUTPUT)
if __name__=='__main__':main()
