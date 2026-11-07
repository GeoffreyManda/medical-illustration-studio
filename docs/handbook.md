# The medical illustration handbook

## 1. Begin with the question, not the style

An illustration succeeds when a reader can make the intended anatomical or scientific distinction without acquiring a false one. A visually pleasing heart with the wrong connections is not a lower-quality version of a correct figure; it is a different and potentially misleading explanation. AMI describes the profession as a combination of scientific understanding, visual communication and collaboration with subject experts. This toolkit therefore separates scientific specification, geometry, communication and final review. [ami-profession]

Write the figure's central statement as a sentence. “Show the epithelium” is an object request. “Explain how the luminal surface, intercellular junctions and basal interface are organised” is a communication objective. The latter determines the view, necessary structures, labels and omissions. For a mechanism, the corresponding sentence must identify the process and its evidence status. For a patient explanation, it must identify the understanding or decision the visual is intended to support.

The title may name the subject; the composition must answer the question. Do not make a specimen or a diagram decorative simply because the title is already informative. Choose the smallest complete scientific explanation rather than the smallest possible drawing.

## 2. Keep three reference functions separate

An identity reference establishes what a structure or process is called. A spatial or mechanistic reference supports where it is, what it connects to or what relation is asserted. A communication reference demonstrates an effective way to explain it. One source may serve more than one role, but a famous atlas plate is not a licence to copy its artwork, and an ontology label is not a geometric reference.

Use a source ledger with exact version, figure or section, the claim it supports, the reason it is relevant and the applicable reuse conditions. Distinguish reviewed sources from verification targets. An agent should not convert “a source exists in the bibliography” into “this arrow has been verified.” The source records included here deliberately retain incomplete-retrieval and verification-target states.

For anatomy, inspect more than one appropriate view when a single projection leaves spatial ambiguity. For a molecular structure, distinguish measured coordinates, a computational model and a symbolic cartoon. RCSB's policies also distinguish archive coordinate data from its educational artwork. [rcsb]

## 3. Define the biological contract

The contract specifies identity, relationships, variation and exclusions. At minimum it declares the subject system, species, life stage, anatomical view, laterality and scale policy. Where relevant, add body region, sex characteristics, developmental stage, clinical context and normal or pathological variation. These are not decorative descriptors; they can change which geometry is defensible.

List the structures that must be present, the structures deliberately omitted, the relationships that must remain true and the claims that are uncertain. The scene's `relations` array represents structural assertions without adding visual clutter. `part_of`, `contains`, `branches_from`, `drains_into`, `lines`, `passes_through`, `innervates` and positional predicates are different relations. The compiler catches unresolved entities, proper part-whole cycles and direct positional contradictions. It cannot establish whether an asserted course or attachment is true.

For a mechanism, build a claim ledger before drawing arrows. Established claims require references. Proposed and illustrative claims remain distinguishable in the graphic. The example signalling figure intentionally uses an abstract hypothetical mechanism rather than inventing evidence for a named receptor pathway.

## 4. Select the representation

A regional anatomical plate explains three-dimensional relationships. A tissue section explains organisation at a cut surface. An unfolded map explains continuity at the expense of spatial shape. A mechanism explains interactions and state changes. A structure-based molecular view explains coordinates or surfaces. A workflow explains activities and information movement. A graphical abstract explains the supported contribution of a study. These are not interchangeable styles.

Choose the representation that makes the important relationship legible with the fewest necessary transformations. A complicated organ may need a locator plus a registered section. A simple membrane interaction rarely benefits from a full-body silhouette. A long tubular system may be clearer when unfolded, provided the alteration of spatial form is explicit. A magnified inset must identify its source region and must not resemble a causal arrow.

The 28 layout recipes are organised by reader question, reading order, required inputs and invariants. Their normalized slots execute as placement scaffolds. They do not supply the anatomical geometry or decide scientific truth. The eight specimens demonstrate complete uses of selected recipes.

## 5. Build geometry in the right order

Start with the outer extent and principal axis. Place the major compartments and structures. Resolve adjacency, continuity, entry and exit points, branching, cut planes and hidden surfaces. Only then add internal features, tissue texture and labels. Fixing a mistaken topology after painting is slower and more error-prone than detecting it in a sparse structural drawing.

Treat meaningful negative space as part of the anatomy. A lumen is not just a blank background. A tissue plane is not a convenient gap for a label. A vessel passing behind another structure must remain distinguishable from one entering it. A line crossing is not a junction unless the figure intentionally encodes one.

Reference-based geometry can come from a reviewed vector, a correctly registered 3D model or original drawing by an illustrator. The imported asset must retain its identity, viewpoint, rights and limitations. Do not stretch an organ to occupy a layout box. The compositor preserves aspect ratio and transforms its landmarks together with the geometry.

## 6. Use semantic detail instead of decorative density

Add a feature because the reader needs it to recognise, distinguish or understand the object. A selected membrane protein can be drawn at a larger illustrative scale to explain its role, but the scaling must not pretend to be measured. An organelle count chosen to balance a composition is not abundance data. Colour changes and surface marks cannot be used to imply a diagnostic difference without support.

Scale and omission are deliberate editorial decisions. Goodsell's molecular landscapes provide a useful research example: their explanatory construction combines several evidence types and deliberately leaves some components out. The lesson is explicit reconstruction and selective inclusion, not a request to imitate an artist's surface treatment. [goodsell]

A restrained schematic can be excellent. A detailed anatomical rendering can also be excellent. Flatness, realism, softness, minimalism and visual complexity are not quality scores on their own. Their value depends on the scientific task and the reader.

## 7. Compose the reading path

Place the dominant explanatory structure first. Give it sufficient space. Establish a small number of subordinate elements: a locator, inset, counterpart or legend only when needed. Use proximity to indicate grouping, alignment to support comparison and whitespace to distinguish unrelated content. Avoid boxing every object into an interface card.

For a paired comparison, lock the viewpoint, magnification, object identity, baseline colours and label vocabulary. Change only the declared variable or state. Otherwise the viewer cannot know whether the difference reflects biology or drawing choices. The paired epithelial specimen changes only the annotation, making the invariant geometry visible without fabricating a treatment effect.

Reserve label space before the final detailed drawing. Avoid letting the figure occupy every available point and then attaching a ring of tiny labels. Reading at the intended physical size is more informative than judging the artwork at a large zoom. Audience, message and medium should shape figure design. [figure-design]

## 8. Label the structure, not the bounding box

A label needs an actual target. An automatic line to an asset's nearest rectangle edge is not a guarantee that it touches the named structure. Each asset therefore has normalized landmarks. Custom anatomical assets should replace generic bounding-box landmarks with specific named points or clearly identified regions.

Use short unambiguous labels, consistent naming and a controlled abbreviation policy. Keep endpoints visibly attached to the intended structure. Do not run leaders through unrelated labels. Route leader lines separately from biological connectors and use no causal arrowheads on annotations. A dot endpoint can identify the selected point without asserting directional flow.

The software checks label-box overlap, canvas bounds, available text metrics and final physical type size. It does not automatically solve every line crossing or determine whether a point is on the correct anatomical surface. Those are image-review tasks.

## 9. Make uncertainty visible

Separate three questions: whether the object exists, whether the depicted relationship is supported, and whether its dimensions are measured. A real protein can appear in a hypothetical interaction. An established process can be drawn at an illustrative scale. A measured image can have an uncertain interpretation. Do not collapse these distinctions into a single “verified” flag.

A proposed relation should remain visually different from an established one. The house notation uses a dashed line for proposed and illustrative relations. It uses line and endpoint differences to distinguish association, activation, inhibition, transport, sequence and zoom. This is declared house notation, not a claim of formal SBGN compliance. SBGN defines distinct languages with their own semantics and specifications. [sbgn; sbgn-spec]

Captions should state meaningful omissions and the scope of inference. They should not contain production status, tests passed or assurances of quality. “Vasculature omitted” is a substantive limitation. “Passed QC” is not an explanation of the figure.

## 10. Accessibility is part of the explanation

Preserve meaning without colour alone. Use labels, shapes, line types or patterns to support distinctions. Check the most important relationships in grayscale and under appropriate colour-vision simulation. Avoid using a change in hue as the sole sign that a process is activated or inhibited. [wai-colour]

Every complete SVG has a title and a description. A useful long description explains the organisation and the intended takeaway, not merely a list of colours or the phrase “diagram of cells.” Complex figures can need a companion textual explanation. Patient materials require comprehension testing with their intended readers, not only a readability score. [wai-complex]

The default 7-point minimum at 180 mm width and 4.5:1 canvas-text contrast threshold are house settings. They are not substitutes for the current target journal's rules or the actual viewing conditions. The final production environment may substitute fonts; review the exported image there.

## 11. Keep observations and illustrations distinct

A realistic-looking generated image is not a microscope observation, a scan, a pathology specimen or patient evidence. Keep actual research images on a separate workflow with source preservation and permitted processing. The conceptual study-workflow specimen deliberately stops at the activity of microscopy; it does not manufacture a microscopy result.

Journal policies must be checked by figure category. Under the reviewed Elsevier policy, explanatory diagrams, data visualisations, primary research images and graphical abstracts have different conditions. Do not convert an exception for one class into blanket permission for another. The current target journal and any applicable disclosure requirement still control submission. [elsevier-ai]

Patient-related illustrations also need appropriate handling of consent, confidentiality and potentially identifying detail. Do not upload source photographs or clinical images to an external model merely because it would improve the drawing. Confidentiality and ethical conduct are part of the professional obligation. [ami-ethics]

## 12. Review the artifact that will actually be used

Scientific review should examine identity, topology, labels, omissions, evidence and interpretation. Visual review should examine reading order, hierarchy, clutter, legibility, line routing and colour/shape semantics. The reviewer must see the final image and its intended context, not only the prompt or a checklist.

Bind approval to the actual scene, used asset records, renderer and SVG. A later geometry edit, label change or substituted asset invalidates that binding. Keep the production record separate from the figure. Machine checks are useful because they make some errors cheap to catch; they are not a substitute for a qualified review of medical content.

The standard of success is the requested scientific communication, not completion of a checklist. When a defect is found, name it, change the relevant component and recheck the affected dependencies. Do not restart the entire figure or add unrelated tests unless a new material uncertainty requires it.
