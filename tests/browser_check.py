import asyncio,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
(ROOT/"work").mkdir(exist_ok=True)
from playwright.async_api import async_playwright
async def run():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(os.environ.get('HDB_PREVIEW_URL','http://127.0.0.1:8000/'),wait_until='networkidle')
  await page.wait_for_function('!!window.HDBAtlas',timeout=60000)
  await page.screenshot(path=str(ROOT/'work'/'desktop.png'),full_page=False)
  print('INITIAL',await page.evaluate('({count:HDBAtlas.filtered.length,stats:HDBAtlas.stats(HDBAtlas.filtered),rows:HDBAtlas.rows.length,mapSymbols:document.querySelectorAll("#priceMap circle").length})'))
  await page.select_option('#year','2025',force=True);await page.select_option('#type','3',force=True);await page.select_option('#town','24',force=True)
  print('FILTER',await page.evaluate('({count:HDBAtlas.filtered.length,stats:HDBAtlas.stats(HDBAtlas.filtered),expected:HDBAtlas.rows.filter(r=>2017+Math.floor(r[0]/12)===2025&&r[2]===3&&r[1]===24).length})'))
  await page.click('#reset')
  await page.locator('#lease').scroll_into_view_if_needed();await page.wait_for_timeout(700)
  await page.screenshot(path=str(ROOT/'work'/'property.png'))
  canvas=await page.locator('#scatter').bounding_box();await page.mouse.move(canvas['x']+canvas['width']*.45,canvas['y']+100);await page.mouse.down();await page.mouse.move(canvas['x']+canvas['width']*.75,canvas['y']+100,steps=10);await page.mouse.up();await page.wait_for_timeout(700)
  print('BRUSH',await page.evaluate('({brush:HDBAtlas.state.brush,count:HDBAtlas.filtered.length})'))
  await page.click('#clearBrush');await page.locator('#geography').scroll_into_view_if_needed();await page.wait_for_timeout(700)
  await page.screenshot(path=str(ROOT/'work'/'map.png'))
  await page.click('#theme');await page.wait_for_timeout(400);await page.screenshot(path=str(ROOT/'work'/'dark.png'))
  await page.click('#methodBtn');await page.wait_for_function('document.querySelector("#methods").open');await page.click('#closeMethods')
  await page.click('#present');await page.wait_for_timeout(400);await page.screenshot(path=str(ROOT/'work'/'presentation.png'))
  await page.click('#pNext');await page.click('#pNext');await page.wait_for_timeout(600)
  print('PRESENT',await page.evaluate('({current:document.querySelector(".chapter.current").id,canvasWidth:document.querySelector("#scatter").width})'))
  await page.click('#pExit');await page.click('#theme')
  await page.set_viewport_size({'width':390,'height':844});await page.goto(os.environ.get('HDB_PREVIEW_URL','http://127.0.0.1:8000/'),wait_until='networkidle');await page.wait_for_function('!!window.HDBAtlas');await page.wait_for_timeout(700);await page.screenshot(path=str(ROOT/'work'/'mobile.png'))
  print('MOBILE',await page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})'))
  print('ERRORS',json.dumps(errors));await browser.close()
asyncio.run(run())
