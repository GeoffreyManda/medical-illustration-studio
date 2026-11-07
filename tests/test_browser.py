"""Chromium integration tests with an in-process ASGI bridge.

No remote browser navigation is needed. The full server, validation, persistence
and UI code run; a test-only fetch bridge carries browser requests to TestClient.
The standalone test uses a test-only localStorage adapter on an opaque origin.
"""
from pathlib import Path
import base64,shutil
import pytest
from fastapi.testclient import TestClient
from medillustrate.server import make_app
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def browser():
    from playwright.sync_api import sync_playwright
    exe=shutil.which('chromium') or shutil.which('chromium-browser')
    with sync_playwright() as p:
        try:b=p.chromium.launch(executable_path=exe,headless=True,args=['--no-sandbox'])
        except Exception as exc:pytest.skip('Install a Playwright Chromium browser: '+str(exc)[:100])
        yield b;b.close()


def page_setup(browser,html):
    page=browser.new_page(viewport={'width':1600,'height':1060});errors=[]
    page.set_default_timeout(5000);page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html,wait_until='load');page.wait_for_selector('#paper svg');return page,errors


def exercise(page):
    page.click('[data-prompt="labels 19"]');page.wait_for_selector('#accept-proposal')
    assert page.locator('#preview-banner').is_visible()
    page.click('#compare-proposal');assert page.locator('.compare-grid svg').count()==2;page.click('#modal-close')
    page.click('#accept-proposal');page.wait_for_selector('#accept-proposal',state='detached')
    assert page.locator('#revision-count').inner_text()=='2'
    page.click('[data-right="inspector"]');page.locator('#figure-title-input').fill('Renal anatomy study');page.click('#save-title')
    page.wait_for_function("document.querySelector('#revision-count').textContent==='3'")
    page.click('[data-left="library"]');page.fill('#asset-search','kidney');assert page.locator('[data-asset]').count()>=2
    page.click('[data-asset="atlas-kidney-section"]');assert page.locator('#download-asset').is_visible();page.click('#modal-close')
    page.click('[data-left="artboards"]');page.click('#add-board');page.click('[data-template="atlas-peripheral-nerve"]');page.wait_for_function("document.querySelectorAll('[data-frame]').length===2")
    page.click('[data-right="paint"]');assert page.locator('#pixel-editor-open').is_visible()
    page.click('#history-open');page.wait_for_selector('.history-item');assert page.locator('.history-item').count()==4;page.click('#modal-close')
    page.click('#export-open');assert page.locator('[data-export="svg"]').is_enabled();page.click('#modal-close')


def test_standalone_ui(browser):
    html=(ROOT/'studio-preview.html').read_text()
    storage="<script>window.testStorage={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>window.testStorage[k]||null,setItem:(k,v)=>window.testStorage[k]=v,removeItem:k=>delete window.testStorage[k]}});</script>"
    page,errors=page_setup(browser,html.replace('<head>','<head>'+storage));exercise(page)
    assert not errors;assert page.evaluate("Object.keys(window.testStorage).length")>0;page.close()


def test_server_ui_with_real_backend(browser,tmp_path):
    app=make_app(tmp_path/'browser.db')
    with TestClient(app) as client:
        page=browser.new_page(viewport={'width':1600,'height':1060});errors=[];page.set_default_timeout(5000);page.on('pageerror',lambda e:errors.append(str(e)))
        def bridge(url,options):
            r=client.request(options.get('method','GET'),url,headers=options.get('headers',{}),content=options.get('body'))
            return {'status':r.status_code,'headers':dict(r.headers),'body':base64.b64encode(r.content).decode()}
        page.expose_function('__asgi',bridge)
        script="""<script>window.fetch=async(url,options={})=>{const r=await window.__asgi(String(url),options);return new Response(Uint8Array.from(atob(r.body),c=>c.charCodeAt(0)),{status:r.status,headers:r.headers});};</script>"""
        static=ROOT/'medillustrate'/'static';html=(static/'studio.html').read_text().replace('<head>','<head>'+script).replace('<link rel="stylesheet" href="/static/studio.css">','<style>'+(static/'studio.css').read_text()+'</style>').replace('<script src="/static/studio.js"></script>','<script>'+(static/'studio.js').read_text()+'</script>')
        page.set_content(html,wait_until='load');page.wait_for_selector('#paper svg');exercise(page)
        assert not errors;assert app.state.store.list_projects()[0]['version']==4;page.close()
