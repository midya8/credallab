/* Finite credal decision sets. Classical rules, explicit strict dominance. */
(function(root){
'use strict';
const C=typeof module!=='undefined'?require('./credal-engine.js'):root.Credal;
const{Q,zero,one,add,neg,sub,mul,cmp,eq,sum,min,max,dot,keys,rat,choose,vertices,certify,gcd}=C.linear;
function compile(p){
 keys(p,['version','worlds','constraints','utilities']);
 if(p.version!==1||!Number.isInteger(p.worlds)||p.worlds<1||p.worlds>6)throw Error('decision version/worlds');
 const m=C.compile({version:1,worlds:p.worlds,constraints:p.constraints,query:{event:[],given:Array.from({length:p.worlds},(_,i)=>i)}});
 if(!Array.isArray(p.utilities)||p.utilities.length<1||p.utilities.length>6)throw Error('1..6 action utility vectors required');
 let den=1n;
 const u=p.utilities.map(r=>{if(!Array.isArray(r)||r.length!==m.n)throw Error('one exact utility per world required');return r.map(v=>{const q=rat(v);den=den/gcd(den,q[1])*q[1];if(den>1000000n)throw Error('utility denominator LCM limit');return q;});});
 if(choose(2*p.constraints.length+m.n+u.length,m.n)>20000)throw Error('20000 candidate decision-margin bases limit');
 return{...m,u};
}
function marginSystem(m,i){const{n,rows,rhs,u}=m,{h,a,b}=C.system(n,rows,rhs);return{h:[...h,zero],a:[...a.map(r=>[...r,zero]),...u.map(r=>[...r.map((x,j)=>sub(x,u[i][j])),one])],b:[...b,...u.map(()=>zero)]};}
function choiceSets(actions,pairwise){const lo=actions.map(x=>x.lower.value),hi=actions.map(x=>x.upper.value),ids=actions.map((_,i)=>i);return{
 e_admissible:ids.filter(i=>eq(actions[i].best_case_margin.value,zero)),
 maximal:ids.filter(i=>ids.every(j=>cmp(pairwise[j][i].value,zero)<=0)),
 interval_undominated:ids.filter(i=>ids.every(j=>cmp(lo[j],hi[i])<=0)),
 gamma_maximin:ids.filter(i=>eq(lo[i],max(lo))),gamma_maximax:ids.filter(i=>eq(hi[i],max(hi)))
};}
function analyze(p){const m=compile(p),{n,rows,rhs,u}=m;let{h,a,b}=C.system(n,rows,rhs,true);const phase=certify(h,a,b,vertices(h,a,b),[...Array(n).fill(zero),neg(one)]),base={version:1,kind:'credallab-decisions',input:p,phase};if(cmp(phase.value,zero)<0)return{...base,status:'infeasible',actions:null,pairwise:null,choices:null};
 ({h,a,b}=C.system(n,rows,rhs));const vs=vertices(h,a,b);
 const lower=c=>{const z=certify(h,a,b,vs,c.map(neg));return{value:neg(z.value),certificate:z};},upper=c=>{const z=certify(h,a,b,vs,c);return{value:z.value,certificate:z};};
 const actions=u.map((c,i)=>{const mh=marginSystem(m,i),z=certify(mh.h,mh.a,mh.b,vertices(mh.h,mh.a,mh.b),[...Array(n).fill(zero),one]);let exclusion=null;if(cmp(z.value,zero)<0){exclusion={weights:z.multipliers.slice(a.length),guaranteed_advantage:neg(z.value),certificate:{value:z.value,point:z.point.slice(0,n),multipliers:z.multipliers.slice(0,a.length),equality:z.equality}};}return{lower:lower(c),upper:upper(c),best_case_margin:z,exclusion};});
 const pairwise=u.map(c=>u.map(d=>lower(c.map((v,j)=>sub(v,d[j])))));
 return{...base,status:'feasible',actions,pairwise,choices:choiceSets(actions,pairwise)};
}
const api={analyze,compile,marginSystem,parse:C.parse,stringify:C.stringify};if(typeof module!=='undefined')module.exports=api;root.CredalDecisions=api;
})(typeof globalThis!=='undefined'?globalThis:this);
