import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fitPCA,nearest,premium,portfolioSeries} from '../math.js';
const snapshot=JSON.parse(fs.readFileSync('snapshot.json','utf8'));
const history=JSON.parse(fs.readFileSync('history.json','utf8'));
assert(snapshot.stocks.length>5000);
assert.equal(new Set(snapshot.stocks.map(s=>s.id)).size,snapshot.stocks.length,'duplicate security id');
for(const s of snapshot.stocks){assert(s.price>0);if(s.financialScope==='2026Q3'){assert.equal(s.reportDate,'2026-09-30');assert(s.noticeDate<='2026-11-02')}if(s.market==='H')assert.equal(s.profitGrowth,null,'unverified H report must not be used')}
assert(snapshot.stocks.filter(s=>s.financialScope==='2026Q3').length>5000,'earnings table pagination incomplete');
for(const s of history.series){assert(snapshot.stocks.some(t=>t.id===s.id));assert(s.daily.length>250);for(let i=1;i<s.daily.length;i++)assert(s.daily[i][0]>s.daily[i-1][0]);for(const p of s.snapshots){const v=Object.values(p).filter(v=>typeof v==='number');assert(v.every(Number.isFinite));assert(p.vol>=0);assert(p.drawdown<=1e-9);assert(s.daily.some(r=>r[0]===p.date))}}
const p=fitPCA([[1,2,3],[2,4,6],[3,6,9],[4,8,12]],[1,1,1]);assert(p.explained>.99);assert(p.project([2,4,6]).every(Number.isFinite));
const zero=fitPCA([[1,1],[1,1],[1,1]],[1,1]);assert(zero.project([1,1]).every(Number.isFinite));
const n=nearest([0,0],[{id:'far',vector:[5,4]},{id:'near',vector:[.1,.2]}]);assert.equal(n[0].id,'near');
assert(Math.abs(premium(10,10,.9)-11.1111111)<1e-5);assert.equal(premium(10,0,.9),null);
const series=[{id:'a',daily:[['2020-01-01',100],['2020-01-02',110],['2020-01-03',90]]},{id:'b',daily:[['2020-01-01',100],['2020-01-02',90],['2020-01-03',110]]}];
const r=portfolioSeries(series,{a:1,b:1},'2020-01-01','2020-01-03');assert(r);assert.deepEqual(r.values,[100,100,100]);assert(Math.abs(r.returnPct)<1e-10);assert.equal(r.maxDD,0);
const one=portfolioSeries(series,{a:1},'2020-01-01','2020-01-03');assert(Math.abs(one.maxDD-(90/110-1)*100)<1e-8);
const excluded=portfolioSeries(series,{a:1,b:1},'2019-12-31','2020-01-03');assert.equal(excluded,null);
console.log(JSON.stringify({checks:'passed',stocks:snapshot.stocks.length,datedReports:snapshot.stocks.filter(s=>s.financialScope==='2026Q3').length,historicalSeries:history.series.length}));
