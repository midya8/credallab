"""Native expected visible rows, independently calculated from report witnesses."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fractions import Fraction as F
from credallab import analyze
from credallab.controls import controls
from credallab.model import parse,system

def fmt(v):return str(v.numerator)if v.denominator==1 else str(v.numerator)+'/'+str(v.denominator)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
out=[]
for c in controls():
 r=analyze(c['input']);n,rows,rhs,q,g=parse(c['input']);ds=[('phase',r['phase'],[F(0)]*n+[F(-1)],True)]
 if r['bounds']:
  for k,v in [('event',q),('given',g)]:
   for side,sign in [('lower',-1),('upper',1)]:ds.append((k+'-'+side,r['bounds'][k][side]['certificate'],[sign*x for x in v],False))
  if r['conditional']:
   for side,sign in [('lower',-1),('upper',1)]:
    ratio=F(*r['conditional'][side]['value']);ds.append(('conditional-'+side,r['conditional'][side]['certificate'],[sign*(x*y-ratio*y)for x,y in zip(q,g)],False))
 audits={}
 for id,z,obj,phase in ds:
  h,a,b=system(n,rows,rhs,phase);x=[F(*v)for v in z['point']];lam=[F(*v)for v in z['multipliers']];eta=F(*z['equality']);names=['world '+str(i)if i<n else'common slack t'for i in range(len(h))]
  labels=[];m=2*len(c['input']['constraints'])
  for i in range(len(a)):
   if i<m:labels.append('assessment '+str(i//2)+' / '+('lower'if i%2 else'upper'))
   elif i<m+n:labels.append('world '+str(i-m)+' nonnegative')
   else:labels.append('t nonnegative'if i==m+n else't ≤ 1')
  audits[id]=dict(worlds=[[name,fmt(v),fmt(ci),fmt(hi)]for name,v,ci,hi in zip(names,x,obj,h)],inequalities=[[labels[i],', '.join(map(fmt,ai)),fmt(bi),fmt(dot(ai,x)),fmt(bi-dot(ai,x)),fmt(li)]for i,(ai,bi,li)in enumerate(zip(a,b,lam))],dual=[[names[j],fmt(ci),fmt(eta*h[j]+sum(lam[i]*a[i][j]for i in range(len(a))))]for j,ci in enumerate(obj)])
 out.append(dict(report=json.dumps(r,sort_keys=True,separators=(',',':')),audits=audits))
print(json.dumps(out,separators=(',',':')))
