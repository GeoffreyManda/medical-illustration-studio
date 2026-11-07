import io,json
import numpy as np
import pytest,httpx
from PIL import Image
from medillustrate import providers,core,atelier
from medillustrate.workspace import Store,new_project,get_frame

def png(size=(400,500),value=(1,2,3)):
 o=io.BytesIO();Image.new('RGB',size,value).save(o,format='PNG');return o.getvalue()

@pytest.mark.parametrize('asset',list(atelier.library()))
def test_prompt_budget_and_no_labels(asset):
 text=providers.paint_prompt(get_frame(new_project(template_id=asset)),'Refine tissue surfaces')
 assert len(text)<=2000 and 'No lettering' in text

def test_mask_keeps_every_outside_pixel():
 source=png();out=providers.preserve_outside_region(source,png(value=(200,30,90)),[.2,.2,.3,.3])
 a=np.array(Image.open(io.BytesIO(out)));assert np.all(a[:80,:,:3]==[1,2,3]);assert np.all(a[130:180,100:150,:3]==[200,30,90])

@pytest.mark.parametrize('region',[[0,0,0,1],[-1,0,1,1],[.9,0,.2,1],[float('nan'),0,.2,1]])
def test_bad_mask_rejected(region):
 with pytest.raises(core.IllustrationError):providers.mask_png((100,100),region)

def test_figurelabs_adapter_contract():
 calls=[]
 def handler(req):
  calls.append(req);assert req.headers['Authorization']=='Bearer test-key'
  return httpx.Response(200,json={'task_id':'task_123','status':'pending'} if req.method=='POST' else {'status':'processing'})
 with httpx.Client(transport=httpx.MockTransport(handler)) as client:
  api=providers.FigureLabs(client,key='test-key');assert api.submit({'mode':'generations','prompt':'test'})['task_id']=='task_123';assert api.status('task_123')['status']=='processing'
 assert calls[0].url.path=='/v1/images/generations' and calls[1].url.path=='/v1/tasks/task_123'

def test_no_billable_retry_after_ambiguous_failure(tmp_path):
 s=Store(tmp_path/'s.db');p=s.create()['project']['id']
 class Fake:
  calls=0
  def submit(self,payload):self.calls+=1;raise TimeoutError('ambiguous')
 api=Fake()
 with pytest.raises(core.IllustrationError):providers.submit_paint(s,p,1,'Refine surface',consent=True,provider=api)
 assert api.calls==1 and s.jobs(p)[0]['status']=='submission_unknown';assert s.get(p)['version']==1

def test_completed_candidate_is_not_auto_adopted(tmp_path):
 s=Store(tmp_path/'s.db');p=s.create()['project']['id']
 class Fake:
  def submit(self,payload):assert payload['imageUrl'].startswith('data:image/png');return {'task_id':'x123','status':'pending'}
  def status(self,tid):return {'status':'succeeded','output_url':'https://storage.example/file'}
  def download(self,url):return png()
 api=Fake();j=providers.submit_paint(s,p,1,'Refine surface',consent=True,provider=api);j=providers.poll_paint(s,p,j['id'],provider=api)
 assert j['candidate_media_id'] and not get_frame(s.get(p)['project'])['artwork_media_id']
