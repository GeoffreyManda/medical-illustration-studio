"""Command-line interface; all output paths are explicit and no network is used."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from . import core


def dump(value): return json.dumps(value,indent=2,ensure_ascii=False)+'\n'

def main(argv=None) -> int:
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {'studio','mcp'}:
        if argv[0]=='studio':from .server import main as run
        else:from .mcp_server import main as run
        run(argv[1:]);return 0
    p=argparse.ArgumentParser(prog='medillustrate',description='Editable, evidence-aware medical illustration scenes. Offline; no proprietary assets.')
    p.add_argument('--version',action='version',version='2.1.0')
    sub=p.add_subparsers(dest='command',required=True)
    cat=sub.add_parser('catalogue',help='Search bundled assets, optionally with a local imported asset catalogue')
    cat.add_argument('--query',default=''); cat.add_argument('--category'); cat.add_argument('--library'); cat.add_argument('--json',action='store_true')
    for name in ['layouts','rules','sources','providers']:
        q=sub.add_parser(name);q.add_argument('--id')
    a=sub.add_parser('asset',help='Export one editable standalone SVG');a.add_argument('id');a.add_argument('-o','--output',required=True);a.add_argument('--library');a.add_argument('--force',action='store_true')
    v=sub.add_parser('validate');v.add_argument('scene');v.add_argument('--library');v.add_argument('--publication',action='store_true');v.add_argument('--review');v.add_argument('--json',action='store_true')
    r=sub.add_parser('render');r.add_argument('scene');r.add_argument('-o','--output',required=True);r.add_argument('--library');r.add_argument('--record');r.add_argument('--publication',action='store_true');r.add_argument('--review');r.add_argument('--force',action='store_true')
    e=sub.add_parser('export');e.add_argument('svg');e.add_argument('-o','--output',required=True);e.add_argument('--width-px',type=int);e.add_argument('--dpi',type=float,default=300);e.add_argument('--force',action='store_true')
    i=sub.add_parser('init');i.add_argument('--layout',default='anatomical-plate');i.add_argument('--id',default='new-figure');i.add_argument('-o','--output',required=True);i.add_argument('--force',action='store_true')
    b=sub.add_parser('brief');b.add_argument('scene');b.add_argument('--library');b.add_argument('-o','--output');b.add_argument('--force',action='store_true')
    im=sub.add_parser('import-svg');im.add_argument('svg');im.add_argument('--id',required=True);im.add_argument('--label',required=True);im.add_argument('--creator',required=True);im.add_argument('--license',required=True);im.add_argument('--source-url',required=True);im.add_argument('--representation',choices=['schematic','anatomical'],default='schematic');im.add_argument('--scale-class',choices=['molecular','organelle','cell','tissue','organ','body','equipment'],default='cell');im.add_argument('-o','--output',required=True);im.add_argument('--force',action='store_true')
    bench=sub.add_parser('benchmark');bench.add_argument('--ratings')
    check=sub.add_parser('check-library');check.add_argument('--library')
    sub.add_parser('doctor')
    plate=sub.add_parser('plate',help='Render an atlas plate specification')
    plate.add_argument('specification');plate.add_argument('-o','--output',required=True);plate.add_argument('--stage',choices=['colour','values','contours'],default='colour');plate.add_argument('--force',action='store_true')
    args=p.parse_args(argv)
    try:
        cmd=args.command
        if cmd=='plate':
            from .atelier import render_plate
            core.write_file(args.output,render_plate(core.load_json(args.specification),stage=args.stage),force=args.force);print(args.output)
        elif cmd in ['layouts','rules','sources','providers']:
            rows=core.resource(cmd+'.json')[cmd]
            if args.id:
                rows=[x for x in rows if x['id']==args.id]
                if not rows: raise core.IllustrationError('Unknown record ID')
            print(dump(rows),end='')
        elif cmd=='catalogue':
            rows=list(core.assets(args.library).values())
            rows=[a for a in rows if (not args.category or a['category']==args.category) and args.query.casefold() in (a['label']+' '+a['id']+' '+' '.join(a['aliases'])).casefold()]
            if args.json: print(dump([{k:v for k,v in a.items() if k!='svg'} for a in rows]),end='')
            else:
                for a in rows: print(f"{a['id']:26} {a['label']} [{a['category']}]")
                print(f'{len(rows)} matching assets')
        elif cmd=='asset':
            lib=core.assets(args.library)
            if args.id not in lib: raise core.IllustrationError('Unknown asset')
            core.write_file(args.output,lib[args.id]['svg'],force=args.force);print(args.output)
        elif cmd in ['validate','render','brief']:
            scene=core.load_json(args.scene);lib=core.assets(args.library)
            review=core.load_json(args.review) if getattr(args,'review',None) else None
            if cmd=='validate':
                issues=core.validate(scene,lib,publication=args.publication,review=review)
                if args.json: print(dump([x.to_dict() for x in issues]),end='')
                else:
                    for issue in issues: print(f'{issue.severity.upper()} {issue.code} {issue.path}: {issue.message}')
                    print(f"{sum(i.severity=='error' for i in issues)} errors; {sum(i.severity=='warning' for i in issues)} warnings")
                return 2 if any(i.severity=='error' for i in issues) else 0
            elif cmd=='render':
                if Path(args.output).suffix.lower()!='.svg': raise core.IllustrationError('Render output must be .svg; use export for PDF or PNG')
                if args.record and Path(args.output).resolve()==Path(args.record).resolve(): raise core.IllustrationError('Figure and control record require separate paths')
                for out in [args.output,args.record]:
                    if out and Path(out).exists() and not args.force: raise core.IllustrationError(f'Refusing to overwrite {out}')
                svg=core.render(scene,lib,publication=args.publication,review=review)
                core.write_file(args.output,svg,force=args.force)
                if args.record: core.write_file(args.record,dump(core.control_record(scene,lib)),force=args.force)
                print(args.output)
            else:
                text=core.production_brief(scene,lib)
                if args.output: core.write_file(args.output,text,force=args.force);print(args.output)
                else: print(text,end='')
        elif cmd=='export':
            path=Path(args.svg)
            if path.stat().st_size>core.MAX_FILE: raise core.IllustrationError('SVG exceeds export input size limit')
            data=core.export_svg(path.read_text(encoding='utf-8'),Path(args.output).suffix.lower().lstrip('.'),width_px=args.width_px,dpi=args.dpi)
            core.write_file(args.output,data,force=args.force);print(args.output)
        elif cmd=='init':
            scene=core.make_scene(args.id,args.layout)
            errors=[x for x in core.validate(scene) if x.severity=='error']
            if errors: raise core.IllustrationError(errors[0].message)
            core.write_file(args.output,dump(scene),force=args.force);print(args.output)
        elif cmd=='import-svg':
            a=core.import_svg(args.svg,id=args.id,label=args.label,creator=args.creator,license=args.license,source_url=args.source_url,representation=args.representation,scale_class=args.scale_class)
            core.write_file(args.output,dump(a),force=args.force);print(args.output)
        elif cmd=='benchmark': print(dump(core.score_benchmark(core.load_json(args.ratings)) if args.ratings else core.resource('benchmark-tasks.json')),end='')
        elif cmd=='check-library':
            lib=core.assets(args.library);print(f'{len(lib)} asset records satisfy the schema and passive SVG checks. Medical review is a separate requirement.')
        elif cmd=='doctor':
            import importlib.util, platform
            print(dump({'version':core.VERSION,'python':platform.python_version(),'core':'available','jsonschema':bool(importlib.util.find_spec('jsonschema')),'defusedxml':bool(importlib.util.find_spec('defusedxml')),'cairosvg':bool(importlib.util.find_spec('cairosvg')),'pillow':bool(importlib.util.find_spec('PIL')),'font_metrics':'DejaVu Sans' if core._font(18) is not None else 'conservative fallback','network':'not used','medical_certification':False}),end='')
        return 0
    except (core.IllustrationError,OSError,ValueError,KeyError,TypeError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__': raise SystemExit(main())
