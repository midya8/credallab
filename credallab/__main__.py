import argparse,json,sys
from pathlib import Path
from .model import loads

def main():
 p=argparse.ArgumentParser(description='Exact finite event-probability constraints and checked bounds');p.add_argument('command',choices=['run','verify','demo','decisions','verify-decisions','demo-decisions']);p.add_argument('file',nargs='?');args=p.parse_args()
 try:
  if args.command in ['demo','demo-decisions']:
   if args.command=='demo-decisions':
    from .decision_controls import controls
   else:
    from .controls import controls
   data=controls()[0]['input']
  else:
   if not args.file:raise ValueError('input file required')
   limit=8*1024*1024 if args.command in ['verify','verify-decisions']else 65536;raw=Path(args.file).read_bytes()
   if len(raw)>limit:raise ValueError('input size limit')
   data=loads(raw.decode('utf-8'))
  if args.command=='verify-decisions':
   from .decision_certificate import verify_decisions
   verify_decisions(data);result={'valid':True}
  elif args.command in ['decisions','demo-decisions']:
   from .decisions import analyze_decisions
   result=analyze_decisions(data)
  elif args.command=='verify':
   from .certificate import verify
   verify(data);result={'valid':True}
  else:
   from .engine import analyze
   result=analyze(data)
  print(json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False))
 except(ValueError,OSError,UnicodeError)as e:print(str(e),file=sys.stderr);return 2
 return 0
if __name__=='__main__':sys.exit(main())
