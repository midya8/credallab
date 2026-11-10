"""Strict finite-world input and shared mathematical convention, not a solver."""
from fractions import Fraction as F
from math import comb,lcm
import json

def integer(x):
 if type(x)is not int:raise ValueError('expected non-boolean integer')
 return x

def rational(x):
 if type(x)is int:
  integer(x)
  if abs(x)>1000000:raise ValueError('rational component limit')
  q=F(x)
 elif type(x)is list and len(x)==2:
  a,b=map(integer,x)
  if b<=0:raise ValueError('denominator must be positive')
  if max(abs(a),b)>1000000:raise ValueError('rational component limit')
  q=F(a,b)
 else:raise ValueError('expected integer or [numerator,denominator]')
 if max(abs(q.numerator),q.denominator)>1000000:raise ValueError('rational component limit')
 return q

def keys(x,ks):
 if type(x)is not dict or set(x)!=set(ks):raise ValueError('unexpected object fields')

def event(x,n):
 if type(x)is not list or len(x)>n or any(type(i)is not int or not 0<=i<n for i in x) or x!=sorted(set(x)):raise ValueError('event must list sorted distinct world indices')
 return [F(int(i in x))for i in range(n)]

def parse(p):
 keys(p,['version','worlds','constraints','query'])
 if type(p['version'])is not int or p['version']!=1:raise ValueError('version must be 1')
 n=integer(p['worlds'])
 if not 1<=n<=6:raise ValueError('world count must be 1..6')
 cs=p['constraints']
 if type(cs)is not list or len(cs)>6 or comb(n+2*len(cs)+2,n)>20000:raise ValueError('at most 6 constraints and 20000 candidate phase-I bases')
 rows=[];rhs=[];bounds=[]
 for item in cs:
  keys(item,['event','lower','upper']);a=event(item['event'],n);lo,hi=rational(item['lower']),rational(item['upper'])
  if not 0<=lo<=hi<=1:raise ValueError('bounds must satisfy 0 <= lower <= upper <= 1')
  rows.extend([a,[-x for x in a]]);rhs.extend([hi,-lo]);bounds.extend([lo,hi])
 keys(p['query'],['event','given']);q=event(p['query']['event'],n);g=event(p['query']['given'],n)
 if lcm(*(v.denominator for v in bounds))>1000000:raise ValueError('bound denominator LCM limit')
 return n,rows,rhs,q,g

def system(n,rows,rhs,phase=False):
 if not phase:return [F(1)]*n,rows+[[F(-int(i==j))for i in range(n)]for j in range(n)],rhs+[F(0)]*n
 h=[F(1)]*n+[F(0)];a=[r+[F(-1)]for r in rows]+[[F(-int(i==j))for i in range(n)]+[F(0)]for j in range(n)]+[[F(0)]*n+[F(-1)],[F(0)]*n+[F(1)]]
 return h,a,rhs+[F(0)]*(n+1)+[F(1)]

def encode(x):
 if isinstance(x,F):return[x.numerator,x.denominator]
 if type(x)is list:return[encode(y)for y in x]
 if type(x)is dict:return{k:encode(v)for k,v in x.items()}
 return x

def loads(text):
 def obj(pairs):
  out={}
  for k,v in pairs:
   if k in out:raise ValueError('duplicate object key')
   out[k]=v
  return out
 def no(_):raise ValueError('JSON floats/constants are forbidden')
 return json.loads(text,object_pairs_hook=obj,parse_float=no,parse_constant=no)
