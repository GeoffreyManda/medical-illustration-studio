"""Figure exports. Native lettering stays separate from painted image layers."""
from __future__ import annotations
from copy import deepcopy
from html import escape
import io
import os
import sys
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
from . import core,atelier
from .workspace import Store,get_frame,render_frame,annotated_asset,library,json_text


def cairo_renderer():
    # Homebrew's native libraries are outside macOS's default dyld search path.
    if sys.platform=='darwin' and 'DYLD_FALLBACK_LIBRARY_PATH' not in os.environ:
        folders=[str(p) for p in (Path('/opt/homebrew/lib'),Path('/usr/local/lib')) if (p/'libcairo.2.dylib').is_file()]
        if folders:os.environ['DYLD_FALLBACK_LIBRARY_PATH']=':'.join(folders+['/usr/lib'])
    try:
        import cairosvg
        return cairosvg
    except (ImportError,OSError) as error:
        raise core.IllustrationError('PNG, PDF and PowerPoint export require CairoSVG and the native Cairo library') from error


def dimensions(frame):
    d=frame['document']
    if frame['kind'] in {'plate','graphics'}:return d['width'],d['height'],d['print_width_mm']
    return d['canvas']['width'],d['canvas']['height'],d['canvas']['print_width_mm']


def frame_bytes(store:Store,pid:str,frame:dict,fmt:str,*,width_px=2400):
    if fmt not in {'svg','png','pdf','pptx'}:raise core.IllustrationError('Supported export formats are SVG, PNG, PDF and PPTX')
    svg=render_frame(frame,lambda mid:store.get_media(pid,mid))
    if fmt=='svg':return svg.encode()
    if not 300<=width_px<=8000:raise core.IllustrationError('Export width must be 300–8,000 px')
    w,h,_=dimensions(frame)
    if width_px*width_px*h/w>32_000_000:raise core.IllustrationError('Raster export exceeds 32 million pixels')
    if fmt=='pptx':return powerpoint(store,pid,[frame])
    cairosvg=cairo_renderer()
    if fmt=='png':return cairosvg.svg2png(bytestring=svg.encode(),output_width=width_px)
    return cairosvg.svg2pdf(bytestring=svg.encode())


def powerpoint(store:Store,pid:str,frames:list[dict]) -> bytes:
    """Atlas artwork is one picture; titles, captions, labels and leaders are native.

    This is a hybrid PPTX, not a promise that raster anatomy becomes editable
    biological structures. Schematics are embedded as one image per artboard.
    """
    from pptx import Presentation
    from pptx.util import Inches,Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_CONNECTOR
    from pptx.enum.text import MSO_AUTO_SIZE
    cairosvg=cairo_renderer()
    prs=Presentation();w0,h0,_=dimensions(frames[0]);prs.slide_width=Inches(10);prs.slide_height=Inches(10*h0/w0)
    for f in frames:
        slide=prs.slides.add_slide(prs.slide_layouts[6]);w,h,_=dimensions(f)
        factor=min(prs.slide_width/w,prs.slide_height/h)
        ox=(prs.slide_width-w*factor)/2;oy=(prs.slide_height-h*factor)/2
        def box(x,y,bw,bh):return [round(ox+x*factor),round(oy+y*factor),round(bw*factor),round(bh*factor)]
        def text(value,x,y,bw,bh,size,serif=False):
            shape=slide.shapes.add_textbox(*box(x,y,bw,bh));tf=shape.text_frame
            tf.clear();tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
            tf.word_wrap=True;tf.auto_size=MSO_AUTO_SIZE.NONE
            for i,line in enumerate(value.split('\n')):
                p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line
                p.font.name='Georgia' if serif else 'Arial';p.font.size=Pt(size*factor/12700)
                p.font.color.rgb=RGBColor.from_string('38332E');p.space_after=Pt(0)
            return shape
        if f['kind']!='plate':
            raw=frame_bytes(store,pid,f,'png',width_px=2400)
            slide.shapes.add_picture(io.BytesIO(raw),*box(0,0,w,h));continue
        d=f['document'];a=annotated_asset(f);x,y,bw,bh=d['art_box']
        if f.get('artwork_media_id'):
            raw=store.get_media(pid,f['artwork_media_id'])['data']
        else:
            svg=atelier.staged_svg(a['svg'],f['stage']);raw=core.export_svg(svg,'png',width_px=1800)
        from PIL import Image
        aw,ah=Image.open(io.BytesIO(raw)).size;scale=min(bw/aw,bh/ah)
        slide.shapes.add_picture(io.BytesIO(raw),*box(x+(bw-aw*scale)/2,y+(bh-ah*scale)/2,aw*scale,ah*scale))
        text(d['title'],42,22,w-84,43,30,True)
        text(d['subtitle'],42,67,w-84,27,15)
        text(d['caption'],42,h-115,w-84,65,14)
        text(d['reference_line'],42,h-47,w-84,30,11)
        if f['show_labels']:
            fs=d['label_size']
            for row in atelier.label_layout(d,a):
                tx,ty=row['target'];cy=row['y']+row['height']/2
                if row['side']=='left':
                    tw=max(core.text_width(line,fs) for line in row['lines']);sx=row['x']+tw+7;ex=max(sx+8,min(tx-15,row['x']+row['width']+22))
                else:sx=row['x']-8;ex=min(sx-8,max(tx+15,row['x']-25))
                for x1,y1,x2,y2 in [(sx,cy,ex,cy),(ex,cy,tx,ty)]:
                    line=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,round(ox+x1*factor),round(oy+y1*factor),round(ox+x2*factor),round(oy+y2*factor))
                    line.line.color.rgb=RGBColor.from_string('665E57');line.line.width=Pt(.6)
                text('\n'.join(row['lines']),row['x'],row['y']-fs*.12,row['width'],row['height']+fs*.25,fs)
    out=io.BytesIO();prs.save(out);return out.getvalue()


def bundle(store:Store,pid:str) -> bytes:
    p=store.get(pid)['project'];out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('project.json',json.dumps(p,indent=2))
        used=set()
        for f in p['frames']:
            z.writestr('figures/'+f['id']+'.svg',render_frame(f,lambda mid:store.get_media(pid,mid)))
            if f.get('artwork_media_id'):used.add(f['artwork_media_id'])
            if f['kind']=='graphics':used.update(f['document'][k] for k in ('native_media_id','preview_media_id','svg_media_id') if f['document'].get(k))
        used.update(r['media_id'] for r in p['references'] if r.get('media_id'))
        for mid in sorted(used):
            m=store.get_media(pid,mid);z.writestr('media/'+mid,m['data'])
            z.writestr('media/'+mid+'.json',json_text({'id':mid,'name':m['name'],'mime':m['mime'],'metadata':m['metadata']}))
        z.writestr('README.txt','Editable project document and figures. Original bundled SVG assets are CC0-1.0. Imported or provider-generated media retain their own terms; they are not relicensed as CC0. Hybrid SVG/PPTX images do not expose raster anatomy as vector structures. Source and licence declarations appear in project references. Production control records are deliberately excluded from this figure bundle.\n')
    return out.getvalue()


def import_bundle(store:Store,raw:bytes) -> dict:
    """Restore a portable project without extracting arbitrary paths to disk."""
    from pathlib import PurePosixPath
    from .workspace import ident,validate_project,media_normalize,now,MAX_MEDIA,MAX_PROJECT
    if not raw or len(raw)>18_000_000:raise core.IllustrationError('Portable bundle limit is 18 MB')
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            info=z.infolist();names=[n.filename for n in info]
            if len(info)>200 or sum(n.file_size for n in info)>64_000_000:raise core.IllustrationError('Bundle expands beyond the allowed size')
            if len(set(names))!=len(names):raise core.IllustrationError('Duplicate bundle entry')
            if any(PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts or '\\' in n for n in names):raise core.IllustrationError('Unsafe bundle path')
            if 'project.json' not in names or z.getinfo('project.json').file_size>MAX_PROJECT:raise core.IllustrationError('Missing or oversized project document')
            p=json.loads(z.read('project.json'));validate_project(p);p['id']=ident('project')
            ids={f['artwork_media_id'] for f in p['frames'] if f.get('artwork_media_id')}
            ids.update(f['document'][k] for f in p['frames'] if f['kind']=='graphics' for k in ('native_media_id','preview_media_id','svg_media_id') if f['document'].get(k))
            ids.update(r['media_id'] for r in p['references'] if r.get('media_id'))
            graphics_svgs={f['document']['svg_media_id'] for f in p['frames'] if f['kind']=='graphics' and f['document'].get('svg_media_id')}
            rows=[];mapping={}
            for old in ids:
                key='media/'+old
                if key not in names or key+'.json' not in names or z.getinfo(key).file_size>MAX_MEDIA:raise core.IllustrationError('Missing or oversized media')
                meta=json.loads(z.read(key+'.json'))
                ext={'image/png':'.png','image/svg+xml':'.svg','application/pdf':'.pdf','text/plain':'.txt'}.get(meta['mime'])
                if meta['mime'] in {'application/x-photocraft','application/x-vectorcraft'}:
                    mime=meta['mime'];data=z.read(key);metadata={'native':True,'engine':'photo' if mime.endswith('photocraft') else 'vector'};ext='.pcraft' if mime.endswith('photocraft') else '.vectorcraft'
                elif old in graphics_svgs:
                    from .graphics import passive_svg
                    data=z.read(key);passive_svg(data);mime='image/svg+xml';metadata={'engine':'vector'};ext='.svg'
                else:
                    if not ext:raise core.IllustrationError('Unsupported bundle media')
                    mime,data,metadata=media_normalize('import'+ext,z.read(key))
                metadata.update({'imported_from_bundle':True,'medical_review':False})
                mid=ident('media');mapping[old]=mid;rows.append((mid,p['id'],str(meta.get('name','import'+ext))[:240],mime,data,json_text(metadata),now()))
            for f in p['frames']:
                if f.get('artwork_media_id'):f['artwork_media_id']=mapping[f['artwork_media_id']]
                if f['kind']=='graphics':
                    for k in ('native_media_id','preview_media_id','svg_media_id'):
                        if f['document'].get(k):f['document'][k]=mapping[f['document'][k]]
            for r in p['references']:
                if r.get('media_id'):r['media_id']=mapping[r['media_id']]
            validate_project(p);text=json_text(p);stamp=now()
            with store.connect() as c:
                c.execute('INSERT INTO projects VALUES(?,?,?,?)',(p['id'],1,text,stamp))
                c.execute('INSERT INTO versions VALUES(?,?,?,?,?)',(p['id'],1,text,'Imported portable project',stamp))
                c.executemany('INSERT INTO media VALUES(?,?,?,?,?,?,?)',rows)
            return {'project':p,'version':1}
    except core.IllustrationError:raise
    except (KeyError,TypeError,ValueError,zipfile.BadZipFile,UnicodeError) as exc:raise core.IllustrationError('Invalid portable project bundle') from exc
