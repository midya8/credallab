"""Build and test a wheel from outside the source checkout."""
import json,os,subprocess,sys,tempfile,venv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from credallab.controls import controls
from credallab import analyze

def call(args,**kw):return subprocess.run(args,check=True,capture_output=True,text=True,**kw).stdout
with tempfile.TemporaryDirectory()as d:
 t=Path(d);w=t/'wheels';w.mkdir();call([sys.executable,'-m','pip','wheel','--no-deps','--no-build-isolation','-w',str(w),str(ROOT)]);wheel=next(w.glob('*.whl'));env=t/'env';venv.create(env,with_pip=True);py=str(env/'bin/python');exe=str(env/'bin/credallab');call([py,'-m','pip','install','--no-deps',str(wheel)]);clean=t/'outside';clean.mkdir();en=os.environ.copy();en.pop('PYTHONPATH',None)
 code='''import importlib,importlib.metadata,pathlib,sys
assert importlib.metadata.version('credallab-finite')=='0.2.0'
for name in ['credallab','credallab.model','credallab.engine','credallab.certificate','credallab.controls','credallab.__main__']:
 p=pathlib.Path(importlib.import_module(name).__file__).resolve();assert 'site-packages' in str(p)and not str(p).startswith(sys.argv[1])
''';call([py,'-c',code,str(ROOT)],cwd=clean,env=en)
 for i,c in enumerate(controls()):
  f=clean/'input.json';f.write_text(json.dumps(c['input']));expected=analyze(c['input'])
  for cmd in [[py,'-m','credallab'],[exe]]:
   result=json.loads(call(cmd+['run',str(f)],cwd=clean,env=en));assert result==expected;report=clean/'report.json';report.write_text(json.dumps(result));assert json.loads(call(cmd+['verify',str(report)],cwd=clean,env=en))=={'valid':True}
   result['phase']['value'][0]+=1;report.write_text(json.dumps(result));bad=subprocess.run(cmd+['verify',str(report)],cwd=clean,env=en,capture_output=True,text=True);assert bad.returncode==2 and not bad.stdout
 print(json.dumps(dict(wheel=wheel.name,module_origins=6,controls=len(controls()),entrypoints=2,cli_forgery_rejections=2*len(controls()))))
