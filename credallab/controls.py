"""Declared developed teaching controls, not a held-out benchmark."""
import copy

def controls():
 def p(n,cs,q,g):return dict(version=1,worlds=n,constraints=[dict(event=e,lower=l,upper=h)for e,l,h in cs],query=dict(event=q,given=g))
 rows=[
 ('triangle_impossible',p(4,[([1,2],1,1),([1,3],1,1),([2,3],1,1)],[1],[1,2,3])),
 ('triangle_boundary',p(4,[([1,2],[2,3],1),([1,3],[2,3],1),([2,3],[2,3],1)],[1],[1,2,3])),
 ('marginals_not_independence',p(4,[([2,3],[1,2],[1,2]),([1,3],[1,2],[1,2])],[3],[0,1,2,3])),
 ('conditional_uncertain',p(4,[([1,3],[1,4],[3,4]),([2,3],[1,2],[1,2])],[3],[1,3])),
 ('conditional_informative',p(4,[([1,3],[1,2],[3,4]),([3],[1,4],[1,4])],[3],[1,3])),
 ('conditioning_can_vanish',p(3,[([1,2],0,[1,2])],[1],[1,2])),
 ('conditioning_impossible',p(3,[([1,2],0,0)],[1],[1,2])),
 ('unique_joint',p(3,[([0],[1,6],[1,6]),([1],[1,3],[1,3])],[1],[1,2])),
 ('no_assessments',p(3,[],[0,1],[1,2])),
 ('empty_query',p(2,[],[],[0,1])),
 ('certain_query',p(2,[],[0,1],[0,1])),
 ('empty_given',p(2,[],[0],[])),
 ('single_world',p(1,[],[0],[0])),
 ('duplicate_bounds',p(3,[([0],[1,3],[2,3]),([0],[1,3],[2,3])],[0],[0,1,2])),
 ('tiny_positive_given',p(3,[([1,2],[1,1000000],[1,1000000]),([1],[1,1000000],[1,1000000])],[1],[1,2])),
 ('impossible_empty_event',p(2,[([],1,1)],[0],[0,1])),
 ]
 return[dict(id=k,input=copy.deepcopy(v))for k,v in rows]
