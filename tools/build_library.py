"""Build original, editable schematic assets. No third-party drawings are embedded.
Run from any directory: python tools/build_library.py
All coordinates are declarative illustrations, not measurements or specimen data.
"""
from __future__ import annotations
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'medillustrate' / 'data'
INK='#354753'; MEM='#6D8890'; CYTO='#EAF1EF'; NUC='#9B8BB5'; NUC_D='#66567F'
TISSUE='#E9BCAD'; TISSUE_D='#A26C5C'; BLUE='#749DB6'; TEAL='#77AAA1'; GOLD='#D4B66F'
ASSETS=[]

def el(tag, **attrs):
    from html import escape
    return '<'+tag+' '+ ' '.join(f'{k.replace("_","-")}="{escape(str(v),quote=True)}"' for k,v in attrs.items()) + '/>'
def path(d, fill='none', stroke=INK, sw=1.5, **kw):
    return el('path',d=d,fill=fill,stroke=stroke,stroke_width=sw,stroke_linecap='round',stroke_linejoin='round',**kw)
def circle(x,y,r,fill,stroke=INK,sw=1.3,**kw): return el('circle',cx=x,cy=y,r=r,fill=fill,stroke=stroke,stroke_width=sw,**kw)
def ellipse(x,y,rx,ry,fill,stroke=INK,sw=1.3,**kw):return el('ellipse',cx=x,cy=y,rx=rx,ry=ry,fill=fill,stroke=stroke,stroke_width=sw,**kw)
def rect(x,y,w,h,fill,stroke=INK,sw=1.3,rx=0,**kw):return el('rect',x=x,y=y,width=w,height=h,rx=rx,fill=fill,stroke=stroke,stroke_width=sw,**kw)
def line(x1,y1,x2,y2,c=INK,w=1.3,**kw):return el('line',x1=x1,y1=y1,x2=x2,y2=y2,stroke=c,stroke_width=w,stroke_linecap='round',**kw)
def nucleus(x=50,y=52,rx=19,ry=23):
    return ellipse(x,y,rx,ry,NUC,NUC_D)+ellipse(x,y,rx-2,ry-2,'none',NUC_D,.6)+circle(x+3,y+3,4,NUC_D,NUC_D,.6)
def points_on(cx,cy,rx,ry,n,off=0):
    return [(cx+rx*math.cos(2*math.pi*i/n+off),cy+ry*math.sin(2*math.pi*i/n+off)) for i in range(n)]
def add(id,label,cat,body,w=100,h=100,landmarks=None,limits='',refs=None,scale='cell',mirror=True,aliases=()):
    lm={'centre':[.5,.5],'top':[.5,.04],'bottom':[.5,.96],'left':[.04,.5],'right':[.96,.5]}
    lm.update(landmarks or {})
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{label}</title>{body}</svg>'
    ASSETS.append({'id':id,'label':label,'category':cat,'svg':svg,'view_box':[0,0,w,h], 'landmarks':lm,
       'scale_class':scale,'representation':'schematic','view':'illustrative projection','mirror_safe':mirror,
       'license':'CC0-1.0','creator':'Medical Illustration Studio; original programmatic drawing, AI-assisted',
       'reference_ids':refs or ['openstax-organelles'],'review_status':'schematic_unreviewed',
       'limitations':limits or 'Symbolic geometry; not to scale; not a diagnostic, quantitative or species-specific reconstruction.',
       'aliases':list(aliases)})

# Organelles: surfaces are purposefully restrained and distinct from their internal features.
add('cell-outline','Cell boundary','organelles',path('M12 45 C8 18 30 7 53 10 C83 6 98 27 94 57 C99 82 74 94 43 91 C15 94 6 71 12 45 Z',CYTO,MEM,1.8),landmarks={'membrane':[.94,.57],'cytoplasm':[.68,.65]})
add('nucleus','Nucleus, envelope and nucleolus','organelles',nucleus(50,50,37,40),landmarks={'envelope':[.87,.5],'envelope-left':[.13,.5],'nucleolus':[.53,.53]})
add('nucleolus','Nucleolus','organelles',circle(50,50,35,NUC_D,NUC_D)+path('M30 40 Q46 22 63 42 M35 66 Q48 50 70 59','none','#B4A8C9',2),scale='organelle')
mito=path('M9 47 C7 22 30 15 53 18 C74 11 94 29 93 50 C97 77 75 85 47 80 C23 88 8 71 9 47 Z','#ECD7BE','#967650',2)
mito+=path('M16 49 C13 28 34 23 52 25 C72 18 87 32 86 48 C89 69 72 77 49 73 C28 82 16 65 16 49 Z','none','#B08B58',1.4)
mito+=path('M23 36 Q38 32 29 49 Q23 62 39 68 M44 27 Q59 38 42 48 Q36 60 55 72 M68 26 Q78 40 61 49 Q54 61 73 67 M81 37 Q90 49 76 53','none','#967650',2.2)
add('mitochondrion','Mitochondrion','organelles',mito,landmarks={'outer-membrane':[.92,.5],'cristae':[.43,.48],'matrix':[.56,.62]},scale='organelle')
for rough in [True,False]:
    b=''
    for i in range(4):
        y=23+i*15
        b+=path(f'M10 {y} C29 {y-12} 50 {y+10} 78 {y-3} Q94 {y-8} 91 {y+2} C66 {y+17} 38 {y+2} 12 {y+10} Z','#D6E4E6',MEM,1.2)
        if rough:
            for x in (18,32,47,63,79): b+=circle(x,y-3+(x%3),1.6,NUC_D,NUC_D,.4)
    add('rough-er' if rough else 'smooth-er','Rough endoplasmic reticulum' if rough else 'Smooth endoplasmic reticulum','organelles',b,landmarks={'cisterna':[.5,.39]},scale='organelle')
b=''
for i in range(5):
    y=23+i*12
    b+=path(f'M{17+i*2} {y} Q50 {y+14} {84-i*3} {y-1} Q92 {y+9} {82-i*3} {y+10} Q50 {y+24} {18+i*2} {y+9} Q8 {y+4} {17+i*2} {y} Z','#D3CAB2','#8C805B',1.2)
for x,y,r in [(9,21,5),(91,65,5),(14,85,4),(84,89,5)]: b+=circle(x,y,r,'#D3CAB2','#8C805B',1)
add('golgi','Golgi apparatus','organelles',b,scale='organelle',landmarks={'cis':[.5,.25],'trans':[.5,.83]})
for id,label,col,inside in [('lysosome','Lysosome','#D7B2A8','dots'),('peroxisome','Peroxisome','#CAD8B5','core'),('vesicle','Transport vesicle','#D7E6E4','empty')]:
    b=circle(50,50,35,col,MEM,1.7)+circle(50,50,31,'none',MEM,.6)
    if inside=='dots':
        for x,y in [(40,35),(60,40),(31,55),(50,60),(67,59),(51,31)]:b+=circle(x,y,3,'#A87868','none')
    elif inside=='core': b+=path('M39 37 L63 43 L61 64 L36 60 Z','#8FA17A','#6F825A')+line(39,37,61,64,'#CAD8B5')
    add(id,label,'organelles',b,scale='organelle')
add('ribosome','Ribosome, two subunits','organelles',path('M16 56 Q14 20 45 17 Q80 12 86 52 Q65 66 16 56 Z','#BBADD0',NUC_D)+path('M22 65 Q52 57 80 64 Q78 84 50 85 Q29 86 22 65 Z','#D4C9DF',NUC_D),scale='molecular',landmarks={'large-subunit':[.5,.38],'small-subunit':[.5,.74]})
b=''
for x,y,ang in [(37,45,-25),(66,62,45)]:
    b+=f'<g transform="translate({x} {y}) rotate({ang})">'+rect(-12,-27,24,54,'#D4B887','#8A734E',1.1,5)
    for dx in [-8,-3,3,8]:b+=line(dx,-20,dx,20,'#8A734E',1)
    b+='</g>'
add('centrosome','Centrosome, paired centrioles','organelles',b,scale='organelle')
b=path('M6 34 Q50 23 94 34 L94 66 Q50 56 6 66 Z','#D5CCE0',NUC_D)+path('M6 40 Q50 29 94 40 M6 60 Q50 50 94 60','none',NUC_D,.8)
for x in [27,72]:b+=rect(x-8,29,16,40,CYTO,NUC_D,1,5)
add('nuclear-envelope','Nuclear envelope with pores','organelles',b,scale='organelle',landmarks={'pore':[.27,.5]})

# Molecular and membrane symbols. None purport to represent a measured protein fold.
b=''
for x in range(7,198,12):
    b+=circle(x,16,4,TEAL,MEM,.9)+line(x-1,21,x-3,35,MEM,1)+line(x+1,21,x+3,35,MEM,1)
    b+=circle(x,64,4,TEAL,MEM,.9)+line(x-1,59,x-3,45,MEM,1)+line(x+1,59,x+3,45,MEM,1)
add('lipid-bilayer','Lipid bilayer segment','membranes',b,w=204,h=80,scale='molecular',landmarks={'outer-leaflet':[.5,.2],'inner-leaflet':[.5,.8],'hydrophobic-core':[.5,.5]})
add('phospholipid','Phospholipid symbol','membranes',circle(50,21,13,TEAL,MEM,1.5)+path('M44 35 L42 54 L35 81 M56 35 L58 51 L67 60 L62 83','none',MEM,4),scale='molecular')
add('receptor-single','Single-pass receptor symbol','membranes',path('M31 11 Q42 3 49 23 Q61 3 72 14 L64 39 L58 42 L58 66 Q74 76 57 91 L43 89 Q32 77 44 66 L44 43 L37 39 Z','#CAB9D7',NUC_D,1.8),scale='molecular',landmarks={'binding-site':[.5,.2],'intracellular-domain':[.52,.8],'membrane-centre':[.5,.53]},mirror=False)
add('receptor-dimer','Dimeric receptor symbol','membranes',path('M17 11 L34 11 L38 41 L37 71 Q48 90 29 91 Q14 88 22 70 L22 38 Z','#CAB9D7',NUC_D)+path('M83 11 L66 11 L62 41 L63 71 Q52 90 71 91 Q86 88 78 70 L78 38 Z','#CAB9D7',NUC_D),scale='molecular',landmarks={'binding-site':[.5,.2],'intracellular-domain':[.5,.84]},mirror=False)
b=''
for i in range(7):
    x=12+i*12
    b+=rect(x,29,7,42,'#B9CCD6','#617F91',1,3)
    if i<6:b+=path(f'M{x+7} {33 if i%2==0 else 67} Q{x+10} {11 if i%2==0 else 91} {x+12} {33 if i%2==0 else 67}','none','#617F91',1.4)
add('receptor-seven-pass','Seven-pass receptor topology symbol','membranes',b,scale='molecular',limits='Seven membrane traversals are depicted; not the fold, sequence or activation state of a specific receptor.',mirror=False)
for state in ['open','closed']:
    b=path('M13 14 Q32 4 42 20 L38 44 L38 56 L42 81 Q24 96 13 85 Q22 61 22 48 Q20 30 13 14 Z','#B5CDC8','#567C75',1.5)+path('M87 14 Q68 4 58 20 L62 44 L62 56 L58 81 Q76 96 87 85 Q78 61 78 48 Q80 30 87 14 Z','#B5CDC8','#567C75',1.5)
    if state=='closed': b+=path('M37 44 Q50 35 63 44 L63 57 Q50 65 37 57 Z','#B5CDC8','#567C75',1.5)
    add('channel-'+state,'Channel, '+state+' state symbol','membranes',b,scale='molecular',landmarks={'pore':[.5,.5]},mirror=False)
add('transporter','Transporter, conformational symbol','membranes',path('M22 12 Q51 0 49 38 L37 50 L50 64 Q48 100 20 87 Q7 55 22 12 Z','#B1C8D5','#5D7F94')+path('M78 12 Q54 1 57 38 L72 50 L56 64 Q53 99 80 87 Q93 53 78 12 Z','#B1C8D5','#5D7F94'),scale='molecular',mirror=False)
for id,label,kind in [('tight-junction','Tight junction','zip'),('adherens-junction','Adherens junction','belt'),('desmosome','Desmosome','spot'),('gap-junction','Gap junction','pore')]:
    b=line(28,12,28,88,MEM,3)+line(72,12,72,88,MEM,3)
    if kind=='zip':
        for y in [29,42,55,68]: b+=path(f'M28 {y} L46 {y-6} L54 {y+6} L72 {y}', 'none',TEAL,4)
    elif kind=='belt':
        for y in [37,51,65]: b+=path(f'M28 {y} Q50 {y-15} 72 {y}', 'none',TEAL,3)
        b+=line(17,20,17,80,GOLD,4)+line(83,20,83,80,GOLD,4)
    elif kind=='spot':
        b+=rect(16,30,11,40,GOLD,'#937E47',1,3)+rect(73,30,11,40,GOLD,'#937E47',1,3)
        for y in [37,50,63]: b+=line(29,y,71,100-y,TEAL,2)
        for y in [18,36,64,82]:b+=line(2,y,16,50,NUC_D,1)+line(84,50,98,y,NUC_D,1)
    else:
        for y in [34,49,64]:b+=rect(28,y-5,44,10,'#ADC3D2','#617F91',1,2)+line(31,y,69,y,'#FAFBFA',2)
    add(id,label,'membranes',b,scale='molecular',refs=['openstax-epithelium'],landmarks={'junction':[.5,.5]})
add('integrin','Integrin adhesion symbol','membranes',path('M24 89 L40 48 L32 29 Q31 9 48 8 Q64 5 68 21 L60 42 L74 88 M40 48 L50 62 L60 42','none','#8F769D',9),scale='molecular',mirror=False)
add('ligand','Generic ligand','molecules',path('M26 16 Q45 2 59 16 Q84 15 86 41 Q98 59 77 74 Q72 96 45 86 Q24 94 18 68 Q3 52 18 34 Q12 23 26 16 Z','#D5B36D','#8C754B',1.8),scale='molecular',refs=['openstax-signalling'])
add('protein','Generic globular protein','molecules',path('M16 31 Q14 13 35 12 Q51 1 64 17 Q87 7 89 30 Q100 46 82 57 Q99 75 75 86 Q53 100 43 81 Q21 94 16 72 Q-1 54 16 31 Z','#C3B3D2',NUC_D,1.8)+path('M29 29 Q55 24 65 43 Q76 65 48 66','none','#A08DB5',1.3),scale='molecular',refs=['openstax-signalling'])
add('kinase','Kinase, symbolic catalytic cleft','molecules',path('M13 32 Q20 6 47 12 L58 36 L79 14 Q97 29 85 56 Q98 82 65 87 Q39 98 28 78 Q4 69 13 32 Z','#B0C7DA','#5D7D98',1.8),scale='molecular',landmarks={'cleft':[.58,.36]},refs=['openstax-signalling'])
add('phosphatase','Phosphatase, symbolic catalytic cleft','molecules',path('M20 16 Q55 0 79 18 L63 42 L90 57 Q91 82 64 88 Q43 98 25 82 Q5 74 12 51 Q4 27 20 16 Z','#BBCDA8','#6C8658',1.8),scale='molecular',refs=['openstax-signalling'])
add('antibody','IgG antibody symbol','molecules',path('M46 89 L46 58 L20 30 L10 12 M54 89 L54 58 L80 30 L90 12','none','#856B9B',9)+path('M38 49 L14 33 L4 18 M62 49 L86 33 L96 18','none','#B5A5C4',6)+line(44,61,56,61,GOLD,2),scale='molecular',landmarks={'fab-left':[.1,.15],'fab-right':[.9,.15],'fc':[.5,.84]},limits='IgG-like Y symbol, not all immunoglobulin classes, a measured conformation or an antigen affinity model.',refs=['openstax-immune'])
add('transcription-factor','DNA-binding factor symbol','molecules',path('M13 24 Q36 5 50 24 Q68 7 87 24 L86 68 L68 84 L53 63 L36 84 L15 66 Z','#C5B4CC','#86698F',1.6),scale='molecular',refs=['openstax-signalling'])
add('small-molecule','Unspecified small-molecule symbol','molecules',circle(50,50,23,GOLD,'#8C754B',1.8),scale='molecular',limits='A token, not a chemical structure. Do not infer stereochemistry, composition, binding, dose or size.',refs=['openstax-signalling'])
add('phosphate','Phosphate group token','molecules',circle(50,50,24,'#E8D3A6','#947B43',1.4)+'<text x="50" y="59" text-anchor="middle" font-family="sans-serif" font-size="26" fill="#544724">P</text>',scale='molecular',refs=['openstax-signalling'])
b=path('M6 51 C18 15 29 87 43 51 S69 18 82 49 S98 79 98 52','none','#AF7A66',3)
for i,(x,y) in enumerate([(13,41),(26,61),(38,55),(53,38),(67,35),(80,48),(93,65)]): b+=line(x,y,x,y-10 if i%2 else y+10,'#997058',2)
add('rna','RNA strand symbol','molecules',b,scale='molecular',limits='Unspecified RNA; no sequence or measured secondary structure is encoded.')
b=''
for i in range(15):
    x=8+i*6; yy=50+22*math.sin(i*math.pi/7)
    b+=line(x,yy,x,100-yy,'#B7BDAF',1.2)
b+=path('M8 50 C22 9 38 9 50 50 S80 91 92 50','none','#719F99',3)+path('M8 50 C22 91 38 91 50 50 S80 9 92 50','none','#A48CB5',3)
add('dna-symbol','DNA double-strand symbol','molecules',b,scale='molecular',mirror=False,limits='A two-strand diagram, not a geometric helix or evidence of helical handedness. Do not use for stereochemical explanation.')
add('microtubule','Microtubule segment','molecules',rect(9,32,81,36,'#DDD0A7','#978851',1,8)+ellipse(90,50,8,18,'#F3EEDB','#978851',1)+ellipse(90,50,4,12,'#FFFFFF','#978851',1)+''.join(line(15, y,83,y,'#B5A670',1) for y in [37,44,51,58,64]),scale='organelle')
add('actin','Actin filament symbol','molecules',''.join(circle(9+i*6,46+(4 if i%2 else -4),5,'#B4C8B4','#708B71',.8) for i in range(15)),scale='molecular')

# Cells. Shapes encode specific structural differences, not cosmetic colour variants.
b=path('M24 13 Q50 8 76 13 L82 89 Q51 96 18 89 Z','#E6C1AF',TISSUE_D,1.8)+nucleus(49,68,14,19)
for x in range(25,77,5):b+=path(f'M{x} 14 L{x-1} 3','none',TISSUE_D,1.6)
add('enterocyte','Columnar enterocyte','cells',b,landmarks={'apical':[.5,.12],'basal':[.5,.91],'nucleus':[.49,.68],'microvilli':[.5,.04]},mirror=False,refs=['openstax-epithelium'])
b=path('M19 11 Q48 2 81 11 L73 44 Q67 58 59 67 L64 91 L37 91 L40 67 Q29 57 23 44 Z','#DCE6CF','#78926C',1.6)+ellipse(50,77,10,12,'#A8B796','#6B7E5C',1)
for x,y,r in [(31,22,6),(49,19,7),(67,23,6),(39,37,7),(58,36,7),(48,50,6)]:b+=circle(x,y,r,'#ECF0E3','#A2B191',.7)
add('goblet-cell','Goblet cell','cells',b,landmarks={'mucin-granules':[.49,.25],'nucleus':[.5,.77],'apical':[.5,.1]},mirror=False,refs=['openstax-epithelium'])
add('cuboidal-cell','Cuboidal epithelial cell','cells',path('M13 17 Q48 8 85 17 L88 83 Q49 90 12 83 Z','#E9CBB9',TISSUE_D,1.6)+nucleus(50,54,18,21),refs=['openstax-epithelium'])
add('squamous-cell','Squamous epithelial cell, profile','cells',path('M5 65 Q24 61 33 51 Q51 36 67 51 Q77 61 95 65 L94 74 L6 74 Z','#E9CBB9',TISSUE_D,1.5)+ellipse(51,59,15,8,NUC,NUC_D,1),refs=['openstax-epithelium'])
add('adipocyte','White adipocyte','cells',path('M13 32 Q8 10 43 10 Q76 2 91 29 Q102 56 83 80 Q53 101 24 83 Q5 66 13 32 Z','#EEE1B9','#A38F57',1.6)+ellipse(48,47,33,32,'#FCF7E7','#D0BD82',1)+ellipse(20,68,6,11,NUC,NUC_D,1),refs=['openstax-connective'])
add('erythrocyte','Erythrocyte, oblique disc','blood',ellipse(50,50,42,29,'#CA7D74','#924D49',1.7)+ellipse(50,50,23,13,'#E7AEA5','#B66D63',1)+path('M17 61 Q49 80 82 59','none','#AF6059',1.4),landmarks={'central-pallor':[.5,.5]},refs=['openstax-blood'])
add('erythrocyte-profile','Erythrocyte, sectional profile','blood',path('M9 38 Q19 19 37 38 Q50 50 65 37 Q81 19 92 38 Q105 62 81 69 Q66 71 56 58 Q51 53 43 60 Q23 77 10 62 Q3 52 9 38 Z','#CA7D74','#924D49',1.6),refs=['openstax-blood'])
add('lymphocyte','Lymphocyte','blood',circle(50,50,40,'#E0E7E5',MEM,1.7)+ellipse(48,49,31,32,'#9688B5',NUC_D,1.2)+path('M33 29 Q61 18 68 47 M29 58 Q37 76 58 70','none','#AFA1C7',1.5),refs=['openstax-blood'])
b=circle(50,50,40,'#F0E8E0',MEM,1.5)
for x,y in [(32,35),(61,31),(58,66)]:b+=ellipse(x,y,12,16,'#9D88AF',NUC_D,1)
b+=path('M40 27 Q49 17 54 23 M68 42 Q77 51 69 60 M47 70 Q35 71 34 52','none',NUC_D,2)
for x,y in [(27,63),(45,52),(73,53),(45,80),(72,73),(19,48)]:b+=circle(x,y,1.5,'#BAA4B4','none')
add('neutrophil','Neutrophil','blood',b,refs=['openstax-blood'])
add('monocyte','Monocyte','blood',circle(50,50,41,'#DCE6E8',MEM,1.6)+path('M26 27 Q59 10 73 32 Q86 61 54 78 Q29 83 28 66 Q23 54 43 47 Q60 40 43 40 Q21 45 26 27 Z','#A091B8',NUC_D,1.2),refs=['openstax-blood'])
b=path('M10 32 L24 29 Q18 7 36 18 Q53 1 60 19 Q88 7 83 32 L96 41 L84 56 Q98 76 78 74 Q78 96 61 85 Q40 99 32 83 Q11 92 17 71 Q0 62 15 52 Q1 40 10 32 Z','#CCDCD7','#708F85',1.7)+path('M33 36 Q67 23 70 45 Q72 58 56 67 Q36 73 31 56 Q46 47 33 36 Z','#A291B5',NUC_D,1)
for x,y in [(24,40),(72,75),(78,39),(42,78),(21,62)]:b+=circle(x,y,4,'#B2C6B7','#839E89',.7)
add('macrophage','Macrophage, generic activated outline','blood',b,refs=['openstax-immune'],limits='Generic irregular outline; morphology alone does not establish activation phenotype or function.')
add('platelet','Platelet','blood',path('M30 26 Q37 14 48 29 Q66 16 72 35 Q87 42 73 55 Q82 75 60 74 Q47 88 35 70 Q13 68 27 51 Q13 35 30 26 Z','#C3AACB','#856C93',1.4)+''.join(circle(x,y,2,NUC_D,'none') for x,y in [(41,39),(58,42),(48,62),(64,58),(33,53)]),refs=['openstax-blood'])
add('fibroblast','Fibroblast','cells',path('M3 73 Q29 53 35 37 Q41 24 53 36 Q65 49 97 27 Q74 53 68 66 Q61 82 48 65 Q35 54 3 73 Z','#D4CEB6','#8B886B',1.5)+ellipse(51,51,12,8,NUC,NUC_D,1,transform='rotate(-18 51 51)'),refs=['openstax-connective'])
add('smooth-muscle-cell','Smooth muscle cell','cells',path('M3 55 Q26 27 49 31 Q77 31 97 46 Q74 72 51 69 Q27 71 3 55 Z','#E3B7AF','#A76F66',1.6)+ellipse(50,50,14,7,NUC,NUC_D,1),refs=['openstax-vessels'])
b=rect(7,23,86,53,'#E2BAB2','#A57469',1.4,12)
for x in range(16,91,9):b+=line(x,26,x,73,'#B8877C',1.5)
for x,y in [(19,29),(43,69),(79,29)]:b+=ellipse(x,y,7,2.8,NUC,NUC_D,.7)
add('skeletal-muscle','Skeletal muscle fibre segment','cells',b,refs=['openstax-connective'])
b=path('M36 39 L42 28 L46 4 M41 28 L25 16 L17 5 M28 18 L6 23 M55 37 L71 21 L82 5 M71 21 L96 27 M63 46 L82 40 L97 46 M32 47 L17 39 L2 43 M40 58 L29 72 L8 77 M29 72 L27 91 M58 59 L65 77 L87 88','none','#8C826A',2)
b+=path('M35 34 Q48 27 63 38 Q75 47 62 60 Q48 71 34 59 Q23 48 35 34 Z','#D7D0B2','#8C826A',1.5)+circle(47,46,8,NUC,NUC_D,1)+path('M51 64 L52 93','none','#8C826A',4)
add('neuron','Multipolar neuron, local schematic','cells',b,landmarks={'soma':[.48,.48],'dendrite':[.27,.18],'axon':[.52,.89]},refs=['openstax-organelles'],limits='Truncated neuron symbol, not a complete projection, tract, synaptic circuit or scale-accurate dendritic tree.',mirror=False)
b=''
for x,y in points_on(50,50,45,43,7,-1.2): b+=path(f'M50 50 Q{(50+x)/2+4} {(50+y)/2-3} {x:.2f} {y:.2f}','none','#8DA6AA',5)
b+=circle(50,50,16,'#C4D6D6','#708F94',1.4)+circle(50,50,9,NUC,NUC_D,1)
add('astrocyte','Astrocyte symbol','cells',b,refs=['openstax-organelles'],limits='A generic stellate glial symbol; processes and endfeet are not specimen-derived.')
add('chondrocyte','Chondrocyte in lacuna','cells',ellipse(50,50,39,33,'#EDF0DE','#A4AE81',1)+ellipse(48,48,26,23,'#CAD3B4','#879567',1.5)+nucleus(48,48,11,12),refs=['openstax-connective'])
b=ellipse(50,50,21,13,'#CEBCAA','#97816C',1.4)+nucleus(50,50,9,7)
for x,y in points_on(50,50,45,40,10,.3):b+=path(f'M{50+(x-50)*.36:.2f} {50+(y-50)*.25:.2f} L{x:.2f} {y:.2f}','none','#97816C',1.1)
add('osteocyte','Osteocyte symbol','cells',b,refs=['openstax-connective'])

# Tissue forms and technical motifs.
b=''
for y in [25,37,49,61,73]:
    b+=path(f'M3 {y} C24 {y-13} 35 {y+13} 56 {y} S84 {y-12} 98 {y+1}','none','#B7A787',3)
    for x in range(13,96,13):b+=line(x,y-3,x+2,y+3,'#8D8068',.7)
add('collagen','Collagen fibre bundle','tissue',b,refs=['openstax-connective'],scale='tissue')
add('elastin','Elastic fibre network','tissue',path('M3 24 Q30 9 42 32 T95 28 M5 66 Q29 90 43 67 T98 76 M24 22 Q13 48 32 76 M72 31 Q84 52 66 74','none','#B69C5E',3),refs=['openstax-connective'],scale='tissue')
add('basement-membrane','Basement membrane, planar strip','tissue',path('M2 39 Q30 34 60 39 T118 39 L118 54 Q88 49 58 54 T2 54 Z','#CBC6AC','#8C876D',1.2)+path('M2 58 Q32 52 59 58 T118 58','none','#AAA68A',1.1),w=120,h=90,refs=['openstax-epithelium'],scale='tissue',landmarks={'basal-lamina':[.5,.43],'reticular-side':[.5,.64]})
add('mucus-layer','Mucus layer, schematic','tissue',path('M2 28 Q20 17 34 26 T68 23 T102 24 T138 26 L138 61 Q107 48 73 57 T2 58 Z','#E6ECDB','#A5B28F',1)+path('M13 38 Q26 48 43 36 M67 43 Q81 32 99 43 M107 37 Q119 48 129 38','none','#C1CDAD',1),w=140,h=80,refs=['openstax-epithelium'],scale='tissue')
b=ellipse(50,50,45,42,'#E8D8C4','#A38E73',1.4)+ellipse(50,50,36,34,'#D7A39A','#A3665D',1.3)+ellipse(50,50,26,24,'#E6C5A3','#A58D67',1.3)+ellipse(50,50,22,20,'#FCFBF8','#A38B78',1.2)
for a in range(0,360,30):
    x=50+31*math.cos(math.radians(a)); y=50+29*math.sin(math.radians(a))
    b+=ellipse(x,y,4,1.2,'#9D7069','none',transform=f'rotate({a+90} {x} {y})')
add('artery-section','Muscular artery, transverse schematic','tissue',b,refs=['openstax-vessels'],scale='tissue',landmarks={'lumen':[.5,.5],'intima':[.74,.5],'media':[.81,.5],'adventitia':[.91,.5]},limits='Generic muscular artery section; thickness and shape are explanatory, not a measured vessel or diagnostic wall ratio.')
b=path('M9 37 Q15 10 43 17 Q72 5 90 38 Q101 65 71 85 Q38 95 15 72 Q2 58 9 37 Z','#E4DCCF','#9D9180',1.5)+path('M17 42 Q23 20 46 25 Q68 17 83 43 Q91 64 67 77 Q40 85 22 67 Q10 57 17 42 Z','#BACDDB','#64849A',1.4)+path('M24 45 Q37 26 52 35 Q70 25 76 47 Q81 62 64 68 Q40 77 27 60 Q17 56 24 45 Z','#F3F7F8','#64849A',1)
add('vein-section','Vein, transverse schematic','tissue',b,refs=['openstax-vessels'],scale='tissue',limits='Generic schematic; wall-to-lumen ratio is not quantitative and colour does not assert oxygenation.')
b=path('M8 28 Q50 15 92 29 L92 71 Q51 83 8 71 Z','#F6EEEE','#A97971',1.3)+path('M8 36 Q50 23 92 37 M8 63 Q50 75 92 63','none','#C1968C',1.8)+ellipse(32,29,9,3,NUC,NUC_D,.7)+ellipse(67,71,9,3,NUC,NUC_D,.7)
add('capillary','Capillary, longitudinal schematic','tissue',b,refs=['openstax-vessels'],scale='tissue',landmarks={'lumen':[.5,.5],'endothelium':[.32,.29]})
b=path('M17 70 Q3 42 22 21 Q43 3 67 17 Q94 18 94 45 Q96 67 79 77 L91 93 L75 98 L66 80 Q35 89 17 70 Z','#EAD1BB','#9D7960',1.5)+ellipse(49,46,34,29,'#F9F3E9','#C5A68A',1)
for d in ['M24 37 C48 11 74 44 41 63 C13 65 28 34 65 33 C91 30 71 70 50 68','M35 23 C71 10 76 52 50 57 C31 62 19 42 40 39 C65 33 64 60 38 70']:
    b+=path(d,'none','#BC7F75',4)
add('renal-corpuscle','Renal corpuscle, simplified section','tissue',b,refs=['openstax-kidney'],scale='tissue',landmarks={'glomerulus':[.48,.45],'capsular-space':[.83,.47],'urinary-pole':[.82,.87]},mirror=False,limits='Tuft and capsule shown schematically; vascular pole, filtration ultrastructure and mesangium are not reconstructed.')
# Nephron topology separated from vasculature; continuous lumen paths do not imply blood flow.
b=ellipse(45,41,25,25,'#F1D8C5','#9D7960',1.4)
b+=path('M24 39 C44 15 62 37 47 50 C26 64 28 31 53 31 C72 42 53 60 34 52','none','#BC7F75',3)
nd='M66 47 C97 67 76 12 104 23 C126 32 88 57 114 66 C141 75 140 27 155 37 C170 47 153 67 150 90 L150 212 C150 253 194 251 194 213 L194 99 C194 63 214 56 226 43 C242 28 210 17 205 35 C199 55 233 63 246 47 C261 31 277 53 262 67 L281 81'
b+=path(nd,'none','#B78A54',9)+path(nd,'none','#F5E1C3',5)
b+=path('M286 26 L286 259','none','#98734C',11)+path('M286 26 L286 259','none','#E1C497',7)
add('nephron','Nephron and collecting duct, unfolded map','tissue',b,w=310,h=280,refs=['openstax-kidney'],scale='organ',mirror=False,landmarks={'corpuscle':[45/310,41/280],'proximal-tubule':[111/310,62/280],'descending-limb':[150/310,160/280],'loop':[174/310,241/280],'ascending-limb':[194/310,160/280],'distal-tubule':[232/310,44/280],'collecting-duct':[286/310,179/280]},limits='Unfolded juxtamedullary-type nephron map, not to scale. Tubule calibre/segments are simplified. Collecting duct is associated drainage, not part of the nephron. Vasculature and filtration barrier are omitted.')
add('villus','Intestinal villus, section symbol','tissue',path('M19 93 L20 47 Q20 8 49 6 Q81 8 81 47 L82 93 Z','#E7C4B0','#A17763',1.7)+path('M29 93 L30 48 Q30 18 49 17 Q71 18 71 48 L72 93','#F0E1CA','#B29B7A',1.1)+path('M47 91 L47 42 Q51 30 55 43 L55 91','none','#95AD86',4)+path('M36 90 L36 43 Q37 28 46 24 M63 90 L63 42 Q61 28 53 24','none','#BB7D75',2),refs=['openstax-epithelium'],scale='tissue',mirror=False,landmarks={'epithelium':[.8,.55],'core':[.4,.55],'central-lacteal':[.51,.7]},limits='Generic villus section. Capillary circuit, innervation, muscle and lymph drainage are incomplete.')

# Equipment are not anatomical assets; workflows remain descriptive, not operating protocols.
add('microtube','Microcentrifuge tube','equipment',path('M30 18 L70 18 L70 65 L52 91 Q50 95 48 91 L30 65 Z','#F1F4F5','#80929B',1.5)+rect(24,10,51,10,'#D2E0E3','#80929B',1.3,3)+path('M34 52 L66 52 L66 64 L50 87 L34 64 Z','#C5DCDD','none',0),scale='equipment',refs=['house-design'])
add('petri-dish','Petri dish','equipment',path('M8 40 L8 60 C10 84 90 84 92 60 L92 40 Z','#E4EBE8','#84978E',1.3)+ellipse(50,40,42,23,'#F4F2DD','#84978E',1.3)+ellipse(50,40,35,17,'none','#BAB88F',.8),scale='equipment',refs=['house-design'])
add('culture-flask','Cell-culture flask','equipment',path('M33 17 L62 17 L62 35 L84 51 L83 86 L16 86 L16 48 L33 34 Z','#EFF3F4','#81949D',1.3)+rect(30,9,35,10,'#BACCD3','#81949D',1,2)+path('M21 60 L78 60 L78 81 L21 81 Z','#E8CEC5','none'),scale='equipment',refs=['house-design'])
add('microscope','Optical microscope symbol','equipment',path('M44 23 Q78 19 79 56 L70 75 L85 85 L84 92 L14 92 L14 84 L53 81 Q74 64 65 44 L53 41 Z','#C6D2D7','#566F7B',1.5)+path('M30 9 L45 15 L32 45 L19 39 Z','#8FA6B2','#566F7B',1.5)+rect(18,53,42,7,'#91A7B2','#566F7B',1,2)+circle(65,53,8,'#E5ECEF','#566F7B',1.4),scale='equipment',refs=['house-design'])
add('pipette','Micropipette symbol','equipment',path('M44 15 L58 15 L63 31 L59 62 L52 80 L47 92 L43 78 L40 60 L39 31 Z','#DEE7EA','#718791',1.4)+rect(43,6,16,10,'#AAC5D0','#718791',1,2)+rect(45,30,11,19,'#FBFCFA','#718791',.8,1),scale='equipment',refs=['house-design'])
add('microscope-slide','Microscope slide','equipment',rect(6,29,88,45,'#F0F4F4','#8B9DA3',1.5,2)+rect(9,32,18,39,'#DDE5E8','none')+rect(47,35,32,32,'none','#AEBBC0',1)+ellipse(61,52,9,7,'#B9CDD0','#86A5AE',1),scale='equipment',refs=['house-design'])
b=rect(3,13,114,74,'#E5EBEC','#81969E',1.4,5)
for row in range(8):
    for col in range(12):b+=circle(10+col*9,20+row*8.5,2.5,'#F9FAFA','#96AAB1',.65)
add('well-plate-96','96-well plate, 8 by 12','equipment',b,w=120,h=100,scale='equipment',refs=['house-design'],limits='Exactly 8 rows by 12 columns; no sample identity, assay results, dispensing order or operating protocol is encoded.')
add('sample-vial','Sample vial','equipment',rect(27,18,47,72,'#EEF2F3','#8298A2',1.3,9)+rect(24,10,53,17,'#BBCFD7','#8298A2',1.3,3)+rect(32,51,37,29,'#DDE9E7','none',0,3)+rect(33,33,35,20,'#FFFFFF','#B5C3C8',.7,1),scale='equipment',refs=['house-design'])


# A continuous tissue assembly: boundaries and landmarks are authored together.
b=path('M10 73 Q180 68 360 73 T710 73 L710 237 Q530 242 360 237 T10 237 Z','#E8C3AF','#A17763',1.4)
for i in range(1,8):
    x=10+i*87.5
    b+=path(f'M{x} 73 Q{x-3} 125 {x+2} 170 L{x} 237','none','#B08673',1.4)
for i in range(8):
    cx=53.75+i*87.5
    if i!=4:
        b+=nucleus(cx,184,18,24)
        for x in range(round(cx-35),round(cx+37),7):b+=path(f'M{x} 73 L{x-1} 58','none','#A17763',1.4)
        for x,y in [(cx-23,118),(cx+17,138)]:
            b+=ellipse(x,y,5,11,'#D9BC91','#A48B62',.7)+line(x-2,y-6,x+2,y+5,'#AD966D',.7)
    else:
        b+=path(f'M{cx-33} 72 Q{cx} 60 {cx+33} 72 L{cx+27} 125 Q{cx+24} 149 {cx+8} 163 L{cx+13} 232 L{cx-13} 232 L{cx-8} 163 Q{cx-27} 147 {cx-28} 125 Z','#DCE6CF','#83986F',1.4)
        b+=ellipse(cx,204,11,17,'#A8B796','#6B7E5C',1)
        for dx,dy,r in [(-17,88,7),(0,84,8),(17,89,7),(-10,105,8),(11,105,8),(0,125,7)]: b+=circle(cx+dx,dy,r,'#F2F3E6','#A8B494',.8)
for x in [97.5,185,272.5,360,447.5,535,622.5]:
    b+=line(x-5,83,x+5,83,'#628E88',4)+line(x-5,89,x+5,89,'#628E88',3)
b+=path('M10 242 Q180 238 360 242 T710 242 L710 251 Q530 248 360 251 T10 251 Z','#C8C2A7','#8F896E',1.1)
for x in range(18,690,86):b+=path(f'M{x} 270 Q{x+22} 252 {x+54} 269','none','#C0AD8C',1.6)
add('epithelial-sheet','Continuous epithelial tissue section','tissue',b,w=720,h=280,scale='tissue',mirror=False,refs=['openstax-epithelium'],landmarks={'microvilli':[.16,.215],'apical':[.14,.26],'enterocyte':[.20,.46],'nucleus':[53.75/720,184/280],'goblet-cell':[403.75/720,120/280],'mucin':[403.75/720,90/280],'junction':[185/720,86/280],'basement-membrane':[.25,246/280],'connective-tissue':[.78,.96]},limits='Original continuous epithelial schematic with illustrative cell counts and geometry. No measured histology, species-specific morphology, disease severity or diagnostic evidence is encoded.')
add('process-node','Process node, house notation','notation',rect(30,30,40,40,'#FFFFFF','#354753',2),landmarks={'left':[.3,.5],'right':[.7,.5],'top':[.5,.3],'bottom':[.5,.7]},scale='molecular',refs=['house-design'],limits='A process glyph for the declared house notation, not an assertion of SBGN conformance.')

if __name__=='__main__':
    ids=[a['id'] for a in ASSETS]
    assert len(ids)==len(set(ids))
    DATA.mkdir(parents=True,exist_ok=True)
    (DATA/'assets.json').write_text(json.dumps({'version':'1.0.0','assets':ASSETS},indent=2)+'\n')
    print(f'Wrote {len(ASSETS)} original schematic assets')
