#!/usr/bin/env python3
"""Smoke/numerical tests for the public pilot reproducer; not a security test."""
import numpy as np
from robust_fisher_heldout_reproducer import (
  REPO,model_load,decode_p,calibrate,sample,dataset,evalobj,boundary,bernoulli_kl)
import torch

def test():
    torch.set_num_threads(1)
    model=model_load(REPO/"data"/"s5_vae_mnist.pt")
    z=np.array([.13,-.21]);p=decode_p(model,z)
    cal=calibrate(sample(1942,p,1000))
    d=dataset(1943,p,2000,cal)
    r=evalobj(model,z,p,d,True)
    g=np.asarray(r["gradient"]);F=np.asarray(r["fisher"])
    assert np.linalg.eigvalsh(F).min()>0
    assert np.allclose(F,F.T,atol=1e-8)
    h=1e-4
    fd=np.array([(evalobj(model,z+np.eye(2)[i]*h,p,d)["J"]-
                  evalobj(model,z-np.eye(2)[i]*h,p,d)["J"])/(2*h) for i in range(2)])
    assert np.allclose(g,fd,rtol=.006,atol=1e-5),(g,fd)
    dF=np.linalg.solve(F+1e-6*np.eye(2),g)
    local=(g@dF)/np.sqrt(dF@F@dF)
    euclidean=(g@g)/np.sqrt(g@F@g)
    assert local+1e-8>=euclidean
    for direction in (g,dF):
        to=boundary(model,z,p,direction,.02)
        assert abs(bernoulli_kl(decode_p(model,to),p)-.02)<1e-6
    print("PASS: gradient-FD, symmetric SPD Fisher, local Fisher gain, KL-budget")
if __name__=="__main__":test()
