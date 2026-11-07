"""Build the self-contained offline atlas editor from the same assets and UI source."""
from pathlib import Path
from copy import deepcopy
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from medillustrate import core
from medillustrate.workspace import library,seed_data


def main():
    templates=deepcopy(seed_data()['templates'])
    for t in templates:
        if t['kind']=='scene':t['svg']=core.render(t['document'],library())
    data={'assets':list(library().values()),'templates':templates,'contracts':core.resource('anatomy-contracts.json')['contracts'],'materials':core.resource('tissue-materials.json')['materials'],'sources':core.resource('refinement-sources.json')['sources']}
    static=ROOT/'medillustrate'/'static'
    html=(static/'studio.html').read_text()
    html=html.replace('<link rel="stylesheet" href="/static/studio.css">','<style>'+(static/'studio.css').read_text()+'</style>')
    embedded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    html=html.replace('<script src="/static/studio.js"></script>','<script id="studio-data" type="application/json">'+embedded+'</script><script>'+(static/'studio.js').read_text().replace('</script','<\\/script')+'</script>')
    (ROOT/'studio-preview.html').write_text(html,encoding='utf-8')
    print('Built standalone atlas editor:',len(data['assets']),'assets;',len(templates),'artboards')
if __name__=='__main__':main()
