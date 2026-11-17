import assert from 'node:assert/strict';import fs from 'node:fs';import crypto from 'node:crypto';
import {confidenceSummary} from '../site/assets/neuron-confidence.mjs';
const raw=fs.readFileSync(new URL('../site/assets/no-sort-example.json',import.meta.url)),d=JSON.parse(raw),c=JSON.parse(fs.readFileSync(new URL('../site/assets/neuron-confidence.json',import.meta.url)));
assert.equal(c.source_sha256,crypto.createHash('sha256').update(raw).digest('hex'));
const truths=d.query_pairs.map(([a,b])=>a+b);let count=0;
for(const [out,saved] of [[c.original,d.original_answers],...c.slots.flatMap((s,i)=>Object.entries(s.methods).map(([k,m])=>[m,d.slots[i].methods[k].answers]))]){
 assert.deepEqual(out.answers,saved);
 out.probabilities.forEach((p,i)=>{assert.equal(p.length,19);assert(p.every(x=>x>=0&&x<=1));assert(Math.abs(p.reduce((a,b)=>a+b,0)-1)<1e-12);assert.equal(p.indexOf(Math.max(...p)),saved[i]);assert.equal(out.correct_probability[i],p[truths[i]]);assert(Math.abs(out.nll[i]+Math.log(p[truths[i]]))<1e-12);count++;});
 const summary=confidenceSummary(c.original,out,truths);assert.equal(summary.higher+summary.lower+summary.same,100);assert.equal(summary.wrong,saved.filter((x,i)=>x!==truths[i]).length);
}
const self=confidenceSummary(c.original,c.original,truths);assert.equal(self.same,100);assert.equal(self.broken,0);
console.log(JSON.stringify({status:'passed',queries:count,argmaxMismatches:0}));
