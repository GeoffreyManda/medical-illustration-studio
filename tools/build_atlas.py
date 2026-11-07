"""Build a self-contained, offline handbook and asset browser.
Requires the optional docs dependency: markdown-it-py.
No remote stylesheets, fonts, images, analytics or assets are loaded.
"""
from __future__ import annotations
from pathlib import Path
import base64
import html
import json
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from markdown_it import MarkdownIt
from medillustrate.core import assets, resource

DOCS=[('handbook','The handbook','docs/handbook.md'),('grammar','Visual grammar','docs/grammar.md'),
 ('art-direction','Anatomy and art direction','docs/anatomy-and-art-direction.md'),
 ('layouts','Layout atlas','docs/layout-atlas.md'),('workflows','Agent workflows','docs/agent-workflows.md'),
 ('research','Research and sources','docs/research-and-open-resources.md'),
 ('benchmark','Comparative evaluation','docs/benchmark.md'),('quickstart','Run the toolkit','README.md')]
CSS='''
:root{color-scheme:light;--ink:#263e49;--muted:#536874;--line:#d9e0e1;--paper:#fff;--tint:#f5f7f7;--link:#215b71}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:28px}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
a{color:var(--link);text-underline-offset:3px}a:hover{text-decoration-thickness:2px}button,input,select{font:inherit}button{cursor:pointer;color:var(--ink);background:#fff;border:1px solid #a8b7bd;padding:9px 15px;border-radius:3px}button:hover{background:var(--tint)}button:focus-visible,input:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid #426f86;outline-offset:3px}
.shell{display:grid;grid-template-columns:226px minmax(0,1fr);max-width:1530px;margin:auto}aside{border-right:1px solid var(--line);padding:38px 25px;position:sticky;top:0;height:100vh;overflow:auto}.brand{font-weight:650;font-size:18px;line-height:1.4;margin-bottom:8px}.edition{font-size:13px;color:var(--muted);margin:0 0 28px}nav a{display:block;padding:7px 0;text-decoration:none;font-size:14px}nav a:hover{text-decoration:underline}.aside-note{font-size:12px;line-height:1.6;color:var(--muted);border-top:1px solid var(--line);padding-top:19px;margin-top:26px}
main{min-width:0;padding:44px 54px 100px}header{max-width:960px;margin-bottom:34px}.eyebrow{font-size:13px;letter-spacing:.08em;color:var(--muted);text-transform:uppercase;margin:0 0 13px}h1{font-size:36px;line-height:1.2;font-weight:650;letter-spacing:-.025em;margin:0 0 20px}h2{font-size:27px;line-height:1.35;font-weight:620;letter-spacing:-.018em;margin:42px 0 17px}h3{font-size:20px;line-height:1.4;font-weight:650;margin:30px 0 12px}h4{font-size:17px;line-height:1.4}p{margin:0 0 17px}.lede{font-size:19px;line-height:1.6;max-width:820px}.meta{font-size:14px;color:var(--muted)}.section{border-top:1px solid var(--line);padding-top:16px;margin-top:56px}.prose{max-width:850px}.prose>h1{font-size:30px;margin-top:22px}.prose li{margin-bottom:6px}.prose table{border-collapse:collapse;display:block;overflow-x:auto;font-size:14px;width:100%;margin:24px 0}.prose th,.prose td{text-align:left;vertical-align:top;padding:11px 14px;border-bottom:1px solid var(--line);min-width:140px}.prose th{font-weight:650;background:var(--tint)}.prose code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.86em;background:#f0f3f3;padding:2px 4px;border-radius:2px}.prose pre{background:var(--tint);padding:20px;overflow:auto;line-height:1.6;font-size:14px;border:1px solid var(--line)}.prose pre code{background:none;padding:0;font-size:inherit}.prose blockquote{margin:24px 0;padding:4px 24px;border-left:2px solid #9eb3bc;color:#3d5561}.cite{font-size:.88em;white-space:normal}.jump{font-size:13px;margin-bottom:20px;display:inline-block}
.figure{margin:28px 0 42px}.figure img{display:block;width:100%;height:auto;border:1px solid #e2e6e7;background:#fff}.figure figcaption{font-size:14px;color:var(--muted);padding-top:11px}.hero-example{max-width:980px}
.toolbar{display:flex;align-items:end;gap:18px;flex-wrap:wrap;margin:25px 0}.field{display:flex;flex-direction:column;gap:6px}.field label{font-size:14px;font-weight:600}input,select{border:1px solid #a8b7bd;border-radius:3px;padding:10px 12px;color:var(--ink);background:#fff}input{min-width:310px}#asset-count{font-size:14px;color:var(--muted);margin-bottom:4px}.asset-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0 23px}.asset{border:0;border-bottom:1px solid var(--line);border-radius:0;padding:20px 0;text-align:left;display:flex;flex-direction:column;background:#fff;min-width:0}.asset:hover{background:#fafbfb}.asset img{width:100%;height:145px;object-fit:contain;padding:10px 12px;margin-bottom:12px}.asset strong{font-size:14px;font-weight:600;line-height:1.4;display:block}.asset span{font-size:12px;color:var(--muted);display:block;margin-top:4px}.empty{padding:30px 0;color:var(--muted)}
dialog{border:1px solid var(--line);border-radius:4px;color:var(--ink);padding:30px;width:min(850px,94vw);max-height:90vh;overflow:auto}dialog::backdrop{background:rgba(20,35,43,.4)}.dialog-head{display:flex;justify-content:space-between;align-items:start;gap:20px}.dialog-head h2{margin:0;font-size:25px}.dialog-body{display:grid;grid-template-columns:260px minmax(0,1fr);gap:30px;margin:20px 0}.dialog-body img{width:100%;height:270px;object-fit:contain}.dialog-body p{font-size:14px}.dialog-body dt{font-size:13px;font-weight:650}.dialog-body dd{margin:1px 0 12px;font-size:14px}.buttons{display:flex;gap:12px;flex-wrap:wrap}details{margin:18px 0}summary{cursor:pointer;font-weight:600}#asset-json{white-space:pre-wrap;font-size:12px;background:var(--tint);padding:18px;overflow-wrap:anywhere}.footer{border-top:1px solid var(--line);padding-top:25px;margin-top:60px;font-size:13px;color:var(--muted)}
@media(max-width:1150px){main{padding:38px 30px}.asset-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.shell{grid-template-columns:205px minmax(0,1fr)}aside{padding:30px 20px}}
@media(max-width:800px){.shell{display:block}aside{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line);padding:25px}nav{display:flex;gap:3px 19px;flex-wrap:wrap}.aside-note{display:none}.edition{margin-bottom:10px}main{padding:30px 22px 70px}h1{font-size:31px}.asset-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.dialog-body{grid-template-columns:1fr}.dialog-body img{height:200px}.field,input,select{max-width:100%}input{min-width:0;width:100%}.toolbar{align-items:stretch;flex-direction:column}}
@media print{aside,.toolbar,.asset-grid,dialog,.jump{display:none}.shell{display:block}main{padding:0}body{font-size:10pt}.prose{max-width:none}a{color:inherit}.figure{break-inside:avoid}.section{break-before:page}.prose pre{white-space:pre-wrap}.prose table{display:table}h2,h3{break-after:avoid}}
'''
JS=r'''
const library=JSON.parse(document.getElementById('library-data').textContent);
const search=document.getElementById('search');const category=document.getElementById('category');
const grid=document.getElementById('asset-grid');const count=document.getElementById('asset-count');
const dialog=document.getElementById('asset-dialog');let selected=null;
function uri(svg){return 'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);}
function download(name,content,type){const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function showAsset(a){selected=a;document.getElementById('asset-title').textContent=a.label;document.getElementById('asset-image').src=uri(a.svg);document.getElementById('asset-image').alt=a.label;
 document.getElementById('asset-limits').textContent=a.limitations;document.getElementById('asset-identity').textContent=a.id;
 document.getElementById('asset-category').textContent=a.category+' / '+a.scale_class;
 document.getElementById('asset-rights').textContent=a.license+'; '+a.creator;
 document.getElementById('asset-status').textContent='Schematic; independent asset-level medical review has not been performed.';
 const metadata={...a};delete metadata.svg;document.getElementById('asset-json').textContent=JSON.stringify(metadata,null,2);dialog.showModal();}
function redraw(){const q=search.value.toLowerCase().trim();const cat=category.value;const items=library.filter(a=>(!cat||a.category===cat)&&[a.id,a.label,a.category,a.limitations,...a.aliases].join(' ').toLowerCase().includes(q));
 grid.replaceChildren();count.textContent=items.length+' of '+library.length+' original vector records';
 if(!items.length){const p=document.createElement('p');p.className='empty';p.textContent='No matching asset. Try a broader biological term or clear the category filter.';grid.appendChild(p);return;}
 for(const a of items){const button=document.createElement('button');button.className='asset';button.type='button';button.setAttribute('aria-label','Inspect '+a.label);const img=document.createElement('img');img.src=uri(a.svg);img.alt='';img.loading='lazy';const title=document.createElement('strong');title.textContent=a.label;const sub=document.createElement('span');sub.textContent=a.category;button.append(img,title,sub);button.addEventListener('click',()=>showAsset(a));grid.appendChild(button);}}
for(const c of [...new Set(library.map(a=>a.category))].sort()){const option=document.createElement('option');option.value=c;option.textContent=c;category.appendChild(option);}
search.addEventListener('input',redraw);category.addEventListener('change',redraw);document.getElementById('clear').addEventListener('click',()=>{search.value='';category.value='';redraw();search.focus();});
document.getElementById('close-dialog').addEventListener('click',()=>dialog.close());
document.getElementById('save-svg').addEventListener('click',()=>{if(selected)download(selected.id+'.svg',selected.svg,'image/svg+xml');});
document.getElementById('save-record').addEventListener('click',()=>{if(selected)download(selected.id+'.asset.json',JSON.stringify(selected,null,2)+'\n','application/json');});
redraw();
'''

def b64svg(text):return 'data:image/svg+xml;base64,'+base64.b64encode(text.encode()).decode()

def main():
    library=list(assets().values());sources={s['id']:s for s in resource('sources.json')['sources']}
    md=MarkdownIt('commonmark',{'html':True}).enable('table')
    def citations(text):
        def repl(m):
            keys=[x.strip() for x in m[1].split(';')]
            if not keys or any(x not in sources for x in keys):return m[0]
            return '['+'; '.join(f'<a class="cite" href="#source-{k}" title="{html.escape(sources[k]["title"],quote=True)}">{k}</a>' for k in keys)+']'
        return re.sub(r'\[([a-z][a-z0-9;-]*(?:\s+[a-z0-9;-]+)*)\]',repl,text)
    nav='<a href="#overview">Overview</a><a href="#library">Original assets</a><a href="#specimens">Eight specimens</a>'+''.join(f'<a href="#{id}">{label}</a>' for id,label,_ in DOCS)
    content=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Medical Illustration Studio | Atlas and toolkit</title><style>{CSS}</style></head><body><div class="shell"><aside><div class="brand">Medical Illustration<br>Studio</div><p class="edition">Illustrated field guide · 1.0.0</p><nav aria-label="Contents">{nav}</nav><p class="aside-note">Offline handbook and original asset library.<br><br>Scientific schematics are not patient observations or independently reviewed anatomical plates.</p></aside><main><header id="overview"><p class="eyebrow">Medical and scientific illustration</p><h1>From scientific meaning<br>to an editable figure</h1><p class="lede">A scene language, original vector library and practical field guide for agents producing medical illustrations.</p><p class="meta">77 original vector records · 28 layout recipes · 8 complete schematic examples · reference directory and executable Python tools</p><p>Choose the representation that answers the reader's question. Preserve anatomy, evidence and visual clarity as separate requirements. Reference-based anatomical work needs appropriate geometry and qualified review; this collection does not replace a complete anatomical atlas.</p></header>'''
    hero=(ROOT/'examples/epithelial-barrier.svg').read_text()
    content+=f'<figure class="figure hero-example"><img src="{b64svg(hero)}" alt="A labelled schematic of an epithelial barrier with microvilli, cell junctions, a goblet cell and a basement membrane."><figcaption>Original tissue assembly composed with the included scene language. All labels and vector structures remain editable.</figcaption></figure>'
    content+='''<section class="section" id="library"><h2>The original asset library</h2><p>Select an asset to inspect its scope, landmarks and rights, or export an editable SVG. The collection is schematic and has not received independent asset-level medical review. External provider artwork is not bundled.</p><div class="toolbar"><div class="field"><label for="search">Search the collection</label><input id="search" type="search" placeholder="Try epithelium, membrane, kidney…" autocomplete="off"></div><div class="field"><label for="category">Category</label><select id="category"><option value="">All categories</option></select></div><button id="clear" type="button">Clear filters</button></div><p id="asset-count" aria-live="polite"></p><div class="asset-grid" id="asset-grid"></div><noscript><p>Enable local JavaScript for the interactive asset browser. The handbook and specimen illustrations remain readable without it.</p></noscript></section>'''
    content+='<section class="section" id="specimens"><h2>Eight complete schematic specimens</h2><p>These examples are rendered from the supplied scene files. They demonstrate composition and notation, not clinical observations, diagnostic evidence or independently approved anatomical reconstructions.</p>'
    order=['epithelial-barrier','renal-nephron','vascular-wall','cell-signalling','cell-interior','paired-epithelium','study-workflow','multi-scale-tissue']
    for name in order:
        scene=json.loads((ROOT/'examples'/f'{name}.scene.json').read_text());svg=(ROOT/'examples'/f'{name}.svg').read_text()
        content+=f'<figure class="figure"><img src="{b64svg(svg)}" alt="{html.escape(scene["description"],quote=True)}" loading="lazy"><figcaption><strong>{html.escape(scene["title"])}</strong> · Scene: <code>{name}.scene.json</code></figcaption></figure>'
    content+='</section>'
    for id,label,path in DOCS:
        text=(ROOT/path).read_text().replace('anchored definitions','explicit definitions')
        rendered=md.render(citations(text))
        content+=f'<section class="section prose" id="{id}"><a class="jump" href="#overview">Return to contents</a>{rendered}</section>'
    content+='''<footer class="footer">Original software and documentation: MIT. Original schematic art: CC0 1.0 to the extent rights exist and are held by contributors. Source artwork retains its own rights. No medical certification, professional affiliation or market-superiority claim is made.</footer></main></div><dialog id="asset-dialog" aria-labelledby="asset-title"><div class="dialog-head"><h2 id="asset-title"></h2><button id="close-dialog" type="button" aria-label="Close asset details">Close</button></div><div class="dialog-body"><img id="asset-image" alt=""><div><dl><dt>Asset identifier</dt><dd id="asset-identity"></dd><dt>Category and scale class</dt><dd id="asset-category"></dd><dt>Rights and origin</dt><dd id="asset-rights"></dd></dl><p id="asset-status"></p><p id="asset-limits"></p></div></div><div class="buttons"><button id="save-svg" type="button">Export SVG</button><button id="save-record" type="button">Export asset record</button></div><details><summary>Landmarks and complete metadata</summary><pre id="asset-json"></pre></details></dialog>'''
    data=json.dumps(library,ensure_ascii=False).replace('</','<\\/')
    content+=f'<script id="library-data" type="application/json">{data}</script><script>{JS}</script></body></html>'
    (ROOT/'atlas.html').write_text(content,encoding='utf-8')
    print(f'Built offline atlas with {len(library)} assets, {len(order)} examples and {len(DOCS)} reference chapters')

if __name__=='__main__':main()
