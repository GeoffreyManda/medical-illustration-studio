"""Atlas plate composition and material-aware SVG rendering.

The anatomical contours are authored explicitly. Texture and lighting never create,
move or name an anatomical structure. All plate lettering remains separate vectors.
"""
from __future__ import annotations
from copy import deepcopy
from html import escape
import json, math, re
from typing import Any, Mapping
import xml.etree.ElementTree as ET
from jsonschema import Draft202012Validator
from . import core


def library() -> dict[str, Any]:
    rows=core.resource('atlas-assets.json')['assets']
    result={}
    for row in rows:
        issues=core.asset_issues(row)
        if issues: raise core.IllustrationError(f"{row.get('id')}: {issues[0].message}")
        if row['id'] in result: raise core.IllustrationError('Duplicate atlas asset ID')
        result[row['id']]=row
    return result


def material(name: str) -> dict[str, Any]:
    rows=core.resource('tissue-materials.json')['materials']
    if name not in rows: raise core.IllustrationError(f'Unknown material: {name}')
    return deepcopy(rows[name])


class Paint:
    """Bounded passive SVG paint primitives. Geometry is supplied, never inferred."""
    def __init__(self, width: float, height: float, title: str):
        if not (0 < width <= 10000 and 0 < height <= 10000):
            raise core.IllustrationError('Invalid paint dimensions')
        self.width,self.height,self.title=width,height,title
        self.defs=[];self.body=[];self.counter=0
    def uid(self, stem='paint'):
        self.counter+=1;return f'{stem}-{self.counter}'
    def gradient(self, name: str, colours: list[str], *, radial=False, vector=None):
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9-]*',name): raise core.IllustrationError('Invalid gradient ID')
        if len(colours)<2 or any(not re.fullmatch(r'#[0-9a-fA-F]{6}',c) for c in colours):
            raise core.IllustrationError('Gradient needs at least two hex colours')
        tag='radialGradient' if radial else 'linearGradient'
        attrs='cx="32%" cy="25%" r="83%"' if radial else 'x1="0%" y1="0%" x2="100%" y2="70%"'
        if vector is not None:
            if len(vector)!=4 or any(not math.isfinite(float(v)) for v in vector): raise core.IllustrationError('Invalid gradient vector')
            attrs='gradientUnits="userSpaceOnUse" '+ ' '.join(f'{k}="{v}"' for k,v in zip(['x1','y1','x2','y2'],vector))
        stops=''.join(f'<stop offset="{100*i/(len(colours)-1):.2f}%" stop-color="{c}"/>' for i,c in enumerate(colours))
        self.defs.append(f'<{tag} id="{name}" {attrs}>{stops}</{tag}>');return f'url(#{name})'
    def clip(self, path: str, name=None):
        name=name or self.uid('clip')
        self.defs.append(f'<clipPath id="{name}"><path d="{path}"/></clipPath>');return name
    def add(self, text: str): self.body.append(text)
    def path(self, d: str, fill='none', stroke=None, width=1, opacity=1, id=None):
        a=f' fill="{fill}"'
        if stroke: a+=f' stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'
        if opacity!=1:a+=f' opacity="{opacity}"'
        if id:a+=f' id="{id}"'
        self.add(f'<path d="{d}"{a}/>')
    def tube(self,d: str,width:float,colours: list[str],id=None):
        if width<=0 or len(colours)!=4:raise core.IllustrationError('Tube needs a positive width and four colours')
        if id:self.add(f'<g id="{id}">')
        for frac,c in zip([1,.88,.64,.28],colours): self.path(d,stroke=c,width=width*frac)
        if id:self.add('</g>')
    def finish(self):
        svg=f'<svg xmlns="{core.SVG_NS}" viewBox="0 0 {self.width} {self.height}" role="img"><title>{escape(self.title)}</title><defs>'+''.join(self.defs)+'</defs>'+''.join(self.body)+'</svg>'
        core.secure_svg(svg);return svg


def staged_svg(svg: str, stage: str) -> str:
    if stage not in {'colour','values','contours'}: raise core.IllustrationError('Unknown painting stage')
    root=core.secure_svg(svg)
    if stage=='colour':return svg
    if stage=='contours':
        # Detail marks do not substitute for the anatomical drawing.
        for parent in root.iter():
            for child in list(parent):
                if child.get('id','').startswith('texture-'):parent.remove(child)
        for node in root.iter():
            if core.local_name(node.tag) in {'path','ellipse','circle','polygon','polyline','rect'}:
                node.set('fill','none');node.set('stroke','#74695F');node.set('stroke-width','0.9');node.set('opacity','0.65')
    else:
        def gray(m):
            c=m[0]; rgb=[int(c[i:i+2],16) for i in (1,3,5)]
            g=round(.2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2]);return '#'+f'{g:02X}'*3
        for node in root.iter():
            for k,v in list(node.attrib.items()):node.set(k,re.sub(r'#[0-9A-Fa-f]{6}\b',gray,v))
    return ET.tostring(root,encoding='unicode')


def validate_plate(plate: Mapping[str, Any], assets=None) -> list[core.Issue]:
    errors=[core.Issue('PLATE-SCHEMA','.'.join(map(str,e.path)),e.message) for e in Draft202012Validator(core.resource('plate.schema.json')).iter_errors(plate)]
    if errors:return errors
    assets=assets or library(); p=plate
    if p['asset'] not in assets:return [core.Issue('PLATE-ASSET','asset','Unknown anatomical asset')]
    a=assets[p['asset']]
    if p['anatomy']['view']!=a['view']:
        errors.append(core.Issue('PLATE-VIEW','anatomy.view','Declared view must match the authored asset; a text field cannot change viewpoint'))
    if p['label_size']*p['print_width_mm']*72/25.4/p['width'] < 7:
        errors.append(core.Issue('PLATE-TYPE','label_size','Labels fall below 7 pt at specified print width'))
    if not core.contained(p['art_box'],[0,115,p['width'],p['height']-265]):
        errors.append(core.Issue('PLATE-BOUNDS','art_box','Artwork outside the allocated illustration area'))
    used=set()
    for i,l in enumerate(p['labels']):
        if l['landmark'] not in a['landmarks']:errors.append(core.Issue('PLATE-LANDMARK',f'labels.{i}','Unknown landmark'))
        if l['landmark'] in used:errors.append(core.Issue('PLATE-LANDMARK',f'labels.{i}','Duplicate target landmark'))
        used.add(l['landmark'])
    if p['art_box'][2] <= 0 or p['art_box'][3] <= 0:
        errors.append(core.Issue('PLATE-BOUNDS','art_box','Artwork dimensions must be positive'))
    if p['intended_use']=='clinical-publication':
        errors.append(core.Issue('PLATE-REVIEW','intended_use','This plate compositor does not confer medical approval. Use an independently reviewed source and the review-bound scene publication workflow.'))
    return errors


def label_layout(plate,asset):
    """Stable, ordered two-bank labelling with bounded vertical separation."""
    node={'id':'anatomy','box':plate['art_box']};fs=plate['label_size'];w=plate['width']
    result=[]
    for side in ('left','right'):
        rows=[]
        for label in plate['labels']:
            if label['side']!=side:continue
            target_asset=asset
            if 'target' in label:
                target_asset=deepcopy(asset);target_asset['landmarks'][label['landmark']]=label['target']
            target=core.landmark(node,target_asset,label['landmark'])
            width=plate['label_bank_width']
            lines=core.wrap_text(label['text'],width,fs)
            rows.append({'label':label,'target':target,'lines':lines,'height':len(lines)*fs*1.28,'desired':label.get('y',target[1])})
        rows.sort(key=lambda r:r['desired'])
        start=145;end=plate['height']-170;gap=18
        if sum(r['height']+gap for r in rows)>end-start:
            raise core.IllustrationError('Label bank is overfull; split this plate rather than shrink lettering')
        for i,row in enumerate(rows):
            row['y']=max(row['desired']-row['height']/2,start if not i else rows[i-1]['y']+rows[i-1]['height']+gap)
        if rows and rows[-1]['y']+rows[-1]['height']>end:
            rows[-1]['y']=end-rows[-1]['height']
            for i in range(len(rows)-2,-1,-1):rows[i]['y']=min(rows[i]['y'],rows[i+1]['y']-rows[i]['height']-gap)
        for r in rows:
            r['side']=side;r['x']=42 if side=='left' else w-42-plate['label_bank_width'];r['width']=plate['label_bank_width'];result.append(r)
    return result


def render_plate(plate, assets=None, *, stage='colour', labels=True):
    assets=assets or library();errors=validate_plate(plate,assets)
    if errors:raise core.IllustrationError('; '.join(f'{e.code}: {e.message}' for e in errors))
    a=deepcopy(assets[plate['asset']]);a['svg']=staged_svg(a['svg'],stage)
    w,h=plate['width'],plate['height'];mm=plate['print_width_mm'];fs=plate['label_size'];e=escape
    parts=[f'<svg xmlns="{core.SVG_NS}" viewBox="0 0 {w} {h}" width="{mm}mm" height="{mm*h/w:.4f}mm" role="img" aria-labelledby="plate-title plate-desc">',f'<title id="plate-title">{e(plate["title"])}</title><desc id="plate-desc">{e(plate["description"])}</desc>',f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>',f'<text x="42" y="52" font-family="Georgia, Times New Roman, serif" font-size="30" fill="#292620">{e(plate["title"])}</text>',f'<text x="42" y="83" font-family="{core.FONT}" font-size="15" fill="#69645E">{e(plate["subtitle"])}</text>',core._embed(a,{'id':'anatomy','box':plate['art_box']})]
    if labels:
        parts.append('<g id="plate-labels">')
        for r in label_layout(plate,a):
            tx,ty=r['target'];cy=r['y']+r['height']/2
            if r['side']=='left':
                # Leaders leave the actual text, not an arbitrary label rectangle.
                tw=max(core.text_width(line,fs) for line in r['lines']);sx=r['x']+tw+7;ex=max(sx+8,min(tx-15,r['x']+r['width']+22))
            else:sx=r['x']-8;ex=min(sx-8,max(tx+15,r['x']-25))
            parts.append(f'<g id="plate-label-{e(r["label"]["landmark"])}">')
            parts.append(f'<path d="M{sx:.3f} {cy:.3f} L{ex:.3f} {cy:.3f} L{tx:.3f} {ty:.3f}" fill="none" stroke="#665E57" stroke-width="0.85"/>')
            parts.append(f'<circle cx="{tx:.3f}" cy="{ty:.3f}" r="1.6" fill="#665E57"/>')
            parts.append(core._draw_text(r['label']['text'],[r['x'],r['y']-fs*.12,r['width'],r['height']],fs,'#38332E'))
            parts.append('</g>')
        parts.append('</g>')
    parts.append(core._draw_text(plate['caption'],[42,h-115,w-84,54],14,'#625B53'))
    parts.append(core._draw_text(plate['reference_line'],[42,h-47,w-84,26],11,'#7A7269'))
    parts.append('</svg>');svg=''.join(parts);core.secure_svg(svg);return svg


def generation_brief(plate, assets=None):
    """A provider-neutral painting brief. It does not call a model or verify anatomy."""
    assets=assets or library()
    errors=validate_plate(plate,assets)
    if errors:raise core.IllustrationError(errors[0].message)
    a=assets[plate['asset']]
    contract=core.resource('anatomy-contracts.json')['contracts'].get(a['id'],{})
    return {'subject':a['label'],'view':a['view'],'mode':'edit supplied contour/reference only','anatomy_must_preserve':contract.get('invariants',[]),'visible_structures':[l['text'] for l in plate['labels']], 'rendering':'Classical clinical atlas painting, restrained gouache-like modelling, material-specific texture, directional fibres, quiet white page. Preserve supplied topology and silhouette.','forbidden':['baked-in labels or leader lines','signatures, credentials, institutions or endorsements','invented branches or unexplained tissue removal','ornament, glow, lens effects or background anatomy','using texture to invent diagnostic detail'],'labels':'Render separately from validated landmarks after artwork review.','delivery':'Unlabelled artwork plus masks/layers when supported. A flattened bitmap is not editable anatomy.','review_status':'unreviewed_candidate'}


def plate_record(plate, assets=None):
    assets=assets or library();a=assets[plate['asset']]
    svg=render_plate(plate,assets)
    return {'plate_id':plate['id'],'version':core.VERSION,'scene_sha256':core.sha256(core.canonical(plate)),'asset_sha256':core.sha256(a['svg']),'output_sha256':core.sha256(svg),'anatomical_review':'not performed independently','rendering':'original structured SVG; labels are editable vectors','sources':a['reference_ids'],'checks':[i.to_dict() for i in validate_plate(plate,assets)]}
