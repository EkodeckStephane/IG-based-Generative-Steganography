"""Three self-contained mathematical counterexamples for manuscript pre-submission audit.
Runs with Python standard library only. Full checkpoint audit is separate.
"""
import math
sig=lambda v:1/(1+math.exp(-v))
x,xt=1.5,-.7
F=sig(x)*(1-sig(x))
Ft=sig(xt)*(1-sig(xt))
new=x-(F*(x-xt))/F
assert abs(F-Ft)>.05 and abs(new-xt)<1e-12
# Fisher-flat Bernoulli angle parameter: p(u)=sin^2(u/2), F(u)=1.
p=lambda u:math.sin(u/2)**2
u,ut=1.4,math.pi/3
v,w=p(u),p(ut)
grad=math.sin(u)/2*math.log(v*(1-w)/(w*(1-v)))
step=u-grad
assert abs(step-ut)>.01
# Leading-order metric normalization mismatch in the original KL-curvature lemma.
# For n independent N(mu,sigma^2), F at sigma=1 = diag(n,2n), curvature=-1/(2n).
n=4;d=.1;t=.001
sigma=1+d*t/math.sqrt(2*n)
kl=n*(math.log(sigma)+.5/(sigma*sigma)-.5)
intrinsic=.5*(d*t)**2
invalid=n*intrinsic
assert abs(kl/intrinsic-1)<.002 and invalid/kl>3.9
print("PASS: variable F, exact one-step; start F:",F,"target F:",Ft)
print("PASS: constant F, fails one-step; next:",step,"target:",ut)
print("PASS: false curvature inequality coefficient; actual:",kl,"spurious:",invalid)
