"""Artcraft engines, confined to a disposable copy of one project document.

The unmodified upstream binaries and their notices live under vendor/artcraft.
No model chooses an executable, a filesystem root or an output path.
"""
from __future__ import annotations
import base64
from contextlib import contextmanager
from functools import lru_cache
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading
import time
import re
from defusedxml import ElementTree as SafeET
from . import core
from .workspace import Conflict, get_frame, ident, json_text, now, render_frame

ROOT=Path(__file__).resolve().parents[1]/'vendor/artcraft'
VERSIONS={'photo':'0.19.0','vector':'0.20.0'}
REPOS={'photo':'photocraft','vector':'vectorcraft'}
NATIVE={'photo':'.pcraft','vector':'.vectorcraft'}

def passive_svg(data):
    """Validate engine output without dropping editable metadata or visual effects."""
    text=data.decode() if isinstance(data,bytes) else data
    if len(text.encode())>16_000_000 or re.search(r'<!DOCTYPE|<!ENTITY',text,re.I):raise core.IllustrationError('Unsafe or oversized SVG')
    try:root=SafeET.fromstring(text)
    except Exception as e:raise core.IllustrationError('Invalid graphics SVG') from e
    if root.tag.rsplit('}',1)[-1]!='svg':raise core.IllustrationError('Expected SVG artwork')
    for n in root.iter():
        tag=n.tag.rsplit('}',1)[-1].lower()
        if tag in {'script','foreignobject','style','iframe','object','embed','animate','set','animatetransform','animatemotion','a'}:raise core.IllustrationError('Active SVG elements are unavailable')
        for key,value in n.attrib.items():
            key=key.rsplit('}',1)[-1].lower();low=value.lower()
            if key.startswith('on') or any(t in low for t in ['javascript:','file:','@import','expression(','http:','https:']):raise core.IllustrationError('External or active SVG attributes are unavailable')
            if key in {'href','src'} and not (value.startswith('#') or re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=\s]+',value)):raise core.IllustrationError('SVG references must remain inside the artwork')
            if 'url(' in low and re.search(r'url\(\s*["\']?(?!#)',low):
                # Check each URL independently; permit local paint/filter references only.
                if any(not x.strip(' \"\'').startswith('#') for x in re.findall(r'url\(([^)]+)\)',low)):raise core.IllustrationError('External SVG resources are unavailable')
    return text

def binary(engine):
    if engine not in REPOS:raise core.IllustrationError('Choose Photo or Vector')
    repo=REPOS[engine]
    path=ROOT/repo/'cli'/f'{repo}-cli-{VERSIONS[engine]}-macos-universal'/f'{repo}-cli'
    if not path.is_file():raise core.IllustrationError(repo+' is not installed')
    return path

def status():
    return {e:{'installed':(ROOT/r/'cli'/f'{r}-cli-{VERSIONS[e]}-macos-universal'/f'{r}-cli').is_file(),
               'version':VERSIONS[e],'name':r,'web':web_root(e).is_dir()} for e,r in REPOS.items()}

def web_root(engine):
    if engine not in REPOS:raise core.IllustrationError('Unknown editing engine')
    folder=ROOT/REPOS[engine]/'web'
    pages=list(folder.rglob('index.html')) if folder.is_dir() else []
    return pages[0].parent if pages else folder/'unavailable'


class Session:
    """One JSONL engine process. Its file authority is only the temporary folder."""
    def __init__(self,engine,folder,cancel=None):
        self.engine=engine;self.folder=Path(folder);self.cancel=cancel;self.counter=0;self.queue=queue.Queue()
        args=[str(binary(engine)), 'serve' if engine=='photo' else 'mcp']
        if engine=='vector':args+=['--headless']
        args+=['--automation-read-root',str(folder),'--automation-write-root',str(folder)]
        env={**os.environ,'VECTORCRAFT_NO_PREFS':'1','PHOTOCRAFT_NO_PREFS':'1'}
        self.process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,cwd=folder,env=env)
        def read():
            try:
                for line in self.process.stdout:self.queue.put(line)
            finally:self.queue.put(None)
        threading.Thread(target=read,daemon=True).start()
        try:
            if engine=='vector':
                self.rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'Medical Illustration Studio','version':'2.2'}})
                self.process.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n');self.process.stdin.flush()
        except Exception:
            self.close();raise
    def close(self):
        if self.process.poll() is None:self.process.terminate()
        try:self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
        self.process.stdin.close();self.process.stdout.close()
    def rpc(self,method,params):
        self.counter+=1;rid=self.counter
        req={'id':rid,'method':method,'params':params}
        if self.engine=='vector':req['jsonrpc']='2.0'
        self.process.stdin.write((json_text(req)+'\n').encode());self.process.stdin.flush()
        until=time.monotonic()+75
        while time.monotonic()<until:
            if self.cancel and self.cancel.is_set():raise core.IllustrationError('Editing stopped')
            try:line=self.queue.get(timeout=.15)
            except queue.Empty:continue
            if line is None:raise core.IllustrationError('Editing engine stopped unexpectedly')
            if len(line)>24_000_000:raise core.IllustrationError('Engine reply is too large')
            reply=json.loads(line)
            if reply.get('id')!=rid:continue
            if 'error' in reply or reply.get('ok') is False:raise core.IllustrationError(str(reply.get('error'))[:1800])
            return reply.get('result')
        raise core.IllustrationError('Editing engine timed out; source document preserved')
    def tool(self,name,args):
        result=self.rpc('tools/call',{'name':name,'arguments':args})
        if result.get('isError'):raise core.IllustrationError(' '.join(x.get('text','') for x in result.get('content',[]))[:1800])
        if 'structuredContent' in result:return result['structuredContent']
        chunks=result.get('content',[])
        texts=[x['text'] for x in chunks if x.get('type')=='text']
        if texts:
            try:return json.loads('\n'.join(texts))
            except ValueError:return {'text':'\n'.join(texts)}
        return result
    def open(self,path):return self.rpc('doc.open',{'path':str(path)}) if self.engine=='photo' else self.tool('open_file',{'path':str(path)})
    def inspect(self):return self.rpc('doc.inspect',{}) if self.engine=='photo' else self.tool('doc_inspect',{'depth':3,'childLimit':60})
    def commands(self,query=''):
        rows=self.rpc('engine.commands',{}) if self.engine=='photo' else self.tool('command_list',{'filter':query})
        if isinstance(rows,dict):rows=rows.get('commands',[])
        return [r for r in rows if query.lower() in json.dumps(r).lower()] if query else rows
    def execute(self,command,params):
        return self.rpc('engine.execute',{'command':command,'params':params}) if self.engine=='photo' else self.tool('command_run',{'id':command,'params':params})
    def save(self,path):return self.rpc('doc.save',{'path':str(path)}) if self.engine=='photo' else self.tool('save_file',{'path':str(path)})
    def preview(self,path):
        if self.engine=='photo':return self.rpc('doc.save',{'path':str(path)})
        return self.tool('export',{'format':'png','path':str(path),'scale':1})

@contextmanager
def opened(store,pid,engine,cancel=None,raw=None,name=None):
    with tempfile.TemporaryDirectory(prefix='medillustrate-craft-') as folder:
        root=Path(folder);session=None
        try:
            session=Session(engine,root,cancel)
            frame=get_frame(store.get(pid)['project'])
            if raw is None:
                if frame['kind']=='graphics' and frame['document']['engine']==engine:
                    media=store.get_media(pid,frame['document']['native_media_id']);raw=media['data'];name='input'+NATIVE[engine]
                elif engine=='vector':raw=render_frame(frame,lambda mid:store.get_media(pid,mid)).encode();name='input.svg'
                else:
                    from .exports import frame_bytes
                    raw=frame_bytes(store,pid,frame,'png',width_px=1200);name='input.png'
            path=root/('input'+Path(name).suffix.lower());path.write_bytes(raw)
            session.open(path)
            yield session,root
        finally:
            if session:session.close()

def inspect(store,pid,engine,cancel=None):
    with opened(store,pid,engine,cancel) as (s,_):return s.inspect()

def commands(store,pid,engine,query='',cancel=None):
    if not isinstance(query,str) or len(query)>120:raise core.IllustrationError('Search must be under 120 characters')
    with opened(store,pid,engine,cancel) as (s,_):
        rows=s.commands(query)
        return {'count':len(rows),'commands':rows[:24]}

def validate_steps(steps):
    if not isinstance(steps,list) or not 1<=len(steps)<=24:raise core.IllustrationError('Use 1–24 editing steps')
    # File I/O is host-owned. Deny indirect action/plugin/script paths as well.
    for step in steps:
        if set(step)-{'command','params'} or not isinstance(step.get('command'),str) or not isinstance(step.get('params',{}),dict):raise core.IllustrationError('Each step needs command and object params')
        command=step['command'].lower()
        if any(t in command for t in ['file.','app.','document.open','document.save','document.export','document.place','script','plugin','action','automate','batch','droplet','library','preset','font','preferences','help.','web','url','linked','relink','package','import','export','save','open','print']):
            raise core.IllustrationError('File and application actions are managed by the workspace: '+step['command'])
        def check(value):
            if isinstance(value,dict):
                for k,v in value.items():
                    if any(t in k.lower() for t in ['file','url','script','directory','folder']) or ('path' in k.lower() and isinstance(v,str)):raise core.IllustrationError('Editing steps cannot supply filesystem paths')
                    check(v)
            elif isinstance(value,list):
                for v in value:check(v)
            elif isinstance(value,str) and (value.startswith(('/','~','file:','http:','https:')) or '..' in value.split('/')):raise core.IllustrationError('External paths are unavailable in editing steps')
        check(step.get('params',{}))

def persist(store,pid,s,root,engine,title):
    native=root/('result'+NATIVE[engine]);preview=root/'preview.png'
    s.save(native);s.preview(preview);info=s.inspect()
    from PIL import Image
    import io
    image=Image.open(io.BytesIO(preview.read_bytes()));w,h=image.size
    if w*h>24_000_000:raise core.IllustrationError('Artwork exceeds 24 million pixels')
    ids=[]
    for path,mime in [(native,'application/x-'+REPOS[engine]),(preview,'image/png')]:
        data=path.read_bytes()
        if not data or len(data)>16_000_000:raise core.IllustrationError('Editing result exceeds the 16 MB media limit')
        mid=ident('media');ids.append(mid)
        meta={'engine':engine,'version':VERSIONS[engine],'sha256':core.sha256(data),'width':w,'height':h,'native':path==native}
        with store.connect() as c:c.execute('INSERT INTO media VALUES(?,?,?,?,?,?,?)',(mid,pid,path.name,mime,data,json_text(meta),now()))
    doc={'title':title[:160],'engine':engine,'native_media_id':ids[0],'preview_media_id':ids[1],'width':w,'height':h,'print_width_mm':190,'inspection':info}
    if engine=='vector':
        path=root/'result.svg';s.tool('export',{'format':'svg','path':str(path)})
        data=path.read_bytes();passive_svg(data)
        mid=ident('media');doc['svg_media_id']=mid
        with store.connect() as c:c.execute('INSERT INTO media VALUES(?,?,?,?,?,?,?)',(mid,pid,path.name,'image/svg+xml',data,json_text({'engine':engine,'sha256':core.sha256(data)}),now()))
    return doc

def propose(store,pid,base,engine,steps,summary,cancel=None):
    if store.get(pid)['version']!=base:raise Conflict('The project changed before editing')
    validate_steps(steps)
    with opened(store,pid,engine,cancel) as (s,root):
        for step in steps:
            if cancel and cancel.is_set():raise core.IllustrationError('Editing stopped')
            s.execute(step['command'],step.get('params',{}))
        f=get_frame(store.get(pid)['project']);doc=persist(store,pid,s,root,engine,f['document']['title'])
    if cancel and cancel.is_set():raise core.IllustrationError('Editing stopped')
    op={'op':'graphics_result','document':doc,'new_id':ident('frame')}
    return store.propose(pid,base,{'summary':summary,'operations':[op],'warnings':[],'provider':REPOS[engine]+' '+VERSIONS[engine]})

def import_artwork(store,pid,base,engine,name,raw,replace=False,title=None):
    if not raw or len(raw)>16_000_000:raise core.IllustrationError('Artwork limit is 16 MB')
    if Path(name).suffix.lower() not in {'.svg','.png','.jpg','.jpeg','.webp','.psd','.psb','.pcraft','.vectorcraft','.pdf','.tif','.tiff'}:raise core.IllustrationError('Unsupported artwork format')
    if store.get(pid)['version']!=base:raise Conflict('Artwork import is stale')
    if Path(name).suffix.lower()=='.svg':core.secure_svg(raw.decode())
    with opened(store,pid,engine,raw=raw,name=name) as (s,root):doc=persist(store,pid,s,root,engine,title or Path(name).stem)
    return store.edit(pid,base,[{'op':'graphics_result','document':doc,'new_id':ident('frame'),'append':not replace}],'Saved artwork' if replace else 'Imported artwork')
