#!/usr/bin/env python3
"""A1-A3: auditable generator-constrained Fisher energy diagnostics.

No claim of novel mathematics or global certification of VAE optimizer.
Dependencies: numpy scipy matplotlib torch, and the original sim_s5_vae_mnist.py
plus SHA-256 checked s5_vae_mnist.pt in the same directory.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse, hashlib, json, math, csv, sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad, cumulative_trapezoid
from scipy.optimize import minimize
from scipy.special import xlogy, expit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results'; FIG = ROOT/'figures'
OUT.mkdir(exist_ok=True, parents=True); FIG.mkdir(exist_ok=True,parents=True)
SEED=20261104
CHECKSUM='e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61'

def bern_kl(p,q):
    p=np.asarray(p,dtype=np.float64);q=np.asarray(q,dtype=np.float64)
    return float(np.sum(xlogy(p,p/q)+xlogy(1-p,(1-p)/(1-q))))

def bern_ambient(p,q):
    p=np.asarray(p,dtype=float);q=np.asarray(q,dtype=float)
    log_b=np.log(np.sqrt(p*q)+np.sqrt((1-p)*(1-q))).sum()
    return float(2*np.arccos(np.clip(np.exp(log_b),0,1)))

def ring_probs(theta):
    return np.stack([.5+.22*np.cos(theta),.5+.23*np.sin(theta)],axis=-1)

def ring_fisher(theta):
    p=ring_probs(theta);dp=np.stack([-.22*np.sin(theta),.23*np.cos(theta)],axis=-1)
    return np.sum(dp**2/(p*(1-p)),axis=-1)

def ring_length(a,b):
    return abs(quad(lambda u: math.sqrt(float(ring_fisher(u))),a,b,epsabs=1e-11,epsrel=1e-11)[0])

def arc_inverse(a,b,n):
    # High-resolution deterministic arclength reparametrization, no repeated root quadrature.
    s=np.linspace(0,1,16385)
    u=a+(b-a)*s
    speed=np.sqrt(ring_fisher(u))*abs(b-a)
    cumulative=np.r_[0.,cumulative_trapezoid(speed,s)]
    target=np.linspace(0,cumulative[-1],n+1)
    angles=a+(b-a)*np.interp(target,cumulative,s)
    return angles,float(cumulative[-1])

def scalar_chain(th):
    p=ring_probs(th)
    return sum(bern_kl(x,y) for x,y in zip(p[1:],p[:-1]))

def toy_ring():
    a=-.65;b=2.35
    short, Lshort=arc_inverse(a,b,256)
    long, Llong=arc_inverse(a,b-2*np.pi,256)
    # Confirm orientation-independent signed-arc lengths
    dg=min(Lshort,Llong);da=bern_ambient(ring_probs(a),ring_probs(b))
    assert da < dg and np.all(ring_fisher(np.linspace(0,2*np.pi,500))>.01)
    results={'theta_a':a,'theta_b':b,'d_ambient_exact':da,'d_generator_exact':dg,
             'generator_excess_squared_exact':dg**2-da**2,
             'arc_lengths':{'direct':Lshort,'other':Llong},'finite_N':[]}
    for N in [4,8,16,32,64,128,256]:
        x,l=arc_inverse(a,b,N);xx,ll=arc_inverse(a,b-2*np.pi,N)
        Cshort=scalar_chain(x);Clong=scalar_chain(xx)
        best=min(Cshort,Clong)
        results['finite_N'].append({'N':N,'N_times_short_path_KL':N*Cshort,
                                    'N_times_other_path_KL':N*Clong,
                                    'best_of_two_curve_candidates':N*best,
                                    'target_half_dg2':.5*dg**2,
                                    'ratio_short_to_limit':N*Cshort/(.5*dg**2)})
    # Three-term exact identity on a non-optimal/non-uniform 1D feasible path
    t=np.linspace(0,1,10001)
    th=a+(b-2*np.pi-a)*(t**2)  # choose intentionally long arc and nonconstant speed
    thp=2*(b-2*np.pi-a)*t
    g=ring_fisher(th)
    ell=float(np.trapezoid(np.abs(thp)*np.sqrt(g),t))
    energy=float(np.trapezoid(thp**2*g,t))
    pieces=[energy-ell**2,ell**2-dg**2,dg**2-da**2]
    assert min(pieces)>-1e-7
    assert abs((energy-da**2)-sum(pieces))<1e-8
    results['decomposition']={'energy':energy,'length':ell,'total_excess':energy-da**2,
       'speed_excess':pieces[0],'route_excess':pieces[1],'generator_excess':pieces[2],
       'reconstruction_error':(energy-da**2)-sum(pieces)}
    return results

class VAEModel:
    def __init__(self):
        import torch
        from sim_s5_vae_mnist import VAE
        ck=Path(__file__).with_name('s5_vae_mnist.pt')
        actual=hashlib.sha256(ck.read_bytes()).hexdigest()
        if actual!=CHECKSUM:raise RuntimeError('Checkpoint mismatch: '+actual)
        torch.set_num_threads(1)
        m=VAE();m.load_state_dict(torch.load(ck,map_location='cpu',weights_only=True));m.eval()
        self.layers=[]
        for i in (0,2,4):
            self.layers.append((m.dec[i].weight.detach().cpu().numpy().astype(np.float64),
                                m.dec[i].bias.detach().cpu().numpy().astype(np.float64)))
        self.hash=actual
    def logits_J(self,z):
        z=np.asarray(z,dtype=np.float64);(A,a),(B,b),(C,c)=self.layers
        v=A@z+a; w=B@np.maximum(v,0)+b
        h=C@np.maximum(w,0)+c
        J=C@((B*(w>0)[:,None])@((v>0)[:,None]*A))
        return h,J
    def probs_F(self,z):
        logits,J=self.logits_J(z);p=expit(logits)
        F=J.T@((p*(1-p))[:,None]*J)
        return p,F
    def metric(self,z):return self.probs_F(z)[1]

def segment_breakpoints(model,x,y):
    # All ReLU activation boundaries on a linear latent segment, determined analytically
    # from piecewise affine pre-activation functions of both hidden layers.
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    (A,a),(B,b),_=model.layers
    v0=A@x+a;v1=A@y+a; dv=v1-v0
    bp=[0.,1.]
    for val,delta in zip(v0,dv):
        if abs(delta)>1e-14:
            t=-val/delta
            if 1e-13<t<1-1e-13:bp.append(float(t))
    bp=np.unique(np.round(bp,14))
    extra=[]
    for left,right in zip(bp[:-1],bp[1:]):
        va=v0+dv*left;vb=v0+dv*right
        wa=B@np.maximum(va,0)+b;wb=B@np.maximum(vb,0)+b
        for v0j,v1j in zip(wa,wb):
            den=v1j-v0j
            if abs(den)>1e-13:
                frac=-v0j/den
                if 1e-12<frac<1-1e-12:extra.append(float(left+frac*(right-left)))
    return np.unique(np.round(np.r_[bp,extra],13))

def gauss2_segment(model,x,y,order=8):
    # Accurate *feasible* path length: integrate separately across every ReLU kink.
    # No derivative continuity is assumed across an activation boundary.
    points=segment_breakpoints(model,x,y)
    xi,wi=np.polynomial.legendre.leggauss(order)
    delta=np.asarray(y)-np.asarray(x)
    total=0.
    for left,right in zip(points[:-1],points[1:]):
        mid=(left+right)/2;half=(right-left)/2
        for u,w in zip(xi,wi):
            t=mid+half*u
            F=model.metric(np.asarray(x)+t*delta)
            total+=float(w*half*np.sqrt(max(delta@F@delta,0)))
    return total

def polyline_length(model,nodes,order=8):
    return sum(gauss2_segment(model,a,b,order=order) for a,b in zip(nodes[:-1],nodes[1:]))

def optimize_polyline(model,a,b,n,perturb=0.,seed=123,maxiter=100):
    rng=np.random.default_rng(seed)
    line=np.linspace(a,b,n+1)
    if perturb:line[1:-1]+=rng.normal(scale=perturb,size=(n-1,2))
    def getnodes(v):return np.vstack([a,v.reshape(n-1,2),b])
    # Optimize *length*; every candidate is feasible -> an upper bound for d_G.
    def func(v):return polyline_length(model,getnodes(v),order=3)
    sol=minimize(func,line[1:-1].ravel(),method='L-BFGS-B',options={'maxiter':maxiter,'ftol':1e-10})
    nodes=getnodes(sol.x); L=polyline_length(model,nodes,order=12)
    return {'length':float(L),'nodes':nodes.tolist(),'status':bool(sol.success),'iterations':int(sol.nit),'function_evals':int(sol.nfev)}

def vae_upper_bounds(run_heavy=False):
    model=VAEModel()
    cases=[('local_no_kink',[-.15,-.10],[-.13,-.08]),('local_two_kinks',[-.3,.2],[-.28,.23]),('second_two_kinks',[.1,-.4],[.13,-.37]),('moderate_many_kinks',[-.6,.6],[-.35,.65])]
    results={'checkpoint_sha256':model.hash,'scope':'ReLU VAE: feasible length upper bounds, NOT certified intrinsic distance', 'pairs':[]}
    for i,(name,a,b) in enumerate(cases):
        a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
        p,q=model.probs_F(a)[0],model.probs_F(b)[0]
        da=bern_ambient(p,q)
        line=np.linspace(a,b,25);Lline=polyline_length(model,line,order=12)
        u=optimize_polyline(model,a,b,4,perturb=0,maxiter=20)
        best=u
        if run_heavy:
            for init in [0.12,-.12]:
                z=optimize_polyline(model,a,b,10,perturb=abs(init),seed=31+i,maxiter=70)
                if z['length']<best['length']:best=z
        upper=min(Lline,best['length'])
        _,F_a=model.probs_F(a)
        _,F_b=model.probs_F(b)
        eig_a=np.linalg.eigvalsh(F_a);eig_b=np.linalg.eigvalsh(F_b)
        results['pairs'].append({'name':name,'a':a.tolist(),'b':b.tolist(),
           'ambient_FR_exact':da,'straight_feasible_length':Lline,
           'optimized_feasible_length':best['length'],
           'validated_feasible_upper_length':upper,
           'intrinsic_distance_interval':[da,upper],
           'generator_excess_squared_interval':[0,upper**2-da**2],
           'straight_length_excess_over_optimized_candidate':Lline-best['length'],
           'selected_candidate':best,
           'F_eigenvalues_at_a':eig_a.tolist(),'F_eigenvalues_at_b':eig_b.tolist(),
           'num_relu_jumps_on_straight':relu_jumps(model,a,b)})
    return results

def relu_jumps(model,a,b):
    A,aa=model.layers[0];B,bb=model.layers[1];n=0;last=None
    for t in np.linspace(0,1,101):
        x=a*(1-t)+b*t
        v=A@x+aa;w=B@np.maximum(v,0)+bb
        sign=np.r_[v>0,w>0]
        if last is not None: n+=np.count_nonzero(sign!=last)
        last=sign
    return int(n)

def generate_plots(toy,vae):
    fig,ax=plt.subplots(figsize=(7.2,4.6))
    rows=toy['finite_N']; x=[r['N'] for r in rows]
    ax.plot(x,[r['N_times_short_path_KL'] for r in rows],marker='o',label='N × sum KL along feasible geodesic')
    ax.axhline(.5*toy['d_generator_exact']**2,color='black',linestyle='--',label='0.5 × intrinsic distance squared')
    ax.axhline(.5*toy['d_ambient_exact']**2,color='gray',linestyle=':',label='0.5 × ambient FR distance squared')
    ax.set_xscale('log',base=2);ax.set_xlabel('Number of KL segments N');ax.set_ylabel('Rescaled cumulative KL (nats × steps)')
    ax.set_title('One-dimensional Bernoulli generator: exact intrinsic benchmark')
    ax.legend(loc='best',fontsize=8);fig.tight_layout()
    fig.savefig(FIG/'toy_variational_limit.png',dpi=175);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.2,3.8))
    vs=toy['decomposition'];lbl=['Speed','Nonminimal route','Generator restriction']
    bars=ax.bar(lbl,[vs['speed_excess'],vs['route_excess'],vs['generator_excess']])
    ax.set_ylabel('Excess squared Fisher distance / energy')
    ax.set_title('Exact nonnegative energy decomposition (Bernoulli ring)')
    for p in bars:ax.annotate(f'{p.get_height():.3f}',(p.get_x()+p.get_width()/2,p.get_height()),xytext=(0,3),textcoords='offset points',ha='center',fontsize=9)
    fig.tight_layout();fig.savefig(FIG/'toy_three_gaps.png',dpi=175);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.2,4.6))
    vals=vae['pairs'];xx=np.arange(len(vals));w=.23
    ax.bar(xx-w,[p['ambient_FR_exact'] for p in vals],w,label='Exact ambient lower bound')
    ax.bar(xx,[p['optimized_feasible_length'] for p in vals],w,label='Optimized feasible upper bound')
    ax.bar(xx+w,[p['straight_feasible_length'] for p in vals],w,label='Straight latent path length')
    ax.set_xticks(xx,[p['name'] for p in vals]);ax.set_ylabel('Fisher-Rao path length')
    ax.set_title('ReLU Bernoulli VAE: bounded model distance (not exact)')
    ax.legend(fontsize=8);fig.tight_layout();fig.savefig(FIG/'vae_length_bounds.png',dpi=175);plt.close(fig)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--heavy',action='store_true');args=parser.parse_args()
    toy=toy_ring();vae=vae_upper_bounds(args.heavy)
    results={'study':'DSP-D-26-02810 Phase I A1-A3, 2026-11-04','seed':SEED,'toy':toy,'vae':vae,
      'status':'numerical exploration; theorem treated separately; no global certificate for VAE optimizer'}
    (OUT/'phase1_results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    with (OUT/'phase1_summary.csv').open('w',newline='') as f:
        wr=csv.writer(f);wr.writerow(['model','case','ambient_FR_exact','intrinsic_FR_lower_bound','intrinsic_FR_upper_bound','generator_gap_sq_lower','generator_gap_sq_upper','straight_length'])
        wr.writerow(['ring','test',toy['d_ambient_exact'],toy['d_generator_exact'],toy['d_generator_exact'],toy['generator_excess_squared_exact'],toy['generator_excess_squared_exact'],toy['decomposition']['length']])
        for row in vae['pairs']:
            a,b=row['intrinsic_distance_interval'];lo,hi=row['generator_excess_squared_interval']
            wr.writerow(['VAE',row['name'],row['ambient_FR_exact'],a,b,lo,hi,row['straight_feasible_length']])
    generate_plots(toy,vae)
    print(json.dumps({'toy':{'ambient':toy['d_ambient_exact'],'intrinsic':toy['d_generator_exact'],'generator_excess_sq':toy['generator_excess_squared_exact'],'finite_N_last':toy['finite_N'][-1]},
      'VAE_pairs':[{k:v for k,v in row.items() if k in ['name','ambient_FR_exact','straight_feasible_length','optimized_feasible_length','intrinsic_distance_interval','num_relu_jumps_on_straight']} for row in vae['pairs']]},indent=2))
if __name__=='__main__': main()
