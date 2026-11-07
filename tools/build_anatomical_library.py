"""Build original, structure-first anatomical SVG assets. No downloaded artwork.

Contours and named landmarks are authored here. Procedural marks model material,
not anatomical identity; they are deterministic and clipped to an explicit region.
"""
from pathlib import Path
import sys,json,math,random
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from medillustrate.atelier import Paint
from medillustrate import core

OUTER='M420 80 C265 35 153 150 116 350 C77 552 108 757 243 858 C356 943 499 896 534 790 C557 722 519 657 478 613 C437 569 416 526 438 477 C457 432 509 404 540 359 C608 257 546 125 420 80 Z'
SINUS='M381 263 C342 282 320 331 328 378 C280 407 283 448 316 478 C294 520 315 565 352 578 C339 628 361 679 403 701 C437 676 445 627 452 586 C462 550 485 518 501 488 C470 453 467 413 435 384 C449 335 425 288 381 263 Z'
PYRAMIDS=[((306,150),(433,166),(395,302)),((203,211),(274,170),(337,347)),((152,339),(184,256),(309,410)),((143,478),(141,386),(308,478)),((170,629),(146,530),(323,550)),((249,785),(192,700),(356,626)),((404,831),(290,824),(402,684))]


def record(id,label,svg,landmarks,width,height,refs,view,scale='organ',aliases=()):
    points={'centre':[.5,.5],'top':[.5,.02],'bottom':[.5,.98],'left':[.02,.5],'right':[.98,.5]}
    points.update({k:[round(x/width,6),round(y/height,6)] for k,(x,y) in landmarks.items()})
    return {'id':id,'label':label,'category':'anatomical-plates','svg':svg,'view_box':[0,0,width,height],'landmarks':points,'scale_class':scale,'representation':'anatomical','view':view,'mirror_safe':False,'license':'CC0-1.0','creator':'Medical Illustration Studio; original authored SVG geometry and deterministic material rendering, AI-assisted','reference_ids':refs,'review_status':'anatomical_unreviewed','limitations':'Original idealised educational anatomy; not a patient reconstruction. Independent anatomical review has not been completed. Texture, relative dimensions and structure counts are illustrative rather than measured.','aliases':list(aliases)}


def dot(p,x,y,r,fill,opacity=1):
    p.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}" opacity="{opacity:.3f}"/>')


def vessel(p,d,w,kind,cap):
    cs={'artery':['#87483F','#B76050','#DD8973','#EAA68E'],'vein':['#435D6C','#668699','#98B4C2','#B7CDD5'],'ureter':['#AD8A65','#D0AC80','#E9CAA3','#F3DCB9']}[kind]
    p.tube(d,w,cs)
    x,y,rx,ry=cap
    p.add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{cs[0]}" stroke="{cs[2]}" stroke-width="3"/>')
    p.add(f'<ellipse cx="{x}" cy="{y}" rx="{rx*.57:.2f}" ry="{ry*.68:.2f}" fill="{cs[0]}"/>')


def kidney(section=True):
    p=Paint(800,1000,'Kidney, coronal section' if section else 'Kidney, external surface')
    cortex=p.gradient('cortex',['#F2C0A8','#DEA087','#C0846D','#9D6654'],radial=True)
    cap=p.gradient('capsule',['#EDD0B8','#BD886B','#835F4D'],radial=True)
    cutedge=p.gradient('cut-edge',['#F9DEBF','#E0AE90','#A76D55'])
    sinus=p.gradient('sinus',['#F4E1BA','#DEC092','#B99160'],radial=True)
    surface=p.gradient('surface',['#DBA087','#BE7866','#A66252','#734B40'],radial=True)
    c=p.clip(OUTER,'organ-clip')
    # The visible downstream ureter remains continuous with the pelvis.
    vessel(p,'M450 495 C512 505 562 543 575 602 C590 683 577 827 599 944',38,'ureter',(599,944,19,8))
    vessel(p,'M454 444 C500 429 563 423 676 435',35,'artery',(676,435,12,17.5))
    vessel(p,'M448 486 C513 481 583 471 688 487',47,'vein',(688,487,12,23.5))
    p.path(OUTER,cap,stroke='#8F6552',width=1.4,id='kidney-capsule')
    p.add('<g transform="translate(9 9) scale(.98 .978)">');p.path(OUTER,cortex if section else surface,id='renal-parenchyma');p.add('</g>')
    p.path('M404 91 C257 57 163 176 131 352 C99 538 125 749 254 849',stroke='#EBD0B5',width=3.3,opacity=.85)
    rng=random.Random(763)
    if section:
        # Grain remains a visual texture. It is not a gross-scale image of glomeruli.
        p.add(f'<g id="texture-cortex" clip-path="url(#{c})">')
        for _ in range(1250):
            x,y=rng.uniform(100,565),rng.uniform(80,885)
            dot(p,x,y,rng.uniform(.5,1.9),rng.choice(['#8E4D43','#F8DBC3','#D69B82','#B27863']),rng.uniform(.12,.40))
        p.add('</g>')
        p.path(SINUS,sinus,stroke='#C29A73',width=1.1,id='renal-sinus')
        cs=p.clip(SINUS,'sinus-clip');p.add(f'<g id="texture-sinus-fat" clip-path="url(#{cs})">')
        for _ in range(95):
            x,y=rng.uniform(291,490),rng.uniform(275,708);r=rng.uniform(3,11)
            p.add(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{r:.2f}" ry="{r*.7:.2f}" fill="#F2DDB1" stroke="#CEAA7A" stroke-width=".65" opacity=".6"/>')
        p.add('</g>')
        # Opened collecting system. The upper, middle and lower branches merge.
        channels=[('M393 311 C397 355 377 365 382 405 C386 456 421 474 450 495',34),('M336 354 C354 375 368 387 382 405',28),('M308 417 C333 432 358 432 393 438',27),('M309 484 C357 478 401 482 450 495',30),('M324 556 C358 555 380 541 417 520',30),('M357 633 C393 627 397 601 412 575 C429 546 442 525 450 495',32),('M402 686 C422 656 414 611 412 575',28)]
        p.add('<g id="collecting-system">')
        for d,w in channels:p.tube(d,w,['#B99B73','#DFC197','#EED6AF','#F7E6C7'])
        p.path('M430 473 C447 457 464 461 483 475 C518 501 548 523 565 563 L553 585 C529 551 482 544 447 525 C432 516 422 490 430 473 Z',p.gradient('pelvic-wall',['#F6E4C2','#E2C499','#C6A17A']),stroke='#C09C74',width=1.3,id='renal-pelvis')
        p.path('M443 482 C466 482 503 514 548 547',stroke='#FAEBD0',width=13,opacity=.8)
        p.add('</g>')
        for i,(a,b,t) in enumerate(PYRAMIDS):
            ax,ay=a;bx,by=b;tx,ty=t
            mx,my=(ax+bx)/2,(ay+by)/2
            # Slightly convex base; convergent sides retain the papilla.
            bendx=mx-(tx-mx)*.10;bendy=my-(ty-my)*.10
            d=f'M{ax} {ay} Q{bendx:.2f} {bendy:.2f} {bx} {by} C{bx*.52+tx*.48:.2f} {by*.55+ty*.45:.2f} {tx+12} {ty-3} {tx} {ty} C{tx-12} {ty+4} {ax*.52+tx*.48:.2f} {ay*.55+ty*.45:.2f} {ax} {ay} Z'
            colour=p.gradient(f'medulla-{i}',['#E4AC92','#CD9078','#B47463','#955C53'],vector=[mx,my,tx,ty])
            p.path(d,colour,stroke='#BC826B',width=1.3,id=f'renal-pyramid-{i+1}')
            clip=p.clip(d,f'pyramid-clip-{i}');p.add(f'<g id="texture-pyramid-{i}" clip-path="url(#{clip})">')
            for j in range(78):
                u=j/77;x=ax+(bx-ax)*u;y=ay+(by-ay)*u
                dx=tx-x;dy=ty-y;curl=math.sin(u*math.pi)*8
                dline=f'M{x:.2f} {y:.2f} C{x+dx*.30+curl:.2f} {y+dy*.30:.2f} {tx-dx*.26+curl*.3:.2f} {ty-dy*.25:.2f} {tx+(u-.5)*8:.2f} {ty:.2f}'
                p.path(dline,stroke=['#F8D3B4','#8E554C','#BB7A64'][j%3],width=rng.uniform(.5,1.15),opacity=[.45,.35,.28][j%3])
            p.add('</g>')
            # A small papillary highlight stops before the calyceal wall.
            p.path(f'M{tx-6} {ty-3} Q{tx} {ty+2} {tx+5} {ty-3}',stroke='#F0C4A4',width=2.6)
        # Selected interlobar/arcuate vascular routes, not a complete vascular tree.
        for d in ['M457 437 C421 437 387 416 354 392 C298 351 231 338 171 350', 'M452 486 C413 497 377 513 333 566 C298 608 232 648 189 655', 'M376 395 C326 339 300 280 279 206']:
            p.path(d,stroke='#9C5649',width=3.7,opacity=.8);p.path(d,stroke='#DC9477',width=1.35,opacity=.85)
    else:
        # Explicit superficial vein marks, only within the established silhouette.
        p.add(f'<g id="texture-surface" clip-path="url(#{c})">')
        for j in range(160):
            x,y=rng.uniform(140,520),rng.uniform(125,840)
            p.path(f'M{x:.1f} {y:.1f} q{rng.uniform(-5,5):.1f} 5 {rng.uniform(-8,8):.1f} 12',stroke='#E9B69B',width=.65,opacity=.16)
        p.add('</g>')
        p.path('M502 281 C525 348 488 394 434 444 C403 474 392 518 420 563 C445 601 475 617 488 654',stroke='#704A3B',width=14,opacity=.32)
        p.path('M508 287 C521 348 481 396 435 436',stroke='#EDBC9C',width=4,opacity=.4)
        for d in ['M434 442 C376 403 344 350 301 309 C269 278 261 235 240 207','M429 446 C354 474 305 518 281 589 C265 628 238 643 216 660','M412 490 C368 469 295 458 240 437 C211 426 190 410 175 393']:
            p.path(d,stroke='#D6B0A0',width=1.5,opacity=.38)
    landmarks={'capsule':(128,329),'cortex':(220,243),'medulla':(220,423),'papilla':(309,478),'minor-calyx':(326,484),'major-calyx':(412,595),'pelvis':(462,501),'ureter':(593,805),'artery':(623,430),'vein':(631,480),'column':(196,518),'sinus':(382,452),'upper-pole':(347,80),'lower-pole':(355,891),'lateral-border':(109,538),'hilum':(442,467),'anterior-surface':(290,514)}
    if not section:
        landmarks={k:v for k,v in landmarks.items() if k in {'upper-pole','lower-pole','lateral-border','hilum','anterior-surface','ureter','artery','vein'}}
    return record('atlas-kidney-section' if section else 'atlas-kidney-surface','Kidney, opened coronal section' if section else 'Kidney, external surface',p.finish(),landmarks,800,1000,['openstax-kidney-gross'], 'coronal illustrative section' if section else 'external illustrative view',aliases=['renal','cortex','medullary pyramids','calyces','ureter'])


def artery():
    p=Paint(900,800,'Muscular artery, oblique section')
    rng=random.Random(412)
    outer=p.gradient('adventitia',['#EDDEC9','#C9B497','#AB947B'],radial=True)
    media=p.gradient('media',['#F0C1B2','#D79588','#AF6E65'],radial=True)
    lumen=p.gradient('lumen',['#DFA997','#B77667','#8B574D'],radial=True)
    sheath='M171 141 C240 106 384 133 544 218 C638 267 718 363 718 478 C718 602 623 690 514 675 C361 655 233 524 155 396 C108 314 102 215 171 141 Z'
    p.path(sheath,outer,stroke='#B79C83',width=1.3,id='tunica-adventitia-surface')
    clip=p.clip(sheath,'artery-clip')
    p.add(f'<g id="texture-adventitia" clip-path="url(#{clip})">')
    for j in range(105):
        y=140+j*4.5;x=140+math.sin(j*.25)*14
        p.path(f'M{x:.2f} {y:.2f} C{230+j*.8:.2f} {y-20:.2f} 400 {y+110:.2f} 650 {y+185:.2f}',stroke=['#F5E5CF','#A99077','#D7C2A5'][j%3],width=rng.uniform(.6,1.6),opacity=.42)
    p.add('</g>')
    # End-on elliptical cut; all envelopes share one plane.
    p.add('<g id="artery-cut-face">')
    for rx,ry,col,stroke in [(206,227,outer,'#B59C80'),(178,199,media,'#C08D7C'),(136,156,'#C8AF78','#967C4F'),(126,146,'#EFDAC1','#E2C3AA'),(115,134,lumen,'#B57D6B')]:
        p.add(f'<ellipse cx="514" cy="459" rx="{rx}" ry="{ry}" fill="{col}" stroke="{stroke}" stroke-width="1.7"/>')
    # Oblique concentric smooth-muscle bundles remain circumferential.
    p.add('<g id="texture-muscular-media">')
    for i in range(16):
        rx=140+i*2.3;ry=160+i*2.3
        p.add(f'<ellipse cx="514" cy="459" rx="{rx:.2f}" ry="{ry:.2f}" fill="none" stroke="{["#EAC0AA","#AC746C"][i%2]}" stroke-width=".85" opacity=".57"/>')
    for j in range(86):
        th=2*math.pi*j/86;r=rng.uniform(.04,.95);rx=139+r*35;ry=159+r*35
        x=514+rx*math.cos(th);y=459+ry*math.sin(th)
        p.add(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="3.5" ry="1" transform="rotate({math.degrees(th)+90:.2f} {x:.2f} {y:.2f})" fill="#8F625F" opacity=".45"/>')
    p.add('</g>')
    # Folded internal elastic lamina, one continuous membrane.
    pts=[]
    for i in range(541):
        t=i/540*2*math.pi;wave=2.6*math.sin(t*48)
        pts.append((514+(134+wave)*math.cos(t),459+(154+wave)*math.sin(t)))
    d='M'+' L'.join(f'{x:.2f} {y:.2f}' for x,y in pts)+' Z'
    p.path(d,stroke='#967C4D',width=1.8,id='internal-elastic-lamina')
    # Inner wall face and soft highlight signal an open lumen, not a solid disc.
    p.path('M407 442 C404 370 455 329 513 326 C568 323 610 370 622 422',stroke='#F0C7AE',width=4,opacity=.65)
    p.add('</g>')
    # Sparse vasa vasorum on the outer coat only.
    for d in ['M177 183 C220 229 223 279 265 324 C294 355 292 394 316 419','M235 292 C208 304 201 329 211 361']:
        p.path(d,stroke='#BD7465',width=3,opacity=.8);p.path(d,stroke='#D7AB92',width=.9)
    marks={'adventitia':(349,578),'media':(652,540),'elastic-lamina':(592,588),'intima':(407,510),'lumen':(523,457),'vasa-vasorum':(249,309),'outer-coat':(235,408)}
    return record('atlas-arterial-wall','Muscular artery, oblique section',p.finish(),marks,900,800,['openstax-vessels'],'oblique illustrative section','tissue',['artery','tunica media','elastic lamina','vessel'])


def nerve():
    p=Paint(900,800,'Peripheral nerve, oblique section');rng=random.Random(54)
    epi=p.gradient('epineurium',['#F0E6CD','#D2C1A0','#A99572'],radial=True)
    face=p.gradient('epineurial-face',['#EFE7CF','#DDD1AE','#C7B48A'],radial=True)
    peri=p.gradient('perineurium',['#F7E7B9','#D9C38A','#B7A06B'],radial=True)
    endo=p.gradient('endoneurium',['#F9EBC7','#EAD5A5','#D3B983'],radial=True)
    sheath='M213 90 C130 82 89 153 113 235 C152 364 273 540 411 618 C537 687 697 622 736 499 C774 374 688 273 583 228 C441 170 309 105 213 90 Z'
    p.path(sheath,epi,stroke='#B5A07B',width=1.25,id='epineurium-surface');c=p.clip(sheath,'nerve-clip')
    p.add(f'<g id="texture-nerve-length" clip-path="url(#{c})">')
    for j in range(125):
        y=112+j*3.9
        p.path(f'M113 {y:.2f} C225 {y-15:.2f} 378 {y+149:.2f} 624 {y+198:.2f}',stroke=['#FAEDD0','#A99A7B','#E7D7B3'][j%3],width=rng.uniform(.6,1.7),opacity=.43)
    p.add('</g>')
    p.add(f'<ellipse id="epineurium-cut-face" cx="530" cy="440" rx="218" ry="192" fill="{face}" stroke="#BCA780" stroke-width="2.6"/>')
    fascicles=[(466,324,59,49),(588,330,52,44),(400,418,54,63),(529,433,60,56),(656,438,49,58),(466,544,58,47),(591,550,51,44)]
    for i,(x,y,rx,ry) in enumerate(fascicles):
        p.add(f'<g id="fascicle-{i+1}"><ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{peri}" stroke="#B49A62" stroke-width="1.4"/>')
        p.add(f'<ellipse cx="{x}" cy="{y}" rx="{rx-6}" ry="{ry-6}" fill="{endo}" stroke="#F9EBCA" stroke-width="1.6"/>')
        pts=[]
        for yy in range(-int(ry)+13,int(ry)-10,12):
            for xx in range(-int(rx)+13,int(rx)-10,13):
                dx=xx+(6 if (yy//12)%2 else 0)+rng.uniform(-1.7,1.7);dy=yy+rng.uniform(-1.7,1.7)
                if (dx/(rx-13))**2+(dy/(ry-12))**2<1:pts.append((x+dx,y+dy))
        p.add(f'<g id="texture-fascicle-{i}">')
        for xx,yy in pts:
            rr=rng.uniform(3.6,5.2)
            p.add(f'<ellipse cx="{xx:.2f}" cy="{yy:.2f}" rx="{rr:.2f}" ry="{rr*.86:.2f}" fill="#F7E9C6" stroke="#B69D66" stroke-width=".85"/>')
            dot(p,xx,yy,rr*.32,'#B9874D',.88)
        p.add('</g></g>')
    # Small nutrient vessels are confined to connective tissue between fascicles.
    for x,y,rx,ry in [(532,325,7,9),(604,459,7,10),(435,490,6,8)]:
        p.add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#A56754" stroke="#E4AE8A" stroke-width="2.4"/>')
    for d in ['M152 171 C214 201 256 238 321 270 C355 288 369 307 385 332','M273 247 C255 268 279 304 305 324']:
        p.path(d,stroke='#B87561',width=2.6,opacity=.8)
    marks={'epineurium':(719,489),'fascicle':(457,551),'perineurium':(576,483),'endoneurium':(544,430),'myelinated-fibres':(481,316),'vasa-nervorum':(604,458),'longitudinal-bundles':(256,284)}
    return record('atlas-peripheral-nerve','Peripheral nerve, oblique section',p.finish(),marks,900,800,['openstax-peripheral-nerves'],'oblique illustrative section','tissue',['nerve','fascicle','perineurium','epineurium','myelin'])


def main():
    rows=[kidney(True),kidney(False),artery(),nerve()]
    for row in rows:
        err=core.asset_issues(row)
        if err:raise RuntimeError(err)
    (ROOT/'medillustrate/data/atlas-assets.json').write_text(json.dumps({'version':'2.0.0','assets':rows},ensure_ascii=False,indent=2)+'\n')
    print('Built',len(rows),'anatomical assets;',sum(len(r['svg']) for r in rows),'SVG characters')

if __name__=='__main__':main()
