"""Unit/regression tests; run python -m unittest test_r21_r22.py -v"""
import unittest
from pathlib import Path
import numpy as np
from scipy.special import expit
from r21_r22_experiment import load, pfj, kl_grad, norm_error, VAE, logits_and_J
from r21_smooth_geodesic_stability import trace

class Check(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=load(Path(__file__).resolve().parent/'data/s5_vae_mnist.pt')

    def test_fisher_spd_and_covariance(self):
        z=np.array([.22,-.17]);p,J,F=pfj(self.m,z)
        self.assertGreater(np.linalg.eigvalsh(F).min(),0)
        rng=np.random.default_rng(19)
        x=(rng.random((20000,len(p)))<p).astype(float)
        score=(x-p)@J;S=score.T@score/len(x)
        self.assertLess(norm_error(F,S),.045)

    def test_reverse_KL_gradient(self):
        z=np.array([.11,-.2]);target=np.array([.18,-.14]);kl,g,F=kl_grad(self.m,z,target)
        h=1e-6;fin=[]
        for i in range(2):
            e=np.eye(2)[i]*h
            fin.append((kl_grad(self.m,z+e,target)[0]-kl_grad(self.m,z-e,target)[0])/(2*h))
        self.assertLess(np.max(np.abs(np.array(fin)-g)),1e-6)
        self.assertGreaterEqual(kl,-1e-8)

    def test_decoder_jacobian(self):
        z=np.array([.11,-.2]);out,J=logits_and_J(self.m,z);h=1e-6
        for j in range(2):
            v=np.eye(2)[j]*h
            num=(logits_and_J(self.m,z+v)[0]-logits_and_J(self.m,z-v)[0])/(2*h)
            self.assertLess(np.max(np.abs(J[:,j]-num)),1e-7)

    def test_linear_quadratic_perturbation_bound(self):
        rng=np.random.default_rng(22)
        for _ in range(100):
            A=rng.normal(size=(2,2));F=A.T@A+np.eye(2)
            w,U=np.linalg.eigh(F);S=(U*np.sqrt(w))@U.T
            delta=rng.uniform(.01,.35)
            R=rng.normal(size=(2,2));R=(R+R.T)/2
            v,V=np.linalg.eigh(R);R=R*delta/max(abs(v))
            H=S@(np.eye(2)+R)@S
            e=rng.normal(size=2)
            en=e-np.linalg.solve(H,F@e)
            lhs=np.linalg.norm(S@en);rhs=delta/(1-delta)*np.linalg.norm(S@e)
            self.assertLessEqual(lhs,rhs+1e-9)

    def test_smooth_geodesic_perturbation(self):
        b=trace(0);p=trace(.01);q=trace(.02)
        e1=max(np.linalg.norm(p-b,axis=1));e2=max(np.linalg.norm(q-b,axis=1))
        self.assertGreater(e1,0)
        self.assertLess(abs(e1/.01-e2/.02),.001)

if __name__=='__main__':unittest.main()