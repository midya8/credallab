"""Disclosed deterministic and seeded decision development grid."""
import random
from credallab.decision_controls import controls

def cases():
 out=[c['input']for c in controls()]
 for a in [-1,0,1,2]:
  for b in [-1,0,1,2]:
   for level in [0,[1,2],1]:out.append(dict(version=1,worlds=2,constraints=[],utilities=[[a,b],[b,a],[level,level]]))
 r=random.Random(163)
 for n in range(1,5):
  for _ in range(8):
   k=r.randrange(1,5);cs=[]
   for j in range(2):
    event=[i for i in range(n)if r.randrange(2)];lo=r.randrange(5);hi=r.randrange(lo,5);cs.append(dict(event=event,lower=[lo,4],upper=[hi,4]))
   out.append(dict(version=1,worlds=n,constraints=cs,utilities=[[r.randrange(-3,4)for _ in range(n)]for _ in range(k)]))
 return out
if __name__=='__main__':
 import json
 print(json.dumps(cases()))
