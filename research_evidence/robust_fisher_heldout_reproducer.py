#!/usr/bin/env python3
"""Independent, bounded Fisher-vs-Euclidean robust-decoding pilot.
Run from repo root:
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research_evidence/robust_fisher_heldout_reproducer.py --extent 0.55
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research_evidence/robust_fisher_heldout_reproducer.py --extent 1.5
Requires numpy, scipy, pillow, torch and the checkpoint data/s5_vae_mnist.pt.
Exploratory only: not Algorithm 2, not proof of security, no original iMEC/Discop.
"""
import argparse, json, hashlib
from pathlib import Path
import numpy as np
import torch
from scipy.special import logsumexp
from prototype_original import model_load,decode_p,bernoulli_kl
from operational_fisher_robust_7features import calibrate,bins,transforms

HERE=Path(__file__).resolve().parent
REPO=HERE.parent
SEED=20261031
ATTACKS=["shift_1","flip_0.01","jpeg_50","resize_14"]
BUDGETS=[0.002,0.02]

def sample(seed,p,n):
    return (np.random.default_rng(seed).random((n,784))<p).astype(np.uint8)

def dataset(seed,p,n,cal):
    x=sample(seed,p,n)
    bb=bins(x,cal)
    good=np.column_stack([bins(transforms(x,ch,np.random.default_rng(seed+501+173*k)),cal)==bb
                          for k,ch in enumerate(ATTACKS)]).astype(float)
    return {"x":x,"bins":bb,"good":good,"utility":good.mean(1)}

def evalobj(model,z,p0,data,gradient=False):
    p=decode_p(model,z)
    x=data["x"].astype(float)
    b=data["bins"]
    logw=x@np.log(p/p0)+(1-x)@np.log((1-p)/(1-p0))
    logw-=logsumexp(logw)-np.log(len(logw))
    w=np.exp(logw)
    q=np.bincount(b,weights=w,minlength=4)/len(b)
    if q.min()<.03:raise RuntimeError("Bin support too small")
    ww=w/(4*q[b]);ww/=ww.mean()
    res={"J":float(ww@data["utility"]/len(ww)),
         "KL":bernoulli_kl(p,p0),
         "TV_to_generator_est":float(.5*abs(q-.25).sum())}
    if gradient:
        zz=torch.as_tensor(z,dtype=torch.float32)
        J=torch.autograd.functional.jacobian(lambda t:model.dec(t),zz,vectorize=True).detach().numpy().astype(float)
        scores=(x-p)@J
        gg=np.zeros(2)
        for sb in range(4):
            ii=b==sb
            wi=w[ii]/w[ii].sum()
            ui=data["utility"][ii]
            gg+=((scores[ii]*(ui-wi@ui)[:,None])*wi[:,None]).sum(0)/4
        F=J.T@((p*(1-p))[:,None]*J)
        res["gradient"]=gg
        res["fisher"]=F
    return res

def boundary(model,z0,p0,d,cap):
    d=d/np.linalg.norm(d)
    hi=.001
    for _ in range(45):
        if bernoulli_kl(decode_p(model,z0+hi*d),p0)>=cap:break
        hi*=1.8
    else:raise RuntimeError("Could not bracket fixed KL")
    lo=0.
    for _ in range(38):
        md=(hi+lo)/2
        if bernoulli_kl(decode_p(model,z0+md*d),p0)<=cap:lo=md
        else:hi=md
    return z0+lo*d

def run(extent,nt=4500,ne=6500,ncenters=12):
    torch.set_num_threads(1)
    m=model_load(REPO/"data"/"s5_vae_mnist.pt")
    roots=np.random.default_rng(SEED+710).uniform(-extent,extent,size=(ncenters,2))
    result={"seed":SEED,"latent_extent":extent,"train":nt,"test":ne,
            "channels":ATTACKS,"budgets":BUDGETS,
            "checkpoint_sha256":hashlib.sha256((REPO/"data"/"s5_vae_mnist.pt").read_bytes()).hexdigest(),
            "scope":"Independent samples for heldout evaluation; importance sampling from centre P0; exploratory non-Algorithm2 Bernoulli-VAE.","centres":[]}
    for k,z0 in enumerate(roots):
        p0=decode_p(m,z0)
        cal=calibrate(sample(SEED+1100+401*k,p0,1600))
        tr=dataset(SEED+1800+401*k,p0,nt,cal)
        te=dataset(SEED+950000+401*k,p0,ne,cal)
        initial=evalobj(m,z0,p0,tr,True)
        g=initial["gradient"];F=initial["fisher"]
        directions={"fisher":np.linalg.solve(F+1e-6*np.eye(2),g),
                    "euclidean":g}
        r={"centre":k,"F_cond":float(np.linalg.cond(F)),
           "local_gain_ratio":float((g@directions["fisher"])/np.sqrt(directions["fisher"]@F@directions["fisher"])/((g@directions["euclidean"])/np.sqrt(directions["euclidean"]@F@directions["euclidean"]))),
           "matched_J":evalobj(m,z0,p0,te)["J"],"budgets":{}}
        for cap in BUDGETS:
            vv={}
            for method,d in directions.items():
                z=boundary(m,z0,p0,d,cap)
                vv[method]={"z":z.tolist(),"fit_J":evalobj(m,z,p0,tr)["J"],
                            "test":evalobj(m,z,p0,te)}
            vv["delta_F_minus_E"]=vv["fisher"]["test"]["J"]-vv["euclidean"]["test"]["J"]
            r["budgets"][str(cap)]=vv
        result["centres"].append(r)
        print("center",k,"cond",round(r["F_cond"],2),
              "delta",[(str(c),round(r["budgets"][str(c)]["delta_F_minus_E"],8)) for c in BUDGETS],flush=True)
    rr=np.random.default_rng(74183);result["summary"]={}
    for cap in BUDGETS:
        p=str(cap)
        d=np.array([x["budgets"][p]["delta_F_minus_E"] for x in result["centres"]])
        boot=np.array([rr.choice(d,len(d),replace=True).mean() for _ in range(5000)])
        result["summary"][p]={"mean_delta":float(d.mean()),"cluster_bootstrap95":np.quantile(boot,[.025,.975]).tolist(),
                              "fisher_wins":int(sum(d>0)),"n_centres":len(d),
                              "fisher_J":float(np.mean([x["budgets"][p]["fisher"]["test"]["J"] for x in result["centres"]])),
                              "euclidean_J":float(np.mean([x["budgets"][p]["euclidean"]["test"]["J"] for x in result["centres"]))}
    path=HERE/("robust_fisher_heldout_extent_"+str(extent).replace(".","p")+".json")
    path.write_text(json.dumps(result,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else float(x),indent=2))
    print("SUMMARY",json.dumps(result["summary"],indent=2))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--extent",type=float,required=True,choices=[0.55,1.5])
    ap.add_argument("--ntrain",type=int,default=4500)
    ap.add_argument("--ntest",type=int,default=6500)
    ap.add_argument("--centers",type=int,default=12)
    args=ap.parse_args()
    run(args.extent,args.ntrain,args.ntest,args.centers)
