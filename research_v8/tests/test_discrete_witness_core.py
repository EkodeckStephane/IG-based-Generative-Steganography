import numpy as np
from discrete_witness_core import *
from image_witness_core import exact_cachin_kl_gaussian_lsbm

def test_zero_beta_zero_kl():
    assert exact_discrete_cachin_kl(1.0,0.0)==0.0

def test_fisher_tends_to_continuous_two():
    assert abs(source_fisher_logsigma_discrete(np.array([1.2]))[0]-2)<1e-7

def test_quantization_matters_at_small_sigma():
    d=exact_discrete_cachin_kl(.6,.1); c=exact_cachin_kl_gaussian_lsbm(.6,.1)
    assert abs(d/c-1)>.03

def test_continuous_match_at_sigma_one():
    d=exact_discrete_cachin_kl(1.0,.1); c=exact_cachin_kl_gaussian_lsbm(1.0,.1)
    assert abs(d-c)<1e-7

def test_robust_ge_nominal():
    s=np.array([.7,.9,1.2,1.8,2.2,2.8,3.2,3.8]); c=np.ones(8)*100
    A=np.column_stack([np.ones(8),np.linspace(-1,1,8)]); b=np.linspace(.005,.05,8)
    n=nominal_discrete_risk(s,c,b); r=robust_discrete_risk_2d_fast(s,c,b,A,.08,nphi=360)[0]
    assert r>=n

def test_discrete_embedding_fisher_matches_continuous_when_sigma_one():
    from image_witness_core import embedding_fisher_at_zero
    d=embedding_fisher_beta0_discrete(np.array([1.0]))[0]
    assert abs(d-embedding_fisher_at_zero(1.0))<1e-6

def test_discrete_local_expansion():
    s=.65; b=1e-5
    ex=exact_discrete_cachin_kl(s,b)
    loc=.5*embedding_fisher_beta0_discrete(np.array([s]))[0]*b*b
    assert abs(ex/loc-1)<1e-3

def test_oracle_gradient_matches_finite_difference():
    from image_witness_core import weighted_standardized_logsigma_modes
    s=np.array([.8,1.0,1.4,2.0]); c=np.array([100.,120.,80.,90.]); A,_=weighted_standardized_logsigma_modes(s,c)
    o=DiscreteRobustOracle(s,c,A,.05,nphi=90,radial_levels=(0,.5,1)); b=np.array([.01,.02,.03,.04]); val,g,_=o.value_grad(b)
    h=1e-6
    for j in range(4):
        bp=b.copy();bm=b.copy();bp[j]+=h;bm[j]-=h
        fd=(o.value(bp)-o.value(bm))/(2*h)
        assert abs(fd-g[j])<2e-5

def test_rate_gradient_matches_finite_difference():
    c=np.array([1.,2.,3.]);b=np.array([.01,.03,.07]);g=ideal_rate_grad_bpp(c,b);h=1e-7
    for j in range(3):
        bp=b.copy();bm=b.copy();bp[j]+=h;bm[j]-=h
        fd=(ideal_rate_bpp(c,bp)-ideal_rate_bpp(c,bm))/(2*h)
        assert abs(fd-g[j])<1e-5
