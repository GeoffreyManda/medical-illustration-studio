"""Rebuild the four editable atlas plates and their offline visual workbench."""
from pathlib import Path
import sys,json,base64,html
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from medillustrate import atelier

SPECS=[
('kidney-section','Kidney','Coronal section with the collecting system opened','A section through an idealised adult human kidney shows cortical tissue, medullary pyramids and the opened collecting system. Selected hilar vessels are retained.',
 [('capsule','Fibrous capsule','left'),('cortex','Renal cortex','left'),('medulla','Renal pyramid','left'),('column','Renal column','left'),('papilla','Renal papilla','left'),('artery','Renal artery','right'),('vein','Renal vein','right'),('minor-calyx','Minor calyx','right'),('pelvis','Renal pelvis','right'),('major-calyx','Major calyx','right'),('ureter','Ureter','right')],
 'Illustrative coronal section. Calyces and renal pelvis are opened to show their continuity. Selected vessels only; not to scale.', 'Anatomical reference: OpenStax, Anatomy and Physiology 2e, section 25.3.'),
('kidney-surface','Kidney','External surface and structures at the hilum','An idealised adult kidney has a convex lateral border, a concave medial hilum, a smooth capsular surface, renal artery, renal vein and ureter.',
 [('upper-pole','Superior pole','left'),('lateral-border','Lateral border','left'),('anterior-surface','Capsular surface','left'),('lower-pole','Inferior pole','left'),('artery','Renal artery','right'),('vein','Renal vein','right'),('hilum','Renal hilum','right'),('ureter','Ureter','right')],
 'External illustrative view. Hilar structures have been separated for clarity. No sided anatomical variation is implied; not to scale.', 'Anatomical reference: OpenStax, Anatomy and Physiology 2e, section 25.3.'),
('arterial-wall','Muscular artery','Oblique section through the vessel wall','An oblique section through an idealised muscular artery distinguishes the outer supporting coat, muscular media, internal elastic lamina, intima and lumen. Sparse surface vessels are shown.',
 [('vasa-vasorum','Vasa vasorum','left'),('outer-coat','Outer connective tissue','left'),('adventitia','Tunica adventitia','left'),('lumen','Lumen','right'),('media','Tunica media','right'),('elastic-lamina','Internal elastic lamina','right'),('intima','Tunica intima','right')],
 'Illustrative muscular artery. Wall thickness and layer proportions are exaggerated for visibility; not a quantitative histological section.', 'Anatomical reference: OpenStax, Anatomy and Physiology 2e, section 20.1.'),
('peripheral-nerve','Peripheral nerve','Oblique section showing fascicles and their envelopes','An idealised peripheral nerve in oblique section contains several fascicles within the epineurium. Each fascicle is bounded by perineurium and contains illustrated myelinated fibres and endoneurial supporting tissue.',
 [('longitudinal-bundles','Longitudinal nerve trunk','left'),('myelinated-fibres','Myelinated fibres','left'),('fascicle','Nerve fascicle','left'),('endoneurium','Endoneurial tissue','right'),('vasa-nervorum','Small epineurial vessel','right'),('perineurium','Perineurium','right'),('epineurium','Epineurium','right')],
 'Illustrative nerve section. Fascicle and fibre counts are arbitrary; unmyelinated fibres are omitted. Not a quantitative histological section.', 'Anatomical reference: OpenStax, Anatomy and Physiology 2e, section 13.4.')]


def main():
    lib=atelier.library();plates=[]
    for slug,title,sub,desc,labels,caption,ref in SPECS:
        asset=lib['atlas-'+slug]
        p={'schema_version':'2.0.0','id':'atlas-'+slug,'title':title,'subtitle':sub,'description':desc,'asset':asset['id'],'width':1000,'height':1190,'print_width_mm':190,'label_size':17,'label_bank_width':174,'art_box':[204,142,610,889] if slug.startswith('kidney') else [164,175,687,782], 'anatomy':{'species':'Homo sapiens','life_stage':'adult, idealised','view':asset['view'],'laterality':'unspecified' if slug.startswith('kidney') else 'not-applicable'},'labels':[{'landmark':key,'text':text,'side':side} for key,text,side in labels],'caption':caption,'reference_line':ref,'intended_use':'educational-draft'}
        # Short left-bank papillary label is intentionally offset below the pyramid.
        if slug=='kidney-section':
            for label in p['labels']:
                if label['landmark']=='papilla':label['y']=690
                if label['landmark']=='column':label['y']=777
                if label['landmark']=='minor-calyx':label['y']=665
                if label['landmark']=='pelvis':label['y']=733
                if label['landmark']=='major-calyx':label['y']=804
        (ROOT/'examples'/f'atlas-{slug}.plate.json').write_text(json.dumps(p,indent=2)+'\n')
        svg=atelier.render_plate(p,lib)
        (ROOT/'examples'/f'atlas-{slug}.svg').write_text(svg)
        plates.append((p,svg))
    for stage in ('contours','values'):
        (ROOT/'examples'/f'atlas-kidney-{stage}.svg').write_text(atelier.render_plate(plates[0][0],lib,stage=stage,labels=False))
    make_workbench(plates,lib)
    print('Built four vector atlas plates, two process-stage drawings and the offline workbench.')


def make_workbench(plates,lib):
    # Keep reusable asset geometry and separate label SVG layers; do not rasterise.
    items=[]
    for p,svg in plates:
        items.append({'plate':p,'svg':svg,'asset':lib[p['asset']]})
    data=json.dumps(items,ensure_ascii=False).replace('</','<\\/')
    s='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Medical Illustration Studio · Anatomical plates</title><style>
*{box-sizing:border-box}body{margin:0;background:#eeeae4;color:#322d27;font:15px/1.5 system-ui,sans-serif}header{padding:26px 32px 22px;background:white;border-bottom:1px solid #d6cec4}h1{font:32px Georgia,serif;margin:0 0 7px}header p{margin:0;max-width:940px;color:#6a6258}.shell{display:grid;grid-template-columns:270px 1fr;gap:28px;max-width:1440px;margin:auto;padding:28px}aside{position:sticky;top:20px;align-self:start}button,select{font:inherit;border:1px solid #b7aea2;background:white;color:#322d27;padding:9px 11px;cursor:pointer;border-radius:2px}button:hover{background:#f3efe9}.nav{display:grid;gap:9px}.nav button{text-align:left;padding:13px 12px}.nav button[aria-pressed=true]{background:#3d493f;color:white;border-color:#3d493f}h2{font:23px Georgia,serif}.controls{display:grid;gap:9px;margin-top:25px}.controls label{display:flex;align-items:center;gap:8px}.controls input{width:17px;height:17px}small{font-size:12px}.paper{background:white;box-shadow:0 3px 16px #00000010;overflow:auto}.paper svg{display:block;width:100%;height:auto}main{min-width:0}.info{background:white;padding:20px 24px;margin-top:18px}a{color:#31594b}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;background:#f7f5f1;padding:14px}.note{font-size:13px;color:#746a5f}.stage{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:12px}.stage button[aria-pressed=true]{border-color:#31594b;background:#e9eee8}@media(max-width:850px){.shell{grid-template-columns:1fr;padding:16px;gap:16px}aside{position:static}.nav{grid-template-columns:1fr 1fr}.controls{grid-template-columns:1fr 1fr}header{padding:20px}.paper svg{min-width:650px}}@media print{header,aside,.stage,.info{display:none}.shell{display:block;padding:0}.paper{box-shadow:none}.paper svg{max-height:270mm}.shell main{width:190mm}body{background:white}}
</style><header><h1>Anatomical plates</h1><p>Structure, volume, material and editable lettering. Four original vector studies with separate colour, tonal-value and contour views.</p></header><div class="shell"><aside><nav class="nav" aria-label="Choose an anatomical plate" id="nav"></nav><div class="controls"><label><input id="labels" type="checkbox" checked>Show labels</label><button id="save-plate">Export current SVG</button><button id="save-art">Export unlabelled artwork</button><button id="save-json">Export plate specification</button><button id="save-asset">Export asset record</button></div><p class="note">The artwork and lettering remain editable vectors. These are idealised educational studies, not independently reviewed clinical plates.</p><p><a href="atlas.html">Full handbook and schematic library</a></p><p><a href="docs/painting-grammar.md">Painting grammar</a><br><a href="docs/atlas-refinement.md">Agent production instructions</a></p></aside><main><div class="stage" aria-label="Drawing stage"><button data-stage="colour" aria-pressed="true">Colour</button><button data-stage="values" aria-pressed="false">Tonal values</button><button data-stage="contours" aria-pressed="false">Contours</button></div><div id="paper" class="paper"></div><section class="info"><h2 id="about-title"></h2><p id="about"></p><p id="limitations" class="note"></p><details><summary>View and anatomical landmarks</summary><pre id="details"></pre></details></section></main></div><script id="plate-data" type="application/json">DATA</script><script>
const items=JSON.parse(document.getElementById('plate-data').textContent);let active=0,stage='colour';const paper=document.getElementById('paper');
function save(name,text,mime){const a=document.createElement('a');const u=URL.createObjectURL(new Blob([text],{type:mime}));a.href=u;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),500);}
function transformed(svg){const doc=new DOMParser().parseFromString(svg,'image/svg+xml');if(!document.getElementById('labels').checked){doc.getElementById('plate-labels')?.remove();}if(stage==='values'){for(const el of doc.querySelectorAll('*'))for(const at of [...el.attributes]){el.setAttribute(at.name,at.value.replace(/#[0-9a-f]{6}\b/gi,c=>{const r=parseInt(c.slice(1,3),16),g=parseInt(c.slice(3,5),16),b=parseInt(c.slice(5,7),16);const v=Math.round(.2126*r+.7152*g+.0722*b).toString(16).padStart(2,'0');return '#'+v+v+v;}));}}if(stage==='contours'){for(const el of [...doc.querySelectorAll('[id]')])if(el.id.includes('texture-'))el.remove();const art=doc.getElementById('node-anatomy');for(const el of art.querySelectorAll('path,ellipse,circle,polygon,polyline,rect')){el.setAttribute('fill','none');el.setAttribute('stroke','#74695f');el.setAttribute('stroke-width','0.9');el.setAttribute('opacity','.65');}}return new XMLSerializer().serializeToString(doc.documentElement);}
function draw(){const i=items[active];paper.innerHTML=transformed(i.svg);document.getElementById('about-title').textContent=i.plate.title;document.getElementById('about').textContent=i.plate.description;document.getElementById('limitations').textContent=i.asset.limitations;document.getElementById('details').textContent=JSON.stringify({view:i.asset.view,landmarks:i.asset.landmarks},null,2);document.querySelectorAll('#nav button').forEach((b,j)=>b.setAttribute('aria-pressed',j===active));document.querySelectorAll('[data-stage]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.stage===stage));}
items.forEach((i,j)=>{const b=document.createElement('button');b.textContent=i.plate.title+' · '+(j<2?(j?'surface':'section'):'section');b.onclick=()=>{active=j;draw()};document.getElementById('nav').append(b)});document.querySelectorAll('[data-stage]').forEach(b=>b.onclick=()=>{stage=b.dataset.stage;draw()});document.getElementById('labels').onchange=draw;document.getElementById('save-plate').onclick=()=>save(items[active].plate.id+'-'+stage+'.svg',transformed(items[active].svg),'image/svg+xml');document.getElementById('save-art').onclick=()=>save(items[active].asset.id+'-artwork.svg',items[active].asset.svg,'image/svg+xml');document.getElementById('save-json').onclick=()=>save(items[active].plate.id+'.plate.json',JSON.stringify(items[active].plate,null,2),'application/json');document.getElementById('save-asset').onclick=()=>save(items[active].asset.id+'.asset.json',JSON.stringify(items[active].asset,null,2),'application/json');draw();
</script></html>'''
    (ROOT/'atlas-refined.html').write_text(s.replace('DATA',data),encoding='utf-8')

if __name__=='__main__':main()
