#!/usr/bin/env python3
"""Strict, finite-source diagnostic: Fisher vs Euclidean for robust-message goodput.

This experiment does NOT execute original NG-Stego Algorithm 2 and does NOT
establish a Fisher advantage on a neural generator. Its Fisher matrix is the
categorical exponential-tilt covariance of public two-dimensional MNIST
statistics, not the VAE latent FIM. No security claim beyond finite MNIST pool.

Data: original MNIST IDX train/test gz (not redistributed by this script).
All tuning solely on 20k optimization images, independent 10k test source.
Source cover P0 is uniform over the images of each independently selected pool.
Messages 2 bit uniformly masked, conditioned on public 4-symbol partition.
Validation is exact over finite source, not noisy 420-message Monte Carlo.
"""
from pathlib import Path
import gzip,struct,json,hashlib,time
import numpy as np
from scipy.special import logsumexp
from PIL import Image, ImageFilter
from scipy.ndimage import median_filter

ROOT=Path(__file__).resolve().parent
SEED=20261031


def load(path):
    with gzip.open(path,'rb') as f:data=f.read()
    code,n,h,w=struct.unpack('>IIII',data[:16])
    assert (code,h,w)==(2051,28,28) and len(data)==16+n*h*w
    return np.frombuffer(data[16:],dtype=np.uint8).reshape(-1,784).copy().astype(np.float32)/255


def stats(x):
    xx=np.asarray(x,dtype=np.float64).reshape(-1,28,28)
    weights=np.maximum(xx-.08,0.)
    mass=weights.sum(axis=(1,2)).clip(min=1e-7)
    yy=np.arange(28,dtype=float)[None,:,None]
    xc=np.arange(28,dtype=float)[None,None,:]
    mx=(weights*xc).sum((1,2))/mass
    my=(weights*yy).sum((1,2))/mass
    vx=(weights*(xc-mx[:,None,None])**2).sum((1,2))/mass
    vy=(weights*(yy-my[:,None,None])**2).sum((1,2))/mass
    return np.column_stack([vx,vy])


def robust_stats(x):
    xx=np.asarray(x,dtype=np.float64).reshape(-1,28,28)
    w=np.maximum(median_filter(xx,size=(1,3,3),mode='nearest')-.1,0.)
    mass=w.sum(axis=(1,2)).clip(min=1e-7)
    yy=np.arange(28,dtype=float)[None,:,None]
    xc=np.arange(28,dtype=float)[None,None,:]
    mx=(w*xc).sum((1,2))/mass
    my=(w*yy).sum((1,2))/mass
    vx=(w*(xc-mx[:,None,None])**2).sum((1,2))/mass
    vy=(w*(yy-my[:,None,None])**2).sum((1,2))/mass
    return np.column_stack([vx,vy])


def calibrate(x):
    s=robust_stats(x);t0=float(np.median(s[:,0]));b0=s[:,0]>=t0
    t1=np.array([np.median(s[~b0,1]),np.median(s[b0,1])])
    return [t0,*map(float,t1)]


def bins(x,c):
    v=robust_stats(x);a=v[:,0]>=c[0];b=v[:,1]>=np.where(a,c[2],c[1])
    return (2*a.astype(np.int32)+b.astype(np.int32)).astype(np.uint8)


def transforms(x,kind,rng):
    x=np.asarray(x,dtype=np.float32).reshape(-1,28,28)
    if kind=='clean':return x.reshape(-1,784)
    if kind.startswith('flip_'):
        t=float(kind.split('_')[1]);return np.where(rng.random(x.shape)<t,1.-x,x).reshape(-1,784)
    if kind=='shift_1':
        out=np.zeros_like(x);out[:,1:,:]=x[:,:-1,:];return out.reshape(-1,784)
    out=[]
    for a in x:
        im=Image.fromarray(np.uint8(np.round(a*255)),mode='L')
        if kind=='jpeg_50':
            import io
            buf=io.BytesIO();im.save(buf,format='JPEG',quality=50,subsampling=0);buf.seek(0);im=Image.open(buf).convert('L')
        elif kind=='blur_0.6':im=im.filter(ImageFilter.GaussianBlur(radius=.6))
        elif kind=='resize_14':im=im.resize((14,14),Image.Resampling.BILINEAR).resize((28,28),Image.Resampling.BILINEAR)
        else:raise ValueError(kind)
        out.append(np.asarray(im,dtype=np.float32).ravel()/255.)
    return np.array(out,dtype=np.float32)


def probabilities(T,theta):
    q=T@theta;return np.exp(q-logsumexp(q))


def measures(T,b,correct_by_ch,theta):
    """All metrics *exact* on finite source given fixed transformation realization.
    For iid stochastic flips, fixed-seed realization is a controlled approximation
    of stochastic channel expectation, not analytic integration over channel noise.
    """
    p=probabilities(T,theta);q=np.bincount(b,weights=p,minlength=4)
    if min(q)<1e-7:raise ValueError('Degenerate message bin')
    Q=p/(4*q[b]);tv=float(.5*np.abs(Q-1/len(b)).sum())
    kl=float(np.sum(p*np.log(p*len(b))))
    successes={}
    for ch,good in correct_by_ch.items():
        successes[ch]=float(np.dot(Q,good))
    return {'TV':tv,'KL':max(0.,kl),'draws':float(np.mean(1/q)),'q':q.tolist(),
            'accuracy':successes,'objective':float(np.mean([successes[ch] for ch in ['jpeg_50','blur_0.6','resize_14','shift_1','flip_0.001','flip_0.01']]))}


def gradient(T,b,correct):
    """Gradient of J=(1/4) sum_bin E_{p_theta|bin}[utility(X)]."""
    U=np.mean(np.stack([correct[k].astype(float) for k in ['jpeg_50','blur_0.6','resize_14','shift_1','flip_0.001','flip_0.01']],axis=1),axis=1)
    grad=np.zeros(T.shape[1]);cov=np.cov(T,rowvar=False,bias=True)
    for j in range(4):
        ti=T[b==j];ui=U[b==j]
        grad+=(ti*ui[:,None]).mean(axis=0)-ti.mean(axis=0)*ui.mean()
    return grad/4,cov


def find_feasible(T,b,correct,direction,cap_tv,cap_kl=.02):
    """Radial search, from theta=0, pre-registered constrained line-search."""
    norm=np.linalg.norm(direction)
    if norm<=1e-12:raise ValueError('Zero direction')
    direction=np.asarray(direction)/norm
    # Evaluate increasing radius, retain best feasible objective (not automatically all budget).
    # Grid evaluated on optimisation sample only.
    alphas=np.r_[0,np.geomspace(1e-4,2.,70)]
    candidates=[]
    for a in alphas:
        row=measures(T,b,correct,a*direction)
        if row['TV']<=cap_tv+1e-10 and row['KL']<=cap_kl+1e-10:
            candidates.append((row['objective'],float(a),row))
    best=max(candidates,key=lambda z:z[0])
    return best[1]*direction,best[2]


def ci_diff(v1,v2,b,nboot=400,seed=123):
    # Assesses variability if independently sampled image pool from empirical source;
    # for exact finite-source population metrics, CI is not needed but supports external generalization caveat.
    rng=np.random.default_rng(seed);n=len(b);dif=[]
    for _ in range(nboot):
        ix=rng.integers(0,n,n)
        # Difference of per-image contributions under *fixed* exact original bin masses,
        # a first-order bootstrap approximation, not a full re-optimisation CI.
        dif.append(float((v1[ix]-v2[ix]).mean()*n))
    return [float(np.quantile(dif,.025)),float(np.quantile(dif,.975))]


def q_dist(T,b,theta):
    p=probabilities(T,theta);q=np.bincount(b,weights=p,minlength=4);return p/(4*q[b])


def main():
    t0=time.time();train=load(ROOT/'mnist_train_real.gz');test=load(ROOT/'mnist_test_real.gz')
    c=calibrate(train[5000:20000]);optim=train[20000:40000]
    centers=stats(optim);mean=centers.mean(axis=0);std=centers.std(axis=0)
    T=(centers-mean)/std;Ttest=(stats(test)-mean)/std
    bopt=bins(optim,c);btest=bins(test,c)
    channels=['jpeg_50','blur_0.6','resize_14','shift_1','flip_0.001','flip_0.01']
    def precompute(x,b,seed):
        correct={'clean':np.ones(len(x),dtype=np.float32)}
        for j,k in enumerate(channels):
            xx=transforms(x,k,np.random.default_rng(seed+j*271))
            correct[k]=(bins(xx,c)==b).astype(np.float32)
        return correct
    up=precompute(optim,bopt,SEED+101);ut=precompute(test,btest,SEED+100101)
    grad,F=gradient(T,bopt,up)
    directions={'fisher':np.linalg.solve(F+1e-10*np.eye(2),grad),'euclidean':grad}
    out={'design':'Finite empirical MNIST pool: NOT original NG-Stego Algorithm 2 or neural generator Fisher',
         'seed':SEED,'source_sha256':{},'exploratory_decoder_selection_train':5000,'split':{'calibration_train':15000,'optimisation_train':20000,'unused_detector_train':20000,'heldout_test':10000},
         'features':'T=raw centred moments; message bins=median3x3 + foreground-clipped centred moments, selected exploratory on separate 5k training images','channels':channels,'objective':'mean exact single-image conditional decoder success across 6 channels',
         'caps_TV':[.03,.05,.075],'cap_KL':.02,'generator_Fisher':False,'F':F.tolist(),'grad':grad.tolist(),
         'calibration':c,'results':{}}
    for filename in ['mnist_train_real.gz','mnist_test_real.gz']:
        out['source_sha256'][filename]=hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()
    matched=measures(Ttest,btest,ut,np.zeros(2))
    out['matched_heldout']=matched
    print('MATCHED',matched['objective'],matched['TV'],matched['draws'],flush=True)
    for cap in out['caps_TV']:
        rs={}
        for method in directions:
            theta,fit=find_feasible(T,bopt,up,directions[method],cap)
            ev=measures(Ttest,btest,ut,theta)
            rs[method]={'theta':theta.tolist(),'fit':fit,'heldout':ev}
            print('TV CAP',cap,method,'theta',theta,'fitobj',fit['objective'],'heldout',ev['objective'],
                  'TV',ev['TV'],'KL',ev['KL'],flush=True)
        Pf=q_dist(Ttest,btest,np.array(rs['fisher']['theta']));Pe=q_dist(Ttest,btest,np.array(rs['euclidean']['theta']))
        utest=np.mean(np.array([ut[k] for k in channels]),axis=0)
        dif=utest*(Pf-Pe)
        rs['comparison']={'fisher_minus_euclidean_J':rs['fisher']['heldout']['objective']-rs['euclidean']['heldout']['objective'],
                          'bootstrap95_approx':ci_diff(utest*Pf,utest*Pe,btest,seed=SEED+int(cap*1e5)),
                          'fisher_minus_matched_J':rs['fisher']['heldout']['objective']-matched['objective'],
                          'fisher_tv_minus_euclidean':rs['fisher']['heldout']['TV']-rs['euclidean']['heldout']['TV']}
        out['results'][str(cap)]=rs
    out['elapsed_s']=time.time()-t0
    (ROOT/'operational_fisher_results.json').write_text(json.dumps(out,indent=2,allow_nan=False))
    print('COMPLETE',out['elapsed_s'])

if __name__=='__main__':main()
