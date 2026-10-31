#!/usr/bin/env python3
"""Separate smooth Bernoulli family: verifies IVP geodesic continuity under C1 metric perturbation.
Not a proof for the real ReLU VAE or for a fixed-endpoint BVP.
"""
import json
from pathlib import Path
import numpy as np
from scipy.special import expit
from scipy.integrate import solve_ivp
A=np.array([[.6,.2],[.3,-.5],[-.4,.6],[.7,.4],[-.7,-.3],[.35,.75],[-.75,.25],[.25,-.6],[.4,-.2]],float)
B=np.array([[.7,-.5],[-.5,.6],[.8,.3],[-.7,-.4],[.6,.8],[.4,-.8],[-.8,.5],[.3,.7],[-.4,.6]],float)

def g0(z):
 z=np.array(z,dtype=float);h=A@z+.2*np.sin(B@z);J=A+.2*np.cos(B@z)[:,None]*B
 p=expit(h);return J.T@((p*(1-p))[:,None]*J)

def g(z,eps):
 z=np.array(z,dtype=float);a=.5*np.sin(z[0])+.25*np.cos(z[1]);return (1+eps*a)*g0(z)

def christoffel(z,eps):
 G=g(z,eps);ginv=np.linalg.inv(G);d=np.empty((2,2,2));h=1e-5
 for k in (0,1):
  v=np.eye(2)[k]*h
  d[k]=(g(z+v,eps)-g(z-v,eps))/(2*h)
 gamma=np.zeros((2,2,2))
 for i in (0,1):
  for j in (0,1):
   for k in (0,1):
    gamma[i,j,k]=.5*sum(ginv[i,l]*(d[j,k,l]+d[k,j,l]-d[l,j,k]) for l in (0,1))
 return gamma

def rhs(t,y,eps):
 z=y[:2];v=y[2:];G=christoffel(z,eps)
 return np.r_[v,-np.einsum('ijk,j,k->i',G,v,v)]

def trace(eps):
 sol=solve_ivp(rhs,(0,1),[0.,0.,.55,-.38],args=(eps,),rtol=3e-9,atol=2e-10,
               dense_output=True,max_step=.025)
 assert sol.success,sol.message
 return sol.sol(np.linspace(0,1,101))[:2].T

def main():
 b=trace(0);rows=[]
 for eps in (.005,.01,.02,.05,.1):
  x=trace(eps);err=float(np.max(np.linalg.norm(x-b,axis=1)))
  rows.append({'epsilon':eps,'max_geodesic_coordinate_deviation':err,'deviation_over_eps':err/eps})
 res={'scope':'Smooth synthetic Bernoulli 2-D family, same initial position/velocity, geodesic IVP. Not the ReLU VAE; no BVP result.',
      'metric':'g=(1+epsilon*(0.5 sin z0+0.25 cos z1)) J^T diag(p(1-p)) J',
      'rows':rows}
 out=Path(__file__).resolve().parent/'r21_smooth_geodesic_results.json';out.write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
if __name__=='__main__': main()