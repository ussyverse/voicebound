"""Browser UI QA; no fake model/provider output, no microphone upload."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
# Set PLAYWRIGHT_BROWSERS_PATH externally if Chromium uses a custom cache.
with sync_playwright() as p:
 b=p.chromium.launch(headless=True);page=b.new_page(viewport={'width':1360,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8901');page.locator('#status').get_by_text('Start a new case.',exact=False).wait_for();page.locator('#new').click();page.locator('#game').wait_for()
 page.get_by_role('button',name='Broadcast console',exact=True).click();page.locator('#count').get_by_text('1/3',exact=True).wait_for()
 page.get_by_role('button',name='Engineering bench',exact=True).click();page.locator('#count').get_by_text('2/3',exact=True).wait_for()
 page.get_by_role('button',name='Tape archive',exact=True).click();page.locator('#count').get_by_text('3/3',exact=True).wait_for()
 page.reload();page.locator('#count').get_by_text('3/3',exact=True).wait_for();assert page.locator('.clue').count()==3
 page.screenshot(path=str(root/'.runtime/desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(root/'.runtime/mobile.png'),full_page=True)
 assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
 page.locator('#accused').select_option('inez');page.on('dialog',lambda d:d.accept());page.locator('#accuse').click();page.locator('#status').get_by_text('Case solved.',exact=False).wait_for()
 assert not errors,errors
 report={'browser':'Chromium','checks':['new game','search all clues','reload persistence','mobile no horizontal overflow','correct accusation','no JavaScript exceptions'],'provider_calls':'none in browser QA (see separate live smoke)','passed':True}
 (root/'.runtime/browser-qa.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));b.close()
