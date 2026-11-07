# Agent workflows and handoffs

## A small number of explicit responsibilities

The commissioning role defines the reader, question, scientific scope and deliverable. The research role verifies the relevant sources and rights. The scientific modeller expresses entities, compartments, structural relations and claim status. The illustrator or renderer creates the geometry and composition. The scientific reviewer assesses medical truth; the visual reviewer assesses communication and appearance.

These responsibilities need not correspond to six separate agents. Creating more agents does not create independent medical expertise. A single agent can coordinate the mechanical work, but it cannot manufacture a qualified human approval by assigning a second AI the role name “anatomist.” Keep that distinction explicit.

A handoff should carry the actual scene, assets, supporting sources, outstanding material uncertainties and the requested next transformation. Do not hand off only a prose promise of what was supposedly completed. Downstream work must be based on the current artifact rather than a stale summary of it.

## Workflow A: a scientific schematic

Translate the commission into a statement such as “Explain a membrane interaction while distinguishing physical association from intracellular regulation.” Select a compartment-oriented layout. Identify entities and their required side of the membrane. Write claims for each biological relation and mark the status of each.

Search the existing library for suitable symbolic objects. Inspect their limitations and landmarks. If an asset is sufficient, reuse it. If its identity is wrong or its geometry cannot express the required feature, acquire or create an appropriate asset rather than relabelling it. Do not call a generic single-pass receptor a known multi-pass protein.

Write the scene JSON. Use `validate`, address actual errors, then render an SVG and separate record. Inspect the result at the intended width. Confirm that labels touch the intended features and that compartment assignments agree with the visible geometry. Add the meaningful caption and required source attribution. Qualified review precedes authoritative scientific or medical use.

The completed signalling example is a syntax and composition model, not evidence for a specific pathway. Its hypothetical status is intentional. Agents must not replace hypothetical names with real proteins while retaining the same unsourced arrows.

## Workflow B: a reference-based anatomical plate

Specify the region, exact view, laterality, life stage and required structures. Select a lawful reference set and an appropriate geometry route. The source may be an approved vector illustration, a reviewed model or an illustrator's reconstruction. Reference images are not automatically a redistributable asset library.

Resolve anatomical relationships before stylistic refinement. Use the structural relation contract to express the important adjacency, continuity, hierarchy and orientation assertions. Verify any ontology bindings separately. Import the geometry only when it is in the supported passive SVG subset or compose the final vector exported from the external anatomical workflow.

The imported asset initially remains unreviewed. Define named landmarks using actual structures, not only the asset rectangle. Preserve the original aspect ratio. Do not reflect an organ to fill a page. Use anatomical mode for primary anatomical geometry, and treat supporting schematic glyphs explicitly as support material.

The human scientific reviewer should see the source references, the exact final view and the named required structures. The visual reviewer should inspect the image at the intended print or screen dimensions. Source or geometry changes after approval require review of the affected content and renewed artifact binding.

## Workflow C: evidence synthesis or a manuscript mechanism

Start from the manuscript's supported claims and uncertainty, not the visual logic of a familiar pathway. Distinguish established relations, proposed mechanisms, associations and study activities. Source every biological edge at the claim level. Where the evidence is indirect, say so in the claim and use the appropriate visual distinction.

Avoid including every plausible biological intermediate. An intermediate that has not been justified can make the figure appear mechanistically complete while weakening its truth. Use a bounded unknown region, a proposed relation or a separate explanation when the evidence cannot establish the missing connection.

Treat causal interpretation as a scientific assertion requiring its own support. The compositor does not turn association into causation. It enforces the declared notation and traceability, while the researcher and reviewer determine whether the interpretation is warranted.

## Workflow D: multi-scale explanation

Identify the parent region before drawing an inset. State which feature is magnified and what information the magnification adds. Use a zoom relation without an arrowhead. Keep orientation correspondence where it matters; explain an intentional reorientation.

Do not use one scale bar across views with unequal magnification. If scales are not calibrated, make that explicit. Keep proportional anatomy and symbolic molecular detail conceptually separate. The multi-scale tissue example uses three uncalibrated explanatory scales rather than fabricated magnification values.

## Workflow E: publication-specific delivery

Classify the figure before choosing a generative route. An illustrative schematic, graphical abstract, primary image and data visualisation can face different restrictions. Check the current target journal's official rules, then choose a compatible process and required disclosure. Do not claim acceptance because a generic exporter can produce a PDF.

Use the source SVG and scene as the editable master. Export the actual requested size and format. Inspect the final output for typography, clipping, colour and changed line appearance. Publication mode requires review records bound to the current artifact, but cannot verify the reviewers' identities or the publisher's decision.

When the journal requests AI disclosure, a methodological explanation or an attribution, include it in the appropriate substantive location. Keep production activity and quality-check narration separate. These are different kinds of information.

## Producing an external image-generation brief

`python -m medillustrate brief figure.scene.json -o figure.production.md` compiles the scientific contract, composition constraints, assets, structural relations and claim ledger. This is an external production brief, not a call to an image model.

A useful anatomical brief names the approved geometry, required structures, view, cut surfaces, lighting, material cues, omissions and invariants. It explicitly forbids adding structures to improve realism. A useful schematic brief identifies compartments, abstraction level, line semantics, evidence status, relative scale and text that must remain editable.

A generative model output is a candidate rendering. It is not a reviewer, a source, a clinical observation or evidence that an anatomical statement is true. Do not allow attractive output to overwrite approved topology. Keep deterministic labels and arrows separate until the image itself has been reviewed.

## Prompt patterns

### Anatomy commission pattern

> Create a regional anatomical explanation of [region] for [reader]. Use [approved reference/geometry], in [documented view and laterality]. The required structures are [list]; the required relationships are [specific relations]. Preserve [named landmarks, continuity and cut plane]. Omit [declared exclusions]. Use selective volumetric rendering with coherent lighting; do not add unsupported texture or structures. Reserve [label areas] and keep labels editable. Deliver the reference-supported geometry, composed SVG and a separate source and review record. Do not treat an AI's visual plausibility judgment as medical approval.

### Mechanism commission pattern

> Explain [process] within [compartments]. The established claims are [claim IDs and sources]. The proposed claims are [IDs and limitations]. Distinguish association, material movement, activation and inhibition. Use [specified abstraction level] and disclose unequal scales. Select or create assets that actually represent the required classes. Do not invent intermediate steps, counts or measured results. Keep the composition focused on [single explanatory sentence].

### Correction pattern

> Preserve the approved figure except for [named defect]. Change [specific node, relation, landmark or label]. Retain [explicit invariants]. Re-render and recheck [affected dependencies]. Do not restyle unrelated content, change the evidence status or regenerate the entire figure without a material reason.

These patterns are deliberately affirmative about the requested work. Prohibitions specify scientific failure boundaries; they should not become the entire creative brief.

## Control records without clutter

The control record may contain sources consulted, source checks, alternative assets, decisions, issues, reviewer statements and artifact hashes. It is established alongside the work and maintained separately. The complete figure should contain only the scientific explanation, necessary attribution or disclosure, and meaningful limitations.

Do not insert approval statements, tool logs, internal file paths or check counts into the SVG description or figure caption. The SVG description is an accessibility explanation of the figure. Its purpose is not to document how the agent worked.

An organisation can store approved records in a controlled system and validate reviewer identity externally. The present record is plain JSON. Its hashes detect a mismatch with the current figure; they are not a digital signature, credential service or tamper-proof audit system.

## Completion and revision

Completion means that the requested figure and its editable source exist, answer the scientific question and have the required review or a clearly stated missing-review limitation. Do not call a layout scaffold a completed plate. Do not call a provider directory an installed asset library. Do not call an executable benchmark protocol a result.

For a new defect, state the requirement it violates and make the corresponding change. Reuse valid prior checks for unchanged content. Work should converge on the requested artifact, not on an expanding collection of checklists and reports.
