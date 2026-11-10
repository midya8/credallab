"""Exact one-shot decisions over a supplied finite credal polytope."""
from fractions import Fraction as F
from .model import system,encode
from .decision_model import compile,margin_system,choice_sets
from .engine import vertices,certify

def analyze_decisions(p):
 n,rows,rhs,u=compile(p);h,a,b=system(n,rows,rhs,True)
 phase=certify(h,a,b,vertices(h,a,b),[F(0)]*n+[F(-1)])
 out=dict(version=1,kind='credallab-decisions',input=p,phase=phase)
 if phase['value']<0:return encode(dict(out,status='infeasible',actions=None,pairwise=None,choices=None))
 h,a,b=system(n,rows,rhs);vs=vertices(h,a,b)
 def lower(c):
  z=certify(h,a,b,vs,[-v for v in c]);return dict(value=-z['value'],certificate=z)
 def upper(c):
  z=certify(h,a,b,vs,c);return dict(value=z['value'],certificate=z)
 actions=[]
 for i,c in enumerate(u):
  mh,ma,mb=margin_system(n,rows,rhs,u,i)
  z=certify(mh,ma,mb,vertices(mh,ma,mb),[F(0)]*n+[F(1)])
  exclusion=None
  if z['value']<0:
   weights=z['multipliers'][len(a):]
   # Projection of the margin dual yields a worst-case mixture advantage.
   cert=dict(value=z['value'],point=z['point'][:n],multipliers=z['multipliers'][:len(a)],equality=z['equality'])
   exclusion=dict(weights=weights,guaranteed_advantage=-z['value'],certificate=cert)
  actions.append(dict(lower=lower(c),upper=upper(c),best_case_margin=z,exclusion=exclusion))
 pairwise=[[lower([x-y for x,y in zip(u[i],u[j])])for j in range(len(u))]for i in range(len(u))]
 choices=choice_sets([(r['lower']['value'],r['upper']['value'])for r in actions],[[v['value']for v in r]for r in pairwise],[r['best_case_margin']['value']for r in actions])
 return encode(dict(out,status='feasible',actions=actions,pairwise=pairwise,choices=choices))
