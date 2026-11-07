# Medical Illustration Studio · 2.1

An editable local workspace for anatomical plates and scientific diagrams, with a visual grammar, original vector library, source-linked anatomy constraints, versioned projects and optional agent/provider connections.

**Start with `studio-preview.html`** for the standalone atlas editor, or run the complete local workspace:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[studio]'
python -m medillustrate studio
```

Open `http://127.0.0.1:8765`. A model key is not required for local rendering, editing, project history or export. `studio.command` and `studio.bat` are launch helpers. See [the working guide](docs/agentic-studio.md) for installation, environment variables, source uploads, model consent, exports and backup.

## What the workspace does

Use Artboards for the illustration sequence, Library for 81 original vector records, and Sources for reference material. The canvas has drawing stages, editable labels, zoom and a region selector. The Inspector controls lettering and protected texture layers. The Assistant prepares bounded changes for comparison and acceptance. Revisions are stored in a local SQLite database; stale proposals cannot overwrite later manual edits.

The four anatomical studies cover the renal section, kidney surface, arterial wall and peripheral nerve. They use more detailed original geometry, directional texture and material-specific tonal treatment than the original schematic collection. They remain idealised anatomical vector studies, not a clinically certified atlas or a demonstrated equivalent of Netter's paintings. The eight previous schematic examples, broader handbook and deterministic renderer remain included.

## Agents and painting are separate

- **Local commands** are explicitly a command interpreter, not a language model.
- **Ollama** can interpret free-form requests into allowed edit operations when a local model is configured. Its results remain proposals.
- **MCP** exposes six local tools to an external agent. The agent can propose but cannot accept its own changes.
- **FigureLabs** is an optional reference-guided painting provider, enabled only by a server-side API key and per-task consent. It returns an unadopted candidate, not an automatically approved medical figure.

The protocol adapters were exercised with controlled responses; no paid FigureLabs image generation or live Ollama model inference was performed for this distribution. External credentials, provider subscriptions, installed models and host-specific MCP configuration are not bundled.

## Editing and file formats

Original anatomy, schematic assets, titles, captions and leaders are editable SVG. Painted replacements remain raster images. PDF preserves the composed print-size figure. Atlas PPTX exports use native lettering and leader segments with separate artwork images; schematic PPTX slides embed their figures. Portable ZIP projects contain their required media and self-contained SVGs. Production records are exported separately.

The standalone HTML supports atlas editing, local commands, comparisons, the asset browser and SVG/PNG/JSON export. Its schematic examples are read-only previews. The local server adds connected schematic editing, PDF text extraction, SQLite persistence, media-bundle import/export, PDF/PPTX export and optional provider calls.

## Read the illustration methods

[Painting grammar](docs/painting-grammar.md) explains form, edge hierarchy, tissue treatment, section surfaces and native lettering. [Atlas refinement](docs/atlas-refinement.md) describes the agent's production workflow. [FigureLabs study](docs/figurelabs-study.md) records what was adapted from public documentation. [Anatomical sources](docs/anatomy-reference-register.md) distinguish source support from illustrative choices.

`SKILL.md` is the agent entry point. `atlas.html` retains the original broad handbook. `atlas-refined.html` provides a separate four-plate workbench. The core schematic scene schema remains version 1.0.0 for compatibility; the project format is 2.1.0 and the plate format 2.0.0.

## Rebuild and test

```sh
python -m pip install -e '.[studio,test,docs]'
python tools/build_anatomical_library.py
python tools/build_atlas_plates.py
python tools/build_studio.py
python -m pytest -q
```

Browser tests need a Chromium installation usable by Playwright. They exercise the UI with an in-process API bridge and isolated test storage. Provider tests use controlled HTTP/task responses; they do not establish third-party model quality or medical accuracy.

## Licence and limitations

Software is MIT-licensed. Original bundled artwork is offered under CC0-1.0. Imported source material and provider-generated media retain their own terms and are not relicensed as CC0. The original illustration library includes no Netter plates, BioRender icons, FigureLabs proprietary assets or patient records. The integrated ArtCraft distributions include separately licensed fonts and assets; their original notices and licence texts are retained under vendor/artcraft.

This is a single-user local application. It is not deployed hosting, shared multi-user collaboration, a hospital information system, an automatic anatomical validator or a promise that all journal policies permit generated figures. Public deployment would require a separate identity, authorisation, security, storage and operational design.


## Subscription-backed illustration composer

Run `python3 -m medillustrate.server --port 8876`, then open `http://127.0.0.1:8876/`. The Assistant contains a conversation composer with artboard context, selected source text, engine selection, Send and Stop. Enter submits; Shift+Enter adds a line. The plus control adds a reference; select its text under Sources before including it.

Codex uses the same Python subscription harness as Science Studio at `../science-studio/src/raso/rstudioHarness.py` and the installed Codex CLI login. No API key is copied or exposed to the browser. An unavailable engine fails explicitly; local commands remain a separately named option. The standalone HTML does not run subscription inference: use the local server.

The agent can inspect the artboard and propose validated operations. Validation errors are returned to the model for correction, up to four calls per turn. It cannot run host tools, unlock anatomy or guess landmark targets. Changes remain a preview until Accept is clicked. Stop cancels the installed CLI process; no proposal is applied automatically. Conversations persist in the project’s local production record. Source excerpts are sent only when selected and the request is authorised.

### Pixel and vector editing

The server integrates the unmodified ArtCraft **PhotoCraft 0.19.0** and **VectorCraft 0.20.0** engines under `vendor/artcraft`, with their original licence and asset notices. The engines are MIT/Apache-2.0; the host does not adopt upstream trademarks as its identity. Their alpha releases do not establish complete Adobe format or feature compatibility.

Use **Import artwork** for PNG/JPEG, SVG, PDF, PSD or either native format. Ask the composer to edit layers, paths, shapes, type, colours, masks or image adjustments; it discovers the engines’ actual command descriptions and prepares a rendered copy. Accept to save it, or Discard to retain the original. A general graphics edit of a medical template creates a separate artboard. Native `.pcraft`/`.vectorcraft` files, preview and SVG are versioned in the existing project database and included in portable bundles. **Anatomy**, **Draw** and **Adjust** select tool groups above one shared canvas. Drawing controls create native vector shapes; adjustment controls invoke the pixel engine directly. **Editing tools** searches the upstream command registries and displays parameter controls in the studio sidebar, with an assistant option for commands needing additional choices. There are no embedded editor applications or separate editor save/download steps. Every edit renders a preview and uses the same Accept/Discard and project history. The upstream command engines are reused; the full upstream desktop interfaces are not included in this merged interface.

Model editing commands cannot choose executable paths, filesystem roots, plugins, scripts or save locations. The host confines each engine to a temporary copy. Native documents retain their upstream capabilities; flattening to PNG does not create editable image structures.
