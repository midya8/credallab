"""Exact bounded active-basis enumeration with primal/dual certificates."""
from fractions import Fraction as F
from itertools import combinations
from .model import parse,system,encode

def dot(a,b):return sum(x*y for x,y in zip(a,b))

def solve(a,b):
 n=len(a);m=[list(r)+[v]for r,v in zip(a,b)]
 for j in range(n):
  z=next((i for i in range(j,n)if m[i][j]),None)
  if z is None:return None
  m[j],m[z]=m[z],m[j];v=m[j][j];m[j]=[x/v for x in m[j]]
  for i in range(n):
   if i!=j and m[i][j]:
    v=m[i][j];m[i]=[x-v*y for x,y in zip(m[i],m[j])]
 return[r[-1]for r in m]

def vertices(h,a,b):
 out={};d=len(h)
 for ids in combinations(range(len(a)),d-1):
  basis=[h]+[a[i]for i in ids];x=solve(basis,[F(1)]+[b[i]for i in ids])
  if x is not None and all(dot(r,x)<=v for r,v in zip(a,b)):
   key=tuple(x);out.setdefault(key,[]).append(ids)
 if not out:raise ValueError('no feasible vertex')
 return out

def certify(h,a,b,vs,c,point=None):
 best=max(dot(c,x)for x in vs)
 for x,idslist in vs.items():
  if dot(c,x)!=best or point is not None and tuple(point)!=x:continue
  for ids in idslist:
   basis=[h]+[a[i]for i in ids];dual=solve([list(r)for r in zip(*basis)],c)
   if dual is not None and all(v>=0 for v in dual[1:]):
    weights=[F(0)]*len(a)
    for i,v in zip(ids,dual[1:]):weights[i]=v
    return dict(value=best,point=list(x),multipliers=weights,equality=dual[0])
 raise ValueError('no exact dual certificate')

def analyze(p):
 n,rows,rhs,q,g=parse(p);h,a,b=system(n,rows,rhs,True);pv=vertices(h,a,b);phase=certify(h,a,b,pv,[F(0)]*n+[F(-1)])
 report=dict(version=1,kind='credallab-finite',input=p,phase=phase)
 if phase['value']<0:return encode(dict(report,status='infeasible',bounds=None,conditional=None))
 h,a,b=system(n,rows,rhs);vs=vertices(h,a,b)
 def bounds(c):
  low=certify(h,a,b,vs,[-v for v in c]);high=certify(h,a,b,vs,c)
  return dict(lower=dict(value=-low['value'],certificate=low),upper=dict(value=high['value'],certificate=high))
 bs=dict(event=bounds(q),given=bounds(g));pos=[x for x in vs if dot(g,x)>0]
 conditional=None
 if pos:
  num=[x*y for x,y in zip(q,g)];ratio=[dot(num,x)/dot(g,x)for x in pos];lo,hi=min(ratio),max(ratio)
  def cert(r,sign):
   c=[sign*(x-r*y)for x,y in zip(num,g)];x=next(x for x in pos if dot(num,x)/dot(g,x)==r)
   return dict(value=r,certificate=certify(h,a,b,vs,c,point=x))
  conditional=dict(lower=cert(lo,-1),upper=cert(hi,1))
 return encode(dict(report,status='feasible',bounds=bs,conditional=conditional))
