"""Independent phase-I numerical consistency checks. No assertion of global optimizer optimality."""
import unittest
import numpy as np
from phase1_variational_experiment import (toy_ring,ring_probs,ring_fisher,ring_length,
 bern_ambient,bern_kl,vae_upper_bounds,VAEModel,gauss2_segment,segment_breakpoints)

class PhaseITest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.toy=toy_ring(); cls.model=VAEModel()
 def test_ring_positive_and_nonzero_F(self):
  t=np.linspace(-2*np.pi,2*np.pi,100)
  self.assertTrue(np.all((ring_probs(t)>.25)&(ring_probs(t)<.75)))
  self.assertGreater(np.min(ring_fisher(t)),.1)
 def test_ring_fim_local_KL_expansion(self):
  t=.34;h=1e-4
  kl=bern_kl(ring_probs(t+h),ring_probs(t))
  approx=.5*h*h*ring_fisher(t)
  self.assertLess(abs(kl/approx-1),.001)
 def test_toy_ambient_intrinsic(self):
  t=self.toy;self.assertLess(t['d_ambient_exact'],t['d_generator_exact'])
  self.assertGreater(t['generator_excess_squared_exact'],0)
 def test_toy_variational_limit_and_orientation(self):
  t=self.toy;last=t['finite_N'][-1]
  self.assertLess(abs(last['ratio_short_to_limit']-1),1e-4)
  self.assertGreater(last['N_times_other_path_KL'],last['N_times_short_path_KL'])
 def test_toy_gap_decomposition(self):
  decomp=self.toy['decomposition']; self.assertLess(abs(decomp['reconstruction_error']),1e-9)
  for k in ('speed_excess','route_excess','generator_excess'):self.assertGreaterEqual(decomp[k],-1e-7)
 def test_vae_ck(self):
  self.assertEqual(self.model.hash,'e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61')
 def test_vae_metric_vs_kl(self):
  z=np.array([-.15,-.1]);d=np.array([1.,-.7]); h=1e-5
  p,F=self.model.probs_F(z);q=self.model.probs_F(z+h*d)[0]
  ratio=bern_kl(q,p)/(.5*h*h*d@F@d)
  self.assertLess(abs(ratio-1),.005)
 def test_vae_piecewise_integral(self):
  a=np.array([-.3,.2]);b=np.array([-.28,.23]);pts=segment_breakpoints(self.model,a,b)
  self.assertGreater(len(pts),2)
  s8=gauss2_segment(self.model,a,b,8);s16=gauss2_segment(self.model,a,b,16)
  self.assertLess(abs(s8-s16),5e-7)
 def test_vae_computed_bounds(self):
  result=vae_upper_bounds(False)
  for item in result['pairs']:
   lo,hi=item['intrinsic_distance_interval'];self.assertLessEqual(lo,hi+1e-8)
   self.assertLessEqual(hi,item['straight_feasible_length']+1e-8)
   self.assertGreaterEqual(item['generator_excess_squared_interval'][1],0)

if __name__=='__main__':unittest.main(verbosity=2)
