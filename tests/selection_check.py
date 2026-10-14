import asyncio,json,os
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
async def run():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox']);page=await b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(os.environ.get('HDB_PREVIEW_URL','http://127.0.0.1:8000/'),wait_until='networkidle');await page.wait_for_function('!!window.HDBAtlas');await page.wait_for_timeout(700)
  print('INITIAL',await page.evaluate('({types:HDBAtlas.meta.types,count:HDBAtlas.filtered.length})'))
  assert await page.evaluate('HDBAtlas.filtered.length')==242259
  assert await page.evaluate('HDBAtlas.meta.types.includes("1 ROOM")&&HDBAtlas.meta.types.includes("MULTI-GENERATION")&&!HDBAtlas.meta.types.includes("Others")')
  await page.screenshot(path=str(ROOT/'work/review-front.png'))
  for field,values in [('year',['2024','2025']),('type',['4 ROOM','5 ROOM']),('town',['Bedok','Yishun'])]:
   await page.locator('.multi-filter[data-filter="'+field+'"] summary').click()
   for value in values:await page.locator('.multi-filter[data-filter="'+field+'"] label').filter(has_text=value).locator('input').check()
  await page.locator('h1').click();await page.wait_for_timeout(700)
  result=await page.evaluate('({actual:HDBAtlas.filtered.length,expected:HDBAtlas.rows.filter(r=>[2024,2025].includes(2017+Math.floor(r[0]/12))&&["4 ROOM","5 ROOM"].includes(r[12])&&["BEDOK","YISHUN"].includes(HDBAtlas.meta.towns[r[1]])).length,state:HDBAtlas.state})');print('MULTI',result);assert result['actual']==result['expected'] and result['actual']>0
  await page.click('#reset');await page.locator('.multi-filter[data-filter="type"] summary').click();await page.locator('.multi-filter[data-filter="type"] label').filter(has_text='4 ROOM').locator('input').check();await page.locator('h1').click()
  await page.locator('#market').scroll_into_view_if_needed();await page.wait_for_timeout(700);assert '4 ROOM' in await page.locator('#trendExtrema').inner_text();assert 'Others' not in await page.locator('#trendExtrema').inner_text();await page.screenshot(path=str(ROOT/'work/review-trend.png'))
  await page.click('#reset');await page.locator('#lease').scroll_into_view_if_needed();await page.wait_for_timeout(700);print('FIT',await page.locator('#fitSummary').inner_text());assert 'R²' in await page.locator('#fitSummary').inner_text();await page.screenshot(path=str(ROOT/'work/review-property.png'))
  await page.locator('#floors').scroll_into_view_if_needed();await page.wait_for_timeout(700);assert await page.locator('#boxplot .median-annotation').count()==4;await page.screenshot(path=str(ROOT/'work/review-height.png'))
  await page.select_option('#accessYear','2017');print('HISTORICAL',await page.evaluate('HDBAtlas.accessCohort.length'));assert await page.evaluate('HDBAtlas.accessCohort.every(r=>2017+Math.floor(r[0]/12)===2017)')
  await page.select_option('#accessYear','all');assert await page.evaluate('HDBAtlas.accessCohort.length')>200000
  await page.select_option('#accessYear','2025');await page.locator('#ageAccess').scroll_into_view_if_needed();await page.wait_for_timeout(700);assert await page.evaluate('new Set(Array.from(document.querySelectorAll("#ageAccess circle"),n=>n.getAttribute("r"))).size')==1
  await page.check('#sizeBubbles');await page.wait_for_timeout(700);assert await page.evaluate('new Set(Array.from(document.querySelectorAll("#ageAccess circle"),n=>n.getAttribute("r"))).size')>1
  await page.uncheck('#sizeBubbles');await page.wait_for_timeout(700);await page.screenshot(path=str(ROOT/'work/review-access.png'))
  await page.locator('#mix').scroll_into_view_if_needed();await page.wait_for_timeout(700);print('HEATMAP',await page.evaluate('({rows:document.querySelectorAll("#heatmap .heat-label:not(.type-label)").length,height:document.querySelector("#heatmap").clientHeight})'));await page.screenshot(path=str(ROOT/'work/review-matrix.png'))
  await page.set_viewport_size({'width':390,'height':844});await page.goto(os.environ.get('HDB_PREVIEW_URL','http://127.0.0.1:8000/'),wait_until='networkidle');await page.wait_for_function('!!window.HDBAtlas');assert await page.evaluate('document.documentElement.scrollWidth')==390
  print('ERRORS',errors);assert not errors;await b.close()
asyncio.run(run())
