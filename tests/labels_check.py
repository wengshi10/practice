import asyncio,os
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];(ROOT/'work').mkdir(exist_ok=True)
async def run():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox']);page=await b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(os.environ.get('HDB_PREVIEW_URL','http://127.0.0.1:8000/'),wait_until='networkidle');await page.wait_for_function('!!window.HDBAtlas');await page.wait_for_timeout(700)
  types=await page.evaluate('HDBAtlas.meta.types');assert '1 ROOM' in types and 'MULTI-GENERATION' in types and 'Others' not in types;print('ORIGINAL TYPES',types)
  await page.locator('#market').scroll_into_view_if_needed();await page.wait_for_timeout(600)
  assert await page.locator('#market h3').inner_text()=='Monthly Median Resale Price Trend';assert not await page.locator('#trendSubtitle').is_visible();assert '$' not in ''.join(await page.locator('#trend .grid+text').all_text_contents());assert 'Monthly Median Sale Prices ($)' in await page.locator('#trend').text_content();assert '$' in await page.locator('#trendExtrema').inner_text()
  print('EXTREMA COLOURS',await page.evaluate('Array.from(document.querySelectorAll("#trendExtrema span[class]"),n=>getComputedStyle(n).color)'));await page.screenshot(path=str(ROOT/'work/latest-trend.png'))
  await page.click('[data-value="sqm"]');assert await page.locator('#market h3').inner_text()=='Monthly Median Resale Price Per Meter Square Trend';assert 'Monthly Median Transaction-level Price (SGD/m²)' in await page.locator('#trend').text_content();assert '$' not in ''.join(await page.locator('#trend .grid+text').all_text_contents())
  await page.click('[data-value="growth"]');assert 'Change in Percentage' in await page.locator('#trend').text_content();assert await page.locator('.lowest-summary').count()==1
  await page.locator('.multi-filter[data-filter="town"] summary').click();await page.locator('.multi-filter[data-filter="town"] label').filter(has_text='Bedok').locator('input').check();await page.locator('h1').click();await page.wait_for_timeout(700)
  greys=await page.locator('#priceMap circle[fill="#d8d8d8"]').count();assert greys>15;print('GREY DESELECTED TOWNS',greys)
  await page.click('#reset');await page.locator('#floors').scroll_into_view_if_needed();await page.wait_for_timeout(700);assert await page.locator('#floors .chart-heading h3').inner_text()=='Price Distributions by Storey Band';assert 'Storey-Range Midpoint Band' in await page.locator('#boxplot').text_content();assert 'Price Per m² (SGD / m²)' in await page.locator('#boxplot').text_content()
  assert not await page.locator('#accessReading').is_visible();assert not await page.locator('#ageAccessReading').is_visible()
  await page.locator('#mix').scroll_into_view_if_needed();await page.wait_for_timeout(700);await page.screenshot(path=str(ROOT/'work/latest-matrix.png'));assert await page.locator('#heatmap .type-label').filter(has_text='MULTI-GENERATION').count()==2
  await page.click('#present');await page.set_viewport_size({'width':1280,'height':720});
  for _ in range(4):await page.click('#pNext')
  await page.wait_for_timeout(700);await page.screenshot(path=str(ROOT/'work/latest-matrix720.png'));assert await page.evaluate('document.querySelector("#heatmap").getBoundingClientRect().bottom<document.querySelector("#presentationBar").getBoundingClientRect().top')
  print('ERRORS',errors);assert not errors;await b.close()
asyncio.run(run())
