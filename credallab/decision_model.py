"""Decision schema and LP convention. No optimization code."""
from fractions import Fraction as F
from math import comb,lcm
from .model import keys,parse,rational,system,integer

def probability_input(p):
 return dict(version=1,worlds=p['worlds'],constraints=p['constraints'],query=dict(event=[],given=list(range(p['worlds']))))

def compile(p):
 keys(p,['version','worlds','constraints','utilities'])
 if type(p['version'])is not int or p['version']!=1:raise ValueError('decision version must be 1')
 if not 1<=integer(p['worlds'])<=6:raise ValueError('world count must be 1..6')
 n,rows,rhs,_,_=parse(probability_input(p));raw=p['utilities']
 if type(raw)is not list or not 1<=len(raw)<=6:raise ValueError('1..6 action utility vectors required')
 u=[]
 for row in raw:
  if type(row)is not list or len(row)!=n:raise ValueError('one exact utility per world required')
  u.append([rational(x)for x in row])
 if lcm(*(x.denominator for r in u for x in r))>1000000:raise ValueError('utility denominator LCM limit')
 if comb(2*len(p['constraints'])+n+len(u),n)>20000:raise ValueError('20000 candidate decision-margin bases limit')
 return n,rows,rhs,u

def margin_system(n,rows,rhs,u,i):
 h,a,b=system(n,rows,rhs)
 # z <= E(u_i-u_j), including self: z <= 0. z is free below.
 return h+[F(0)],[r+[F(0)]for r in a]+[[u[j][k]-u[i][k]for k in range(n)]+[F(1)]for j in range(len(u))],b+[F(0)]*len(u)

def choice_sets(ranges,pairwise,margins):
 k=len(ranges);lo=[r[0]for r in ranges];hi=[r[1]for r in ranges]
 return dict(e_admissible=[i for i in range(k)if margins[i]==0],
 maximal=[i for i in range(k)if all(pairwise[j][i]<=0 for j in range(k))],
 interval_undominated=[i for i in range(k)if all(lo[j]<=hi[i]for j in range(k))],
 gamma_maximin=[i for i in range(k)if lo[i]==max(lo)],
 gamma_maximax=[i for i in range(k)if hi[i]==max(hi)])
