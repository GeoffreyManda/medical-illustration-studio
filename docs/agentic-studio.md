# Working in Medical Illustration Studio

## Start the complete local workspace

Use Python 3.10 or later. From the extracted package directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[studio]'
python -m medillustrate studio
```

Open `http://127.0.0.1:8765`. The application binds to loopback, not the public network. Stop it with Ctrl+C. Use `--port 8870` for another port or `--db /your/path/workspace.sqlite3` for a different database. The default database is `~/.medillustrate/studio.sqlite3`. No account is created and no model key is needed for ordinary editing.

`studio.command` and `studio.bat` provide equivalent launch paths for macOS/Linux and Windows. Their first installation needs package downloads. Rendering uses CairoSVG; its native Cairo dependencies must be available in the chosen environment. A package-installation or native-library error is not silently replaced with a lower-fidelity renderer.

The separate `studio-preview.html` runs without Python. It provides local atlas editing, the asset library, local commands, comparisons, browser storage and SVG/PNG/JSON export. Schematic artboards in this standalone version are read-only previews; the server is required to update connected schematic geometry, extract PDF reference text, use models or produce PDF/PPTX/bundle exports. The standalone editor is not a hosted service.

## A project rather than an isolated image

A project contains artboards, a brief, source declarations and optional media. An artboard is either an anatomical plate or a scientific schematic. Plate labels target named locations in a known view. Schematic nodes and connectors retain their original scene grammar.

Add artboards from the left column. The four anatomical templates cover a kidney section, kidney surface, arterial wall and peripheral nerve. Eight schematic templates remain available from the original toolkit. Search the 81-record library to inspect and export individual assets; insert symbols into a schematic rather than into the middle of a dissection.

Use Sources to attach a reference, declare its licence, and retain relevant notes. The local server accepts bounded PNG/JPEG/WebP images, passive SVG, PDF and plain text formats. It extracts PDF text with page markers but performs no OCR. A scanned PDF may therefore contain no extracted text. An uploaded document is reference material, not permission to reproduce its illustrations.

Source checkboxes control which reference text is sent to the optional language model. The current artboard and project brief accompany the request. The Ollama adapter sends text, not source images. The FigureLabs painting adapter sends the current unlabelled artwork and painting instruction, not all attached references. No remote link is fetched just because it appears in a note.

## Edit and compare

The Inspector edits the title, subtitle, caption, label size, label text, label bank and vertical position. Drag a label to reposition its text without moving its anatomical target. A separate target-correction control accepts normalized coordinates only with an explicit anatomical reason. Those edits record a user decision; they are not independent medical review.

Colour, Values and Contours expose different renderings of the original vectors. Texture intensity changes only declared texture groups. Geometry protection prevents those controls from quietly hiding structural groups. These controls cannot derive reliable contours or tissue layers from an adopted raster painting; restore a vector revision when those forms of editing are needed.

The assistant produces a proposal, not a direct overwrite. Preview it on the artboard, compare it with the current revision, then accept or discard it. Every accepted edit creates a new revision. Restoring an earlier revision creates another revision rather than deleting intervening work.

A proposal records its base revision and candidate hash. Acceptance fails when another edit has changed the project. New artboard and symbol identifiers are fixed when the proposal is created, so the accepted document is the one that was previewed.

## Three kinds of automation

**Local commands** are deterministic editing commands, not an AI model. Examples:

```text
labels 19; less texture
rename cortex: Renal cortex
move cortex left 330
show contours
add atlas-kidney-surface
```

**Ollama** provides optional free-form interpretation. Start an Ollama installation with a model you have selected, then configure the studio process:

```sh
export MEDILLUSTRATE_OLLAMA_MODEL='your-installed-model-name'
python -m medillustrate studio
```

The optional `MEDILLUSTRATE_OLLAMA_URL` accepts a loopback HTTP/HTTPS address only. The adapter uses the documented chat API and a JSON output schema. Each request makes one planning call; it does not retry indefinitely or silently fall back to a command parser. Invalid plans are rejected. The model cannot execute Python, unlock anatomical geometry, or supply guessed target coordinates. [1]

**External agents** can use the bundled MCP stdio server. Add this configuration to the MCP host's own configuration, using absolute paths appropriate to your installation:

```json
{
  "mcpServers": {
    "medical-illustration": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "medillustrate.mcp_server", "--db", "/absolute/path/to/studio.sqlite3"]
    }
  }
}
```

The tools list/read projects, search assets, read anatomical constraints, propose edits and read proposal state. There is deliberately no acceptance tool. The user accepts proposals in the studio. The implementation supports a bounded JSON-RPC tools subset over stdio, not every optional MCP capability. Configure and verify it with the particular host being used. [2]

## Reference-guided painting

Set `FIGURELABS_API_KEY` in the server environment to enable Paint. A key is never saved in a project, returned to the browser or included in a figure export. No cloud request occurs without per-task authorisation.

Choose a whole-artwork refinement or drag a rectangular Region on the canvas. Submit a specific instruction about material or tonal treatment. The adapter sends an unlabelled reference image, anatomical-preservation instructions and, for a regional edit, a mask. It uses the provider's documented asynchronous task endpoints. Refresh a submitted task's status to retrieve its candidate. [3]

A billable generation POST is never automatically retried. A timeout may leave an uncertain submission state; check the provider account before submitting again. Regional candidates are composited with the original source so that outside-mask pixels remain unchanged. This is a pixel-preservation guarantee, not an anatomical guarantee.

Review the candidate before adoption. Check structure boundaries, continuity, counts, cut surfaces and every leader target. A changed image framing cannot safely inherit old coordinates. The adopter rejects an incompatible aspect ratio or a candidate associated with a different artboard. Full-colour raster art remains a raster layer inside exported SVG/PDF/PPTX.

## Export and preserve the work

SVG retains original vector artwork and editable lettering; a painted replacement is embedded as PNG, not misrepresented as vector anatomy. PNG exports are 2400 pixels wide from the UI. PDF uses the figure's physical dimensions. Atlas PowerPoint exports use native titles, captions, labels and leaders with a separate artwork image; a schematic is embedded as a complete image.

The portable ZIP contains the project document, required media and self-contained SVG figures. Importing it creates a new project identity and retains declared source licences. JSON alone does not contain uploaded images. Separate production records are available from the export dialog but are not inserted into the illustrated figure or portable figure bundle.

For database-level backup, stop both the studio and any connected MCP processes before copying the workspace database and its associated SQLite files. Keep sensitive source material out of provider submissions. This is a single-user local application, not a multi-user hospital record system or an internet-exposed collaboration service.

### Technical sources

1. Ollama chat API: https://docs.ollama.com/api/chat
2. MCP server documentation: https://modelcontextprotocol.io/docs/develop/build-server
3. FigureLabs API: https://www.figurelabs.ai/api/docs
