"""Independent visible-row arithmetic, rebuilt from input and report witnesses."""
import json,sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from credallab import analyze_decisions
from credallab.decision_controls import controls

def q(x):return F(x)if type(x)is int else F(*x)
def fmt(x):return str(x.numerator)if x.denominator==1 else f'{x.numerator}/{x.denominator}'
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def vec(x):return ', '.join(map(fmt,x))
out=[]
for control in controls():
 p=control['input'];r=analyze_decisions(p);n=p['worlds'];u=[[q(v)for v in row]for row in p['utilities']];k=len(u);a=[];b=[];labels=[]
 for i,c in enumerate(p['constraints']):
  row=[F(int(j in c['event']))for j in range(n)];a.extend([row,[-x for x in row]]);b.extend([q(c['upper']),-q(c['lower'])]);labels.extend([f'assessment {i} / upper',f'assessment {i} / lower'])
 for j in range(n):a.append([F(-int(i==j))for i in range(n)]);b.append(F(0));labels.append(f'world {j} nonnegative')
 h=[F(1)]*n;pa=[row+[F(-1)]if i<2*len(p['constraints'])else row+[F(0)]for i,row in enumerate(a)]+[[F(0)]*n+[F(-1)],[F(0)]*n+[F(1)]];pb=b+[F(0),F(1)]
 ds=[('phase',r['phase'],[F(0)]*n+[F(-1)],h+[F(0)],pa,pb,labels+['t nonnegative','t ≤ 1'],'common slack t')];action_rows=[]
 if r['actions']:
  for i,z in enumerate(r['actions']):
   for side,sign in [('lower',-1),('upper',1)]:ds.append((f'{i}-{side}',z[side]['certificate'],[sign*x for x in u[i]],h,a,b,labels,None))
   ma=[row+[F(0)]for row in a]+[[u[j][t]-u[i][t]for t in range(n)]+[F(1)]for j in range(k)]
   ds.append((f'{i}-margin',z['best_case_margin'],[F(0)]*n+[F(1)],h+[F(0)],ma,b+[F(0)]*k,labels+[f'z ≤ E(u{i} − u{j})'for j in range(k)],'shared margin z'))
   point=[q(v)for v in z['best_case_margin']['point'][:n]];expected=[dot(row,point)for row in u];ar=dict(witness=[[str(j),fmt(v),fmt(expected[i]-v),'yes'if v==max(expected)else'no']for j,v in enumerate(expected)])
   if z['exclusion']:
    exc=z['exclusion'];w=[q(x)for x in exc['weights']];mix=[sum(w[j]*u[j][t]for j in range(k))for t in range(n)];ds.append((f'{i}-exclusion',exc['certificate'],[u[i][j]-mix[j]for j in range(n)],h,a,b,labels,None));ar['weights']=[[str(j),fmt(v)]for j,v in enumerate(w)];ar['worlds']=[[str(j),fmt(u[i][j]),fmt(v),fmt(v-u[i][j])]for j,v in enumerate(mix)]
   action_rows.append(ar)
  for i,row in enumerate(r['pairwise']):
   for j,z in enumerate(row):ds.append((f'pair-{i}-{j}',z['certificate'],[u[j][t]-u[i][t]for t in range(n)],h,a,b,labels,None))
 audits={}
 for id,z,c,hh,aa,bb,ll,last in ds:
  x=[q(v)for v in z['point']];lam=[q(v)for v in z['multipliers']];eta=q(z['equality']);names=[f'world {i}'if i<n else last for i in range(len(hh))]
  audits[id]=dict(worlds=[[name,fmt(v),fmt(ci),fmt(hi)]for name,v,ci,hi in zip(names,x,c,hh)],inequalities=[[label,vec(row),fmt(bound),fmt(dot(row,x)),fmt(bound-dot(row,x)),fmt(w)]for label,row,bound,w in zip(ll,aa,bb,lam)],dual=[[names[j],fmt(v),fmt(eta*hh[j]+sum(lam[i]*aa[i][j]for i in range(len(aa))))]for j,v in enumerate(c)])
 out.append(dict(report=json.dumps(r,sort_keys=True,separators=(',',':')),audits=audits,actions=action_rows,utilities=[[str(i),*map(fmt,row)]for i,row in enumerate(u)],ranges=[[str(i),fmt(q(z['lower']['value'])),fmt(q(z['upper']['value'])),fmt(q(z['best_case_margin']['value'])),'yes'if i in r['choices']['e_admissible']else'no']for i,z in enumerate(r['actions']or[])],pairwise=[['Action '+str(i),*[fmt(q(z['value']))for z in row]]for i,row in enumerate(r['pairwise']or[])]))
print(json.dumps(out,separators=(',',':')))
