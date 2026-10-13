"""Local browser verification for the requested refinement and accessibility charts."""
import asyncio,json,os
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
async def run():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto('http://127.0.0.1:8000/',wait_until='networkidle');await page.wait_for_function('!!window.HDBAtlas');await page.wait_for_timeout(700)
  assert await page.locator('.masthead .brand').inner_text() == 'HDB Singapore\nSINGAPORE · PROPERTY INTELLIGENCE'
  assert await page.locator('.filter-title').count()==0
  assert await page.locator('[data-value="index"]').count()==0
  await page.locator('#market').scroll_into_view_if_needed();await page.wait_for_timeout(700)
  await page.screenshot(path=str(ROOT/'work/refined-trend.png'))
  ticks=await page.locator('#trend .grid+text').all_text_contents();print('TREND_TICKS',ticks)
  await page.click('[data-value="growth"]');await page.wait_for_timeout(700)
  bars=await page.evaluate('Array.from(document.querySelectorAll("#trend g[data-key^=growth]"),g=>({key:g.dataset.key,label:g.querySelector("text").textContent,dash:g.querySelector("rect").getAttribute("stroke-dasharray")}))')
  print('GROWTH',bars);assert len(bars)==10;assert bars[-1]['dash']=='5 4'
  await page.screenshot(path=str(ROOT/'work/refined-growth.png'))
  await page.click('[data-value="price"]');await page.select_option('#year','2017');await page.wait_for_timeout(700)
  before=await page.evaluate('({path:document.querySelector("#trend g[data-key=none]")?.outerHTML||document.querySelector("#trend path").getAttribute("d"),width:document.querySelector("#trend-reveal rect").getAttribute("width")})')
  await page.click('#play');await page.wait_for_timeout(2200)
  after=await page.evaluate('({path:document.querySelector("#trend path").getAttribute("d"),width:document.querySelector("#trend-reveal rect").getAttribute("width"),year:HDBAtlas.state.year})')
  assert before['path']==after['path'];assert float(after['width'])>float(before['width']);print('PLAYBACK',{k:v for k,v in after.items() if k!='path'})
  await page.click('#play');await page.click('#reset');await page.locator('#floors').scroll_into_view_if_needed();await page.wait_for_timeout(700)
  print('TUKEY',await page.evaluate('HDBAtlas.tukey([1,2,3,4,5,6,7,8,9,100])'));assert await page.evaluate('HDBAtlas.tukey([1,2,3,4,5,6,7,8,9,100]).high')==9
  await page.screenshot(path=str(ROOT/'work/refined-floors.png'))
  await page.locator('#amenityMap').scroll_into_view_if_needed();await page.wait_for_timeout(700)
  assert await page.locator('#amenityMap circle[fill="#7b45a3"]').count()==179
  print('SCHOOLS',await page.evaluate('HDBAtlas.geoData.schoolPoints.length'));assert await page.evaluate('HDBAtlas.geoData.schoolPoints.length')==179
  await page.screenshot(path=str(ROOT/'work/refined-schools.png'))
  n=await page.evaluate('HDBAtlas.accessCohort.length');counts={}
  for amenity in ['mrt','school','hawker']:
   await page.select_option('#accessAmenity',amenity);await page.wait_for_timeout(700);counts[amenity]=await page.evaluate('HDBAtlas.accessCohort.length');assert counts[amenity]==n
  print('SAME_COHORT',counts)
  await page.select_option('#accessAmenity','mrt');await page.locator('#accessBox').scroll_into_view_if_needed();await page.wait_for_timeout(700);await page.screenshot(path=str(ROOT/'work/refined-accessibility.png'))
  await page.locator('#accessBox g[data-key="distance-0"]').click(force=True);assert await page.evaluate('HDBAtlas.state.distanceBand')==0
  await page.click('#clearDistance');await page.locator('#ageAccess').scroll_into_view_if_needed();await page.wait_for_timeout(700);await page.screenshot(path=str(ROOT/'work/refined-age-access.png'))
  await page.click('#present');await page.set_viewport_size({'width':1280,'height':720});
  for _ in range(5):await page.click('#pNext')
  await page.click('#amenityViews [data-view="distance"]');await page.wait_for_timeout(700);await page.screenshot(path=str(ROOT/'work/refined-access-720.png'))
  await page.click('#amenityViews [data-view="age"]');await page.wait_for_timeout(700);await page.screenshot(path=str(ROOT/'work/refined-age-720.png'))
  await page.click('#pExit');await page.set_viewport_size({'width':390,'height':844});await page.goto('http://127.0.0.1:8000/',wait_until='networkidle');await page.wait_for_function('!!window.HDBAtlas');await page.wait_for_timeout(700)
  assert await page.evaluate('document.documentElement.scrollWidth')==390
  print('ERRORS',errors);assert not errors;await browser.close()
asyncio.run(run())
