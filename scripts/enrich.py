"""Replace A-share report metrics with explicit report/announcement dates from provider's earnings-report table."""
import json,urllib.parse,concurrent.futures,datetime
from collect import ROOT,get,num
BASE='https://datacenter-web.eastmoney.com/api/data/v1/get?'
def fetch(p):
 return get(BASE+urllib.parse.urlencode(dict(reportName='RPT_LICO_FN_CPD',columns='ALL',filter="(REPORTDATE='2026-09-30')",pageNumber=p,pageSize=500,sortColumns='SECURITY_CODE',sortTypes='1'))).get('result')
def category(name):
 if any(x in name for x in ['银行','证券','保险','多元金融']):return '金融'
 if any(x in name for x in ['医药','医疗','中药','生物','化学制药']):return '医药'
 if any(x in name for x in ['酒','食品','饮料','家电','服装','纺织','百货','商业','农牧','美容','旅游','酒店','文化传媒','汽车整车','珠宝','家用轻工']):return '消费'
 if any(x in name for x in ['半导体','计算机','通信','电子','软件','光学','电池','互联网','光伏','电网','仪器']):return '科技'
 if any(x in name for x in ['电力','燃气','石油','煤炭','公用','环保']):return '能源与公用'
 return '工业与材料' if name else '未分类'
def run():
 first=fetch(1)
 if not first:raise RuntimeError('financial endpoint missing result')
 rows=first['data']
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
  for r in ex.map(fetch,range(2,first['pages']+1)):
   if r:rows+=r['data']
 reports={r['SECURITY_CODE']:r for r in rows if (r.get('NOTICE_DATE') or '')[:10]<=datetime.date.today().isoformat()}
 path=ROOT/'snapshot.json';j=json.loads(path.read_text());n=0
 for s in j['stocks']:
  if s['market']=='A' and s['code'] in reports:
   r=reports[s['code']];n+=1
   s.update(roe=num(r.get('WEIGHTAVG_ROE')),revenueGrowth=num(r.get('YSTZ')),profitGrowth=num(r.get('SJLTZ')),eps=num(r.get('BASIC_EPS')),cfoPerShare=num(r.get('MGJYXJJE')),grossMargin=num(r.get('XSMLL')),reportDate=r['REPORTDATE'][:10],noticeDate=r['NOTICE_DATE'][:10],industry=r.get('PUBLISHNAME'),financialScope='2026Q3')
   s['sector']=category(r.get('PUBLISHNAME') or '')
  elif s['market']=='A':
   s.update(roe=None,revenueGrowth=None,profitGrowth=None,reportDate=None,noticeDate=None,financialScope='missing')
  else:
   # Financial zeros in H-share quote fields are frequently placeholders, not observations.
   # Until report-date verification, preserve only ROE as a displayed provider value.
   s.update(revenueGrowth=None,profitGrowth=None,debt=None,financialScope='unverified-H')
 j['meta'].update(financialSource='东方财富业绩报表 RPT_LICO_FN_CPD，2026-09-30 A 股报告；公告日不晚于采集日',financialSourceUrl='https://data.eastmoney.com/bbsj/202609/yjbb.html',financialReportCount=n,financialBasis='A 股采用 2026 三季报累计加权 ROE、营收及归母净利同比，并保留公告日；港股财报尚未校准，不纳入经营距离。')
 path.write_text(json.dumps(j,ensure_ascii=False,separators=(',',':')))
 print('dated A-share reports',n,'rows',len(rows),flush=True)
if __name__=='__main__':run()
