# FigureLabs: useful ideas for this studio

Research date: 5 October 2026. This is a study of the provider's public product and API documentation, not an independent evaluation of its medical accuracy, private implementation, reliability, or image quality.

## What to borrow

FigureLabs presents illustration as an iterative workspace: a scientific request, reference material, generated figure, canvas edits, and subsequent revisions belong to the same project. Its product documentation describes local redraw, text edits, background changes and style controls. The useful principle is continuity of work, rather than a succession of disconnected image prompts. [1,2]

Its MCP documentation describes connecting an external agent to the figure workflow, with project context and persistent results. Its API instead exposes explicit image tasks. These are distinct integration surfaces: an agent can operate a workspace, while a rendering provider can produce an image candidate for that workspace. [3,4]

The public image API uses asynchronous generation and task-status requests. It accepts reference imagery, supports a region-redraw mode with a mask, and returns downloadable results. The studio adapter uses that documented task model and stores downloaded candidate media locally rather than depending on a provider result URL remaining available. [4]

## Decisions implemented here

| Product idea | Local implementation | Medical-illustration distinction |
|---|---|---|
| Conversation beside canvas | Assistant, Inspector and Paint beside a shared artboard | A text edit, a structural drawing and a painted surface are different operations. |
| Iterative scientific figure creation | Project brief, references, artboards and revision history | References retain their declared source and licence; they do not automatically become validated anatomical evidence. |
| Local edits | Rectangular artwork mask and separate label editing | Pixels outside the region are restored from the source locally. This does not guarantee correctness within the region. |
| Consistent appearance | Shared material vocabulary, drawing stages and protected geometry | A style instruction never authorises changing anatomy. |
| Agent connection | Six bounded MCP tools and an optional Ollama planner | The external agent can propose changes, but the MCP interface cannot accept its own proposal. |
| Revisions | SQLite snapshots and optimistic concurrency | A stale proposal cannot overwrite later manual edits. |
| Export | SVG, PNG, PDF, PPTX and portable project bundle | Native labels and raster anatomy retain different editing capabilities. |

The UI, code, vector assets and data model are original work. No FigureLabs front-end code, private prompts, private models, proprietary icons or account content was copied. The public API adapter is optional; FigureLabs is not required for local editing or deterministic rendering.

## What not to infer

An image that looks plausible is not thereby anatomically accurate. A vendor's publication-oriented export options do not establish compliance with every journal's AI-image policy. Vectorising an image also does not recover a semantically labelled dissection: editable curves are not the same as editable anatomical structures.

The implementation deliberately does not market an automatic clinical sign-off, autonomous anatomical correction, universal journal acceptance, or demonstrated superiority over all open-source products. The comparative task set from the earlier package remains available for actual expert evaluation.

## Sources

1. FigureLabs, product overview: https://www.figurelabs.ai/
2. FigureLabs, product documentation: https://www.figurelabs.ai/docs
3. FigureLabs, MCP integration: https://www.figurelabs.ai/mcp
4. FigureLabs, API reference: https://www.figurelabs.ai/api/docs

The source register stores these separately from the anatomical references. Product documentation is evidence of documented product behaviour, not an anatomical source.
