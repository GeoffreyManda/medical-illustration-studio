"""Build eight editable specimens through the public scene compiler.
These are educational schematics, not patient observations or expert-approved plates.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from medillustrate.core import assets, make_scene, render, validate
LIB=assets(); SOURCES={x['id']:x for x in json.loads((ROOT/'medillustrate/data/sources.json').read_text())['sources']}

def source(id,kind='reference'):
 s=SOURCES[id];return {'id':id,'title':s['title'],'url':s['url'],'kind':kind}
def node(id,asset,box,**kw):return {'id':id,'asset':asset,'box':box,**kw}
def label(id,text,box,target=None,landmark='centre',**kw):
 d={'id':id,'text':text,'box':box,**kw}
 if target:d['target']={'node':target,'landmark':landmark}
 return d
def edge(id,a,al,b,bl,type,**kw):return {'id':id,'source':{'node':a,'landmark':al},'target':{'node':b,'landmark':bl},'type':type,**kw}
def comp(id,label,box,fill='#F3F6F5',boundary='none',kind='region'):return dict(id=id,label=label,box=box,fill=fill,boundary=boundary,kind=kind)
def base(id,layout,title,subtitle,description,refs,caption):
 s=make_scene(id,layout);s.update(title=title,subtitle=subtitle,description=description,sources=[source(x) for x in refs],caption=caption)
 s['claims']=[{'id':'structure','text':description,'status':'established','sources':refs}] if refs and refs!=['house-design'] else []
 return s
SCENES=[]
s=base('epithelial-barrier','epithelial-section','The epithelial barrier','A continuous tissue section, from the lumen to the supporting tissue',
 'An explanatory section of a polarised epithelial sheet. Its apical surface and microvilli are above the cell bodies; a goblet cell lies among columnar cells. Junctions lie between neighbouring cells, and a basement membrane separates the epithelial layer from the underlying connective tissue.',
 ['openstax-epithelium'],'Schematic; not to scale. Cell number and dimensions are illustrative. Anatomy reference: OpenStax, Anatomy and Physiology 2e, section 4.2.')
s['nodes']=[node('sheet','epithelial-sheet',[135,220,930,362])]
s['labels']=[
 label('lumen','LUMEN',[50,152,180,32],role='heading',font_size=20),
 label('microvilli','Microvilli',[230,154,155,30],'sheet','microvilli',leader_via=[[292,220]]),
 label('junction','Intercellular junction',[435,152,245,32],'sheet','junction',leader_via=[[428,220]]),
 label('mucin','Mucin granules',[767,152,210,32],'sheet','mucin',leader_via=[[836,202]]),
 label('nucleus','Nucleus',[50,586,120,30],'sheet','nucleus',leader_via=[[182,562]]),
 label('basement','Basement membrane',[332,597,235,32],'sheet','basement-membrane',leader_via=[[398,570]]),
 label('goblet','Goblet cell',[792,597,140,32],'sheet','goblet-cell',leader_via=[[766,574],[766,422]]),
 label('stroma','CONNECTIVE TISSUE',[50,654,260,30],role='heading',font_size=18)]
SCENES.append(s)

s=base('renal-nephron','unfolded-tubule','Continuity of the nephron','The tubular route is unfolded to make its connections legible',
 'A simplified nephron map shows a renal corpuscle leading to a proximal tubule, a descending limb, the nephron loop, an ascending limb and a distal tubule. The distal route drains into an associated collecting duct. Cortex and medulla are indicated; vascular branches are omitted.',
 ['openstax-kidney'],'Unfolded schematic; not to scale. The collecting duct is associated drainage, not part of the nephron. Blood vessels and the filtration barrier are omitted.')
s['compartments']=[comp('cortex','CORTEX',[50,146,1100,228],'#F7F0E7'),comp('medulla','MEDULLA',[50,374,1100,310],'#F2F5F4')]
s['nodes']=[node('nephron','nephron',[280,169,574,518])]
s['labels']=[label('corpuscle','Renal corpuscle',[67,241,176,55],'nephron','corpuscle'),label('proximal','Proximal tubule',[391,152,170,30],'nephron','proximal-tubule'),label('distal','Distal tubule',[746,152,160,30],'nephron','distal-tubule'),label('descending','Descending limb',[76,475,185,55],'nephron','descending-limb',leader_via=[[480,502]]),label('ascending','Ascending limb',[893,469,218,32],'nephron','ascending-limb',leader_via=[[715,484]]),label('collecting','Collecting duct',[893,592,218,32],'nephron','collecting-duct'),label('loop','Nephron loop',[354,649,174,30],'nephron','loop')]
SCENES.append(s)

s=base('vascular-wall','vascular-cross-section','A muscular artery in section','The wall is organised into layers around a continuous lumen',
 'A transverse explanatory view of a generic muscular artery. Labels identify the lumen, the tunica intima, the tunica media and the tunica externa or adventitia. The repeated elongated marks in the media symbolise circumferential smooth muscle, not measured cell counts.',
 ['openstax-vessels'],'Schematic; not to scale. Layer widths are explanatory, not measured. The outer layer is the tunica externa (adventitia). Reference: OpenStax, A&P 2e, section 20.1.')
s['nodes']=[node('artery','artery-section',[198,154,603,516])]
s['labels']=[label('lumen','Lumen',[63,211,100,30],'artery','lumen',leader_via=[[178,256],[360,333]]),label('intima','Tunica intima',[890,237,220,32],'artery','intima',leader_via=[[845,262],[742,367]]),label('media','Tunica media',[890,380,220,32],'artery','media'),label('adventitia','Tunica externa',[890,539,250,32],'artery','adventitia',leader_via=[[857,519]]),label('view','TRANSVERSE VIEW',[67,641,250,30],font_size=18,role='heading')]
SCENES.append(s)

s=base('cell-signalling','membrane-signalling','A signal is not a transported molecule','House notation separates association, activation and inhibition',
 'An intentionally hypothetical signalling example. A ligand associates with an extracellular receptor domain. The receptor is shown at a membrane boundary. A proposed intracellular activation leads to a generic effector, while a second proposed relation inhibits the effector. Dashed relationships are illustrative, not an asserted named pathway.',
 ['openstax-signalling'],'Illustrative mechanism only; not a named pathway or evidence of molecular binding. Dashed lines denote hypothetical relationships. Open arrow: activation. T-bar: inhibition. Plain line: association.')
s['claims']=[{'id':'association','text':'A ligand associates with the receptor in this explanatory example.','status':'illustrative','sources':[]},{'id':'activation','text':'A receptor-associated signal activates an effector in this invented example.','status':'illustrative','sources':[]},{'id':'inhibition','text':'A regulator inhibits the effector in this invented example.','status':'illustrative','sources':[]}]
s['compartments']=[comp('extracellular','EXTRACELLULAR',[50,143,1100,196],'#F8F7F2',kind='extracellular'),comp('intracellular','INTRACELLULAR',[50,365,1100,320],'#F0F5F4',kind='intracellular')]
s['nodes']=[node('bilayer'+str(i),'lipid-bilayer',[50+i*183,310,204,80]) for i in range(6)]
s['nodes'] += [node('ligand','ligand',[381,163,91,98]),node('receptor','receptor-single',[433,267,140,193],compartment='intracellular',placement='boundary'),node('effector','kinase',[742,489,151,151],compartment='intracellular'),node('regulator','phosphatase',[992,478,112,132],compartment='intracellular')]
s['edges']=[edge('bind','ligand','bottom','receptor','binding-site','association',claim='association',via=[[426,252],[504,252]]),edge('activate','receptor','intracellular-domain','effector','left','activation',claim='activation',via=[[503,574],[704,574]],label='activates',label_position=[553,540]),edge('inhibit','regulator','left','effector','right','inhibition',claim='inhibition',via=[[950,554],[950,562]])]
s['labels']=[label('ligand','Ligand',[179,206,145,32],'ligand','left'),label('receptor','Receptor',[213,449,162,32],'receptor','intracellular-domain',leader_via=[[408,463]]),label('effector','Effector',[756,645,145,32]),label('inhibitor','Regulator',[979,633,145,32]),label('membrane','Lipid bilayer',[692,282,190,32],'bilayer4','outer-leaflet')]
SCENES.append(s)

s=base('cell-interior','cell-interior','Selective detail inside a cell','Compartment relationships are preserved; relative sizes are explanatory',
 'A generic nucleated cell is shown with a nucleus, mitochondria, rough endoplasmic reticulum, Golgi apparatus and a lysosome. Organelles are contained within the cell outline. Their numbers and relative dimensions are chosen for explanation rather than representing a measured cell.',
 ['openstax-organelles'],'Schematic; not to scale. A generic cell, not a complete cell-type reconstruction. Organelle counts and positions are illustrative. Each selected structure remains individually editable.')
# This is a verification target rather than an asserted evidence check in this build.
s['claims'][0]['status']='illustrative'
s['nodes']=[node('cell','cell-outline',[180,123,763,568]),node('nucleus','nucleus',[362,316,160,183]),node('mito1','mitochondrion',[628,474,153,111]),node('mito2','mitochondrion',[618,241,130,109],rotation=90),node('er','rough-er',[545,323,187,154]),node('golgi','golgi',[405,503,132,114]),node('lysosome','lysosome',[724,372,80,84]),node('vesicle','vesicle',[706,444,43,43])]
s['labels']=[label('membrane','Plasma membrane',[892,493,279,34],'cell','membrane',leader_via=[[854,504]]),label('nucleus-label','Nucleus',[70,306,175,30],'nucleus','envelope-left'),label('mitochondrion','Mitochondrion',[857,585,256,34],'mito1','outer-membrane'),label('er-label','Rough endoplasmic reticulum',[913,305,235,56],'er','cisterna',leader_via=[[881,366]]),label('golgi-label','Golgi apparatus',[80,580,205,32],'golgi','centre'),label('lysosome-label','Lysosome',[921,415,190,32],'lysosome','centre')]
s['relations']=[{'id':'part-'+n['id'],'subject':n['id'],'predicate':'part_of','object':'cell','claim':'structure'} for n in s['nodes'] if n['id']!='cell']
SCENES.append(s)

s=base('paired-epithelium','paired-state','A matched view preserves the comparison','The same tissue geometry, shown at the same scale, supports two reading tasks',
 'Two identical epithelial sections are displayed at a shared scale. The left annotation identifies cellular organisation; the right identifies the basal interface. Only the annotation changes. The figure does not depict disease, treatment, before-and-after improvement or measured clinical data.',
 ['openstax-epithelium'],'Matched explanatory views; not patient observations. Geometry, orientation and magnification are fixed. Only the selected label changes; no disease or treatment effect is implied.')
s['nodes']=[node('left-tissue','epithelial-sheet',[68,283,496,193]),node('right-tissue','epithelial-sheet',[634,283,496,193])]
s['labels']=[label('A','A  Cellular organisation',[68,165,462,42],font_size=24,role='heading'),label('B','B  Basal interface',[634,165,462,42],font_size=24,role='heading'),label('goblet','Goblet cell',[173,539,180,32],'left-tissue','goblet-cell',leader_via=[[346,512],[346,407]]),label('basement','Basement membrane',[779,539,281,32],'right-tissue','basement-membrane',leader_via=[[876,509]]),label('shared','Identical geometry and scale',[402,649,420,32],align='centre',role='heading')]
SCENES.append(s)

s=base('study-workflow','study-workflow','From a specimen to an interpretable image','A descriptive workflow, without fabricated experimental results',
 'A conceptual research workflow progresses from a labelled sample vial to a prepared microscope slide, then to optical microscopy. The arrows indicate the order of activities, not a biological mechanism. No sample results, operating instructions, measurements or patient identifiers are shown.',
 ['house-design'],'Conceptual workflow; not an operating protocol. Sequence arrows indicate stages of work, not causal biological effects. No microscopy result or sample measurement is fabricated.')
s['sources']=[source('house-design','illustrative')];s['claims']=[]
s['nodes']=[node('sample','sample-vial',[145,266,180,213]),node('slide','microscope-slide',[488,287,225,173]),node('scope','microscope',[876,246,196,241])]
s['edges']=[edge('prepare','sample','right','slide','left','sequence',via=[[409,373]],label='prepare',label_position=[349,313]),edge('observe','slide','right','scope','left','sequence',via=[[791,373]],label='observe',label_position=[744,313])]
s['labels']=[label('sample-label','1  Specimen',[128,183,251,42],font_size=24,role='heading'),label('slide-label','2  Prepared slide',[470,183,315,42],font_size=24,role='heading'),label('scope-label','3  Microscopy',[866,183,272,42],font_size=24,role='heading'),label('sample-note','A defined material and an explicit identity',[114,545,268,70],font_size=18),label('slide-note','Preparation is described in the study methods',[477,545,281,70],font_size=18),label('scope-note','Observed data remain separate from illustration',[863,545,278,70],font_size=18)]
SCENES.append(s)

s=base('multi-scale-tissue','multiscale-zoom','One tissue, three explanatory scales','Zoom connectors indicate correspondence, not biological causation',
 'A tissue section, a columnar cell symbol and a membrane-junction detail are displayed at different illustrative scales. The first zoom begins in the epithelial sheet and selects a columnar cell. The second selects the upper lateral interface and shows a generic junction between membranes. No magnification value is claimed.',
 ['openstax-epithelium'],'Schematic at unequal, uncalibrated scales. Dashed connectors mean a change of scale, not transport or causation. Junction detail is symbolic, not a molecular reconstruction.')
s['nodes']=[node('tissue','epithelial-sheet',[43,300,400,156]),node('cell','enterocyte',[502,251,215,322]),node('junction','tight-junction',[837,286,223,231])]
s['edges']=[edge('zoom-cell','tissue','enterocyte','cell','left','zoom',via=[[430,259],[490,259]]),edge('zoom-junction','cell','right','junction','left','zoom',via=[[785,412]])]
s['labels']=[label('tissue-label','TISSUE',[60,180,241,32],role='heading',font_size=20),label('cell-label','CELL',[501,180,204,32],role='heading',font_size=20),label('detail-label','MEMBRANE INTERFACE',[828,180,320,32],role='heading',font_size=20),label('tissue-note','The cell within a continuous epithelial sheet',[62,580,335,63]),label('cell-note','Cell polarity is retained',[497,608,284,32]),label('detail-note','Neighbouring membranes with a junctional symbol',[838,580,301,63])]
SCENES.append(s)

if __name__=='__main__':
 for s in SCENES:
    issues=validate(s,LIB); errors=[x for x in issues if x.severity=='error']
    if errors:
        for x in errors:print(s['id'],x)
        raise SystemExit(1)
    (ROOT/'examples'/f"{s['id']}.scene.json").write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n')
    (ROOT/'examples'/f"{s['id']}.svg").write_text(render(s,LIB))
    print(s['id'])
