import asyncio,os
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];(ROOT/'work').mkdir(exist_ok=True)
async def run():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox']);page=await b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(os.environ.get('HDB_PREVIEW_URL','http://127.0.0.1:8000/'),wait_until='networkidle');await page.wait_for_function('!!window.HDBAtlas');await page.wait_for_timeout(700)
  assert await page.locator('#play').inner_text()=='▶ Play';assert await page.locator('.comparison-actions').count()==0;assert await page.locator('#startOver').count()==0
  assert 'Middle recorded resale price' in await page.locator('.kpi-grid').inner_text();assert 'Middle resale price per m²' in await page.locator('.kpi-grid').inner_text();assert 'Middle remaining lease in years' in await page.locator('.kpi-grid').inner_text()
  assert not await page.locator('#accessCoverage').is_visible();assert not await page.locator('#accessScope').is_visible();assert not await page.locator('#accessAdjusted').is_visible();assert not await page.locator('#distanceSelection').is_visible()
  await page.locator('#models').scroll_into_view_if_needed();await page.wait_for_timeout(700);assert await page.locator('.model-card h3').inner_text()=='Flat Model'
  displayed=await page.evaluate('Array.from(document.querySelectorAll("#models g[data-key]"),g=>({index:+g.dataset.key,value:g.querySelectorAll("text")[1].textContent}))');expected=await page.evaluate('Array.from(new Set(HDBAtlas.filtered.map(r=>r[7]))).map(m=>{const rs=HDBAtlas.filtered.filter(r=>r[7]===m);return {index:m,n:rs.length,v:HDBAtlas.stats(rs).price}}).filter(d=>d.n>=5).sort((a,b)=>b.v-a.v).slice(0,10)');assert [d['index'] for d in displayed]==[d['index'] for d in expected];assert all(int(a['value'].replace(',',''))==round(e['v']) for a,e in zip(displayed,expected));print('MODEL_TOTAL_PRICE',displayed)
  await page.screenshot(path=str(ROOT/'work/copy-models.png'))
  await page.locator('#accessBox').scroll_into_view_if_needed();assert await page.locator('#accessTitle').inner_text()=='Distance to The Nearest MRT Exit vs. Price';assert 'Resale Price (SGD / m²)' in await page.locator('#accessBox').text_content();await page.screenshot(path=str(ROOT/'work/copy-distance.png'))
  assert 'Median Remaining Lease (years)' in await page.locator('#ageAccess').text_content();assert 'in records' in await page.locator('#blockMapSubtitle').inner_text();assert 'selected MRT' not in await page.locator('#blockMapSubtitle').inner_text()
  await page.click('#methodBtn');text=await page.locator('#methods').inner_text();assert 'DATA TRANSPARENCY' in text;assert 'Coverage and Match' in text;assert 'Values beyond the whiskers are outliers' in text;assert '9740' in text.replace(',','');assert 'SHA-256' not in text;assert 'Source files' in text;print('METHODOLOGY_OK');await page.screenshot(path=str(ROOT/'work/copy-methodology.png'));await page.click('#closeMethods')
  await page.set_viewport_size({'width':390,'height':844});await page.goto(os.environ.get('HDB_PREVIEW_URL','http://127.0.0.1:8000/'),wait_until='networkidle');await page.wait_for_function('!!window.HDBAtlas');assert await page.evaluate('document.documentElement.scrollWidth')==390
  print('ERRORS',errors);assert not errors;await b.close()
asyncio.run(run())
