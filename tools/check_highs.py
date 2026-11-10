"""Optional numerical reference built directly from input. Never production."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fractions import Fraction as F
import scipy
from scipy.optimize import linprog
from cases import cases
from credallab import analyze

def f(x):return float(F(*x))if type(x)is list else float(x)
count=0;worst=0;statuses={'feasible':0,'infeasible':0};conditional=0
for p in cases():
 n=p['worlds'];A=[];b=[]
 for row in p['constraints']:
  a=[int(j in row['event'])for j in range(n)];A.extend([a,[-v for v in a]]);b.extend([f(row['upper']),-f(row['lower'])])
 r=analyze(p);phase=linprog([0]*n+[1],A_ub=[a+[-1]for a in A]or None,b_ub=b or None,A_eq=[[1]*n+[0]],b_eq=[1],bounds=[(0,None)]*n+[(0,1)],method='highs');count+=1;assert phase.success
 exact=-f(r['phase']['value']);worst=max(worst,abs(phase.fun-exact));assert abs(phase.fun-exact)<1e-8
 feasible=linprog([0]*n,A_ub=A or None,b_ub=b or None,A_eq=[[1]*n],b_eq=[1],bounds=(0,None),method='highs');count+=1
 if r['status']=='infeasible':assert feasible.status==2;statuses['infeasible']+=1;continue
 assert feasible.success;statuses['feasible']+=1
 for name in ['event','given']:
  c=[int(j in p['query'][name])for j in range(n)]
  for side,sign in [('lower',1),('upper',-1)]:
   z=linprog([sign*v for v in c],A_ub=A or None,b_ub=b or None,A_eq=[[1]*n],b_eq=[1],bounds=(0,None),method='highs');count+=1;assert z.success;err=abs(sign*z.fun-f(r['bounds'][name][side]['value']));worst=max(worst,err);assert err<1e-8
 if r['conditional']is not None:
  g=[int(j in p['query']['given'])for j in range(n)];q=[int(j in p['query']['given']and j in p['query']['event'])for j in range(n)]
  # Charnes-Cooper: y=p/P(G), t=1/P(G), sum(y)=t, G.y=1.
  for side,sign in [('lower',1),('upper',-1)]:
   z=linprog([sign*v for v in q]+[0],A_ub=[a+[-v]for a,v in zip(A,b)]or None,b_ub=[0]*len(A)or None,A_eq=[[1]*n+[-1],g+[0]],b_eq=[0,1],bounds=(0,None),method='highs');count+=1;conditional+=1;assert z.success;err=abs(sign*z.fun-f(r['conditional'][side]['value']));worst=max(worst,err);assert err<1e-8
print(json.dumps(dict(scipy=scipy.__version__,cases=len(cases()),lp_solves=count,conditional_ratio_solves=conditional,classification=statuses,worst_abs_error=worst,tolerance=1e-8)))
