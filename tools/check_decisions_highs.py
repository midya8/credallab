"""Independent LP construction from decision input, optional floating reference."""
import json,sys
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import linprog
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from credallab import analyze_decisions
from decision_cases import cases

def q(v):return float(v)if type(v)is int else v[0]/v[1]
count=0;worst=0.;feasible=0;excluded=0

def run(c,a,b,h,bounds):
 global count
 count+=1;r=linprog(c,A_ub=np.array(a)if a else None,b_ub=np.array(b)if b else None,A_eq=[h],b_eq=[1.],bounds=bounds,method='highs')
 if not r.success:raise AssertionError((r.status,r.message))
 return r.fun

def check(x,v):
 global worst
 error=abs(x-q(v));worst=max(worst,error);assert error<=1e-8,(x,v,error)

for p in cases():
 r=analyze_decisions(p);n=p['worlds'];k=len(p['utilities']);u=np.array([[q(v)for v in row]for row in p['utilities']]);a=[];b=[]
 for row in p['constraints']:
  ev=[float(j in row['event'])for j in range(n)];a.extend([ev,[-x for x in ev]]);b.extend([q(row['upper']),-q(row['lower'])])
 phase=run([0.]*n+[1.],[row+[-1.]for row in a],b,[1.]*n+[0.],[(0,None)]*n+[(0,1)]);check(-phase,r['phase']['value']);assert (phase<1e-8)==(r['status']=='feasible')
 if r['status']!='feasible':continue
 feasible+=1
 for i,row in enumerate(r['actions']):
  check(run(u[i],a,b,[1.]*n,[(0,None)]*n),row['lower']['value']);check(-run(-u[i],a,b,[1.]*n,[(0,None)]*n),row['upper']['value'])
  aa=[x+[0.]for x in a]+[list(u[j]-u[i])+[1.]for j in range(k)];bb=b+[0.]*k
  check(-run([0.]*n+[-1.],aa,bb,[1.]*n+[0.],[(0,None)]*n+[(None,None)]),row['best_case_margin']['value'])
  if row['exclusion']:
   excluded+=1;w=np.array([q(x)for x in row['exclusion']['weights']]);difference=w@u-u[i];check(run(difference,a,b,[1.]*n,[(0,None)]*n),row['exclusion']['guaranteed_advantage'])
 for i,row in enumerate(r['pairwise']):
  for j,z in enumerate(row):check(run(u[i]-u[j],a,b,[1.]*n,[(0,None)]*n),z['value'])
print(json.dumps(dict(scipy=scipy.__version__,reports=len(cases()),feasible=feasible,excluded_mixtures=excluded,lp_solves=count,worst_abs_error=worst,tolerance=1e-8)))
