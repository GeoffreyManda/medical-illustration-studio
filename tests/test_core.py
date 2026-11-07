"""Executable checks. Synthetic review identities below are test fixtures, not approvals."""
from __future__ import annotations
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import json
import math
import subprocess
import sys
import xml.etree.ElementTree as ET
import pytest
from PIL import Image
from medillustrate import core

ROOT=Path(__file__).resolve().parents[1]
LIB=core.assets()
SCENES=sorted((ROOT/'examples').glob('*.scene.json'))

def errors(s,**kwargs):return [x for x in core.validate(s,LIB,**kwargs) if x.severity=='error']
def specimen():return core.load_json(ROOT/'examples/cell-signalling.scene.json')
def simple():
 s=core.make_scene('test-figure','cell-interior')
 s['description']='A generic cell boundary used only as a software test.'
 s['nodes']=[{'id':'cell','asset':'cell-outline','box':[300,200,400,400]}]
 return s

def approved_fixture(s,lib=LIB):
 r=core.control_record(s,lib)
 r['approvals']=[{'role':role,'name':f'SYNTHETIC TEST {role}','reviewer_id':f'fixture-{role}','qualification':'Test fixture only, not a real medical qualification','date':'2026-10-05','approved':True,'statement':'Automated test fixture. Not an actual review or approval.'} for role in ['scientific','visual']]
 return r

@pytest.mark.parametrize('id',sorted(LIB))
def test_asset_metadata_and_passive_svg(id):
 a=LIB[id]
 assert not core.asset_issues(a)
 assert a['license']=='CC0-1.0'
 assert a['review_status']=='schematic_unreviewed'
 assert a['limitations'] and a['reference_ids']
 assert len(a['landmarks'])>=5

@pytest.mark.parametrize('id',sorted(LIB))
def test_every_asset_renders_nonempty(id):
 a=LIB[id];data=core.export_svg(a['svg'],'png',width_px=180)
 im=Image.open(BytesIO(data));assert im.width==180 and im.height>0
 assert im.convert('RGBA').getbbox() is not None

@pytest.mark.parametrize('path',SCENES,ids=lambda p:p.stem)
def test_examples_are_reproducible_and_nonempty(path):
 s=core.load_json(path)
 assert not errors(s)
 a=core.render(s,LIB);b=core.render(deepcopy(s),LIB)
 assert a==b
 assert a==(path.with_suffix('').with_suffix('.svg')).read_text()
 root=ET.fromstring(a)
 assert root.tag.endswith('svg')
 assert 'figure-title' in a and 'figure-description' in a
 assert s['nodes']
 png=core.export_svg(a,'png',width_px=600)
 assert Image.open(BytesIO(png)).size==(600,400)
 assert core.export_svg(a,'pdf').startswith(b'%PDF')

@pytest.mark.parametrize('layout',core.resource('layouts.json')['layouts'],ids=lambda x:x['id'])
def test_all_layout_slots_execute(layout):
 s=core.make_scene('layout-check',layout['id'])
 s['nodes']=[{'id':f'node{i}','asset':'protein','slot':slot} for i,slot in enumerate(layout['slots'])]
 assert not errors(s)
 r=core.resolve_scene(s)
 assert all('box' in n and 'slot' not in n for n in r['nodes'])
 assert '<svg' in core.render(s,LIB)

@pytest.mark.parametrize('fragment',[
 '<script>alert(1)</script>', '<foreignObject/>', '<image href="https://example.test/a.png"/>',
 '<use href="#a"/>', '<filter/>', '<style>path{fill:red}</style>',
 '<path d="M0 0" onclick="alert(1)"/>', '<path d="M0 0" fill="url(https://example.test/x)"/>',
 '<path d="M0 0" style="fill:var(--x)"/>', '<path d="M0 0" fill="url(#missing)"/>',
 '<path d="M0 0" style="background:red"/>', '<g id="a"/><g id="a"/>',
 '<rect width="1e999" height="5"/>', '<path d="M1e999 0 L0 5"/>',
 '<g transform="translate(1e999 0)"/>',
])
def test_svg_attack_and_unsupported_features_rejected(fragment):
 svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'+fragment+'</svg>'
 with pytest.raises(core.IllustrationError):core.secure_svg(svg)

def test_xml_entities_rejected():
 with pytest.raises(core.IllustrationError):
  core.secure_svg('<!DOCTYPE svg [<!ENTITY x "evil">]><svg viewBox="0 0 1 1"><text>&x;</text></svg>')

def test_external_namespace_rejected():
 with pytest.raises(core.IllustrationError):core.secure_svg('<svg xmlns="http://example.test/fake" viewBox="0 0 1 1"/>')

def test_no_viewbox_rejected():
 with pytest.raises(core.IllustrationError):core.secure_svg('<svg xmlns="http://www.w3.org/2000/svg"/>')

def test_nonfinite_json(tmp_path):
 p=tmp_path/'bad.json';p.write_text('{"x":NaN}')
 with pytest.raises(core.IllustrationError):core.load_json(p)
 s=simple();s['nodes'][0]['box'][0]=float('inf')
 assert errors(s)[0].code=='FMT-04'

def test_unknown_property_is_not_silently_ignored():
 s=simple();s['unimplemented_feature']=True
 assert errors(s)

def test_missing_asset():
 s=simple();s['nodes'][0]['asset']='nonexistent'
 assert any(e.code=='FMT-03' for e in errors(s))

def test_duplicate_ids():
 s=simple();s['nodes'].append(deepcopy(s['nodes'][0]))
 assert any(e.code=='FMT-02' for e in errors(s))

def test_unresolved_node_and_landmark():
 s=specimen();s['edges'][0]['target']['node']='missing'
 assert any(e.code=='FMT-03' for e in errors(s))
 s=specimen();s['edges'][0]['target']['landmark']='invented-site'
 assert any(e.code=='GEO-03' for e in errors(s))

def test_established_claim_needs_real_reference_type():
 s=specimen();s['claims'][0]['status']='established'
 assert any(e.code=='SEM-02' for e in errors(s))
 s['sources']=[{'id':'fake','title':'Invented','url':'urn:example:fake','kind':'illustrative'}]
 s['claims'][0]['sources']=['fake']
 assert any(e.code=='SEM-02' for e in errors(s))

def test_biological_edge_requires_claim():
 s=specimen();del s['edges'][0]['claim']
 assert any(e.code=='SEM-01' for e in errors(s))

def test_missing_claim_source_rejected():
 s=specimen();s['claims'][0]['sources']=['absent']
 assert any(e.code=='FMT-03' for e in errors(s))

def test_hypothesis_is_visibly_dashed_and_association_undirected():
 svg=core.render(specimen(),LIB)
 root=ET.fromstring(svg)
 paths={el.attrib['id']:el for el in root.iter() if el.tag.endswith('path') and 'id' in el.attrib}
 assert 'stroke-dasharray' in paths['edge-bind'].attrib
 assert 'marker-end' not in paths['edge-bind'].attrib
 assert paths['edge-activate'].attrib['marker-end']=='url(#arrow-activation)'
 assert paths['edge-inhibit'].attrib['marker-end']=='url(#arrow-inhibition)'

def test_consumption_and_production_require_process_node():
 s=simple();s['nodes'].append({'id':'process','asset':'process-node','box':[800,300,100,100]})
 s['claims']=[{'id':'hypothesis','text':'A test reaction.','status':'illustrative','sources':[]}]
 s['edges']=[{'id':'consume','source':{'node':'cell','landmark':'right'},'target':{'node':'process','landmark':'left'},'type':'consumption','claim':'hypothesis'}]
 assert any(e.code=='SEM-06' for e in errors(s))
 s['nodes'][1]['kind']='process';assert not errors(s)
 s['edges'][0].update(type='production',source={'node':'process','landmark':'right'},target={'node':'cell','landmark':'left'})
 assert not errors(s)

def test_aspect_ratio_and_landmarks_transform_together():
 n={'box':[100,200,400,100],'rotation':0};a=LIB['protein']
 assert core.placement(n,a)[2]==1
 assert core.landmark(n,a,'centre')==(300,250)
 n['rotation']=90
 left=core.landmark(n,a,'left')
 assert math.isclose(left[0],300) and left[1]<250
 n['flip_x']=True
 assert core.landmark(n,a,'left')[1]>250

def test_mirror_safe_not_inferred_from_symmetry():
 s=simple();s['nodes'][0].update(asset='receptor-single',flip_x=True)
 assert any(e.code=='GEO-06' for e in errors(s))

def test_anatomical_mode_rejects_schematic_primary_assets():
 s=simple();s['representation']='anatomical'
 assert any(e.code=='SCI-02' for e in errors(s))

def test_compartment_containment_and_boundary_rules():
 s=simple();s['compartments']=[{'id':'c','label':'Compartment','box':[250,200,500,450],'fill':'#FFFFFF','boundary':'solid','kind':'cell'}]
 s['nodes'][0].update(compartment='c',placement='inside');assert not errors(s)
 s['nodes'][0]['box'][0]=700
 assert any(e.code=='GEO-04' for e in errors(s))
 s['nodes'][0]['box']=[200,300,100,100];s['nodes'][0]['placement']='boundary';assert not errors(s)
 s['nodes'][0]['box']=[300,300,100,100]
 assert any(e.code=='GEO-05' for e in errors(s))

def test_outside_canvas():
 s=simple();s['nodes'][0]['box']=[1100,200,400,400]
 assert any(e.code=='GEO-01' for e in errors(s))

def test_labels_fit_and_do_not_overlap():
 s=simple();s['labels']=[{'id':'a','text':'Label','box':[50,200,100,40]},{'id':'b','text':'Other','box':[70,210,100,40]}]
 assert any(e.code=='TXT-04' for e in errors(s))
 s['labels']=[{'id':'a','text':'UNBREAKABLYLONGWORDWITHOUTSPACE','box':[50,200,80,30]}]
 assert any(e.code=='TXT-03' for e in errors(s))
 s['labels']=[{'id':'a','text':'Label','box':[50,200,200,40],'font_size':8}]
 assert any(e.code=='TXT-02' for e in errors(s))

def test_colour_contrast():
 assert core.contrast_ratio('#FFFFFF','#000000')==21
 s=simple();s['canvas']['text_colour']='#EEEEEE'
 assert any(e.code=='ACC-02' for e in errors(s))

def test_scale_bar_requires_calibration_and_consistent_dimensions():
 s=simple();s['sources']=[{'id':'cal','title':'Test calibration','url':'urn:test:calibration','kind':'original-data'}]
 s['scale_bars']=[{'id':'b','start':[400,650],'length_px':100,'label':'10 micrometres','units_per_px':.1,'physical_length':10,'unit':'micrometre','source':'cal'}]
 assert any(e.code=='SCI-03' for e in errors(s))
 s['frame']['scale_policy']='calibrated';assert not errors(s)
 s['scale_bars'][0]['physical_length']=15
 assert any(e.code=='SCI-03' for e in errors(s))

def test_escaped_label_text():
 s=simple();s['labels']=[{'id':'x','text':'A < B & C','box':[50,200,200,40]}]
 svg=core.render(s,LIB);assert 'A &lt; B &amp; C' in svg
 ET.fromstring(svg)

def test_import_requires_provenance_and_retains_unreviewed_status(tmp_path):
 p=tmp_path/'safe.svg';p.write_text(LIB['protein']['svg'])
 with pytest.raises(core.IllustrationError):core.import_svg(p,id='external',label='External',creator='',license='CC0-1.0',source_url='urn:test:a')
 a=core.import_svg(p,id='external',label='External',creator='Test fixture',license='CC0-1.0',source_url='urn:test:a')
 assert a['review_status']=='imported_unreviewed' and not a['mirror_safe']
 assert len(core.assets(a))==len(LIB)+1

def test_import_preserves_root_presentation_and_prefixes_local_ids(tmp_path):
 svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="#AACCBB"><defs><linearGradient id="g"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#AAAAAA"/></linearGradient></defs><rect x="10" y="10" width="80" height="80" fill="url( #g )"/></svg>'
 p=tmp_path/'safe.svg';p.write_text(svg)
 a=core.import_svg(p,id='external-gradient',label='Test gradient',creator='Test fixture',license='CC0-1.0',source_url='urn:test:gradient')
 lib=core.assets(a);s=simple();s['nodes'][0]['asset']=a['id'];s['nodes'].append({'id':'duplicate-art-not-id','asset':a['id'],'box':[800,300,200,200]})
 out=core.render(s,lib)
 assert 'asset-cell-g' in out and 'asset-duplicate-art-not-id-g' in out
 assert 'fill="#AACCBB"' in out
 core.export_svg(out,'png',width_px=600)

def test_write_refuses_overwrite(tmp_path):
 p=tmp_path/'file.txt';core.write_file(p,'one')
 with pytest.raises(core.IllustrationError):core.write_file(p,'two')
 core.write_file(p,'two',force=True);assert p.read_text()=='two'

def test_publication_requires_review_and_does_not_treat_json_as_identity_proof():
 s=simple()
 assert any(e.code=='REL-01' for e in errors(s,publication=True))
 r=approved_fixture(s);assert not errors(s,publication=True,review=r)
 assert core.render(s,LIB,publication=True,review=r)
 # Test fixtures only: the tool validates assertions in a record, not credentials.
 assert 'SYNTHETIC TEST' not in core.render(s,LIB)

def test_stale_review_is_rejected_after_scene_or_asset_change():
 s=simple();r=approved_fixture(s)
 s['title']='Changed scientific title'
 assert any(e.code=='REL-02' for e in errors(s,publication=True,review=r))
 s=simple();lib=deepcopy(LIB);lib['cell-outline']['limitations']+=' New omission.'
 assert any(e.code=='REL-02' for e in core.validate(s,lib,publication=True,review=r))

def test_missing_review_role_and_reused_identity_rejected():
 s=simple();r=approved_fixture(s);r['approvals']=r['approvals'][:1]
 assert any(e.code=='REL-03' for e in errors(s,publication=True,review=r))
 r=approved_fixture(s);r['approvals'][1]['reviewer_id']=r['approvals'][0]['reviewer_id']
 assert any(e.code=='REL-03' for e in errors(s,publication=True,review=r))

def test_blank_scaffold_cannot_be_published():
 s=core.make_scene();r=approved_fixture(s)
 assert any(e.code=='REL-01' for e in errors(s,publication=True,review=r))

def test_production_record_is_separate_from_drawing():
 s=simple();r=core.control_record(s,LIB);svg=core.render(s,LIB)
 assert len(r['svg_sha256'])==64
 assert r['svg_sha256']==core.sha256(svg)
 assert 'approvals' not in svg and 'renderer_sha256' not in svg

@pytest.mark.parametrize('dpi,width',[(-1,600),(300,1),(300,100000),(float('inf'),600),(300,20000)])
def test_export_resource_limits(dpi,width):
 with pytest.raises(core.IllustrationError):core.export_svg(core.render(simple(),LIB),'png',dpi=dpi,width_px=width)

def test_untrusted_export_cannot_fetch_external_content():
 svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><image href="https://example.test/image.png"/></svg>'
 with pytest.raises(core.IllustrationError):core.export_svg(svg,'png',width_px=600)

def test_pdf_uses_physical_dimensions():
 with pytest.raises(core.IllustrationError):core.export_svg(core.render(simple(),LIB),'pdf',width_px=600)

def test_benchmark_critical_failure_cannot_be_averaged_away():
 r={'task_id':'MED-01','candidate_id':'test','reviewer_id':'synthetic-test','scores':{k:4 for k in core.resource('benchmark-tasks.json')['weights']},'critical_errors':['Wrong patient laterality']}
 result=core.score_benchmark(r)
 assert result['weighted_score']==100 and result['critical_error_fail']
 r['scores']['scientific_accuracy']=float('nan')
 with pytest.raises(core.IllustrationError):core.score_benchmark(r)

def test_every_source_reference_resolves_and_counts_are_not_marketed_as_review():
 ids={x['id'] for x in core.resource('sources.json')['sources']}
 assert all(set(a['reference_ids']).issubset(ids) for a in LIB.values())
 assert core.resource('benchmark-tasks.json')['status']=='protocol-only-no-comparative-results'
 assert not any(x['bundled'] for x in core.resource('providers.json')['providers'])

def test_cli_render_and_control_outputs(tmp_path):
 a=tmp_path/'figure.svg';r=tmp_path/'figure.control.json'
 run=subprocess.run([sys.executable,'-m','medillustrate','render',str(ROOT/'examples/epithelial-barrier.scene.json'),'-o',str(a),'--record',str(r)],cwd=ROOT,capture_output=True,text=True)
 assert run.returncode==0,run.stderr
 assert a.exists() and r.exists()
 assert json.loads(r.read_text())['svg_sha256']==core.sha256(a.read_bytes())
 repeat=subprocess.run([sys.executable,'-m','medillustrate','render',str(ROOT/'examples/epithelial-barrier.scene.json'),'-o',str(a)],cwd=ROOT,capture_output=True,text=True)
 assert repeat.returncode==2

def test_cli_fails_invalid_input_without_traceback(tmp_path):
 p=tmp_path/'invalid.json';p.write_text('{}')
 run=subprocess.run([sys.executable,'-m','medillustrate','render',str(p),'-o',str(tmp_path/'bad.svg')],cwd=ROOT,capture_output=True,text=True)
 assert run.returncode==2 and 'Traceback' not in run.stderr and not (tmp_path/'bad.svg').exists()

def test_brief_contains_scientific_contract_not_a_factuality_claim():
 text=core.production_brief(specimen(),LIB)
 assert 'illustrative' in text and 'Do not invent' in text and 'Netter equivalence' in text

def relation_scene():
 s=simple();s['nodes'].append({'id':'nucleus','asset':'nucleus','box':[400,300,100,100]})
 s['claims']=[{'id':'structure','text':'A schematic part-whole test.','status':'illustrative','sources':[]}]
 s['relations']=[{'id':'r1','subject':'nucleus','predicate':'part_of','object':'cell','claim':'structure'}]
 return s

def test_part_whole_relations_do_not_add_visual_arrows():
 s=relation_scene();assert not errors(s)
 assert 'edge-r1' not in core.render(s,LIB)

def test_part_whole_cycles_rejected():
 s=relation_scene();s['relations'].append({'id':'r2','subject':'cell','predicate':'part_of','object':'nucleus','claim':'structure'})
 assert any(x.code=='SEM-12' for x in errors(s))

def test_spatial_contradictions_rejected_but_inverse_equivalence_allowed():
 s=relation_scene();s['relations'][0]['predicate']='anterior_to'
 s['relations'].append({'id':'r2','subject':'cell','predicate':'anterior_to','object':'nucleus','claim':'structure'})
 assert any(x.code=='SEM-13' for x in errors(s))
 s['relations'][1]['predicate']='posterior_to';assert not errors(s)

def test_structural_relation_ids_resolve():
 s=relation_scene();s['relations'][0]['object']='imaginary'
 assert any(x.code=='FMT-03' for x in errors(s))

def test_deep_part_whole_graph_is_bounded_without_recursion():
 s=simple();s['nodes']=[{'id':f'n{i}','asset':'protein','box':[300,200,100,100]} for i in range(500)]
 s['claims']=[{'id':'test','text':'Synthetic hierarchy for a software boundary test.','status':'illustrative','sources':[]}]
 s['relations']=[{'id':f'r{i}','subject':f'n{i}','predicate':'part_of','object':f'n{i+1}','claim':'test'} for i in range(499)]
 assert not errors(s)
 s['relations'].append({'id':'cycle','subject':'n499','predicate':'part_of','object':'n0','claim':'test'})
 assert any(x.code=='SEM-12' for x in errors(s))

def test_png_metadata_matches_selected_physical_width():
 s=simple();png=core.export_svg(core.render(s,LIB),'png',width_px=1200)
 info=Image.open(BytesIO(png)).info
 assert math.isclose(info['dpi'][0],1200/(180/25.4),rel_tol=.001)

def test_well_plate_has_exactly_96_wells():
 root=core.secure_svg(LIB['well-plate-96']['svg'])
 assert sum(el.tag.endswith('circle') for el in root.iter())==96
