"""Loopback-only web workspace. No provider credentials are served to the browser."""
from __future__ import annotations
import argparse
import base64
from copy import deepcopy
import json
import os
from pathlib import Path
import secrets
from urllib.parse import urlparse
from typing import Any
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import HTMLResponse,JSONResponse,Response,FileResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from . import core,atelier
from .workspace import Store,Conflict,library,new_project,get_frame,render_frame,apply_operations,seed_data,VERSION
from . import agent,providers,exports,graphics

STATIC=Path(__file__).parent/'static'


def make_app(db: str|Path | None=None) -> FastAPI:
    app=FastAPI(title='Medical Illustration Studio',version=VERSION,docs_url=None,redoc_url=None)
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=['127.0.0.1','localhost','[::1]','testserver'])
    store=Store(db or os.environ.get('MEDILLUSTRATE_DB',str(Path.home()/'.medillustrate'/'studio.sqlite3')))
    if not store.list_projects():store.create()
    token=secrets.token_urlsafe(32);app.state.store=store;app.state.csrf=token

    @app.middleware('http')
    async def local_security(request:Request,call_next):
        origin=request.headers.get('origin')
        if origin and origin!=str(request.base_url).rstrip('/'):
            return JSONResponse({'error':'Cross-origin access is not allowed'},status_code=403)
        if request.method not in {'GET','HEAD','OPTIONS'}:
            if not secrets.compare_digest(request.headers.get('x-studio-token',''),token):
                return JSONResponse({'error':'Missing or invalid workspace session token'},status_code=403)
            try:length=int(request.headers.get('content-length','0'))
            except ValueError:return JSONResponse({'error':'Invalid request length'},status_code=400)
            if length>24_000_000:return JSONResponse({'error':'Request exceeds 24 MB'},status_code=413)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Cache-Control']='no-store'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; frame-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        if request.url.path.startswith('/engines/'):
            response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; worker-src 'self' blob:; object-src 'none'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
        return response

    @app.exception_handler(core.IllustrationError)
    async def illustration_error(request,exc):return JSONResponse({'error':str(exc)},status_code=409 if isinstance(exc,Conflict) else 400)

    @app.exception_handler(KeyError)
    async def missing_field(request,exc):return JSONResponse({'error':'Missing required request field: '+str(exc)},status_code=400)

    @app.exception_handler(ValueError)
    @app.exception_handler(TypeError)
    async def invalid_field(request,exc):return JSONResponse({'error':'Invalid request value: '+str(exc)[:240]},status_code=400)

    async def body(request):
        try:
            raw=await request.body()
            if len(raw)>24_000_000:raise HTTPException(413,'Request is too large')
            value=json.loads(raw)
            if not isinstance(value,dict):raise ValueError('Object required')
            return value
        except (ValueError,UnicodeError):raise HTTPException(400,'Expected a JSON object')

    @app.get('/')
    def home():return HTMLResponse((STATIC/'studio.html').read_text())
    @app.get('/static/{name}')
    def static(name:str):
        if name not in {'studio.js','studio.css'}:raise HTTPException(404)
        return FileResponse(STATIC/name)
    @app.get('/engines/{engine}/{asset:path}')
    def engine_asset(engine:str,asset:str):
        root=graphics.web_root(engine).resolve();path=(root/(asset or 'index.html')).resolve()
        if engine=='photo' and asset.startswith('app/snippets/'):
            path=(root/asset.removeprefix('app/')).resolve()
        if not path.is_relative_to(root) or not path.is_file():raise HTTPException(404)
        return FileResponse(path)
    @app.get('/api/session')
    def session():return {'token':token,'version':VERSION,'mode':'server','providers':{'local':True,'codex':agent.subscription_status()['installed'],'ollama':bool(os.environ.get('MEDILLUSTRATE_OLLAMA_MODEL')),'figurelabs':bool(os.environ.get('FIGURELABS_API_KEY'))},'ollama_model':os.environ.get('MEDILLUSTRATE_OLLAMA_MODEL','')}
    @app.get('/api/bootstrap')
    def bootstrap():
        assets=[]
        for a in library().values():assets.append({k:v for k,v in a.items()})
        templates=deepcopy(seed_data()['templates'])
        for t in templates:
            if t['kind']=='scene':t['svg']=core.render(t['document'],library())
        return {'assets':assets,'templates':templates,'contracts':core.resource('anatomy-contracts.json')['contracts'],'materials':core.resource('tissue-materials.json')['materials'],'sources':core.resource('refinement-sources.json')['sources']}
    @app.get('/api/graphics')
    def graphics_status():return graphics.status()
    @app.get('/api/projects/{pid}/graphics/commands')
    def graphics_commands(pid:str,engine:str,query:str=''):return graphics.commands(store,pid,engine,query)
    @app.get('/api/projects/{pid}/graphics/inspect')
    def graphics_inspect(pid:str,engine:str):return graphics.inspect(store,pid,engine)
    @app.post('/api/projects/{pid}/graphics/propose')
    async def graphics_propose(pid:str,request:Request):
        b=await body(request)
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(graphics.propose,store,pid,b['base_version'],b['engine'],b['steps'],b.get('summary','Graphics edit'))
    @app.post('/api/projects/{pid}/graphics/import')
    async def graphics_import(pid:str,request:Request):
        b=await body(request)
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(graphics.import_artwork,store,pid,b['base_version'],b['engine'],b['name'],base64.b64decode(b['data'],validate=True),b.get('replace',False),b.get('title'))
    @app.get('/api/projects/{pid}/graphics/native')
    def graphics_native(pid:str):
        f=get_frame(store.get(pid)['project'])
        if f['kind']!='graphics':raise core.IllustrationError('Select a pixel or vector artboard')
        m=store.get_media(pid,f['document']['native_media_id'])
        return Response(m['data'],media_type=m['mime'],headers={'Content-Disposition':'attachment; filename="artwork'+graphics.NATIVE[f['document']['engine']]+'"'})
    @app.get('/api/projects')
    def projects():return store.list_projects()
    @app.post('/api/projects')
    async def create(request:Request):
        b=await body(request)
        return store.create(new_project(b.get('title','Untitled illustration'),b.get('template_id','atlas-kidney-section')))
    @app.get('/api/projects/{pid}')
    def project(pid:str,version:int|None=None):return store.get(pid,version)
    @app.post('/api/projects/{pid}/edit')
    async def edit(pid:str,request:Request):
        b=await body(request);return store.edit(pid,b['base_version'],b['operations'],b.get('reason','Manual edit'))
    @app.get('/api/projects/{pid}/history')
    def history(pid:str):return store.history(pid)
    @app.post('/api/projects/{pid}/restore')
    async def restore(pid:str,request:Request):
        b=await body(request);return store.restore(pid,b['base_version'],b['version'])
    @app.post('/api/projects/{pid}/agent')
    async def agent_edit(pid:str,request:Request):
        b=await body(request)
        # Run blocking model request outside the asynchronous request loop.
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(agent.propose,store,pid,b['base_version'],b['prompt'],b.get('provider','local'),b.get('reference_ids',[]),b.get('consent',False))
    @app.post('/api/projects/{pid}/composer')
    async def composer(pid:str,request:Request):
        b=await body(request)
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(agent.compose,store,pid,b['base_version'],b['prompt'],b.get('reference_ids',[]),b.get('consent',False),b.get('run_id'))
    @app.get('/api/projects/{pid}/conversation')
    def conversation(pid:str):return agent.composer_history(store,pid)
    @app.post('/api/projects/{pid}/composer/cancel')
    async def cancel_composer(pid:str,request:Request):
        b=await body(request);return agent.cancel_composer(pid,b['run_id'])
    @app.get('/api/projects/{pid}/proposals/{qid}')
    def proposal(pid:str,qid:str):return store.proposal(pid,qid)
    @app.get('/api/projects/{pid}/proposals')
    def proposals_list(pid:str):
        store.get(pid)
        with store.connect() as c:
            return [{**json.loads(r['body']),'status':r['status']} for r in c.execute('SELECT body,status FROM proposals WHERE project=? ORDER BY created DESC',(pid,))]
    @app.post('/api/projects/{pid}/proposals/{qid}/decide')
    async def decide(pid:str,qid:str,request:Request):
        b=await body(request)
        if not isinstance(b.get('accept'),bool):raise core.IllustrationError('accept must be boolean')
        return store.decide(pid,qid,b['accept'])
    @app.get('/api/projects/{pid}/render')
    def render(pid:str,frame_id:str|None=None,version:int|None=None,proposal_id:str|None=None):
        snap=store.get(pid,version);p=snap['project']
        if proposal_id:
            q=store.proposal(pid,proposal_id)
            if q['base_version']!=snap['version']:raise Conflict('Preview proposal is stale')
            p=apply_operations(p,q['operations'])
        f=get_frame(p,frame_id)
        return Response(render_frame(f,lambda mid:store.get_media(pid,mid)),media_type='image/svg+xml')
    @app.post('/api/projects/{pid}/references')
    async def reference(pid:str,request:Request):
        b=await body(request);raw=None
        if b.get('data'):
            try:raw=base64.b64decode(b['data'],validate=True)
            except ValueError:raise core.IllustrationError('Invalid file encoding')
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(store.add_reference,pid,b['base_version'],title=b['title'],url=b.get('url',''),note=b.get('note',''),name=b.get('name'),raw=raw,licence=b.get('licence','Not specified'))
    @app.get('/api/projects/{pid}/media/{mid}')
    def media(pid:str,mid:str):
        m=store.get_media(pid,mid)
        # PDFs are served as attachments, never as an active document inside the application.
        headers={'Content-Disposition':'attachment'} if m['mime']=='application/pdf' else {}
        return Response(m['data'],media_type=m['mime'],headers=headers)
    @app.get('/api/projects/{pid}/references/{rid}/text')
    def reference_text(pid:str,rid:str):
        r=next((r for r in store.get(pid)['project']['references'] if r['id']==rid),None)
        if r is None:raise HTTPException(404)
        m=store.get_media(pid,r['media_id']) if r['media_id'] else None
        return {'text':(r['note']+'\n'+(m['metadata'].get('extracted_text','') if m else ''))[:60000]}
    @app.post('/api/projects/{pid}/paint')
    async def paint(pid:str,request:Request):
        b=await body(request)
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(providers.submit_paint,store,pid,b['base_version'],b['instruction'],consent=b.get('consent',False),region=b.get('region'))
    @app.get('/api/projects/{pid}/paint')
    def jobs(pid:str):return [{k:v for k,v in j.items() if k!='frame_snapshot'} for j in store.jobs(pid)]
    @app.post('/api/projects/{pid}/paint/{jid}/refresh')
    def refresh_paint(pid:str,jid:str):return providers.poll_paint(store,pid,jid)
    @app.post('/api/projects/{pid}/adopt')
    async def adopt(pid:str,request:Request):
        b=await body(request);return store.adopt_candidate(pid,b['base_version'],b['frame_id'],b['media_id'],confirm_landmarks=b.get('confirm_landmarks',False))
    @app.get('/api/projects/{pid}/export/{fmt}')
    def export(pid:str,fmt:str,frame_id:str|None=None,width_px:int=2400):
        p=store.get(pid)['project'];f=get_frame(p,frame_id)
        if fmt=='json':data=json.dumps(p,indent=2).encode();mime='application/json'
        elif fmt=='zip':data=exports.bundle(store,pid);mime='application/zip'
        elif fmt=='control':data=json.dumps(store.control(pid),indent=2).encode();mime='application/json'
        else:
            data=exports.frame_bytes(store,pid,f,fmt,width_px=width_px)
            mime={'svg':'image/svg+xml','png':'image/png','pdf':'application/pdf','pptx':'application/vnd.openxmlformats-officedocument.presentationml.presentation'}.get(fmt,'application/octet-stream')
        return Response(data,media_type=mime,headers={'Content-Disposition':f'attachment; filename="{pid}.{fmt if fmt!="control" else "control.json"}"'})
    @app.post('/api/import')
    async def import_project(request:Request):
        b=await body(request);p=b['project'];p['id']='project-'+secrets.token_hex(8)
        # JSON-only imports cannot resolve external blobs. Reject instead of producing broken artwork.
        if any(f.get('artwork_media_id') or f.get('kind')=='graphics' for f in p['frames']) or any(r.get('media_id') for r in p['references']):
            raise core.IllustrationError('This JSON needs media. Restore its original database or import the project bundle, not a detached document.')
        return store.create(p)
    @app.post('/api/import-bundle')
    async def import_bundle(request:Request):
        b=await body(request)
        try:raw=base64.b64decode(b['data'],validate=True)
        except ValueError:raise core.IllustrationError('Invalid bundle encoding')
        return exports.import_bundle(store,raw)
    return app


def main(argv=None):
    p=argparse.ArgumentParser(description='Local medical illustration workspace')
    p.add_argument('--port',type=int,default=8765);p.add_argument('--db');args=p.parse_args(argv)
    if not 1024<=args.port<=65535:raise SystemExit('Choose a port between 1024 and 65535')
    import uvicorn
    uvicorn.run(make_app(args.db),host='127.0.0.1',port=args.port,log_level='warning')

if __name__=='__main__':main()
