'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),cp=require('node:child_process'),C=require('../docs/decision-engine.js');
test('complete exact decision reports match Python and replay independently',{timeout:120000},()=>{
 const data=JSON.parse(cp.execFileSync(process.env.PYTHON||'python',['-c','import sys,json;sys.path.insert(0,"tools");from decision_cases import cases;from credallab import analyze_decisions;print(json.dumps([[p,json.dumps(analyze_decisions(p),sort_keys=True,separators=(",",":"))]for p in cases()]))'],{encoding:'utf8',maxBuffer:64*1024*1024}));const rs=[];
 for(const[p,expected]of data){const raw=C.stringify(C.analyze(p));assert.equal(raw,expected);rs.push(raw);}
 cp.execFileSync(process.env.PYTHON||'python',['-c','import sys,json;from credallab import verify_decisions;assert all(verify_decisions(r)for r in json.load(sys.stdin))'],{input:'['+rs.join(',')+']',maxBuffer:64*1024*1024});console.log('BIGINT_DECISION_REPORTS',rs.length);
});
test('strict decision schema and bounded worlds',()=>{for(const worlds of[true,0,7,1e9,'2'])assert.throws(()=>C.analyze({version:1,worlds,constraints:[],utilities:[[1,0]]}));for(const utilities of[[],[[true,0]],[[1]],[[1.1,0]],[[[1000001,1000001],0]]])assert.throws(()=>C.analyze({version:1,worlds:2,constraints:[],utilities}));});
