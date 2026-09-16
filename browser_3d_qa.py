import os,json
from playwright.sync_api import sync_playwright
# Configure PLAYWRIGHT_BROWSERS_PATH externally when needed.
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader']);page=b.new_page(viewport={'width':1280,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8901');page.locator('#new').click();page.locator('#game').wait_for();v=page.locator('#viewport');page.wait_for_function("document.querySelector('#viewport').dataset.z !== undefined")
 v.focus();page.keyboard.down('KeyA');page.wait_for_timeout(1000);page.keyboard.up('KeyA');page.keyboard.down('KeyW');page.wait_for_timeout(650);page.keyboard.up('KeyW');page.wait_for_function("document.querySelector('#viewport').dataset.near === 'inez'");page.keyboard.press('KeyE');assert page.locator('#question').evaluate('(e)=>e===document.activeElement');assert 'Inez' in page.locator('#status').inner_text()
 v.focus();page.keyboard.down('KeyA');page.wait_for_timeout(950);page.keyboard.up('KeyA');page.wait_for_function("document.querySelector('#viewport').dataset.near === 'archive'");page.keyboard.press('KeyE');page.locator('#count').get_by_text('1/3',exact=True).wait_for();assert 'hidden reel' in page.locator('#clues').inner_text().lower()
 page.screenshot(path='.runtime/threejs-desktop.png',full_page=True);page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(200);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');assert not errors,errors
 print(json.dumps({'passed':True,'checks':['WebGL scene renders','keyboard walking','proximity selects Inez','E selects dialogue and focuses question','walk to archive','E discovers authoritative clue','mobile width','no JS errors']}));b.close()
