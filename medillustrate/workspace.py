"""Versioned local workspace and bounded, declarative editing operations.

All public mutations use optimistic concurrency. An agent creates a proposal;
only explicit acceptance commits it. Review records live outside exported figures.
"""
from __future__ import annotations
import base64
from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
import io
import json
import math
from pathlib import Path
import re
import sqlite3
from typing import Any
import uuid
import xml.etree.ElementTree as ET
from jsonschema import Draft202012Validator
from . import atelier, core

VERSION = '2.1.0'
MAX_PROJECT = 8_000_000
MAX_MEDIA = 16_000_000
MAX_PIXELS = 24_000_000

class Conflict(core.IllustrationError):
    """The project changed after this operation was prepared."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def ident(prefix='item') -> str:
    return f'{prefix}-{uuid.uuid4().hex[:16]}'


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def safe_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,99}', value):
        raise core.IllustrationError('Invalid identifier')
    return value


@lru_cache(maxsize=1)
def library() -> dict[str, Any]:
    return {**core.assets(), **atelier.library()}


@lru_cache(maxsize=1)
def seed_data() -> dict[str, Any]:
    return core.resource('studio-seeds.json')


def template_frame(template_id: str) -> dict[str, Any]:
    choices = {r['id']: r for r in seed_data()['templates']}
    if template_id not in choices:
        raise core.IllustrationError('Unknown template')
    result = deepcopy(choices[template_id])
    result['id'] = ident('frame')
    result['template_id'] = template_id
    result.pop('svg', None)
    result.setdefault('stage', 'colour')
    result.setdefault('show_labels', True)
    result.setdefault('detail', 1.0)
    result.setdefault('hidden_layers', [])
    result.setdefault('geometry_locked', True)
    result.setdefault('artwork_media_id', None)
    return result


def new_project(title='Renal anatomy', template_id='atlas-kidney-section') -> dict[str, Any]:
    frame = template_frame(template_id)
    return {'schema_version': VERSION, 'id': ident('project'), 'title': title,
            'frames': [frame], 'active_frame': frame['id'], 'references': [],
            'brief': '', 'style': {'name': 'Clinical atlas', 'locked': True}}


def get_frame(project: dict, frame_id: str | None = None) -> dict:
    fid = frame_id or project['active_frame']
    for frame in project['frames']:
        if frame['id'] == fid:
            return frame
    raise core.IllustrationError('Unknown artboard')


def validate_project(project: dict) -> None:
    text = json_text(project)
    if len(text.encode()) > MAX_PROJECT:
        raise core.IllustrationError('Project exceeds the 8 MB document limit')
    errors = list(Draft202012Validator(core.resource('project.schema.json')).iter_errors(project))
    if errors:
        e = errors[0]
        raise core.IllustrationError(f'Project {".".join(map(str,e.path))}: {e.message}')
    ids = [f['id'] for f in project['frames']]
    if len(set(ids)) != len(ids) or project['active_frame'] not in ids:
        raise core.IllustrationError('Artboard IDs must be unique and the active artboard must exist')
    for r in project['references']:
        if r['url'] and not re.match(r'^https?://',r['url']):raise core.IllustrationError('Reference URL must use HTTP or HTTPS')
    for f in project['frames']:
        if f['kind']=='graphics':
            d=f['document']
            if d.get('engine') not in {'photo','vector'} or not isinstance(d.get('title'),str):raise core.IllustrationError('Invalid graphics document')
            if not all(isinstance(d.get(k),int) and 1<=d[k]<=16000 for k in ('width','height')) or d['width']*d['height']>MAX_PIXELS:raise core.IllustrationError('Invalid graphics dimensions')
            for key in ('native_media_id','preview_media_id'):safe_id(d.get(key))
            if d.get('svg_media_id'):safe_id(d['svg_media_id'])
            continue
        if f['kind'] == 'plate':
            errors = atelier.validate_plate(f['document'], library())
        else:
            errors = [e for e in core.validate(f['document'], library()) if e.severity == 'error']
        if errors:
            raise core.IllustrationError(f'{f["id"]}: {errors[0].code}: {errors[0].message}')
        if f['kind'] != 'plate' and f.get('artwork_media_id'):
            raise core.IllustrationError('Raster replacement is available for atlas artwork only')
        valid_layers = {n.get('id') for n in core.secure_svg(library()[f['document']['asset']]['svg']).iter()} if f['kind']=='plate' else set()
        if any(layer not in valid_layers for layer in f['hidden_layers']):
            raise core.IllustrationError('Unknown tissue layer')


def apply_operations(project: dict, operations: list[dict]) -> dict:
    """Apply an atomic, allowlisted editing plan; never execute model-authored code."""
    if not isinstance(operations, list) or not 1 <= len(operations) <= 24:
        raise core.IllustrationError('An edit needs between 1 and 24 operations')
    p = deepcopy(project)
    for op in operations:
        if not isinstance(op, dict) or not isinstance(op.get('op'), str):
            raise core.IllustrationError('Malformed operation')
        name = op['op']
        if name == 'project_title':
            p['title'] = op['value']; continue
        if name == 'brief':
            p['brief'] = op['value']; continue
        if name == 'add_frame':
            f = template_frame(op['template_id']); f['id']=safe_id(op.get('new_id',f['id'])); p['frames'].append(f); p['active_frame'] = f['id']; continue
        if name == 'select_frame':
            get_frame(p, op['frame_id']); p['active_frame'] = op['frame_id']; continue
        if name == 'remove_frame':
            if len(p['frames']) <= 1: raise core.IllustrationError('Keep at least one artboard')
            get_frame(p, op['frame_id'])
            p['frames'] = [f for f in p['frames'] if f['id'] != op['frame_id']]
            if p['active_frame'] == op['frame_id']: p['active_frame'] = p['frames'][0]['id']
            continue
        if name=='graphics_result':
            current=get_frame(p)
            if current['kind']=='graphics' and current['document']['engine']==op['document']['engine'] and not op.get('append'):
                current['document']=deepcopy(op['document'])
            else:
                frame={'id':safe_id(op['new_id']),'kind':'graphics','document':deepcopy(op['document']),'stage':'colour','show_labels':False,'detail':1,'hidden_layers':[],'geometry_locked':True,'artwork_media_id':None}
                p['frames'].append(frame);p['active_frame']=frame['id']
            continue
        f = get_frame(p, op.get('frame_id')); d = f['document']
        if f.get('artwork_media_id') and (name in {'detail','layer'} or name=='stage' and op['value']!='colour'):raise core.IllustrationError('Painted artwork is a raster layer. Restore the vector revision for contour, value and texture editing.')
        if name in {'title', 'subtitle', 'caption', 'description'}:
            d[name] = op['value']
        elif name == 'stage':
            f['stage'] = op['value']
        elif name == 'show_labels':
            f['show_labels'] = op['value']
        elif name == 'detail':
            f['detail'] = op['value']
        elif name == 'geometry_lock':
            f['geometry_locked'] = op['value']
        elif name == 'label_size':
            if f['kind'] != 'plate': raise core.IllustrationError('Global label sizing requires an atlas plate')
            d['label_size'] = op['value']
        elif name == 'label':
            if f['kind'] != 'plate': raise core.IllustrationError('This label operation requires an atlas plate')
            found = next((l for l in d['labels'] if l['landmark'] == op.get('landmark')), None)
            if found is None: raise core.IllustrationError('Unknown label landmark')
            allowed = {'text','side','y','target','target_note'}
            values = op.get('values', {})
            if not values or set(values) - allowed: raise core.IllustrationError('Unknown label property')
            if 'target' in values and not values.get('target_note'):
                raise core.IllustrationError('A landmark correction needs an explicit anatomical reason')
            found.update(values)
        elif name == 'art_box':
            if f['kind'] != 'plate': raise core.IllustrationError('Artwork box requires an atlas plate')
            # Moving the entire intact organ changes page layout, not topology.
            d['art_box'] = op['value']
        elif name == 'layer':
            if f['kind'] != 'plate': raise core.IllustrationError('Tissue layers require an atlas plate')
            layer=op['layer_id']
            if not layer.startswith('texture-') and f['geometry_locked']:
                raise core.IllustrationError('Unlock geometry explicitly before hiding anatomical structures')
            hidden=set(f['hidden_layers'])
            if op['visible']: hidden.discard(layer)
            else: hidden.add(layer)
            f['hidden_layers']=sorted(hidden)
        elif name == 'move_node':
            if f['kind'] != 'scene': raise core.IllustrationError('Node movement requires a schematic scene')
            n=next((n for n in d['nodes'] if n['id']==op.get('node_id')),None)
            if n is None: raise core.IllustrationError('Unknown scene node')
            n['box']=op['box']
        elif name == 'add_node':
            if f['kind'] != 'scene': raise core.IllustrationError('Add symbols to a schematic artboard, not inside anatomical tissue')
            if op['asset'] not in library(): raise core.IllustrationError('Unknown asset')
            d['nodes'].append({'id':safe_id(op.get('new_id') or ident('node')), 'asset':op['asset'], 'box':op['box']})
        else:
            raise core.IllustrationError(f'Unsupported edit: {name}')
    validate_project(p)
    return p


def annotated_asset(frame: dict) -> dict:
    a = deepcopy(library()[frame['document']['asset']])
    root = core.secure_svg(a['svg'])
    hidden = set(frame['hidden_layers'])
    for parent in root.iter():
        for child in list(parent):
            if child.get('id') in hidden: parent.remove(child)
    for n in root.iter():
        if n.get('id','').startswith('texture-'):
            n.set('opacity', str(float(n.get('opacity',1))*frame['detail']))
    a['svg'] = ET.tostring(root, encoding='unicode')
    return a


def render_frame(frame: dict, media_loader=None, *, labels: bool | None=None) -> str:
    if frame['kind']=='graphics':
        if media_loader is None:raise core.IllustrationError('Graphics media resolver required')
        d=frame['document']
        if d.get('svg_media_id'):
            from .graphics import passive_svg
            return passive_svg(media_loader(d['svg_media_id'])['data'])
        media=media_loader(d['preview_media_id']);src='data:image/png;base64,'+base64.b64encode(media['data']).decode()
        return f'<svg xmlns="{core.SVG_NS}" width="190mm" height="{190*d["height"]/d["width"]}mm" viewBox="0 0 {d["width"]} {d["height"]}"><title>{escape(d["title"])}</title><image width="{d["width"]}" height="{d["height"]}" href="{src}"/></svg>'
    show = frame['show_labels'] if labels is None else labels
    if frame['kind'] == 'scene':
        d=deepcopy(frame['document'])
        if not show:d['labels']=[]
        return core.render(d, library())
    a=annotated_asset(frame)
    svg=atelier.render_plate(frame['document'],{a['id']:a},stage=frame['stage'],labels=show)
    if frame.get('artwork_media_id'):
        if media_loader is None: raise core.IllustrationError('Artwork media resolver is required')
        media=media_loader(frame['artwork_media_id'])
        if media['mime']!='image/png': raise core.IllustrationError('Artwork must be a normalized PNG')
        root=ET.fromstring(svg)
        node=next((n for n in root.iter() if n.get('id')=='node-anatomy'),None)
        if node is None: raise core.IllustrationError('Artwork group missing')
        node.clear();node.set('id','node-anatomy')
        # The incoming PNG is an image of the asset viewBox, not of the labelled page.
        x,y,w,h=frame['document']['art_box']
        image=ET.SubElement(node,f'{{{core.SVG_NS}}}image',{'x':str(x),'y':str(y),'width':str(w),'height':str(h),'preserveAspectRatio':'xMidYMid meet','href':'data:image/png;base64,'+base64.b64encode(media['data']).decode()})
        svg=ET.tostring(root,encoding='unicode')
    return svg


def media_normalize(name: str, raw: bytes) -> tuple[str,bytes,dict]:
    """Treat uploads as data. No active SVG, EXIF, remote links or OCR execution."""
    if not raw or len(raw)>MAX_MEDIA: raise core.IllustrationError('File is empty or larger than 16 MB')
    suffix=Path(name).suffix.lower()
    if suffix in {'.png','.jpg','.jpeg','.webp'}:
        from PIL import Image, ImageOps
        try:
            image=Image.open(io.BytesIO(raw))
            if image.width*image.height>MAX_PIXELS: raise core.IllustrationError('Image exceeds 24 million pixels')
            image=ImageOps.exif_transpose(image).convert('RGBA')
            out=io.BytesIO();image.save(out,format='PNG')
            return 'image/png',out.getvalue(),{'width':image.width,'height':image.height,'extracted_text':''}
        except core.IllustrationError: raise
        except Exception as e: raise core.IllustrationError('Cannot decode image') from e
    if suffix=='.svg':
        text=raw.decode('utf-8');core.secure_svg(text)
        return 'image/svg+xml',text.encode(),{'extracted_text':'','passive_svg':True}
    if suffix=='.pdf':
        from pypdf import PdfReader
        reader=PdfReader(io.BytesIO(raw))
        if len(reader.pages)>100:raise core.IllustrationError('Reference PDF limit is 100 pages')
        excerpt='\n\n'.join(f'[Page {i+1}]\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages))[:60000]
        return 'application/pdf',raw,{'pages':len(reader.pages),'extracted_text':excerpt,'ocr_performed':False}
    if suffix in {'.txt','.md','.csv','.json'}:
        text=raw.decode('utf-8')
        return 'text/plain',text.encode(),{'extracted_text':text[:60000]}
    raise core.IllustrationError('Supported files: PNG, JPEG, WebP, passive SVG, PDF, TXT, Markdown, CSV and JSON')


class Store:
    """SQLite persistence. Figure contents and internal control records are separate tables."""
    def __init__(self, path: str | Path):
        self.path=Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as c:
            c.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, version INTEGER NOT NULL, body TEXT NOT NULL, updated TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS versions(project TEXT NOT NULL, version INTEGER NOT NULL, body TEXT NOT NULL, reason TEXT NOT NULL, created TEXT NOT NULL, PRIMARY KEY(project,version));
            CREATE TABLE IF NOT EXISTS proposals(id TEXT PRIMARY KEY, project TEXT NOT NULL, base_version INTEGER NOT NULL, body TEXT NOT NULL, status TEXT NOT NULL, created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS media(id TEXT PRIMARY KEY, project TEXT NOT NULL, name TEXT NOT NULL, mime TEXT NOT NULL, data BLOB NOT NULL, metadata TEXT NOT NULL, created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, project TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS control(id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL);
            ''')
    def connect(self):
        c=sqlite3.connect(self.path,timeout=15)
        c.row_factory=sqlite3.Row
        c.execute('PRAGMA busy_timeout=15000')
        return c
    def list_projects(self):
        with self.connect() as c:
            rows=c.execute('SELECT id,version,body,updated FROM projects ORDER BY updated DESC,id').fetchall()
        return [{'id':r['id'],'version':r['version'],'title':json.loads(r['body'])['title'],'updated':r['updated']} for r in rows]
    def create(self, project:dict | None=None):
        p=deepcopy(project or new_project());validate_project(p)
        text=json_text(p);stamp=now()
        try:
            with self.connect() as c:
                c.execute('INSERT INTO projects VALUES(?,?,?,?)',(p['id'],1,text,stamp))
                c.execute('INSERT INTO versions VALUES(?,?,?,?,?)',(p['id'],1,text,'Created project',stamp))
        except sqlite3.IntegrityError as e:raise Conflict('A project with this ID already exists') from e
        return {'project':p,'version':1}
    def get(self, pid:str, version:int | None=None):
        safe_id(pid)
        with self.connect() as c:
            if version is None:r=c.execute('SELECT version,body FROM projects WHERE id=?',(pid,)).fetchone()
            else:r=c.execute('SELECT version,body FROM versions WHERE project=? AND version=?',(pid,version)).fetchone()
        if r is None:raise core.IllustrationError('Project or revision not found')
        return {'project':json.loads(r['body']),'version':r['version']}
    def _commit(self,c,pid,base,p,reason):
        validate_project(p)
        if p['id']!=pid:raise core.IllustrationError('Cannot replace project identity')
        version=base+1;text=json_text(p);stamp=now()
        changed=c.execute('UPDATE projects SET version=?,body=?,updated=? WHERE id=? AND version=?',(version,text,stamp,pid,base)).rowcount
        if changed!=1:raise Conflict('This project changed. Reload and review the edit against the current revision.')
        c.execute('INSERT INTO versions VALUES(?,?,?,?,?)',(pid,version,text,str(reason)[:1000],stamp))
        return {'project':p,'version':version}
    def edit(self,pid:str,base:int,ops:list,reason='Manual edit'):
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            r=c.execute('SELECT version,body FROM projects WHERE id=?',(pid,)).fetchone()
            if r is None:raise core.IllustrationError('Project not found')
            if r['version']!=base:raise Conflict('Stale edit: project has changed')
            p=apply_operations(json.loads(r['body']),ops)
            result=self._commit(c,pid,base,p,reason)
        return result
    def restore(self,pid,base,version):
        p=self.get(pid,version)['project']
        with self.connect() as c:return self._commit(c,pid,base,p,f'Restored revision {version}')
    def history(self,pid):
        self.get(pid)
        with self.connect() as c:
            return [dict(r) for r in c.execute('SELECT version,reason,created FROM versions WHERE project=? ORDER BY version DESC LIMIT 150',(pid,))]
    def propose(self,pid,base,plan):
        snapshot=self.get(pid)
        if snapshot['version']!=base:raise Conflict('Agent proposal was prepared against an older revision')
        plan=deepcopy(plan)
        for op in plan['operations']:
            if op.get('op') in {'add_frame','add_node'}:op.setdefault('new_id',ident('frame' if op['op']=='add_frame' else 'node'))
        candidate=apply_operations(snapshot['project'],plan['operations'])
        proposal={'id':ident('proposal'),'project_id':pid,'base_version':base,'summary':str(plan.get('summary','Proposed edit'))[:1500],
                  'operations':plan['operations'],'provider':str(plan.get('provider','external-agent'))[:100],
                  'candidate_hash':core.sha256(core.canonical(candidate)),'warnings':plan.get('warnings',[])}
        with self.connect() as c:c.execute('INSERT INTO proposals VALUES(?,?,?,?,?,?)',(proposal['id'],pid,base,json_text(proposal),'pending',now()))
        return proposal
    def proposal(self,pid,proposal_id):
        with self.connect() as c:r=c.execute('SELECT body,status FROM proposals WHERE id=? AND project=?',(proposal_id,pid)).fetchone()
        if r is None:raise core.IllustrationError('Proposal not found')
        result=json.loads(r['body']);result['status']=r['status'];return result
    def decide(self,pid,proposal_id,accept:bool):
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            r=c.execute('SELECT * FROM proposals WHERE id=? AND project=?',(proposal_id,pid)).fetchone()
            if r is None or r['status']!='pending':raise Conflict('Proposal is not pending')
            q=json.loads(r['body'])
            if accept:
                row=c.execute('SELECT version,body FROM projects WHERE id=?',(pid,)).fetchone()
                if row['version']!=r['base_version']:raise Conflict('Proposal is stale. Manual edits were preserved; generate a fresh proposal.')
                p=apply_operations(json.loads(row['body']),q['operations'])
                if core.sha256(core.canonical(p))!=q['candidate_hash']:raise Conflict('Proposal candidate changed; prepare a new proposal')
                result=self._commit(c,pid,row['version'],p,q['summary'])
            else:result={'rejected':True}
            c.execute('UPDATE proposals SET status=? WHERE id=?',('accepted' if accept else 'rejected',proposal_id))
        return result
    def add_reference(self,pid,base,*,title,url='',note='',name=None,raw=None,licence='Not specified'):
        if not title or len(title)>240:raise core.IllustrationError('Reference title must be 1–240 characters')
        if url and not re.match(r'^https?://',url):raise core.IllustrationError('Reference URL must use HTTP or HTTPS')
        media_id=None;normalized=None
        if raw is not None:
            mime,data,metadata=media_normalize(name or 'reference.png',raw)
            normalized=(mime,data,metadata);media_id=ident('media')
        ref={'id':ident('ref'),'title':title,'url':url,'note':str(note)[:60000], 'licence':str(licence)[:500], 'media_id':media_id}
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT version,body FROM projects WHERE id=?',(pid,)).fetchone()
            if row is None:raise core.IllustrationError('Project not found')
            if row['version']!=base:raise Conflict('Reference upload is stale; reload')
            p=json.loads(row['body']);p['references'].append(ref)
            if normalized:
                mime,data,metadata=normalized
                c.execute('INSERT INTO media VALUES(?,?,?,?,?,?,?)',(media_id,pid,Path(name).name[:200],mime,data,json_text(metadata),now()))
            result=self._commit(c,pid,base,p,'Added reference')
        return result
    def get_media(self,pid,mid):
        safe_id(mid)
        with self.connect() as c:r=c.execute('SELECT * FROM media WHERE id=? AND project=?',(mid,pid)).fetchone()
        if r is None:raise core.IllustrationError('Media not found in this project')
        return {**dict(r),'metadata':json.loads(r['metadata'])}
    def put_candidate(self,pid,name,raw,metadata):
        self.get(pid);mime,data,info=media_normalize(name,raw)
        if mime!='image/png':raise core.IllustrationError('Painted candidates must be raster images')
        mid=ident('media');info.update(metadata)
        with self.connect() as c:c.execute('INSERT INTO media VALUES(?,?,?,?,?,?,?)',(mid,pid,name,mime,data,json_text(info),now()))
        return mid
    def adopt_candidate(self,pid,base,frame_id,mid,*,confirm_landmarks:bool):
        if not confirm_landmarks:raise core.IllustrationError('Confirm that every leader target has been checked on the replacement artwork')
        m=self.get_media(pid,mid)
        if m['mime']!='image/png':raise core.IllustrationError('Candidate is not a normalized PNG')
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            r=c.execute('SELECT version,body FROM projects WHERE id=?',(pid,)).fetchone()
            if r is None or r['version']!=base:raise Conflict('Project has changed since candidate selection')
            p=json.loads(r['body']);f=get_frame(p,frame_id)
            if f['kind']!='plate':raise core.IllustrationError('Use an anatomical artboard for this artwork')
            a=library()[f['document']['asset']];aw,ah=a['view_box'][2:]
            if abs(m['metadata']['width']/m['metadata']['height']/(aw/ah)-1)>.02:raise core.IllustrationError('Candidate framing has a different aspect ratio. Correct its canvas before reusing anatomical landmark coordinates.')
            if m['metadata'].get('frame_id') and m['metadata']['frame_id']!=frame_id:raise core.IllustrationError('Candidate belongs to a different artboard')
            f['artwork_media_id']=mid;f['stage']='colour'
            result=self._commit(c,pid,base,p,'Adopted painted candidate after user landmark confirmation')
            c.execute('INSERT INTO control(project,kind,body,created) VALUES(?,?,?,?)',(pid,'candidate_adoption',json_text({'media_id':mid,'frame_id':frame_id,'landmarks_confirmed_by_user':True,'independent_medical_review':False}),now()))
        return result
    def event(self,pid,kind,body):
        with self.connect() as c:c.execute('INSERT INTO control(project,kind,body,created) VALUES(?,?,?,?)',(pid,kind,json_text(body),now()))
    def control(self,pid):
        snapshot=self.get(pid)
        with self.connect() as c:rows=c.execute('SELECT kind,body,created FROM control WHERE project=? ORDER BY id',(pid,)).fetchall()
        return {'project_id':pid,'revision':snapshot['version'],'project_sha256':core.sha256(core.canonical(snapshot['project'])),
                'events':[{'kind':r['kind'],'created':r['created'],'data':json.loads(r['body'])} for r in rows],
                'history':self.history(pid),'medical_certification':False}
    def put_job(self,pid,job):
        safe_id(job['id']);self.get(pid)
        with self.connect() as c:c.execute('INSERT INTO jobs VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body',(job['id'],pid,json_text(job),now()))
    def jobs(self,pid):
        with self.connect() as c:return [json.loads(r['body']) for r in c.execute('SELECT body FROM jobs WHERE project=? ORDER BY created DESC',(pid,))]
    def job(self,pid,jid):
        with self.connect() as c:r=c.execute('SELECT body FROM jobs WHERE id=? AND project=?',(jid,pid)).fetchone()
        if r is None:raise core.IllustrationError('Job not found')
        return json.loads(r['body'])
