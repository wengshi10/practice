import csv,json,gzip,glob,re,hashlib,collections,statistics,os
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description='Prepare the six uploaded HDB datasets without external data.');parser.add_argument('input_dir',type=Path);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];out=root/'dist';out.mkdir(exist_ok=True);(root/'work').mkdir(exist_ok=True)
def find(name):return args.input_dir/name
def csvread(name):return list(csv.DictReader(open(find(name),encoding='utf-8-sig')))
raw=csvread('resale_flat_prices_based_on_registration_date_from_jan_2017_onwards.csv'); prop=csvread('HDBPropertyInformation.csv'); schools=csvread('Generalinformationofschools.csv')
keys=lambda b,s:(b.strip().upper(),s.strip().upper())
pmap={keys(r['blk_no'],r['street']):r for r in prop}
towns=sorted({r['town'] for r in raw}); types=sorted({r['flat_type'] for r in raw});models=sorted({r['flat_model'] for r in raw});blocks=sorted({keys(r['block'],r['street_name']) for r in raw});bd={v:i for i,v in enumerate(blocks)}
rows=[];matched=0;missing=[]
for r in raw:
 p=pmap.get(keys(r['block'],r['street_name']));matched+=bool(p)
 if not p:missing.append({'month':r['month'],'block':r['block'],'street':r['street_name']})
 lease=list(map(int,re.findall(r'\d+',r['remaining_lease']))); lease=lease[0]*12+(lease[1] if len(lease)>1 else 0)
 lo,hi=map(int,r['storey_range'].split(' TO '));y,m=map(int,r['month'].split('-'))
 rows.append([(y-2017)*12+m-1,towns.index(r['town']),types.index(r['flat_type']),bd[keys(r['block'],r['street_name'])],lo,hi,float(r['floor_area_sqm']),models.index(r['flat_model']),lease,float(r['resale_price']),int(p['year_completed']) if p else None,int(p['max_floor_lvl']) if p else None])
# Point-in-polygon assignment for amenities only; no HDB geocoding is inferred.
geo=json.load(open(find('MasterPlan2025PlanningAreaBoundaryNoSea.geojson')))
def inring(pt,ring):
 x,y=pt;inside=False
 for i in range(len(ring)):
  a,b=ring[i-1],ring[i]
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
def inside(pt,g):
 polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
 return any(inring(pt,p[0]) and not any(inring(pt,h) for h in p[1:]) for p in polygons)
def assign(pt):
 for f in geo['features']:
  if inside(pt,f['geometry']):return f['properties']['PLN_AREA_N']
 return None
amen={}
for name,k in [('LTAMRTStationExitGEOJSON.geojson','mrt'),('HawkerCentresGEOJSON.geojson','hawker')]:
 features=json.load(open(find(name)))['features'];arr=[]
 for f in features:
  p=f['properties'];pt=f['geometry']['coordinates'];area=assign(pt)
  arr.append({'name':p.get('STATION_NA',p.get('NAME')),'coordinates':pt,'area':area,'detail':p.get('EXIT_CODE',p.get('STATUS','')),'stalls':p.get('NUMBER_OF_COOKED_FOOD_STALLS'),'svy21':[p['LANDXADDRESSPOINT'],p['LANDYADDRESSPOINT']] if 'LANDXADDRESSPOINT' in p else None})
 amen[k]=arr
for f in geo['features']:
 p=f['properties'];f['properties']={'name':p['PLN_AREA_N'],'region':p['REGION_N']}
 # Keep boundary shapes, reduce excessive numeric precision; all rings retained.
 def roundcoords(a):return [round(v,6) for v in a] if isinstance(a[0],(int,float)) else [roundcoords(v) for v in a]
 f['geometry']['coordinates']=roundcoords(f['geometry']['coordinates'])
primary=[{'name':r['school_name'],'area':r['dgp_code'].strip().upper(),'address':r['address'].strip(),'postal':r['postal_code'].strip().zfill(6),'mrt':r['mrt_desc']} for r in schools if r['mainlevel_code']=='PRIMARY']
meta={'towns':towns,'types':types,'models':models,'blocks':[' '.join(b) for b in blocks],'count':len(rows),'matched':matched,'missing':missing,'start':min(r['month'] for r in raw),'end':max(r['month'] for r in raw),'amenities':amen,'schools':primary,'allSchoolCount':len(schools),'propertyCount':len(prop),'geo':geo,'columns':['monthIndex','townIndex','flatTypeIndex','blockIndex','storeyLow','storeyHigh','areaSqm','modelIndex','leaseMonths','resalePrice','yearCompleted','maxFloor'],'sources':[]}
for name in ['Generalinformationofschools.csv','HDBPropertyInformation.csv','HawkerCentresGEOJSON.geojson','LTAMRTStationExitGEOJSON.geojson','MasterPlan2025PlanningAreaBoundaryNoSea.geojson','resale_flat_prices_based_on_registration_date_from_jan_2017_onwards.csv']:
 p=find(name);meta['sources'].append({'name':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
# Block indices are derived from the current input files; stale enrichment must be rebuilt.
(out/'accessibility.json').unlink(missing_ok=True)
(out/'metadata.json').write_text(json.dumps(meta,separators=(',',':')))
# JS loads JSON directly, no CDN and no gzip browser dependency.
(out/'transactions.json').write_text(json.dumps(rows,separators=(',',':')))
with gzip.open(root/'work/transactions.json.gz','wb') as f:f.write((out/'transactions.json').read_bytes())
print(json.dumps({'rows':len(rows),'matched':matched,'unmatched':missing,'period':[meta['start'],meta['end']],'types':types,'years':dict(collections.Counter(2017+r[0]//12 for r in rows)),'transactionBytes':(out/'transactions.json').stat().st_size,'gzipBytes':(root/'work/transactions.json.gz').stat().st_size,'median':statistics.median(r[9] for r in rows)},indent=2))
