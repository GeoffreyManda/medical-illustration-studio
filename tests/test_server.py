import base64,json
import pytest
from fastapi.testclient import TestClient
from medillustrate.server import make_app

@pytest.fixture
def cli(tmp_path):
 with TestClient(make_app(tmp_path/'s.db')) as c:
  token=c.get('/api/session').json()['token'];c.headers['x-studio-token']=token;yield c

def test_bootstrap_and_no_credentials(cli):
 s=cli.get('/api/session').json();assert 'FIGURELABS_API_KEY' not in json.dumps(s)
 b=cli.get('/api/bootstrap').json();assert len(b['assets'])==81 and len(b['templates'])==12

def test_write_auth_and_origin(cli):
 assert cli.post('/api/projects',json={},headers={'x-studio-token':''}).status_code==403
 assert cli.get('/api/projects',headers={'Origin':'https://evil.test'}).status_code==403
 assert cli.post('/api/projects',json={'title':'My figure'}).status_code==200

def test_api_proposal_render_accept_and_stale_edit(cli):
 p=cli.get('/api/projects').json()[0]['id'];q=cli.post(f'/api/projects/{p}/agent',json={'base_version':1,'prompt':'labels 19','provider':'local'}).json()
 r=cli.get(f'/api/projects/{p}/render',params={'proposal_id':q['id']});assert r.status_code==200 and 'plate-label-cortex' in r.text
 r=cli.post(f'/api/projects/{p}/proposals/{q["id"]}/decide',json={'accept':True});assert r.json()['version']==2
 assert cli.post(f'/api/projects/{p}/edit',json={'base_version':1,'operations':[{'op':'title','value':'wrong'}]}).status_code==409

def test_reference_and_portable_import(cli):
 p=cli.get('/api/projects').json()[0]['id'];r=cli.post(f'/api/projects/{p}/references',json={'base_version':1,'title':'Note','name':'note.txt','data':base64.b64encode(b'hello anatomy').decode()});assert r.status_code==200
 rid=r.json()['project']['references'][0]['id'];assert 'hello anatomy' in cli.get(f'/api/projects/{p}/references/{rid}/text').json()['text']
 b=cli.get(f'/api/projects/{p}/export/zip').content;r=cli.post('/api/import-bundle',json={'data':base64.b64encode(b).decode()});assert r.status_code==200 and r.json()['project']['id']!=p

def test_malformed_request_is_rejected(cli):
 p=cli.get('/api/projects').json()[0]['id'];assert cli.post(f'/api/projects/{p}/edit',json={}).status_code==400


def test_upstream_editors_are_local_and_csp_is_scoped(cli):
 from medillustrate import graphics
 if not all(v['web'] for v in graphics.status().values()):pytest.skip('Release web engines not installed')
 for engine in ('photo','vector'):
  r=cli.get(f'/engines/{engine}/index.html')
  assert r.status_code==200 and 'wasm-unsafe-eval' in r.headers['content-security-policy']
 assert 'wasm-unsafe-eval' not in cli.get('/').headers['content-security-policy']
 # Released PhotoCraft glue resolves its shared snippet relative to app/.
 a=cli.get('/engines/photo/app/snippets/eframe-d31a8450ea12dfc1/inline0.js')
 b=cli.get('/engines/photo/snippets/eframe-d31a8450ea12dfc1/inline0.js')
 assert a.status_code==200 and a.content==b.content
 assert cli.get('/engines/vector/%2e%2e/%2e%2e/README.md').status_code==404
