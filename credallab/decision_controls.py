"""Original developed one-shot utility controls, not empirical decisions."""
def controls():
 def p(u,cs=None):return dict(version=1,worlds=len(u[0]),constraints=cs or [],utilities=u)
 def c(e,lo,hi):return dict(event=e,lower=lo,upper=hi)
 return [
 dict(id='maximal_never_best',input=p([[3,0],[0,3],[1,1]])),
 dict(id='interior_only_tie',input=p([[3,0],[0,3],[[3,2],[3,2]]])),
 dict(id='pairwise_not_interval',input=p([[1,0],[[5,4],[1,4]]])),
 dict(id='strict_endpoint_tie',input=p([[1,0],[0,0]])),
 dict(id='fixed_belief_ties',input=p([[3,0],[0,3],[[3,2],[3,2]]],[c([0],[1,2],[1,2])])),
 dict(id='belief_restriction',input=p([[3,0],[0,3],[1,1]],[c([0],[3,4],1)])),
 dict(id='duplicate_actions',input=p([[1,-1],[1,-1],[0,0]])),
 dict(id='one_action',input=p([[3,-2]])),
 dict(id='one_world',input=p([[1],[2],[2],[-1]])),
 dict(id='all_ties',input=p([[0,0],[0,0],[0,0]])),
 dict(id='signed_utilities',input=p([[-2,1],[1,-2],[-1,-1]])),
 dict(id='forced_zero_world',input=p([[1,0],[0,0],[2,0]],[c([0],0,0)])),
 dict(id='tiny_strict_margin',input=p([[1,0],[0,1],[[499999,1000000],[499999,1000000]]])),
 dict(id='three_world_joint',input=p([[3,0,0],[0,3,0],[0,0,3],[[1,2],[1,2],[1,2]]])),
 dict(id='duplicate_assessments',input=p([[2,0],[0,2],[1,1]],[c([0],[1,4],[3,4]),c([0],[1,4],[3,4])])),
 dict(id='infeasible_model',input=p([[1,0],[0,1]],[c([],1,1)])),
 ]
