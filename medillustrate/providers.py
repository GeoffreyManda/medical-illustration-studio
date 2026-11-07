"""Optional FigureLabs adapter, implemented against public V1 documentation.

No request is made without explicit per-task authorization. Billable POSTs are
never retried automatically. A server timeout is an ambiguous submission, not a
license to generate again. Credentials are read from the environment only.
"""
from __future__ import annotations
import base64
import io
import ipaddress
import json
import os
import re
import socket
from urllib.parse import urlparse
from typing import Any
from . import atelier, core
from .workspace import Store,get_frame,ident,now,annotated_asset,Conflict

BASE='https://api.figurelabs.ai'
TERMINAL={'succeeded','failed','rejected','canceled'}


def paint_prompt(frame:dict,instruction:str) -> str:
    brief=atelier.generation_brief(frame['document'])
    text=('Refine the supplied unlabelled anatomical drawing as a classical painted medical atlas illustration. '
          'Preserve silhouette, view, structure boundaries, collecting/vessel continuity and all unselected structures. '
          'Use material-specific tonal modelling, restrained highlights, natural tissue colours, and directional fibres. '
          'White background. No lettering, arrows, signature, credentials, logos, extra structures or decorative effects. '
          +'Anatomical constraints: '+'; '.join(brief['anatomy_must_preserve'])+' Requested refinement: '+instruction.strip())
    if not instruction.strip():raise core.IllustrationError('Describe the desired refinement')
    if len(text)>2000:raise core.IllustrationError('Refinement instruction exceeds the provider prompt allowance; shorten it without dropping anatomy constraints')
    return text


def png_artwork(store:Store,pid:str,frame:dict) -> bytes:
    if frame.get('artwork_media_id'):return store.get_media(pid,frame['artwork_media_id'])['data']
    svg=annotated_asset(frame)['svg']
    return core.export_svg(svg,'png',width_px=1600)


def mask_png(size:tuple[int,int],region:list[float]) -> bytes:
    from PIL import Image,ImageDraw
    if len(region)!=4 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not 0<=v<=1 for v in region):
        raise core.IllustrationError('Mask box must contain four normalized coordinates')
    x,y,w,h=region
    if w<=0 or h<=0 or x+w>1 or y+h>1:raise core.IllustrationError('Mask rectangle must fit within the artwork')
    width,height=size
    im=Image.new('RGB',size,'black');dr=ImageDraw.Draw(im)
    dr.rectangle([int(x*width),int(y*height),min(width-1,int((x+w)*width)-1),min(height-1,int((y+h)*height)-1)],fill='white')
    out=io.BytesIO();im.save(out,format='PNG');return out.getvalue()


def preserve_outside_region(source:bytes,candidate:bytes,region:list[float]) -> bytes:
    """Enforce exact unchanged source pixels outside a local edit mask."""
    from PIL import Image
    src=Image.open(io.BytesIO(source)).convert('RGBA')
    new=Image.open(io.BytesIO(candidate)).convert('RGBA')
    if new.size!=src.size:new=new.resize(src.size,Image.Resampling.LANCZOS)
    mask=Image.open(io.BytesIO(mask_png(src.size,region))).convert('L')
    merged=Image.composite(new,src,mask);out=io.BytesIO();merged.save(out,format='PNG')
    return out.getvalue()


def data_uri(data:bytes) -> str:return 'data:image/png;base64,'+base64.b64encode(data).decode()


def allowed_output_url(url:str) -> None:
    parsed=urlparse(url)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.port not in {None,443}:
        raise core.IllustrationError('Provider output must be an HTTPS URL without credentials')
    try:ips={r[4][0] for r in socket.getaddrinfo(parsed.hostname,443,type=socket.SOCK_STREAM)}
    except OSError as e:raise core.IllustrationError('Cannot resolve provider output host') from e
    if any(not ipaddress.ip_address(ip).is_global for ip in ips):
        raise core.IllustrationError('Provider output URL points to a non-public network')


class FigureLabs:
    def __init__(self,client=None,key=None):
        import httpx
        self.key=key if key is not None else os.environ.get('FIGURELABS_API_KEY','')
        self.client=client or httpx.Client(timeout=90,follow_redirects=False,trust_env=False)
        self.owned=client is None
    def close(self):
        if self.owned:self.client.close()
    def auth(self):
        if not self.key:raise core.IllustrationError('Set FIGURELABS_API_KEY on the server; no key is stored in the browser or project')
        return {'Authorization':'Bearer '+self.key}
    def submit(self,payload:dict) -> dict:
        r=self.client.post(BASE+'/v1/images/generations',headers=self.auth(),json=payload)
        r.raise_for_status();j=r.json()
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',j.get('task_id','')):raise core.IllustrationError('Invalid task identifier in provider response')
        return j
    def status(self,task_id:str) -> dict:
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',task_id):raise core.IllustrationError('Invalid task identifier')
        r=self.client.get(BASE+'/v1/tasks/'+task_id,headers=self.auth());r.raise_for_status();return r.json()
    def download(self,url:str) -> bytes:
        allowed_output_url(url)
        # No Authorization header is forwarded to the signed storage URL.
        with self.client.stream('GET',url) as r:
            r.raise_for_status();data=bytearray()
            for chunk in r.iter_bytes():
                data.extend(chunk)
                if len(data)>16_000_000:raise core.IllustrationError('Provider image is larger than 16 MB')
        return bytes(data)


def submit_paint(store:Store,pid:str,base:int,instruction:str,*,consent:bool,region=None,provider=None):
    if not consent:raise core.IllustrationError('Explicit authorization is required: this transmits the current unlabelled artwork and instruction and may incur provider charges')
    snap=store.get(pid)
    if snap['version']!=base:raise Conflict('The artwork changed before provider submission')
    frame=get_frame(snap['project'])
    if frame['kind']!='plate':raise core.IllustrationError('Reference-guided painting requires an atlas artboard')
    prompt=paint_prompt(frame,instruction);source=png_artwork(store,pid,frame)
    payload={'mode':'generations','prompt':prompt,'style':'hand_drawn','imageUrl':data_uri(source),'format':'png','quality':'high'}
    if region is not None:
        from PIL import Image
        size=Image.open(io.BytesIO(source)).size
        payload.update({'mode':'region_redraw','mask':data_uri(mask_png(size,region))})
    api=provider or FigureLabs()
    # Validate missing credentials before creating an ambiguous-submission record.
    if hasattr(api,'auth'):
        try:api.auth()
        except Exception:
            if provider is None:api.close()
            raise
    job={'id':ident('paint'),'project_id':pid,'base_version':base,'frame_id':frame['id'],
         'status':'submitting','created':now(),'provider':'FigureLabs','instruction':instruction,'region':region,
         'frame_snapshot':frame,'source_sha256':core.sha256(source),'task_id':None,'candidate_media_id':None,
         'anatomical_review':'not performed'}
    store.put_job(pid,job)
    try:
        result=api.submit(payload)
        job.update({'task_id':result['task_id'],'status':result.get('status','processing'),
                    'session_id':result.get('session_id'),'estimated_price':result.get('estimated_price'),'currency':result.get('currency')})
    except Exception as exc:
        job['status']='submission_unknown';job['error']='Submission did not complete locally. Check the provider account before retrying; a task may have been charged.'
        store.put_job(pid,job);store.event(pid,'paint_submission',{'job_id':job['id'],'status':job['status'],'automatic_retries':0})
        raise core.IllustrationError(job['error']) from exc
    finally:
        if provider is None:api.close()
    store.put_job(pid,job);store.event(pid,'paint_submission',{'job_id':job['id'],'task_id':job['task_id'],'source_sha256':job['source_sha256'],'automatic_retries':0})
    return {k:v for k,v in job.items() if k!='frame_snapshot'}


def poll_paint(store:Store,pid:str,jid:str,provider=None):
    job=store.job(pid,jid)
    if not job.get('task_id'):raise core.IllustrationError('No confirmed task ID; check the provider account before resubmitting')
    if job.get('candidate_media_id'):return {k:v for k,v in job.items() if k!='frame_snapshot'}
    api=provider or FigureLabs()
    try:
        result=api.status(job['task_id']);status=result.get('status')
        if status not in TERMINAL|{'pending','processing'}:raise core.IllustrationError('Unrecognized provider task status')
        job['status']=status
        for key in ('actual_price','estimated_price','currency','error'):job[key]=result.get(key)
        if status=='succeeded':
            raw=api.download(result['output_url'])
            if job.get('region'):
                source=png_artwork(store,pid,job['frame_snapshot'])
                raw=preserve_outside_region(source,raw,job['region'])
            mid=store.put_candidate(pid,'painted-candidate.png',raw,{'provider':'FigureLabs','task_id':job['task_id'],'base_version':job['base_version'], 'frame_id':job['frame_id'], 'source_sha256':job['source_sha256'],'medical_review':False,'region':job['region']})
            job['candidate_media_id']=mid
    except core.IllustrationError:raise
    except Exception as e:raise core.IllustrationError('Could not retrieve the provider task. No new generation was submitted.') from e
    finally:
        if provider is None:api.close()
    store.put_job(pid,job)
    return {k:v for k,v in job.items() if k!='frame_snapshot'}
