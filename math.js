export const finite=x=>typeof x==='number'&&Number.isFinite(x);
export const mean=a=>a.reduce((s,x)=>s+x,0)/(a.length||1);
export const quantile=(a,p)=>{const s=[...a].sort((x,y)=>x-y);if(!s.length)return 0;const t=(s.length-1)*p,i=Math.floor(t);return s[i]+(s[Math.ceil(t)]-s[i])*(t-i)};
export const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
export function fitPCA(rows,weights){
 if(!rows.length)return null;
 const d=rows[0].length,n=rows.length,stats=Array.from({length:d},(_,j)=>{const a=rows.map(r=>r[j]),med=quantile(a,.5),iqr=quantile(a,.75)-quantile(a,.25);return {med,scale:iqr>1e-10?iqr:1,lo:quantile(a,.01),hi:quantile(a,.99)}});
 const transform=r=>r.map((x,j)=>Math.max(-4,Math.min(4,(Math.max(stats[j].lo,Math.min(stats[j].hi,x))-stats[j].med)/stats[j].scale))*Math.sqrt(weights[j]??1));
 const z=rows.map(transform),centers=Array.from({length:d},(_,j)=>mean(z.map(r=>r[j]))),center=r=>r.map((x,j)=>x-centers[j]);
 const centered=z.map(center),cov=Array.from({length:d},(_,j)=>Array.from({length:d},(_,k)=>mean(centered.map(r=>r[j]*r[k]))));
 const trace=cov.reduce((s,r,j)=>s+r[j],0),basis=[],eigenvalues=[],def=cov.map(r=>[...r]);
 for(let k=0;k<Math.min(3,d);k++){
  let v=Array.from({length:d},(_,j)=>Math.cos((j+1)*(k+1)*.7)+.1);
  for(let it=0;it<100;it++){let w=def.map(r=>dot(r,v));const norm=Math.sqrt(dot(w,w));if(norm<1e-12){v=Array(d).fill(0);break}v=w.map(x=>x/norm)}
  const lambda=Math.max(0,dot(v,cov.map(r=>dot(r,v))));
  const maxi=v.reduce((i,x,j)=>Math.abs(x)>Math.abs(v[i])?j:i,0);if(v[maxi]<0)v=v.map(x=>-x);
  basis.push(v);eigenvalues.push(lambda);for(let i=0;i<d;i++)for(let j=0;j<d;j++)def[i][j]-=lambda*v[i]*v[j];
 }
 const vector=r=>center(transform(r));const project=r=>{let q=basis.map(v=>dot(v,vector(r)));while(q.length<3)q.push(0);return q};
 return {project,vector,basis,stats,explained:trace?Math.min(1,eigenvalues.reduce((a,b)=>a+b,0)/trace):0,dimensions:d};
}
export function nearest(vector,items,count=20){return items.map(s=>({...s,distance:Math.sqrt(s.vector.reduce((sum,v,i)=>sum+(v-vector[i])**2,0)/Math.max(vector.length,1))})).sort((a,b)=>a.distance-b.distance).slice(0,count)}
export function premium(a,h,fx){return finite(a)&&finite(h)&&finite(fx)&&h>0&&fx>0?(a/(h*fx)-1)*100:null}
export function pearson(a,b){if(a.length<3||a.length!==b.length)return null;const x=mean(a),y=mean(b),p=a.map(v=>v-x),q=b.map(v=>v-y),den=Math.sqrt(dot(p,p)*dot(q,q));return den?dot(p,q)/den:null}
export function portfolioSeries(series,weights,start,end){
 const included=series.filter(s=>weights[s.id]>0&&s.daily.length&&s.daily[0][0]<=start&&s.daily.at(-1)[0]>=end);
 if(!included.length)return null;
 const maps=included.map(s=>new Map(s.daily.filter(r=>r[0]>=start&&r[0]<=end&&r[1]>0).map(r=>[r[0],r[1]])));
 const dates=[...maps[0].keys()].filter(d=>maps.every(m=>m.has(d))).sort();
 if(dates.length<3)return null;
 const wsum=included.reduce((sum,s)=>sum+weights[s.id],0),ws=included.map(s=>weights[s.id]/wsum),base=maps.map(m=>m.get(dates[0]));
 const values=dates.map(d=>100*maps.reduce((sum,m,j)=>sum+ws[j]*m.get(d)/base[j],0));let high=values[0],maxDD=0;
 for(const v of values){high=Math.max(high,v);maxDD=Math.min(maxDD,v/high-1)}
 const rets=values.slice(1).map((v,i)=>Math.log(v/values[i])),avg=mean(rets),vol=Math.sqrt(rets.reduce((s,x)=>s+(x-avg)**2,0)/Math.max(1,rets.length-1)*250)*100;
 const correlations=[];
 for(let i=0;i<maps.length;i++)for(let j=i+1;j<maps.length;j++){const a=dates.slice(1).map((d,k)=>Math.log(maps[i].get(d)/maps[i].get(dates[k]))),b=dates.slice(1).map((d,k)=>Math.log(maps[j].get(d)/maps[j].get(dates[k])));const r=pearson(a,b);if(r!==null)correlations.push(r)}
 return {dates,values,returnPct:(values.at(-1)/values[0]-1)*100,maxDD:maxDD*100,vol,included:included.map(s=>s.id),correlation:correlations.length?mean(correlations):null};
}
