import copy,json,subprocess,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from credallab import analyze_decisions,verify_decisions
from credallab.decision_controls import controls
from credallab.decision_model import compile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from decision_cases import cases

class DecisionTests(unittest.TestCase):
 def test_developed_grid(self):
  rs=[analyze_decisions(p)for p in cases()]
  for r in rs:
   self.assertTrue(verify_decisions(r))
   if r['choices']:
    c=r['choices'];self.assertTrue(set(c['e_admissible'])<=set(c['maximal'])<=set(c['interval_undominated']));self.assertTrue(set(c['gamma_maximin'])<=set(c['maximal']))
  print('DECISION_REPORTS',len(rs),'FEASIBLE',sum(r['status']=='feasible'for r in rs),'EXCLUSIONS',sum(a['exclusion']is not None for r in rs for a in r['actions']or[]))
 def test_quantifier_counterexample(self):
  r=analyze_decisions(controls()[0]['input']);self.assertEqual(r['choices'],dict(e_admissible=[0,1],maximal=[0,1,2],interval_undominated=[0,1,2],gamma_maximin=[2],gamma_maximax=[0,1]));z=r['actions'][2];self.assertEqual(z['best_case_margin']['value'],[-1,2]);self.assertEqual(z['best_case_margin']['point'],[[1,2],[1,2],[-1,2]]);self.assertEqual(z['exclusion']['weights'],[[1,2],[1,2],[0,1]]);self.assertEqual(z['exclusion']['guaranteed_advantage'],[1,2])
 def test_interior_only_admissibility(self):
  r=analyze_decisions(controls()[1]['input']);self.assertEqual(r['actions'][2]['best_case_margin']['point'],[[1,2],[1,2],[0,1]]);self.assertEqual(r['choices']['e_admissible'],[0,1,2]);self.assertIsNone(r['actions'][2]['exclusion'])
 def test_strict_not_weak_dominance(self):
  r=analyze_decisions(controls()[3]['input']);self.assertEqual(r['choices']['e_admissible'],[0,1]);self.assertEqual(r['choices']['maximal'],[0,1]);r=analyze_decisions(controls()[11]['input']);self.assertEqual(r['choices']['e_admissible'],[0,1,2])
 def test_pairwise_not_interval(self):
  r=analyze_decisions(controls()[2]['input']);self.assertEqual(r['pairwise'][1][0]['value'],[1,4]);self.assertEqual(r['choices']['maximal'],[1]);self.assertEqual(r['choices']['interval_undominated'],[0,1])
 def test_tiny_strict_exclusion(self):
  r=analyze_decisions(controls()[12]['input']);self.assertEqual(r['actions'][2]['exclusion']['guaranteed_advantage'],[1,1000000])
 def test_primitive_mutations(self):
  count=0
  for control in controls()[:3]:
   r=analyze_decisions(control['input']);paths=[]
   def walk(x,path):
    if type(x)is dict:
     for k,v in x.items():
      if path or k!='input':walk(v,path+[k])
    elif type(x)is list:
     for i,v in enumerate(x):walk(v,path+[i])
    else:paths.append(path)
   walk(r,[])
   for path in paths:
    z=copy.deepcopy(r);x=z
    for k in path[:-1]:x=x[k]
    v=x[path[-1]];x[path[-1]]=v+1 if type(v)is int else 'changed'
    with self.assertRaises(ValueError,msg=str(path)):verify_decisions(z)
   count+=len(paths)
  print('DECISION_PRIMITIVE_FORGERIES',count)
 def test_omissions_and_type_confusion(self):
  r=analyze_decisions(controls()[0]['input'])
  for key in r:
   z=copy.deepcopy(r);del z[key]
   with self.assertRaises(ValueError):verify_decisions(z)
  for z in [dict(r,version=True),dict(r,extra=1),dict(r,choices={}),dict(r,actions=[]),dict(r,pairwise=None),dict(r,choices={**r['choices'],'maximal':[False,1,2]})]:
   with self.assertRaises(ValueError):verify_decisions(z)
 def test_alternate_nonvertex_attainer(self):
  r=analyze_decisions(controls()[9]['input']);r['actions'][0]['best_case_margin']['point']=[[1,3],[2,3],[0,1]];r['pairwise'][0][1]['certificate']['point']=[[2,3],[1,3]];self.assertTrue(verify_decisions(r))
 def test_checker_import_independence(self):
  code='from credallab import verify_decisions;import sys;assert "credallab.engine" not in sys.modules;assert "credallab.decisions" not in sys.modules';subprocess.run([sys.executable,'-c',code],check=True)
 def test_action_and_world_permutations(self):
  for control in controls()[:8]:
   p=copy.deepcopy(control['input']);r=analyze_decisions(p);p['utilities'].reverse();z=analyze_decisions(p);k=len(p['utilities'])
   self.assertTrue(verify_decisions(z))
   for key in r['choices']:self.assertEqual(sorted(k-1-i for i in r['choices'][key]),z['choices'][key])
   p=copy.deepcopy(control['input']);n=p['worlds'];p['utilities']=[row[::-1]for row in p['utilities']]
   for c in p['constraints']:c['event']=sorted(n-1-i for i in c['event'])
   z=analyze_decisions(p);self.assertTrue(verify_decisions(z));self.assertEqual(r['choices'],z['choices'])
 def test_common_affine_utility_transform(self):
  for control in controls()[:8]:
   p=copy.deepcopy(control['input']);r=analyze_decisions(p)
   p['utilities']=[[[ (3*F(v if type(v)is int else F(*v))+2).numerator,(3*F(v if type(v)is int else F(*v))+2).denominator]for v in row]for row in p['utilities']]
   z=analyze_decisions(p);self.assertTrue(verify_decisions(z));self.assertEqual(r['choices'],z['choices'])
 def test_duplicate_action_retains_ties(self):
  p=copy.deepcopy(controls()[0]['input']);p['utilities'].append(p['utilities'][0]);r=analyze_decisions(p);self.assertEqual(r['choices']['e_admissible'],[0,1,3]);self.assertTrue(verify_decisions(r))
 def test_credal_restriction_narrows_admissible(self):
  broad=analyze_decisions(controls()[0]['input']);narrow=analyze_decisions(controls()[5]['input']);self.assertTrue(set(narrow['choices']['e_admissible'])<=set(broad['choices']['e_admissible']));self.assertEqual(narrow['choices']['e_admissible'],[0])
 def test_strict_schema(self):
  p=controls()[0]['input']
  for key,val in [('worlds',True),('worlds',10**9),('worlds','2'),('utilities',[]),('utilities',[[True,0]]),('utilities',[[1]]),('utilities',[[1.0,0]]),('utilities',[[[1000001,1000001],0]]),('version',True)]:
   z=copy.deepcopy(p);z[key]=val
   with self.assertRaises(ValueError):compile(z)
if __name__=='__main__':unittest.main()
