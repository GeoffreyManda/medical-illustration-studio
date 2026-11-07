"""Deterministic scene validation, SVG composition, safe local imports and review binding.

Geometry checks are geometric checks, not independent verification of medical truth.
No network access, model calls, patient-image generation or proprietary assets are used.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from importlib.resources import files
from copy import deepcopy
from html import escape
from datetime import date
import hashlib
import json
import math
from functools import lru_cache
import re
import xml.etree.ElementTree as ET
from typing import Any, Mapping, Sequence
from defusedxml import ElementTree as SafeET
from jsonschema import Draft202012Validator

VERSION = '1.0.0'
SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)
MAX_FILE = 8_000_000
MAX_SVG = 1_000_000
MAX_PIXELS = 40_000_000
FONT = 'DejaVu Sans, Arial, sans-serif'
BIOLOGICAL_EDGES = {'activation','inhibition','association','transport','consumption','production'}
ALLOWED_TAGS = {'svg','g','path','circle','ellipse','rect','line','polyline','polygon','text','tspan','title','desc','defs','linearGradient','radialGradient','stop','clipPath'}
ALLOWED_ATTRIBUTES = {
 'id','role','aria-label','aria-labelledby','viewBox','preserveAspectRatio','version',
 'x','y','x1','x2','y1','y2','dx','dy','width','height','cx','cy','r','rx','ry','d','points',
 'transform','fill','fill-rule','fill-opacity','stroke','stroke-width','stroke-linecap',
 'stroke-linejoin','stroke-miterlimit','stroke-dasharray','stroke-dashoffset','stroke-opacity',
 'opacity','clip-path','clip-rule','font-family','font-size','font-weight','font-style',
 'text-anchor','dominant-baseline','style','offset','stop-color','stop-opacity',
 'gradientUnits','gradientTransform','spreadMethod','fx','fy','fr','clipPathUnits',
}
STYLE_PROPS = {'fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','stroke-dasharray','fill-rule','fill-opacity','stroke-opacity','opacity','font-family','font-size','font-weight','font-style','text-anchor','stop-color','stop-opacity','clip-path'}

class IllustrationError(ValueError):
    """An invalid, unsupported or unsafe illustration input."""

@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str
    severity: str = 'error'

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def resource(name: str) -> Any:
    if not re.fullmatch(r'[a-z][a-z0-9.-]*\.json', name):
        raise IllustrationError('Invalid bundled resource name')
    return json.loads(files('medillustrate').joinpath('data', name).read_text(encoding='utf-8'))


def load_json(path: str | Path) -> Any:
    p = Path(path)
    if p.stat().st_size > MAX_FILE:
        raise IllustrationError('JSON input exceeds the 8 MB limit')
    def no_constant(value: str) -> None:
        raise IllustrationError(f'Non-finite JSON number: {value}')
    try:
        return json.loads(p.read_text(encoding='utf-8'), parse_constant=no_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise IllustrationError(f'Invalid UTF-8 JSON: {exc}') from exc


def write_file(path: str | Path, value: str | bytes, *, force: bool = False) -> Path:
    p = Path(path)
    if p.exists() and not force:
        raise IllustrationError(f'Refusing to overwrite {p}; pass --force deliberately')
    if not p.parent.exists():
        raise IllustrationError(f'Output directory does not exist: {p.parent}')
    if isinstance(value, bytes): p.write_bytes(value)
    else: p.write_text(value, encoding='utf-8')
    return p


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',',':'), ensure_ascii=False, allow_nan=False).encode('utf-8')


def sha256(value: bytes | str) -> str:
    return hashlib.sha256(value.encode('utf-8') if isinstance(value,str) else value).hexdigest()


def local_name(tag: str) -> str:
    if tag.startswith('{') and not tag.startswith('{'+SVG_NS+'}'):
        raise IllustrationError('Unsupported XML namespace')
    return tag.rsplit('}',1)[-1]


def secure_svg(svg: str) -> ET.Element:
    """Accept a bounded passive SVG subset. Reject unsupported features, never guess.

    Filters, images, use, foreignObject, CSS blocks and external/embedded resources
    are intentionally unsupported. Trusted editor artwork may need conversion to
    plain paths before import. SVG sanitisation is not a proof of anatomy or rights.
    """
    if not isinstance(svg,str) or len(svg.encode('utf-8')) > MAX_SVG:
        raise IllustrationError('SVG must be UTF-8 text of at most 1 MB')
    if re.search(r'<!DOCTYPE|<!ENTITY', svg, re.I):
        raise IllustrationError('DTD and entity declarations are forbidden')
    try:
        root = SafeET.fromstring(svg)
    except Exception as exc:
        raise IllustrationError(f'Invalid or unsafe SVG XML: {exc}') from exc
    if local_name(root.tag) != 'svg': raise IllustrationError('Expected an SVG root')
    ids: set[str] = set(); referenced: set[str] = set()
    stack=[(root,0)]; count=0
    while stack:
        element, depth = stack.pop(); count += 1
        if count>20000 or depth>64: raise IllustrationError('SVG complexity limit exceeded')
        if local_name(element.tag) not in ALLOWED_TAGS:
            raise IllustrationError(f'Unsupported SVG element: {local_name(element.tag)}')
        stack.extend((child, depth+1) for child in element)
        for key, value in element.attrib.items():
            attr=local_name(key)
            if attr.lower().startswith('on') or attr not in ALLOWED_ATTRIBUTES:
                raise IllustrationError(f'Unsupported SVG attribute: {attr}')
            lower=value.lower()
            if any(s in lower for s in ('javascript:','data:','http:','https:','file:','@import','expression(','var(')):
                raise IllustrationError(f'Active or external SVG value in {attr}')
            if attr=='style':
                for entry in value.split(';'):
                    if not entry.strip(): continue
                    if ':' not in entry: raise IllustrationError('Invalid inline SVG style')
                    prop, val=entry.split(':',1)
                    if prop.strip() not in STYLE_PROPS: raise IllustrationError(f'Unsupported SVG style: {prop}')
                    if any(t in val for t in ('{','}','@','\\')): raise IllustrationError('Unsafe style value')
            if 'url(' in lower:
                refs=re.findall(r'url\(\s*#([A-Za-z_][\w.-]*)\s*\)',value)
                if len(refs)!=lower.count('url('): raise IllustrationError('Only local fragment URLs are accepted')
                referenced.update(refs)
            if attr=='id':
                if not re.fullmatch(r'[A-Za-z_][\w.-]*',value) or value in ids:
                    raise IllustrationError('Invalid or duplicate SVG id')
                ids.add(value)
            if attr in {'x','y','x1','y1','x2','y2','cx','cy','r','rx','ry','width','height','d','points','transform','gradientTransform'}:
                nums=re.findall(r'[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?',value)
                if any(not math.isfinite(float(v)) or abs(float(v))>1e7 for v in nums):
                    raise IllustrationError('Excessive or non-finite SVG coordinate')
            if attr=='d':
                if len(value)>400000 or not re.fullmatch(r'[MmZzLlHhVvCcSsQqTtAa0-9eE+.,\s-]*',value):
                    raise IllustrationError('Unsupported SVG path syntax')
            if attr in {'transform','gradientTransform'}:
                if not re.fullmatch(r'(?:(?:matrix|translate|scale|rotate|skewX|skewY)\s*\([0-9eE+.,\s-]+\)\s*)+',value):
                    raise IllustrationError('Unsupported SVG transform')
    if not referenced.issubset(ids): raise IllustrationError('SVG references an undefined fragment')
    vb = root.attrib.get('viewBox')
    if vb is None: raise IllustrationError('SVG requires an explicit viewBox')
    try:
        values=[float(x) for x in re.split(r'[\s,]+',vb.strip())]
    except ValueError as exc: raise IllustrationError('Invalid SVG viewBox') from exc
    if len(values)!=4 or not all(math.isfinite(v) for v in values) or min(values[2:])<=0 or max(abs(v) for v in values)>100000:
        raise IllustrationError('Invalid or excessive SVG viewBox')
    return root


def asset_issues(asset: Mapping[str,Any]) -> list[Issue]:
    out=[]
    for e in Draft202012Validator(resource('asset.schema.json')).iter_errors(asset):
        out.append(Issue('LIC-01','asset.'+'.'.join(map(str,e.path)),e.message))
    if out: return out
    try:
        root=secure_svg(asset['svg'])
        vb=[float(x) for x in re.split(r'[\s,]+',root.attrib['viewBox'].strip())]
        if vb!=asset['view_box']:
            out.append(Issue('FMT-03','asset.view_box','Metadata view_box differs from SVG viewBox'))
    except IllustrationError as exc: out.append(Issue('SEC-01','asset.svg',str(exc)))
    for field in ['license','creator','limitations']:
        if not str(asset[field]).strip(): out.append(Issue('LIC-01',f'asset.{field}','Field may not be empty'))
    return out


def assets(extra: str | Path | Mapping[str,Any] | None = None) -> dict[str,Any]:
    rows=deepcopy(resource('assets.json')['assets'])
    if extra is not None:
        ext=load_json(extra) if isinstance(extra,(str,Path)) else extra
        if not isinstance(ext,Mapping): raise IllustrationError('An asset or asset catalogue object is required')
        rows += list(ext['assets']) if 'assets' in ext else [dict(ext)]
    result={}
    for row in rows:
        problems=asset_issues(row)
        if problems: raise IllustrationError(f"Invalid asset {row.get('id','?')}: {problems[0].message}")
        if row['id'] in result: raise IllustrationError(f"Duplicate asset id: {row['id']}")
        result[row['id']]=row
    return result


def layout_by_id(id: str) -> dict[str,Any]:
    found=next((x for x in resource('layouts.json')['layouts'] if x['id']==id),None)
    if found is None: raise IllustrationError(f'Unknown layout: {id}')
    return deepcopy(found)


def resolve_scene(scene: Mapping[str,Any]) -> dict[str,Any]:
    result=deepcopy(dict(scene))
    layout=layout_by_id(result['layout']) if result.get('layout') else None
    for node in result.get('nodes',[]):
        if 'slot' in node:
            if not layout or node['slot'] not in layout['slots']:
                raise IllustrationError(f"Unknown slot {node['slot']} in the selected layout")
            x,y,w,h=layout['slots'][node.pop('slot')]
            cw,ch=result['canvas']['width'],result['canvas']['height']
            node['box']=[x*cw,y*ch,w*cw,h*ch]
    return result


def contained(a: Sequence[float], b: Sequence[float], tolerance: float=.01) -> bool:
    return a[0]>=b[0]-tolerance and a[1]>=b[1]-tolerance and a[0]+a[2]<=b[0]+b[2]+tolerance and a[1]+a[3]<=b[1]+b[3]+tolerance


def intersects(a: Sequence[float],b: Sequence[float]) -> bool:
    return min(a[0]+a[2],b[0]+b[2])>max(a[0],b[0])+.01 and min(a[1]+a[3],b[1]+b[3])>max(a[1],b[1])+.01


def placement(node: Mapping[str,Any], asset: Mapping[str,Any]) -> tuple[float,float,float,int,bool]:
    x,y,w,h=node['box']; aw,ah=asset['view_box'][2:]
    rotation=node.get('rotation',0)
    if rotation in (90,270): aw,ah=ah,aw
    return x+w/2,y+h/2,min(w/aw,h/ah),rotation,node.get('flip_x',False)


def landmark(node: Mapping[str,Any],asset: Mapping[str,Any],name: str) -> tuple[float,float]:
    if name not in asset['landmarks']: raise IllustrationError(f'Unknown landmark: {name}')
    px,py=asset['landmarks'][name]
    cx,cy,scale,rotation,flip=placement(node,asset)
    aw,ah=asset['view_box'][2:]
    dx=(px-.5)*aw*scale*(-1 if flip else 1); dy=(py-.5)*ah*scale
    r=math.radians(rotation)
    return cx+dx*math.cos(r)-dy*math.sin(r),cy+dx*math.sin(r)+dy*math.cos(r)


@lru_cache(maxsize=48)
def _font(size: float, bold: bool=False):
    try:
        from PIL import ImageFont
        return ImageFont.truetype('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',round(size*4))
    except (ImportError,OSError): return None


def text_width(text: str,size: float,bold: bool=False) -> float:
    f=_font(size,bold)
    return f.getlength(text)/4 if f is not None else len(text)*size*.64


def wrap_text(text: str,width: float,size: float,bold: bool=False) -> list[str]:
    result=[]
    for paragraph in text.split('\n'):
        line=''
        for word in paragraph.split():
            candidate=(line+' '+word).strip()
            if line and text_width(candidate,size,bold)>width:
                result.append(line); line=word
            else: line=candidate
        result.append(line)
    return result or ['']


def contrast_ratio(a: str,b: str) -> float:
    def luminance(col: str):
        channels=[int(col[i:i+2],16)/255 for i in (1,3,5)]
        channels=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in channels]
        return sum(v*w for v,w in zip(channels,(.2126,.7152,.0722)))
    la,lb=sorted((luminance(a),luminance(b)))
    return (lb+.05)/(la+.05)


def _finite(value: Any) -> bool:
    if isinstance(value,float): return math.isfinite(value)
    if isinstance(value,dict): return all(_finite(v) for v in value.values())
    if isinstance(value,list): return all(_finite(v) for v in value)
    return True


def validate(scene: Mapping[str,Any], library: Mapping[str,Any] | None = None, *, publication: bool=False, review: Mapping[str,Any] | None=None) -> list[Issue]:
    if not _finite(scene): return [Issue('FMT-04','scene','Non-finite values are not allowed')]
    out=[]
    for e in Draft202012Validator(resource('scene.schema.json')).iter_errors(scene):
        out.append(Issue('FMT-01','.'.join(map(str,e.path)) or 'scene',e.message))
    if out: return out
    lib=library if library is not None else assets()
    try: s=resolve_scene(scene)
    except IllustrationError as exc: return [Issue('FMT-03','layout',str(exc))]
    w,h=s['canvas']['width'],s['canvas']['height']; canvas=[0,0,w,h]
    if w*h>MAX_PIXELS: out.append(Issue('SEC-04','canvas','Canvas exceeds 40 million coordinate pixels'))
    maps={}
    for field in ['nodes','edges','labels','compartments','sources','claims','scale_bars','relations']:
        ids=[v['id'] for v in s.get(field,[])]
        if len(ids)!=len(set(ids)): out.append(Issue('FMT-02',field,'Duplicate IDs within namespace'))
        maps[field]={v['id']:v for v in s.get(field,[])}
    nodes=maps['nodes']; comps=maps['compartments']; claims=maps['claims']; source_ids=set(maps['sources'])
    for claim in s['claims']:
        if not set(claim['sources']).issubset(source_ids): out.append(Issue('FMT-03',f"claims.{claim['id']}",'Claim source does not resolve'))
        if claim['status']=='established' and not claim['sources']: out.append(Issue('SEM-02',f"claims.{claim['id']}",'Established claims require evidence sources'))
        if claim['status']=='established' and any(maps['sources'][x]['kind']=='illustrative' for x in claim['sources'] if x in source_ids):
            out.append(Issue('SEM-02',f"claims.{claim['id']}",'Illustrative sources cannot establish a biological claim'))
    def check_ref(ref: Mapping[str,Any],path: str):
        if ref['node'] not in nodes: out.append(Issue('FMT-03',path,'Unknown target node')); return
        aid=nodes[ref['node']]['asset']
        if aid in lib and ref['landmark'] not in lib[aid]['landmarks']:
            out.append(Issue('GEO-03',path,'Landmark is not defined on this asset'))
    for field in ['compartments','nodes','labels']:
        for v in s[field]:
            if not contained(v['box'],canvas): out.append(Issue('GEO-01',f"{field}.{v['id']}.box",'Object lies outside canvas'))
    for node in s['nodes']:
        aid=node['asset']; p=f"nodes.{node['id']}"
        if aid not in lib: out.append(Issue('FMT-03',p,'Unknown asset')); continue
        asset=lib[aid]
        if node.get('flip_x') and not asset['mirror_safe']: out.append(Issue('GEO-06',p,'This asset cannot be mirrored'))
        if s['representation']=='anatomical' and node.get('role','primary')=='primary' and asset['representation']!='anatomical':
            out.append(Issue('SCI-02',p,'A schematic symbol cannot serve as primary anatomical geometry'))
        cid=node.get('compartment'); pos=node.get('placement','inside')
        if cid:
            if cid not in comps: out.append(Issue('FMT-03',p,'Unknown compartment'))
            elif pos=='inside' and not contained(node['box'],comps[cid]['box']): out.append(Issue('GEO-04',p,'Node is outside its rectangular compartment'))
            elif pos=='boundary':
                b=comps[cid]['box']; a=node['box']
                if not intersects(a,b) or contained(a,b): out.append(Issue('GEO-05',p,'Boundary node must intersect and extend across the compartment boundary'))
    for e in s['edges']:
        p=f"edges.{e['id']}"; check_ref(e['source'],p+'.source'); check_ref(e['target'],p+'.target')
        if e['type'] in BIOLOGICAL_EDGES and 'claim' not in e: out.append(Issue('SEM-01',p,'Biological relationship requires a claim'))
        if 'claim' in e and e['claim'] not in claims: out.append(Issue('FMT-03',p,'Unknown edge claim'))
        if e['type']=='consumption' and nodes.get(e['target']['node'],{}).get('kind')!='process': out.append(Issue('SEM-06',p,'Consumption must end at a process node'))
        if e['type']=='production' and nodes.get(e['source']['node'],{}).get('kind')!='process': out.append(Issue('SEM-06',p,'Production must start at a process node'))
        if 'label_position' in e and not e.get('label'): out.append(Issue('FMT-01',p,'Label position requires label text'))
        for pt in e.get('via',[])+([e['label_position']] if 'label_position' in e else []):
            if not (0<=pt[0]<=w and 0<=pt[1]<=h): out.append(Issue('GEO-01',p,'Edge control point or label position outside canvas'))
    part_graph={n:set() for n in nodes}; directions={}
    inverses={'anterior_to':'posterior_to','superior_to':'inferior_to','medial_to':'lateral_to','superficial_to':'deep_to','proximal_to':'distal_to'}
    reverse={v:k for k,v in inverses.items()}
    for rel in s.get('relations',[]):
        a,b,pred=rel['subject'],rel['object'],rel['predicate']; rp=f"relations.{rel['id']}"
        if a not in nodes or b not in nodes or rel['claim'] not in claims:
            out.append(Issue('FMT-03',rp,'Structural relation references an unknown entity or claim')); continue
        if a==b: out.append(Issue('SEM-12',rp,'A structural relation must connect distinct entities')); continue
        if pred=='part_of': part_graph[a].add(b)
        elif pred=='contains': part_graph[b].add(a)
        if pred in inverses or pred in reverse:
            axis=pred if pred in inverses else reverse[pred]
            x,y=(a,b) if pred in inverses else (b,a)
            if (axis,y,x) in directions:
                out.append(Issue('SEM-13',rp,'Opposite spatial relations conflict for the same pair'))
            directions[(axis,x,y)]=True
    indegree={entity:0 for entity in part_graph}
    for parents in part_graph.values():
        for parent in parents: indegree[parent]+=1
    ready=[entity for entity,value in indegree.items() if value==0]; seen_count=0
    while ready:
        entity=ready.pop();seen_count+=1
        for parent in part_graph[entity]:
            indegree[parent]-=1
            if indegree[parent]==0: ready.append(parent)
    if seen_count!=len(part_graph):
        out.append(Issue('SEM-12','relations','Part-of / contains relations create a cycle'))
    minpt=s['canvas']['minimum_label_pt']; factor=s['canvas']['print_width_mm']*72/(25.4*w)
    for label in s['labels']:
        p=f"labels.{label['id']}"; size=label.get('font_size',18); x,y,bw,bh=label['box']
        if 'target' in label: check_ref(label['target'],p+'.target')
        if size*factor+1e-8<minpt: out.append(Issue('TXT-02',p,f'Label is {size*factor:.2f} pt at final width, below {minpt:g} pt'))
        lines=wrap_text(label['text'],bw,size,label.get('role')=='heading')
        if len(lines)*size*1.32>bh+.1 or any(text_width(line,size,label.get('role')=='heading')>bw+.1 for line in lines): out.append(Issue('TXT-03',p,'Text does not fit its declared label box'))
        for pt in label.get('leader_via',[]):
            if not (0<=pt[0]<=w and 0<=pt[1]<=h): out.append(Issue('GEO-01',p,'Leader control point outside canvas'))
    labels=s['labels']
    for i,a in enumerate(labels):
        for b in labels[i+1:]:
            if intersects(a['box'],b['box']): out.append(Issue('TXT-04',f"labels.{a['id']}",f"Label box overlaps {b['id']}"))
    if text_width(s['title'],34,True)>w-100: out.append(Issue('TXT-03','title','Title exceeds the one-line title area; shorten it'))
    caption_lines=wrap_text(s['caption'],w-100,17)
    if len(caption_lines)>3: out.append(Issue('TXT-03','caption','Caption exceeds three lines; use the companion text'))
    colour=s['canvas']['text_colour']
    if contrast_ratio(colour,s['canvas']['background'])<4.5: out.append(Issue('ACC-02','canvas.text_colour','Text contrast below the 4.5:1 house threshold'))
    for comp in s['compartments']:
        if comp['label'] and contrast_ratio(colour,comp['fill'])<4.5: out.append(Issue('ACC-02',f"compartments.{comp['id']}",'Compartment heading has insufficient contrast'))
    if not s['description'].strip(): out.append(Issue('ACC-01','description','A useful text description is required'))
    for b in s.get('scale_bars',[]):
        if s['frame']['scale_policy']!='calibrated': out.append(Issue('SCI-03',f"scale_bars.{b['id']}",'Scale bars require calibrated scale policy'))
        if b['source'] not in source_ids: out.append(Issue('SCI-03',f"scale_bars.{b['id']}",'Calibration source must resolve'))
        if not math.isclose(b['length_px']*b['units_per_px'],b['physical_length'],rel_tol=1e-6): out.append(Issue('SCI-03',f"scale_bars.{b['id']}",'Scale-bar length and calibration disagree'))
        if b['start'][0]<0 or b['start'][1]<0 or b['start'][0]+b['length_px']>w or b['start'][1]+26>h:
            out.append(Issue('GEO-01',f"scale_bars.{b['id']}",'Scale bar outside canvas'))
    if publication and not any(i.severity=='error' for i in out): out.extend(review_issues(s,lib,review))
    elif not publication and any(lib[n['asset']]['review_status']!='expert_reviewed' for n in s['nodes'] if n['asset'] in lib):
        out.append(Issue('SCI-REVIEW','scene','Contains schematic or imported artwork without independent asset-level medical review. Final figure review is required before use as authoritative medical material.','warning'))
    return out


def number(v: float) -> str:
    if abs(v)<1e-9: v=0
    return f'{v:.4f}'.rstrip('0').rstrip('.') if isinstance(v,(float,int)) else str(v)


def _draw_text(text: str, box: Sequence[float],size: float=18,colour: str='#354753',align: str='left',weight: str='normal') -> str:
    x,y,w,h=box; lines=wrap_text(text,w,size,weight=='bold')
    tx=x+w if align=='right' else x+w/2 if align=='centre' else x
    anchor={'right':'end','centre':'middle','left':'start'}[align]
    spans=''.join(f'<tspan x="{number(tx)}" y="{number(y+size+i*size*1.32)}">{escape(line)}</tspan>' for i,line in enumerate(lines))
    return f'<text font-family="{FONT}" font-size="{number(size)}" text-anchor="{anchor}" fill="{colour}" font-weight="{weight}">{spans}</text>'


def _embed(asset: Mapping[str,Any],node: Mapping[str,Any]) -> str:
    root=secure_svg(asset['svg']); prefix='asset-'+node['id']+'-'
    for item in root.iter():
        for key,value in list(item.attrib.items()):
            if key=='id': item.set(key,prefix+value)
            elif 'url(' in value: item.set(key,re.sub(r'url\(\s*#([\w.-]+)\s*\)',lambda m:'url(#'+prefix+m[1]+')',value))
    # Do not repeat the standalone asset title inside the final accessible diagram.
    children=[c for c in root if local_name(c.tag) not in {'title','desc'}]
    body=''.join(ET.tostring(c,encoding='unicode').replace(' xmlns="'+SVG_NS+'"','') for c in children)
    inherited={k:v for k,v in root.attrib.items() if local_name(k) not in {'viewBox','width','height','x','y','id','role','aria-label','aria-labelledby','version','preserveAspectRatio'}}
    if inherited:
        attributes=' '.join(f'{k}="{escape(v,quote=True)}"' for k,v in inherited.items())
        body=f'<g {attributes}>'+body+'</g>'
    cx,cy,scale,rot,flip=placement(node,asset); vx,vy,aw,ah=asset['view_box']
    transform=f'translate({number(cx)} {number(cy)}) rotate({rot}) scale({number(-scale if flip else scale)} {number(scale)}) translate({number(-vx-aw/2)} {number(-vy-ah/2)})'
    return f'<g id="node-{node["id"]}" transform="{transform}">{body}</g>'


def _render_validated(s: Mapping[str,Any],lib: Mapping[str,Any]) -> str:
    w,h=s['canvas']['width'],s['canvas']['height']; colour=s['canvas']['text_colour']
    nodes={n['id']:n for n in s['nodes']}; claims={c['id']:c for c in s['claims']}
    def target(ref):
        node=nodes[ref['node']]; return landmark(node,lib[node['asset']],ref['landmark'])
    out=[f'<svg xmlns="{SVG_NS}" width="{number(s["canvas"]["print_width_mm"])}mm" height="{number(h/w*s["canvas"]["print_width_mm"])}mm" viewBox="0 0 {number(w)} {number(h)}" role="img" aria-labelledby="figure-title figure-description">',
         '<title id="figure-title">'+escape(s['title'])+'</title>',
         '<desc id="figure-description">'+escape(s['description'])+'</desc>',
         f'<rect width="{number(w)}" height="{number(h)}" fill="{s["canvas"]["background"]}"/>',
         '<defs><marker id="arrow-flow" viewBox="0 -5 10 10" refX="9" refY="0" markerWidth="10" markerHeight="10" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 -4 L9 0 L0 4 Z" fill="#354753"/></marker><marker id="arrow-activation" viewBox="0 -6 11 12" refX="10" refY="0" markerWidth="11" markerHeight="12" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 -5 L10 0 L1 5" fill="none" stroke="#354753" stroke-width="1.8"/></marker><marker id="arrow-inhibition" viewBox="-2 -8 5 16" refX="0" refY="0" markerWidth="5" markerHeight="16" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 -7 L0 7" stroke="#354753" stroke-width="2.2"/></marker></defs>',
         _draw_text(s['title'],[50,31,w-100,48],34,colour,weight='bold')]
    if s.get('subtitle'): out.append(_draw_text(s['subtitle'],[50,82,w-100,45],18,colour))
    for c in s['compartments']:
        x,y,cw,ch=c['box']; dash=' stroke-dasharray="6 5"' if c['boundary']=='dashed' else ''
        stroke='none' if c['boundary']=='none' else '#B8C4C7'
        out.append(f'<rect id="compartment-{c["id"]}" x="{number(x)}" y="{number(y)}" width="{number(cw)}" height="{number(ch)}" fill="{c["fill"]}" stroke="{stroke}" stroke-width="1"{dash}/>')
        if c['label']: out.append(_draw_text(c['label'],[x+14,y+9,cw-28,28],17,colour))
    for node in s['nodes']: out.append(_embed(lib[node['asset']],node))
    for e in s['edges']:
        pts=[target(e['source'])]+e.get('via',[])+[target(e['target'])]
        data='M'+' L'.join(number(p[0])+' '+number(p[1]) for p in pts)
        status=claims[e['claim']]['status'] if e.get('claim') else 'established'
        dashed=status!='established' or e['type']=='zoom'
        dash=' stroke-dasharray="7 5"' if dashed else ''
        marker='arrow-inhibition' if e['type']=='inhibition' else 'arrow-activation' if e['type']=='activation' else 'arrow-flow' if e['type'] in {'transport','sequence','consumption','production'} else None
        end=f' marker-end="url(#{marker})"' if marker else ''
        out.append(f'<path id="edge-{e["id"]}" d="{data}" fill="none" stroke="{e.get("colour","#354753")}" stroke-width="1.8" stroke-linejoin="round"{dash}{end}/>')
        if e.get('label'):
            p=e.get('label_position') or [(pts[0][0]+pts[-1][0])/2,(pts[0][1]+pts[-1][1])/2-25]
            out.append(_draw_text(e['label'],[p[0],p[1],max(text_width(e['label'],17)+4,70),28],17,colour))
    for label in s['labels']:
        x,y,lw,lh=label['box']
        if 'target' in label:
            tx,ty=target(label['target'])
            # Exit the nearest side of the text rectangle, not its centre.
            if tx<x: start=[x-5,min(max(ty,y+10),y+lh-4)]
            elif tx>x+lw: start=[x+lw+5,min(max(ty,y+10),y+lh-4)]
            elif ty<y: start=[min(max(tx,x+4),x+lw-4),y-5]
            else: start=[min(max(tx,x+4),x+lw-4),y+lh+4]
            pts=[start]+label.get('leader_via',[])+[[tx,ty]]
            d='M'+' L'.join(number(p[0])+' '+number(p[1]) for p in pts)
            out.append(f'<path d="{d}" fill="none" stroke="#61727B" stroke-width="1.05" stroke-linejoin="round"/><circle cx="{number(tx)}" cy="{number(ty)}" r="2.25" fill="#61727B"/>')
        out.append(_draw_text(label['text'],label['box'],label.get('font_size',18),colour,label.get('align','left'),'bold' if label.get('role')=='heading' else 'normal'))
    for b in s.get('scale_bars',[]):
        x,y=b['start']; length=b['length_px']
        out.append(f'<path d="M{number(x)} {number(y-5)} V{number(y)} H{number(x+length)} V{number(y-5)}" fill="none" stroke="{colour}" stroke-width="2"/>')
        out.append(_draw_text(b['label'],[x,y+5,max(length,160),25],17,colour))
    out.append(f'<path d="M50 {number(h-100)} H{number(w-50)}" fill="none" stroke="#CCD4D5" stroke-width="1"/>')
    out.append(_draw_text(s['caption'],[50,h-83,w-100,74],17,colour))
    out.append('</svg>')
    return '\n'.join(out)+'\n'


def render(scene: Mapping[str,Any],library: Mapping[str,Any] | None=None, *, publication: bool=False,review: Mapping[str,Any] | None=None) -> str:
    lib=library if library is not None else assets()
    issues=validate(scene,lib,publication=publication,review=review)
    errors=[i for i in issues if i.severity=='error']
    if errors: raise IllustrationError('\n'.join(f'{i.code} {i.path}: {i.message}' for i in errors))
    return _render_validated(resolve_scene(scene),lib)


def binding(scene: Mapping[str,Any],library: Mapping[str,Any]) -> dict[str,str]:
    s=resolve_scene(scene); used={n['asset']:library[n['asset']] for n in s['nodes']}
    return {'scene_sha256':sha256(canonical(s)), 'assets_sha256':sha256(canonical(used)),
            'renderer_sha256':sha256(Path(__file__).read_bytes()),
            'svg_sha256':sha256(_render_validated(s,library))}


def review_issues(scene: Mapping[str,Any],library: Mapping[str,Any],review: Mapping[str,Any] | None) -> list[Issue]:
    if review is None: return [Issue('REL-01','review','Publication mode requires a human review record for the current figure')]
    out=[]
    if not scene['nodes']:
        out.append(Issue('REL-01','scene.nodes','A blank scaffold cannot be released as a publication figure'))
    expected=binding(scene,library)
    for key,value in expected.items():
        if review.get(key)!=value: out.append(Issue('REL-02',f'review.{key}','Missing or stale artifact binding'))
    approvals=review.get('approvals',[])
    if not isinstance(approvals,list): return out+[Issue('REL-03','review.approvals','Expected a list of human approvals')]
    valid={}; identities=set()
    for approval in approvals:
        if not isinstance(approval,Mapping): out.append(Issue('REL-03','review.approvals','Malformed approval')); continue
        if approval.get('role') not in {'scientific','visual'}: out.append(Issue('REL-03','review.role','Expected scientific or visual review role')); continue
        role=approval['role']
        fields=['name','reviewer_id','qualification','date','statement']
        if not all(isinstance(approval.get(f),str) and approval[f].strip() for f in fields) or approval.get('approved') is not True:
            out.append(Issue('REL-03','review.approvals','Explicit named approval, identity, qualification, date and statement are required')); continue
        try: date.fromisoformat(approval['date'])
        except ValueError: out.append(Issue('REL-03','review.date','Review date must be ISO YYYY-MM-DD')); continue
        valid[role]=approval; identities.add(approval['reviewer_id'])
    if set(valid)!={'scientific','visual'} or len(identities)<2:
        out.append(Issue('REL-03','review.approvals','Separate named scientific and visual reviewers are required'))
    # This checks record completeness and artifact binding, not identity authenticity.
    return out


def control_record(scene: Mapping[str,Any],library: Mapping[str,Any] | None=None) -> dict[str,Any]:
    lib=library if library is not None else assets(); issues=validate(scene,lib)
    if any(x.severity=='error' for x in issues): raise IllustrationError('Cannot bind a structurally invalid scene')
    return {'tool':'medillustrate','version':VERSION,**binding(scene,lib),'sources':scene['sources'],
            'assets':[{'id':id,'creator':lib[id]['creator'],'license':lib[id]['license'],'reference_ids':lib[id]['reference_ids'],'review_status':lib[id]['review_status']} for id in sorted({n['asset'] for n in scene['nodes']})],
            'checks':[i.to_dict() for i in issues], 'approvals':[],
            'limits':['This record is not a medical certificate.','Human identity and qualifications require independent verification.','Review the final raster/PDF export as well as the SVG.']}


def import_svg(path: str | Path, *, id: str,label: str,creator: str,license: str,source_url: str,representation: str='schematic',scale_class: str='cell') -> dict[str,Any]:
    p=Path(path)
    if p.stat().st_size>MAX_SVG: raise IllustrationError('SVG input exceeds 1 MB')
    if not all(v.strip() for v in [creator,license,source_url]): raise IllustrationError('Creator, licence and source URL are mandatory')
    if not re.match(r'^(https://|http://|urn:)',source_url): raise IllustrationError('Use an explicit public source URL or documented provenance URN')
    text=p.read_text(encoding='utf-8'); root=secure_svg(text)
    vb=[float(x) for x in re.split(r'[\s,]+',root.attrib['viewBox'].strip())]
    a={'id':id,'label':label,'category':'imported','svg':text,'view_box':vb,
       'landmarks':{'centre':[.5,.5],'top':[.5,0],'bottom':[.5,1],'left':[0,.5],'right':[1,.5]},
       'scale_class':scale_class,'representation':representation,'view':'not yet specified; verify before use',
       'mirror_safe':False,'license':license,'creator':creator,'reference_ids':[],'source_url':source_url,
       'review_status':'imported_unreviewed','limitations':'Imported geometry, licence and medical identity have not been independently validated. Replace generic bounding-box landmarks with named anatomical landmarks before labeling.','aliases':[]}
    issues=asset_issues(a)
    if issues: raise IllustrationError(issues[0].message)
    return a


def export_svg(svg: str,format: str, *, width_px: int | None=None,dpi: float=300) -> bytes:
    """Export trusted rendered SVG or a validated local SVG with bounded raster size.
    The compositor's marker elements are passive and generated internally.
    """
    if len(svg.encode())>MAX_FILE: raise IllustrationError('Export SVG exceeds 8 MB')
    if re.search(r'<!DOCTYPE|<!ENTITY|<\s*(script|image|foreignObject|use|filter)\b|\bon\w+\s*=|(?:href|src)\s*=',svg,re.I):
        raise IllustrationError('Unsafe or unsupported export SVG')
    # Validate passive drawing content including the internally generated marker subset.
    try:
        root=SafeET.fromstring(svg)
    except Exception as exc: raise IllustrationError('Malformed SVG for export') from exc
    if local_name(root.tag)!='svg': raise IllustrationError('Expected SVG input')
    # Export accepts marker-only extensions to the importer subset.
    for element in root.iter():
        if local_name(element.tag) not in ALLOWED_TAGS|{'marker'}: raise IllustrationError('Unsupported SVG export element')
        for key,value in element.attrib.items():
            key=local_name(key)
            if key not in ALLOWED_ATTRIBUTES|{'marker-end','marker-start','markerWidth','markerHeight','markerUnits','orient','refX','refY'}:
                raise IllustrationError(f'Unsupported SVG export attribute: {key}')
            if re.search(r'(?:https?:|file:|data:|javascript:|@import|expression\(|var\()',value,re.I): raise IllustrationError('External or active SVG export value')
            if 'url(' in value and not re.fullmatch(r'url\(#[A-Za-z_][\w.-]*\)',value):
                # A validated inline style may contain several local URLs. Use strict import check below for non-marker elements.
                if key!='style': raise IllustrationError('Unsupported SVG URL')
    stripped=deepcopy(root)
    for parent in stripped.iter():
        for child in list(parent):
            if local_name(child.tag)=='marker': parent.remove(child)
        for k in list(parent.attrib):
            if local_name(k) in {'marker-end','marker-start'}: del parent.attrib[k]
    # Keep the same active-content and reference checks as the importer.
    secure_svg(ET.tostring(stripped,encoding='unicode'))
    vb=[float(x) for x in root.attrib['viewBox'].split()]
    if not math.isfinite(dpi) or not 36<=dpi<=2400: raise IllustrationError('DPI must be between 36 and 2400')
    if width_px is not None and (not isinstance(width_px,int) or width_px<100 or width_px>20000): raise IllustrationError('Raster width must be an integer from 100 to 20000')
    if width_px is None:
        width_attr=root.attrib.get('width','')
        mm=re.fullmatch(r'([0-9.]+)mm',width_attr)
        estimate=float(mm[1])*dpi/25.4 if mm else vb[2]*dpi/96
    else: estimate=width_px
    if estimate*estimate*vb[3]/vb[2]>MAX_PIXELS: raise IllustrationError('Requested raster exceeds 40 million pixels')
    try: import cairosvg
    except ImportError as exc: raise IllustrationError('Install medillustrate[export] for PNG/PDF output') from exc
    if format not in {'png','pdf'}: raise IllustrationError('Supported export formats: png, pdf')
    if format=='pdf' and width_px is not None: raise IllustrationError('PDF uses physical SVG dimensions; omit width-px')
    kwargs={'bytestring':svg.encode('utf-8'),'dpi':dpi,'unsafe':False}
    if format=='png': kwargs['output_width']=int(round(estimate))
    try:
        output=(cairosvg.svg2png if format=='png' else cairosvg.svg2pdf)(**kwargs)
        if format=='png':
            from io import BytesIO
            from PIL import Image
            effective_dpi=estimate/(float(mm[1])/25.4) if width_px is None and mm else dpi
            if width_px is not None:
                physical=re.fullmatch(r'([0-9.]+)mm',root.attrib.get('width',''))
                if physical: effective_dpi=width_px/(float(physical[1])/25.4)
            image=Image.open(BytesIO(output));buffer=BytesIO()
            image.save(buffer,format='PNG',dpi=(effective_dpi,effective_dpi))
            output=buffer.getvalue()
        return output
    except Exception as exc: raise IllustrationError(f'SVG export failed: {exc}') from exc


def make_scene(id: str='new-figure',layout: str='anatomical-plate') -> dict[str,Any]:
    l=layout_by_id(layout)
    return {'schema_version':VERSION,'id':id,'title':l['title'],'subtitle':'',
     'description':l['reader_question']+' Add a substantive long description of the completed illustration.',
     'audience':'scientific','representation':'schematic',
     'frame':{'species':'human, conceptual unless specified','life_stage':'not specified','view':'schematic projection','laterality':'not-applicable','scale_policy':'not-to-scale','projection':'orthographic schematic'},
     'canvas':{'width':1200,'height':800,'print_width_mm':180,'background':'#FFFFFF','text_colour':'#354753','minimum_label_pt':7},
     'layout':layout,'sources':[],'claims':[],'compartments':[],'nodes':[],'edges':[],'labels':[],
     'caption':'Schematic; not to scale. Add the supported interpretation and important omissions.'}


def production_brief(scene: Mapping[str,Any],library: Mapping[str,Any] | None=None) -> str:
    lib=library if library is not None else assets()
    issues=validate(scene,lib)
    if any(i.severity=='error' for i in issues): raise IllustrationError('Fix the scene before compiling a production brief')
    l=layout_by_id(scene['layout']) if scene.get('layout') else None
    lines=[f"# Illustration commission: {scene['title']}",f"Audience: {scene['audience']}. Representation: {scene['representation']}.",
           f"Purpose: {scene['description']}", '## Coordinate and truth contract',json.dumps(scene['frame'],ensure_ascii=False),
           'Do not invent anatomical structures, measured counts, evidence, study results or procedural instructions.',
           'Use references for spatial reconstruction; a generative image is never evidence that anatomy is correct.',
           'Keep all labels editable and compose them from the approved text after geometry is approved.',
           '## Composition']
    if l:
        lines += [l['reader_question'],'Reading order: '+ ' > '.join(l['reading_order']), 'Preserve: '+ '; '.join(l['locked_invariants'])]
    lines += ['## Required assets and limitations']
    for n in scene['nodes']:
        a=lib[n['asset']]; lines.append(f"{n['id']}: {a['label']}. {a['limitations']}")
    lines += ['## Anatomical relation contract']
    lines += [f"{r['subject']} {r['predicate']} {r['object']} (claim {r['claim']})." for r in scene.get('relations',[])]
    lines += ['## Claim ledger']
    lines += [f"{c['id']} [{c['status']}]: {c['text']} Sources: {', '.join(c['sources']) or 'none; illustrative only'}." for c in scene['claims']]
    lines += ['## Review and handoff','Deliver editable SVG and the scene JSON. Render at the specified print width. Record scientific and visual review separately from the illustration. Do not claim Netter equivalence, BioRender equivalence or clinical approval without independent evidence.']
    return '\n\n'.join(lines)+'\n'


def score_benchmark(ratings: Mapping[str,Any]) -> dict[str,Any]:
    weights=resource('benchmark-tasks.json')['weights']
    scores=ratings.get('scores',{})
    if set(scores)!=set(weights): raise IllustrationError('All benchmark domains, and no unknown domains, are required')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=4 for v in scores.values()):
        raise IllustrationError('Domain ratings must be finite numbers from 0 to 4')
    if not isinstance(ratings.get('critical_errors'),list): raise IllustrationError('Provide an explicit list of critical errors, even if empty')
    if not ratings.get('reviewer_id') or not ratings.get('task_id') or not ratings.get('candidate_id'): raise IllustrationError('Reviewer, task and candidate IDs are required')
    return {'task_id':ratings['task_id'],'candidate_id':ratings['candidate_id'],'reviewer_id':ratings['reviewer_id'],
            'weighted_score':round(sum(weights[k]*scores[k]/4 for k in weights),2),
            'critical_error_fail':bool(ratings['critical_errors']),'critical_errors':ratings['critical_errors'],
            'interpretation':'A single submitted human rating, not a comparative study, validated performance claim or market rank.'}
