#!/usr/bin/env python3
"""Fetch a documented, dated exploratory snapshot; keep missing values null.
No credentials. Network is only used by this optional maintainer command.
Verify provider permission before wider redistribution. Does not run in visitors' browsers.
"""
import urllib.request,urllib.parse,json,time,math,statistics,datetime,pathlib,concurrent.futures,argparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIELDS='f2,f3,f8,f9,f12,f13,f14,f20,f23,f24,f25,f37,f46,f48,f57,f124'
URL='https://push2delay.eastmoney.com/api/qt/clist/get?'
FS={'A':'m:1+t:2,m:1+t:23,m:0+t:6,m:0+t:80,m:0+t:81+s:2048','H':'m:128+t:3,m:128+t:4,m:128+t:1,m:128+t:2'}
def get(url):
 for n in range(3):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
   with urllib.request.urlopen(req,timeout=18) as r:return json.load(r)
  except Exception:
   if n==2:raise

def num(v):return v if isinstance(v,(float,int)) and math.isfinite(v) else None
def page(item):
 m,p=item
 d=get(URL+urllib.parse.urlencode(dict(pn=p,pz=100,po=1,fid='f20',fltt=2,fs=FS[m],fields=FIELDS))).get('data')
 if not d:return []
 vals=d['diff'];vals=vals.values() if isinstance(vals,dict) else vals
 out=[]
 for r in vals:
  if not num(r.get('f2')) or r['f2']<=0:continue
  out.append(dict(id=m+':'+r['f12'],code=r['f12'],name=r['f14'],market=m,secid=str(r['f13'])+'.'+r['f12'],price=num(r.get('f2')),change=num(r.get('f3')),turnover=num(r.get('f8')),pe=num(r.get('f9')),pb=num(r.get('f23')),r60=num(r.get('f24')),ytd=num(r.get('f25')),cap=num(r.get('f20')),roe=num(r.get('f37')),profitGrowth=num(r.get('f46')),revenueGrowth=num(r.get('f48')),debt=num(r.get('f57')),quoteTs=r.get('f124')))
 return out
# Manually reviewed broad categories for key examples; all other issuers remain unclassified.
GROUPS={
 '金融':'工商银行 建设银行 农业银行 中国银行 招商银行 交通银行 邮储银行 兴业银行 平安银行 浦发银行 中信银行 民生银行 光大银行 中国平安 中国人寿 中国太保 中国财险 中信证券 华泰证券 香港交易所 友邦保险 恒生银行 渣打集团 汇丰控股',
 '消费':'贵州茅台 五粮液 泸州老窖 山西汾酒 洋河股份 海天味业 东鹏饮料 农夫山泉 伊利股份 蒙牛乳业 海尔智家 美的集团 格力电器 安踏体育 李宁 申洲国际 百威亚太 华润啤酒 青岛啤酒 承德露露 腾讯控股 美团-W 京东集团-SW 阿里巴巴-W 小米集团-W',
 '科技':'宁德时代 比亚迪 中芯国际 海光信息 寒武纪-U 中际旭创 新易盛 工业富联 立讯精密 中兴通讯 京东方A 北方华创 兆易创新 韦尔股份 长鑫科技 华虹半导体 金山软件 联想集团 快手-W 百度集团-SW 哔哩哔哩-W 网易-S',
 '能源与公用':'中国神华 中国石油 中国石化 中国海油 陕西煤业 兖矿能源 中国电信 中国移动 中国联通 长江电力 华能水电 中国广核 华润电力 中电控股 香港中华煤气 中国燃气 新奥能源 港华智慧能源',
 '工业与材料':'海螺水泥 华新水泥 中国中车 时代电气 中国中铁 中国铁建 中国建筑 三一重工 徐工机械 东方电气 东方电子 紫金矿业 洛阳钼业 山东黄金 宝钢股份 鞍钢股份 江西铜业 中国铝业 中国宏桥 万华化学 中远海控 中远海能',
 '医药':'恒瑞医药 迈瑞医疗 药明康德 药明生物 百济神州-U 百济神州 石药集团 中国生物制药 翰森制药 信达生物 康方生物 联影医疗 爱尔眼科 片仔癀 云南白药'}
def group(name):
 for g,ns in GROUPS.items():
  if name in ns.split():return g
 return '未分类'
WATCH=['600519','000858','002304','605499','000848','000682','600585','688187','601088','601398','600036','601318','300750','002594','688981','601899','600900','000333','600887','600309','600276','600030','601012','601888','600000','601939','600690','601006','600050','600031','600028','601857','600660','000651','002475','601668','601766','600104','600919','600438','00700','03690','02313','03898','00941','00939','01398','00005','01299','09988','09618','01810','02020','02331','00981','01211','00883','00857','00386','01088','00669','02318','00388','09999','02382','01024','02333','00027','00291','02319','01928','00868','00960','01177','02269','01093','00992','06618','09633','01876','00762','00728','00390','00688','01919']
def history(s):
 url='https://push2his.eastmoney.com/api/qt/stock/kline/get?'+urllib.parse.urlencode(dict(secid=s['secid'],klt=101,fqt=1,beg=20190101,end='20500101',fields1='f1,f2,f3,f4,f5,f6',fields2='f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61'))
 d=get(url).get('data')
 if not d:return None
 rows=[]
 for row in d.get('klines',[]):
  z=row.split(',')
  try:rows.append([z[0],float(z[2]),float(z[10])])
  except (ValueError,IndexError):continue
 if len(rows)<270:return None
 # Monthly end snapshots. Last month uses latest available trading date.
 end={}
 for i,r in enumerate(rows):end[r[0][:7]]=i
 snaps=[]
 for month,i in end.items():
  if i<250:continue
  recent=rows[i-59:i+1];rets=[math.log(rows[k][1]/rows[k-1][1]) for k in range(i-59,i+1) if rows[k][1]>0 and rows[k-1][1]>0]
  if len(rets)<50:continue
  p=rows[i][1];top=max(r[1] for r in rows[i-249:i+1])
  snaps.append(dict(date=rows[i][0],price=p,r20=(p/rows[i-20][1]-1)*100,r60=(p/rows[i-60][1]-1)*100,r250=(p/rows[i-250][1]-1)*100,vol=statistics.stdev(rets)*math.sqrt(250)*100,drawdown=(p/top-1)*100,turnover=statistics.mean(r[2] for r in recent)))
 return dict(id=s['id'],snapshots=snaps,daily=rows)
def run():
 stocks=[];errors=[]
 jobs=[(m,p) for m,n in [('A',60),('H',48)] for p in range(1,n+1)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
  fut={ex.submit(page,j):j for j in jobs}
  for f in concurrent.futures.as_completed(fut):
   try:stocks.extend(f.result())
   except Exception as e:errors.append(str(fut[f])+': '+str(e))
 stocks=list({s['id']:s for s in stocks}.values())
 for s in stocks:s['sector']=group(s['name'])
 stocks.sort(key=lambda s:-(s['cap'] or 0))
 print('snapshot',len(stocks),'errors',len(errors),flush=True)
 target=ROOT;target.mkdir(exist_ok=True)
 payload=dict(meta=dict(source='东方财富公开延时行情接口',sourceUrl='https://quote.eastmoney.com/center/gridlist.html',fetchedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),quoteTimestampMax=max(s['quoteTs'] or 0 for s in stocks),count=len(stocks),errors=errors,scope='具有有效报价的 A 股、港股证券；并非经核验的全部上市公司。金融与非金融口径不同，港股字段缺失较多。',currency='A: CNY, H: HKD',financialBasis='第三方最新报告期字段，报告期及披露日未提供，不用于财务历史回测。',peBasis='第三方动态市盈率，非统一 TTM。'),stocks=stocks)
 (target/'snapshot.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')))
 chosen=[s for s in stocks if s['code'] in WATCH]
 hist=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
  fut={ex.submit(history,s):s['id'] for s in chosen}
  for f in concurrent.futures.as_completed(fut):
   try:
    r=f.result()
    if r:hist.append(r)
   except Exception as e:errors.append(fut[f]+': '+str(e))
 (target/'history.json').write_text(json.dumps(dict(meta=dict(source='东方财富前复权日线',fetchedAt=payload['meta']['fetchedAt'],adjustment='前复权，含分红拆股的历史复权；不是现金分红再投资总回报。复权因子随未来公司行动可能重算。',scope='固定观察样本，含幸存者偏差，仅作探索，非全市场历史回测。',count=len(hist)),series=hist),ensure_ascii=False,separators=(',',':')))
 print('history',len(hist),'errors',len(errors),flush=True)
if __name__=='__main__':run()
