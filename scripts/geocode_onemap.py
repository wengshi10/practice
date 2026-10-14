"""Geocode uploaded addresses using the user-approved OneMap Search API.
Run: py scripts/geocode_onemap.py [--workers 4]
Cache and derived coordinates remain local and are ignored by Git.
"""
import argparse,concurrent.futures,json,os,re,threading,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'work/onemap-cache.json';CACHE.parent.mkdir(exist_ok=True)
META=ROOT/'dist/metadata.json'
ALIASES={'RD':'ROAD','AVE':'AVENUE','ST':'STREET','DR':'DRIVE','CRES':'CRESCENT','CL':'CLOSE','TER':'TERRACE','PL':'PLACE','PK':'PARK','LOR':'LORONG','JLN':'JALAN','BT':'BUKIT','KG':'KAMPONG','UPP':'UPPER','STH':'SOUTH','NTH':'NORTH','CTRL':'CENTRAL','HTS':'HEIGHTS','TG':'TANJONG','GDNS':'GARDENS','MKT':'MARKET'}
def norm(s):
 s=s.upper().replace("C'WEALTH",'COMMONWEALTH').replace("'",'');s=re.sub(r'[^A-Z0-9 ]',' ',s)
 s=re.sub(r'\bST\s+(GEORGES?|MICHAEL)\b',r'SAINT \1',s)
 return ' '.join(ALIASES.get(t,t) for t in s.split())
LOCAL=threading.local()
def query(value):
 params=urllib.parse.urlencode({'searchVal':value,'returnGeom':'Y','getAddrDetails':'Y','pageNum':1})
 headers={'User-Agent':'HDBSingapore-UniversityVisualization/1.0','Accept':'application/json'}
 token=os.environ.get('ONEMAP_TOKEN')
 if token:headers['Authorization']=token
 for attempt in range(3):
  try:
   req=urllib.request.Request('https://www.onemap.gov.sg/api/common/elastic/search?'+params,headers=headers)
   with urllib.request.urlopen(req,timeout=25) as response:d=json.load(response)
   results=d.get('results',[])
   if not results and d.get('error'):return {'status':'api_error','error':d['error']}
   return {'status':'ok','results':results,'found':d.get('found',len(results)),'advisory':d.get('error')}
  except urllib.error.HTTPError as e:
   if e.code in [429,502,503,504] and attempt<2:
    try:wait=float(e.headers.get('Retry-After','2'))
    except ValueError:wait=2
    time.sleep(min(20,wait)*(attempt+1));continue
   return {'status':'http_error','code':e.code}
  except Exception as e:
   if attempt<2:time.sleep(1+attempt);continue
   return {'status':'network_error','error':str(e)}
def coordinates(r):
 try:
  lon,lat=float(r['LONGITUDE']),float(r['LATITUDE']);x,y=float(r['X']),float(r['Y'])
  if not 103.5<lon<104.2 or not 1.1<lat<1.6:return None
  return {'coordinates':[lon,lat],'svy21':[x,y],'matchedAddress':r['ADDRESS'],'postal':r.get('POSTAL'),'source':'OneMap Search','retrievedDate':time.strftime('%Y-%m-%d',time.gmtime())}
 except (KeyError,ValueError,TypeError):return None
def resolve(job):
 key,kind,record=job
 if kind=='school':
  queryval=record['postal'];result=query(queryval)
  candidates=[r for r in result.get('results',[]) if str(r.get('POSTAL','')).zfill(6)==queryval]
  named=[r for r in candidates if norm(record['name'])==norm(r.get('BUILDING',''))]
  matches=named or candidates
 else:
  block,road=record.split(' ',1);queryval=block+' '+norm(road);result=query(queryval)
  matches=[r for r in result.get('results',[]) if str(r.get('BLK_NO','')).strip().upper()==block and norm(r.get('ROAD_NAME',''))==norm(road)]
 if not matches and kind=='block':
  fallback=query(record)
  matches=[r for r in fallback.get('results',[]) if str(r.get('BLK_NO','')).strip().upper()==block and norm(r.get('ROAD_NAME',''))==norm(road)]
 coords=[c for r in matches if (c:=coordinates(r))]
 # If co-address results are materially different, do not guess.
 if len(coords)>1:
  x0,y0=coords[0]['svy21']
  if any(((c['svy21'][0]-x0)**2+(c['svy21'][1]-y0)**2)**.5>100 for c in coords[1:]):return key,{'status':'ambiguous','query':queryval,'candidateCount':len(coords)}
 if coords:return key,{'status':'matched','query':queryval,**coords[0]}
 return key,{'status':'unmatched','query':queryval,'responseStatus':result.get('status'),'error':result.get('error')}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4);parser.add_argument('--schools-only',action='store_true');parser.add_argument('--retry-unmatched',action='store_true');args=parser.parse_args()
 meta=json.loads(META.read_text());cache=json.loads(CACHE.read_text()) if CACHE.exists() else {}
 jobs=[('school:'+s['name'],'school',s) for s in meta['schools']]
 if not args.schools_only:jobs += [('block:'+b,'block',b) for b in meta['blocks']]
 pending=[j for j in jobs if j[0] not in cache or args.retry_unmatched and cache[j[0]].get('status')!='matched']
 print('Resolving',len(pending),'addresses; cached:',len(jobs)-len(pending),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(6,args.workers))) as pool:
  futures=[pool.submit(resolve,j) for j in pending]
  for i,future in enumerate(concurrent.futures.as_completed(futures),1):
   key,result=future.result();cache[key]=result
   if i%50==0 or i==len(pending):
    tmp=CACHE.with_suffix('.tmp');tmp.write_text(json.dumps(cache,separators=(',',':')));tmp.replace(CACHE)
    matched=sum(r.get('status')=='matched' for r in cache.values());print('Resolved',i,'/',len(pending),'in this run;',matched,'matched total;',len(cache)-matched,'unmatched/ambiguous',flush=True)
 print('Cache:',CACHE,flush=True)
if __name__=='__main__':main()
