import math
import numpy as np
from image_witness_core import (
    exact_cachin_kl_gaussian_lsbm, embedding_fisher_at_zero, local_fisher_kl,
    mipod_large_sigma_kl, normalized_source_fisher_metric, ellipse_boundary_2d,
    nominal_exact_risk, robust_exact_risk_2d, ideal_rate_bpp,
    optimize_nominal_exact, optimize_robust_exact_2d,
    uniform_shrink_to_robust_feasibility,
    exact_cachin_kl_gaussian_lsbm_vec, robust_exact_risk_2d_fast,
    weighted_standardized_logsigma_modes,
)

def test_zero_embedding_zero_cachin_risk():
    assert abs(exact_cachin_kl_gaussian_lsbm(1.5, 0.0)) < 1e-15

def test_local_fisher_matches_exact_small_beta():
    sigma,beta=1.7,1e-4
    assert math.isclose(exact_cachin_kl_gaussian_lsbm(sigma,beta),local_fisher_kl(sigma,beta),rel_tol=2e-3,abs_tol=1e-12)

def test_large_sigma_mipod_scaling():
    sigma,beta=5.0,0.01
    assert math.isclose(local_fisher_kl(sigma,beta),mipod_large_sigma_kl(sigma,beta),rel_tol=1e-3)

def test_source_metric_spd_and_boundary():
    counts=np.array([100,100,100,100]); z=np.array([-1.5,-0.5,0.5,1.5]); A=np.column_stack([np.ones(4),z])
    G=normalized_source_fisher_metric(counts,A); assert np.all(np.linalg.eigvalsh(G)>0)
    pts=ellipse_boundary_2d(G,0.12,64); vals=np.einsum('ni,ij,nj->n',pts,G,pts)
    assert np.allclose(vals,0.12**2,rtol=1e-10,atol=1e-12)

def test_robust_risk_not_below_nominal():
    sigmas=np.array([1.0,1.4,2.0,3.0]); counts=np.array([100]*4); z=np.array([-1.5,-0.5,0.5,1.5])
    A=np.column_stack([np.ones(4),z]); b=np.array([0.005,0.01,0.03,0.08])
    assert robust_exact_risk_2d(sigmas,counts,b,A,0.10,360)[0] >= nominal_exact_risk(sigmas,counts,b)-1e-12

def test_robust_design_beats_uniform_shrink_in_rate_on_frozen_sanity_case():
    sigmas=np.array([1.2,2.2]); counts=np.array([1200,800]); A=np.eye(2); eps=2e-4; radius=0.12
    bn=optimize_nominal_exact(sigmas,counts,eps); br=optimize_robust_exact_2d(sigmas,counts,A,eps,radius,nphi=180)
    bs,_=uniform_shrink_to_robust_feasibility(bn,sigmas,counts,A,eps,radius,nphi=360)
    assert robust_exact_risk_2d(sigmas,counts,br,A,radius,nphi=1440)[0] <= eps*(1+5e-4)
    assert robust_exact_risk_2d(sigmas,counts,bs,A,radius,nphi=1440)[0] <= eps*(1+5e-4)
    assert ideal_rate_bpp(counts,br)>ideal_rate_bpp(counts,bs)

def test_vectorized_kl_matches_scalar():
    s=np.array([0.9,1.4,2.7]); b=np.array([0.01,0.03,0.08])
    vv=exact_cachin_kl_gaussian_lsbm_vec(s,b)
    ss=np.array([exact_cachin_kl_gaussian_lsbm(float(x),float(y)) for x,y in zip(s,b)])
    assert np.allclose(vv,ss,rtol=1e-12,atol=1e-14)

def test_weighted_modes_have_orthogonal_normalized_metric():
    sig=np.array([0.8,1.0,1.4,2.0,3.0]); cnt=np.array([50,100,200,100,50])
    A,_=weighted_standardized_logsigma_modes(sig,cnt)
    assert np.allclose(normalized_source_fisher_metric(cnt,A),2*np.eye(2),rtol=1e-12,atol=1e-12)

def test_fast_robust_matches_slow_two_group():
    sig=np.array([1.2,2.2]); cnt=np.array([1200,800]); A=np.eye(2); b=np.array([0.013,0.07])
    assert math.isclose(robust_exact_risk_2d(sig,cnt,b,A,0.12,nphi=720)[0],robust_exact_risk_2d_fast(sig,cnt,b,A,0.12,nphi=720)[0],rel_tol=1e-11,abs_tol=1e-13)

def test_exact_kl_decreases_with_sigma():
    vals=[exact_cachin_kl_gaussian_lsbm(s,0.06) for s in [0.8,1.0,1.4,2.0,3.0]]
    assert all(vals[i]>vals[i+1] for i in range(len(vals)-1))
