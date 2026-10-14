"""Derive nearest-amenity straight-line distances from verified OneMap matches.
No transaction, price or amenity records are sourced externally. Uses Python stdlib.
"""
import json,math,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# WGS84 Transverse Mercator, EPSG:3414 (SVY21); lat/lon in decimal degrees.
def svy21(lon,lat):
 a=6378137.;e2=0.0066943799901413165;ep2=e2/(1-e2)
 phi=math.radians(lat);phi0=math.radians(1.3666666666666667);lam=math.radians(lon);lam0=math.radians(103.83333333333333)
 def meridian(p):
  return a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-35*e2**3/3072*math.sin(6*p))
 N=a/math.sqrt(1-e2*math.sin(phi)**2);T=math.tan(phi)**2;C=ep2*math.cos(phi)**2;A=math.cos(phi)*(lam-lam0)
 x=28001.642+N*(A+(1-T+C)*A**3/6+(5-18*T+T*T+72*C-58*ep2)*A**5/120)
 y=38744.572+meridian(phi)-meridian(phi0)+N*math.tan(phi)*(A*A/2+(5-T+9*C+4*C*C)*A**4/24+(61-58*T+T*T+600*C-330*ep2)*A**6/720)
 return [x,y]
def main():
 path=ROOT/'dist/metadata.json';meta=json.loads(path.read_text());cache=json.loads((ROOT/'work/onemap-cache.json').read_text());schools=[];unmatchedSchools=[]
 errors=[]
 for s in meta['schools']:
  c=cache.get('school:'+s['name'],{})
  if c.get('status')=='matched':
   schools.append({**s,'coordinates':c['coordinates'],'svy21':c['svy21'],'matchedAddress':c['matchedAddress'],'source':'OneMap Search'})
   projected=svy21(*c['coordinates']);errors.append(math.hypot(projected[0]-c['svy21'][0],projected[1]-c['svy21'][1]))
  else:unmatchedSchools.append(s['name'])
 amen={'mrt':[{**s,'svy21':svy21(*s['coordinates'])} for s in meta['amenities']['mrt']], 'school':schools,'hawker':[{**s,'svy21':s.get('svy21') or svy21(*s['coordinates'])} for s in meta['amenities']['hawker'] if s['detail'].startswith('Existing') or s['detail']=='Interim Centre']}
 blocks=[];matched=0;unmatched=[]
 for i,b in enumerate(meta['blocks']):
  c=cache.get('block:'+b,{})
  if c.get('status')!='matched':blocks.append(None);unmatched.append(b);continue
  matched+=1;x,y=c['svy21'];dist=[];nearest=[]
  for k in ['mrt','school','hawker']:
   points=amen[k]
   if not points:dist.append(None);nearest.append(None);continue
   j=min(range(len(points)),key=lambda j:(points[j]['svy21'][0]-x)**2+(points[j]['svy21'][1]-y)**2)
   a=points[j];dist.append(round(math.hypot(a['svy21'][0]-x,a['svy21'][1]-y),2));nearest.append(a['name'])
  blocks.append({'coordinates':c['coordinates'],'svy21':c['svy21'],'distances':dist,'nearest':nearest})
 data={'blocks':blocks,'schoolPoints':schools,'amenityCounts':{k:len(v) for k,v in amen.items()},'distanceOrder':['mrt','school','hawker'],'source':'OneMap Search coordinates joined to uploaded addresses','generatedDate':time.strftime('%Y-%m-%d',time.gmtime()),'method':'Straight-line Euclidean distance in EPSG:3414 (SVY21), not walking distance','coverage':{'matchedBlocks':matched,'totalBlocks':len(blocks),'matchedSchools':len(schools),'totalSchools':len(meta['schools']),'unmatchedSchools':unmatchedSchools,'unmatchedBlocks':unmatched},'projectionValidationMaxErrorMetres':max(errors) if errors else None}
 (ROOT/'dist/accessibility.json').write_text(json.dumps(data,separators=(',',':')))
 print(json.dumps({'coverage':data['coverage'],'projectionValidationMaxErrorMetres':data['projectionValidationMaxErrorMetres'],'amenityCounts':data['amenityCounts']},indent=2))
if __name__=='__main__':main()
