import io,json,zipfile
import pytest
from PIL import Image
from pypdf import PdfReader
from pptx import Presentation
from medillustrate import exports,core
from medillustrate.workspace import Store,get_frame

@pytest.fixture
def st(tmp_path):
 s=Store(tmp_path/'s.db');p=s.create()['project']['id'];return s,p

@pytest.mark.parametrize('fmt',['svg','png','pdf','pptx'])
def test_exports_open(st,fmt):
 s,p=st;b=exports.frame_bytes(s,p,get_frame(s.get(p)['project']),fmt,width_px=600)
 if fmt=='svg':assert '<svg' in b.decode()
 if fmt=='png':assert Image.open(io.BytesIO(b)).width==600
 if fmt=='pdf':assert len(PdfReader(io.BytesIO(b)).pages)==1
 if fmt=='pptx':
  r=Presentation(io.BytesIO(b));texts=[x.text for x in r.slides[0].shapes if x.has_text_frame];assert 'Renal cortex' in texts and len(texts)>10

def test_bundle_round_trip_media_and_no_control(st):
 s,p=st;s.add_reference(p,1,title='Anatomy note',name='a.txt',raw=b'Own reference')
 b=exports.bundle(s,p);z=zipfile.ZipFile(io.BytesIO(b));assert not any('control' in n for n in z.namelist())
 r=exports.import_bundle(s,b);assert r['project']['id']!=p
 m=r['project']['references'][0]['media_id'];assert s.get_media(r['project']['id'],m)['data']==b'Own reference'

def test_bundle_traversal_rejected(st):
 s,p=st;o=io.BytesIO()
 with zipfile.ZipFile(o,'w') as z:z.writestr('../evil','x')
 with pytest.raises(core.IllustrationError):exports.import_bundle(s,o.getvalue())
