import ast,copy,json,subprocess,sys,tempfile,unittest
from fractions import Fraction as F
from pathlib import Path
from credallab import analyze,verify
from credallab.controls import controls
from credallab.model import loads,parse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cases import cases

class Tests(unittest.TestCase):
 def test_complete_development_grid(self):
  rs=[analyze(p)for p in cases()]
  for r in rs:self.assertTrue(verify(r))
  print('REPORT_COUNTS',len(rs),sum(r['status']=='feasible'for r in rs),sum(r['conditional']is not None for r in rs))
 def test_impossible_triangle_and_boundary(self):
  a,b=[analyze(c['input'])for c in controls()[:2]];self.assertEqual(a['phase']['value'],[-1,3]);self.assertEqual(b['conditional']['lower']['value'],[1,3]);self.assertEqual(b['conditional']['upper']['value'],[1,3])
 def test_marginals_do_not_assert_independence(self):
  r=analyze(controls()[2]['input']);self.assertEqual(r['bounds']['event']['lower']['value'],[0,1]);self.assertEqual(r['bounds']['event']['upper']['value'],[1,2])
 def test_informative_conditioning(self):
  r=analyze(next(c['input']for c in controls()if c['id']=='conditional_informative'));self.assertEqual([r['conditional'][k]['value']for k in ['lower','upper']],[[1,3],[1,2]])
 def test_zero_mass_is_not_a_posterior(self):
  for id in ['conditioning_impossible','empty_given']:
   r=analyze(next(c['input']for c in controls()if c['id']==id));self.assertIsNone(r['conditional'])
  r=analyze(next(c['input']for c in controls()if c['id']=='conditioning_can_vanish'));self.assertEqual(r['bounds']['given']['lower']['value'],[0,1]);self.assertIsNotNone(r['conditional'])
 def test_certificate_tampering(self):
  count=0
  for c in controls()[:3]:
   r=analyze(c['input']);paths=[]
   def walk(x,ks):
    if type(x)is dict:
     for k,v in x.items():
      if ks or k!='input':walk(v,ks+[k])
    elif type(x)is list:
     for i,v in enumerate(x):walk(v,ks+[i])
    else:paths.append(ks)
   walk(r,[])
   for path in paths:
    x=copy.deepcopy(r);v=x
    for k in path[:-1]:v=v[k]
    old=v[path[-1]];v[path[-1]]=old+1 if type(old)is int else 'changed'
    with self.assertRaises(ValueError):verify(x)
   count+=len(paths)
  print('PRIMITIVE_FORGERIES',count)
 def test_valid_alternative_witnesses(self):
  r=analyze(next(c['input']for c in controls()if c['id']=='no_assessments'));q=copy.deepcopy(r);q['bounds']['given']['upper']['certificate']['point']=[[0,1],[1,1],[0,1]];self.assertTrue(verify(q));self.assertNotEqual(q,r)
 def test_world_permutation_invariance(self):
  for control in controls():
   p=copy.deepcopy(control['input']);n=p['worlds'];r=analyze(p)
   for c in p['constraints']:c['event']=sorted(n-1-i for i in c['event'])
   for k in ['event','given']:p['query'][k]=sorted(n-1-i for i in p['query'][k])
   z=analyze(p);self.assertTrue(verify(z));self.assertEqual(z['status'],r['status']);self.assertEqual(z['phase']['value'],r['phase']['value'])
   if r['bounds']:
    for k in ['event','given']:
     for side in ['lower','upper']:self.assertEqual(z['bounds'][k][side]['value'],r['bounds'][k][side]['value'])
    if r['conditional']:
     for side in ['lower','upper']:self.assertEqual(z['conditional'][side]['value'],r['conditional'][side]['value'])
 def test_duplicate_assessment_invariance(self):
  for control in controls()[:5]:
   p=copy.deepcopy(control['input']);r=analyze(p);p['constraints'].append(copy.deepcopy(p['constraints'][0]));z=analyze(p);self.assertTrue(verify(z));self.assertEqual(r['phase']['value'],z['phase']['value'])
   if r['bounds']:
    for k in ['event','given']:
     for side in ['lower','upper']:self.assertEqual(r['bounds'][k][side]['value'],z['bounds'][k][side]['value'])
 def test_tighter_assessments_narrow_bounds(self):
  p=copy.deepcopy(controls()[2]['input']);r=analyze(p);p['constraints'].append(dict(event=p['query']['event'],lower=[1,4],upper=[1,3]));z=analyze(p);self.assertTrue(verify(z));self.assertEqual(z['bounds']['event']['lower']['value'],[1,4]);self.assertEqual(z['bounds']['event']['upper']['value'],[1,3])
 def test_conditional_alternative_attainer(self):
  p=dict(version=1,worlds=3,constraints=[],query=dict(event=[0,1],given=[0,1]));r=analyze(p);r['conditional']['lower']['certificate']['point']=[[1,2],[1,2],[0,1]];self.assertTrue(verify(r))
 def test_raw_rational_and_complexity_limits(self):
  p=copy.deepcopy(controls()[0]['input'])
  for v in [[1000001,1000001],[True,2],[1,0],[1,-2],[0,1000001]]:
   q=copy.deepcopy(p);q['constraints'][0]['lower']=v
   with self.assertRaises(ValueError):parse(q)
  q=copy.deepcopy(p);q['worlds']=6;q['constraints']=q['constraints']*2
  with self.assertRaises(ValueError):parse(q)
 def test_no_generator_in_checker(self):
  code='from credallab import verify;import sys;assert "credallab.engine" not in sys.modules';self.assertEqual(subprocess.run([sys.executable,'-c',code]).returncode,0)
  t=ast.parse((Path(__file__).resolve().parents[1]/'credallab/certificate.py').read_text());self.assertEqual([x.module for x in ast.walk(t)if isinstance(x,ast.ImportFrom)and x.level],['model'])
 def test_omissions_and_type_confusion(self):
  r=analyze(controls()[2]['input'])
  for key in r:
   x=copy.deepcopy(r);del x[key]
   with self.assertRaises(ValueError):verify(x)
  for x in [dict(r,version=True),dict(r,extra=0),dict(r,bounds=None),dict(r,conditional=None),None,{}]:
   with self.assertRaises(ValueError):verify(x)
 def test_strict_input(self):
  for text in ['{"version":1,"version":1}','{"x":1.0}','{"x":1e0}','NaN','Infinity']:
   with self.assertRaises(ValueError):loads(text)
  p=controls()[0]['input']
  for key,val in [('worlds',True),('worlds',7),('version',True),('constraints',None),('query',{})]:
   x=copy.deepcopy(p);x[key]=val
   with self.assertRaises(ValueError):parse(x)
  for event in [[1,1],[2,1],[-1],[True],[4]]:
   x=copy.deepcopy(p);x['query']['event']=event
   with self.assertRaises(ValueError):parse(x)
 def test_cli_failure_has_no_partial_json(self):
  with tempfile.TemporaryDirectory()as d:
   f=Path(d)/'i.json';f.write_text(json.dumps(controls()[2]['input']));cmd=[sys.executable,'-m','credallab'];r=subprocess.run(cmd+['run',str(f)],capture_output=True,text=True);self.assertEqual(r.returncode,0);f.write_text(r.stdout);r=subprocess.run(cmd+['verify',str(f)],capture_output=True,text=True);self.assertEqual(json.loads(r.stdout),{'valid':True});f.write_text('{}');r=subprocess.run(cmd+['run',str(f)],capture_output=True,text=True);self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'')
if __name__=='__main__':unittest.main()
