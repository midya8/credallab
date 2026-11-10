"""Decision evidence replay. No solver/enumerator/generator imports."""
from fractions import Fraction as F
from .model import system,keys
from .decision_model import compile,margin_system,choice_sets
from .certificate import certificate,fraction

def verify_decisions(r):
 try:
  keys(r,['version','kind','input','phase','status','actions','pairwise','choices'])
  if type(r['version'])is not int or r['version']!=1 or r['kind']!='credallab-decisions':raise ValueError('decision report type')
  n,rows,rhs,u=compile(r['input']);k=len(u);h,a,b=system(n,rows,rhs,True)
  v,_=certificate(r['phase'],h,a,b,[F(0)]*n+[F(-1)])
  if v<0:
   if r['status']!='infeasible'or any(r[x]is not None for x in ['actions','pairwise','choices']):raise ValueError('infeasible decision fields')
   return True
  if v!=0 or r['status']!='feasible':raise ValueError('phase/status mismatch')
  if type(r['actions'])is not list or len(r['actions'])!=k or type(r['pairwise'])is not list or len(r['pairwise'])!=k:raise ValueError('decision dimensions')
  h,a,b=system(n,rows,rhs);ranges=[];margins=[];pairs=[]
  def lower(z,c):
   keys(z,['value','certificate']);v,_=certificate(z['certificate'],h,a,b,[-x for x in c])
   if fraction(z['value'])!=-v:raise ValueError('lower expectation mismatch')
   return -v
  for i,z in enumerate(r['actions']):
   keys(z,['lower','upper','best_case_margin','exclusion']);lo=lower(z['lower'],u[i]);keys(z['upper'],['value','certificate'])
   hi,_=certificate(z['upper']['certificate'],h,a,b,u[i])
   if fraction(z['upper']['value'])!=hi or not min(u[i])<=lo<=hi<=max(u[i]):raise ValueError('utility range mismatch')
   mh,ma,mb=margin_system(n,rows,rhs,u,i);v,_=certificate(z['best_case_margin'],mh,ma,mb,[F(0)]*n+[F(1)])
   if v>0:raise ValueError('positive margin impossible with self row')
   margins.append(v);ranges.append((lo,hi));exc=z['exclusion']
   if v==0:
    if exc is not None:raise ValueError('admissible exclusion')
   else:
    keys(exc,['weights','guaranteed_advantage','certificate'])
    if type(exc['weights'])is not list or len(exc['weights'])!=k:raise ValueError('mixture dimension')
    w=[fraction(x)for x in exc['weights']]
    if any(x<0 for x in w)or sum(w)!=1 or w[i]!=0:raise ValueError('opponent mixture')
    if fraction(exc['guaranteed_advantage'])!=-v:raise ValueError('mixture guarantee')
    c=[u[i][j]-sum(w[t]*u[t][j]for t in range(k))for j in range(n)]
    bound,_=certificate(exc['certificate'],h,a,b,c)
    if bound!=v:raise ValueError('mixture bound mismatch')
  for i,row in enumerate(r['pairwise']):
   if type(row)is not list or len(row)!=k:raise ValueError('pair dimensions')
   pairs.append([lower(z,[u[i][t]-u[j][t]for t in range(n)])for j,z in enumerate(row)])
  expected=choice_sets(ranges,pairs,margins);keys(r['choices'],expected)
  for key,value in expected.items():
   x=r['choices'][key]
   if type(x)is not list or any(type(i)is not int for i in x)or x!=value:raise ValueError('choice set mismatch')
  return True
 except(KeyError,TypeError,IndexError,ZeroDivisionError,OverflowError)as e:raise ValueError('malformed decision report')from e
