"""Finite-source message partition and Fisher tilt: reproducible reference core.
This is NOT original NG-Stego Algorithm 2 and NOT the entire experimental runner.
For the executed full source and datasets see the corresponding research ZIP.
"""
import numpy as np
from scipy.special import logsumexp

def conditional_quantile_partition(calibration_features):
    """2D features from *independent calibration* source; four conditional bins."""
    v=np.asarray(calibration_features,dtype=float)
    t0=float(np.median(v[:,0]))
    upper=v[:,0]>=t0
    t1=[float(np.median(v[~upper,1])),float(np.median(v[upper,1]))]
    return t0,t1

def bin_labels(features,thresholds):
    v=np.asarray(features,dtype=float);t0,t1=thresholds
    b0=(v[:,0]>=t0).astype(int)
    return 2*b0+(v[:,1]>=np.asarray(t1)[b0]).astype(int)

def fisher_tilt_direction(statistics,utility):
    """At theta=0 in finite exponential family P_theta(x) ∝ exp(theta.T @ t(x))."""
    t=np.asarray(statistics,dtype=float)
    u=np.asarray(utility,dtype=float)
    F=np.cov(t,rowvar=False,bias=True)
    g=((t-t.mean(axis=0))*(u-u.mean())[:,None]).mean(axis=0)
    return np.linalg.solve(F,g),g,F

def model_weights(theta,statistics):
    scores=np.asarray(statistics,dtype=float)@np.asarray(theta,dtype=float)
    return np.exp(scores-logsumexp(scores))

def tv_to_uniform_source(model_weights_vector,labels):
    """Q(x)=P(x)/(4 q_label(x)), P0(x)=1/n; exact for finite uniform source."""
    p=np.asarray(model_weights_vector,dtype=float)
    b=np.asarray(labels,dtype=int)
    q=np.bincount(b,weights=p,minlength=4)
    if np.any(q<=0):raise ValueError("All bins must be non-empty")
    Q=p/(4*q[b]);P0=np.ones(len(p))/len(p)
    return .5*np.abs(Q-P0).sum(),q,Q

def same_source_tv(p,labels):
    """TV between Q (uniform messages) and its *own* proposal P (bin selection)."""
    p=np.asarray(p,dtype=float);b=np.asarray(labels,dtype=int)
    q=np.bincount(b,weights=p,minlength=4)
    return .5*np.abs(q-0.25).sum()

def test_exact_identity():
    p=np.array([.10,.20,.25,.05,.15,.10,.15])
    b=np.array([0,0,1,1,2,3,3])
    q=np.bincount(b,weights=p,minlength=4)
    Q=p/(4*q[b])
    assert np.isclose(.5*np.abs(Q-p).sum(),same_source_tv(p,b))
    assert np.isclose(Q.sum(),1.)
    t=np.array([[0.,1.],[1.,2.],[2.,3.],[1.,4.],[3.,2.]],float)
    natural,g,F=fisher_tilt_direction(t,np.array([.1,.3,.2,.8,.4]))
    assert np.isfinite(natural).all()
    return True
if __name__=="__main__":
    print("finite-source TV + Fisher core:", "PASS" if test_exact_identity() else "FAIL")
