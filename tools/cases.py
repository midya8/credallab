"""Disclosed small development grid and seeded finite constraints."""
import random
from credallab.controls import controls

def cases():
 out=[c['input']for c in controls()]
 # Exhaustive ordered pairs of four interval assessments on two distinct events.
 intervals=[(0,0),(0,1),([1,2],[1,2]),(1,1)]
 for e in [[0],[0,1]]:
  for f in [[1],[1,2]]:
   for lo,hi in intervals:
    for l,h in intervals:out.append(dict(version=1,worlds=3,constraints=[dict(event=e,lower=lo,upper=hi),dict(event=f,lower=l,upper=h)],query=dict(event=[0,2],given=[0,1])))
 rng=random.Random(73)
 for n in range(1,6):
  for _ in range(8):
   cs=[]
   for j in range(3 if n<5 else 2):
    e=[i for i in range(n)if rng.randrange(2)];l=rng.randrange(5);h=rng.randrange(l,5);cs.append(dict(event=e,lower=[l,4],upper=[h,4]))
   out.append(dict(version=1,worlds=n,constraints=cs,query=dict(event=[i for i in range(n)if rng.randrange(2)],given=[i for i in range(n)if rng.randrange(2)])))
 return out
if __name__=='__main__':
 import json
 print(json.dumps(cases()))
