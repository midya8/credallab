"""Certificate replay. No generator, vertex enumerator or linear solver imports."""
from fractions import Fraction as F
from .model import parse,system,keys

def fraction(x):
 if type(x)is not list or len(x)!=2 or any(type(i)is not int for i in x)or x[1]<=0:raise ValueError('invalid report fraction')
 q=F(*x)
 if [q.numerator,q.denominator]!=x:raise ValueError('noncanonical report fraction')
 return q

def scalar(a,b):return sum(a[i]*b[i]for i in range(len(a)))

def certificate(z,h,a,b,c):
 keys(z,['value','point','multipliers','equality']);d=len(h)
 if type(z['point'])is not list or len(z['point'])!=d or type(z['multipliers'])is not list or len(z['multipliers'])!=len(a):raise ValueError('certificate dimensions')
 x=[fraction(v)for v in z['point']];lam=[fraction(v)for v in z['multipliers']];eta=fraction(z['equality']);value=fraction(z['value'])
 if scalar(h,x)!=1 or any(scalar(r,x)>v for r,v in zip(a,b))or any(v<0 for v in lam):raise ValueError('primal or dual infeasible')
 if any(c[j]!=eta*h[j]+sum(lam[i]*a[i][j]for i in range(len(a)))for j in range(d)):raise ValueError('dual coefficient mismatch')
 if scalar(c,x)!=value or eta+scalar(lam,b)!=value:raise ValueError('primal/dual gap')
 return value,x

def verify(r):
 try:
  keys(r,['version','kind','input','phase','status','bounds','conditional'])
  if type(r['version'])is not int or r['version']!=1 or r['kind']!='credallab-finite':raise ValueError('report type')
  n,rows,rhs,q,g=parse(r['input']);h,a,b=system(n,rows,rhs,True);v,x=certificate(r['phase'],h,a,b,[F(0)]*n+[F(-1)])
  if v<0:
   if r['status']!='infeasible' or r['bounds']is not None or r['conditional']is not None:raise ValueError('infeasible report fields')
   return True
  if v!=0 or r['status']!='feasible':raise ValueError('phase/status mismatch')
  h,a,b=system(n,rows,rhs);keys(r['bounds'],['event','given']);vals={}
  for k,c in [('event',q),('given',g)]:
   z=r['bounds'][k];keys(z,['lower','upper']);
   for side in ['lower','upper']:keys(z[side],['value','certificate'])
   lo,_=certificate(z['lower']['certificate'],h,a,b,[-v for v in c]);hi,_=certificate(z['upper']['certificate'],h,a,b,c)
   if fraction(z['lower']['value'])!=-lo or fraction(z['upper']['value'])!=hi:raise ValueError('bound value mismatch')
   if not 0<=-lo<=hi<=1:raise ValueError('probability bounds')
   vals[k]=(-lo,hi)
  if vals['given'][1]==0:
   if r['conditional']is not None:raise ValueError('conditioning impossible')
  else:
   keys(r['conditional'],['lower','upper']);rs=[]
   for k,sign in [('lower',-1),('upper',1)]:
    z=r['conditional'][k];keys(z,['value','certificate']);ratio=fraction(z['value']);c=[sign*(q[j]*g[j]-ratio*g[j])for j in range(n)];v,x=certificate(z['certificate'],h,a,b,c)
    if not 0<=ratio<=1 or v!=0 or scalar(g,x)<=0:raise ValueError('conditional witness or bound')
    rs.append(ratio)
   if rs[0]>rs[1]:raise ValueError('reversed conditional bounds')
  return True
 except(KeyError,TypeError,IndexError,ZeroDivisionError,OverflowError)as e:raise ValueError('malformed report')from e
