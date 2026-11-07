import io,json
import pytest
from PIL import Image
from medillustrate import core
from medillustrate.workspace import Store,Conflict,new_project,get_frame,apply_operations,media_normalize,render_frame

@pytest.fixture
def st(tmp_path):
 s=Store(tmp_path/'s.db');p=s.create();return s,p['project']['id']

def test_versioned_atomic_edit_and_restore(st):
 s,p=st;r=s.edit(p,1,[{'op':'title','value':'Renal anatomy'}]);assert r['version']==2
 with pytest.raises(Conflict):s.edit(p,1,[{'op':'title','value':'Wrong'}])
 with pytest.raises(core.IllustrationError):s.edit(p,2,[{'op':'title','value':'Lost'},{'op':'unsupported'}])
 assert get_frame(s.get(p)['project'])['document']['title']=='Renal anatomy'
 r=s.restore(p,2,1);assert r['version']==3 and get_frame(r['project'])['document']['title']=='Kidney'

def test_proposal_is_deterministic_and_does_not_apply(st):
 s,p=st;q=s.propose(p,1,{'operations':[{'op':'add_frame','template_id':'atlas-kidney-surface'}]})
 candidate=apply_operations(s.get(p)['project'],q['operations']);assert len(s.get(p)['project']['frames'])==1
 r=s.decide(p,q['id'],True);assert r['project']==candidate
 with pytest.raises(Conflict):s.decide(p,q['id'],True)

def test_stale_proposal_preserves_manual_work(st):
 s,p=st;q=s.propose(p,1,{'operations':[{'op':'title','value':'Agent title'}]})
 s.edit(p,1,[{'op':'title','value':'Manual title'}])
 with pytest.raises(Conflict):s.decide(p,q['id'],True)
 assert get_frame(s.get(p)['project'])['document']['title']=='Manual title'

def test_rejection_leaves_document_unchanged(st):
 s,p=st;q=s.propose(p,1,{'operations':[{'op':'detail','value':.4}]});s.decide(p,q['id'],False);assert s.get(p)['version']==1

@pytest.mark.parametrize('raw',[b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',b'<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.com/x"/></svg>'])
def test_active_svg_rejected(raw):
 with pytest.raises(core.IllustrationError):media_normalize('x.svg',raw)

def test_reference_is_scoped_and_provenance_separate(st):
 s,p=st;r=s.add_reference(p,1,title='Own note',name='note.txt',raw=b'anatomical reference',licence='Own work');mid=r['project']['references'][0]['media_id']
 assert s.get_media(p,mid)['metadata']['extracted_text']=='anatomical reference'
 other=s.create()['project']['id']
 with pytest.raises(core.IllustrationError):s.get_media(other,mid)
 assert 'medical_certification' not in r['project'];assert s.control(p)['medical_certification'] is False

def test_target_correction_is_explicit(st):
 s,p=st
 with pytest.raises(core.IllustrationError):s.edit(p,1,[{'op':'label','landmark':'cortex','values':{'target':[.2,.3]}}])
 r=s.edit(p,1,[{'op':'label','landmark':'cortex','values':{'target':[.2,.3],'target_note':'Corrected to cortical tissue after reference comparison'}}]);assert 'plate-label-cortex' in render_frame(get_frame(r['project']))

def test_candidate_requires_confirmation_and_matching_canvas(st):
 s,p=st;im=Image.new('RGB',(400,500),'white');o=io.BytesIO();im.save(o,format='PNG');mid=s.put_candidate(p,'x.png',o.getvalue(),{})
 f=get_frame(s.get(p)['project'])
 with pytest.raises(core.IllustrationError):s.adopt_candidate(p,1,f['id'],mid,confirm_landmarks=False)
 r=s.adopt_candidate(p,1,f['id'],mid,confirm_landmarks=True);assert 'data:image/png;base64' in render_frame(get_frame(r['project']),lambda m:s.get_media(p,m))
