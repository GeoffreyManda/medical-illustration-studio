import pytest
from medillustrate import atelier,core
from medillustrate.workspace import new_project,get_frame,validate_project,library,render_frame

@pytest.mark.parametrize('asset',list(atelier.library()))
@pytest.mark.parametrize('stage',['colour','values','contours'])
def test_atlas_render(asset,stage):
 p=new_project(template_id=asset);validate_project(p);f=get_frame(p);f['stage']=stage
 s=render_frame(f);assert '<svg' in s and 'plate-label-' in s;core.secure_svg(s)

def test_external_view_does_not_expose_internal_landmarks():
 assert 'cortex' not in library()['atlas-kidney-surface']['landmarks']

def test_target_correction_requires_note():
 f=get_frame(new_project());f['document']['labels'][0]['target']=[.1,.1]
 assert atelier.validate_plate(f['document'])
