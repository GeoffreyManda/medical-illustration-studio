# The executable visual grammar

## A figure contains several kinds of statements

The scene language distinguishes biological identity, spatial assertions, mechanistic relations, drawing geometry, text and evidence. These distinctions prevent an agent from treating every object as an icon and every relation as an arrow.

A concise conceptual form is:

```text
figure := commission + anatomical_frame + claims + compartments
          + entity_instances + structural_relations + visible_relations
          + labels + calibration + explanation
```

The executable representation is JSON governed by `scene.schema.json`. The renderer accepts version `1.0.0`. Unknown fields are rejected. Extensions should be added deliberately to the schema, implementation and tests rather than silently placed into documents that the renderer ignores.

## Commission and anatomical frame

Required top-level fields include `id`, `title`, `description`, `audience`, `representation`, `frame`, `canvas`, `sources`, `claims`, `compartments`, `nodes`, `edges`, `labels` and `caption`. `subtitle`, `layout`, `relations` and `scale_bars` are optional.

`audience` is one of `scientific`, `clinical`, `student`, `patient` or `public`. `representation` is `schematic` or `anatomical`. Anatomical mode rejects a bundled schematic asset used as primary anatomical geometry. It does not certify imported anatomical geometry.

The required frame fields are `species`, `life_stage`, `view`, `laterality`, `projection` and `scale_policy`. Laterality is `left`, `right`, `bilateral` or `not-applicable`; scale policy is `not-to-scale` or `calibrated`. Optional fields describe body region, sex characteristics, variants and clinical context. These strings make the assumptions explicit. Correct anatomical interpretation still requires expert review.

Canvas coordinates use a top-left origin with positive x to the right and positive y downward. Those are drawing coordinates, not anatomical superior/inferior or patient left/right. DICOM patient coordinates and image orientation require their own documented interpretation. [dicom]

## Sources and claims

A source contains an ID, title, URL or documented provenance URN, and kind: `reference`, `illustrative` or `original-data`. A locator may identify a section or specific source feature. A claim contains ID, text, status and source IDs.

```json
{
  "id": "claim-activation",
  "text": "The proposed regulator activates the response in this explanatory model.",
  "status": "proposed",
  "sources": ["source-study"]
}
```

Allowed statuses are `established`, `proposed` and `illustrative`. An established claim needs source records and cannot rely on a source marked merely illustrative. This is a traceability rule. It does not determine whether a paper supports the claim, whether it is reliable or whether a causal interpretation is justified.

Do not use a bibliography as a substitute for a claim map. Do not create a source record with a convincing title but no actual evidence. For unsourced examples, declare their illustrative status and do not give them the appearance of an established named pathway.

## Entity instances and geometry

Each node instantiates an asset. The asset is the reusable drawing and its metadata; the node is its position and role in this figure. Repeated nodes may use the same asset ID, but node IDs must be unique.

```json
{
  "id": "receptor",
  "asset": "receptor-single",
  "box": [433, 267, 140, 193],
  "compartment": "intracellular",
  "placement": "boundary"
}
```

A box is `[x, y, width, height]`. Asset aspect ratio is preserved inside the box. A tall box does not stretch a square asset into a tall cell. The drawing is centred within its box; some empty space can remain. This distinction is essential when making continuous tissue assemblies.

An alternative to a box is a named `slot` from the chosen layout. Exactly one of box or slot is required. The slot is a normalized positional scaffold. It does not supply content or determine a medically appropriate object size.

Optional `rotation` accepts 0, 90, 180 or 270 degrees. `flip_x` is accepted only for assets declared mirror-safe. Landmarks undergo the same rotation, mirroring and scale as the artwork. Primary anatomical assets must retain clinically meaningful laterality; a transformation that is geometrically supported is not automatically scientifically appropriate.

`kind` is `entity` or `process`. `role` is `primary` or `support`. A process node is required where consumption or production edges use the house reaction notation. A node note can document a substantive local limitation.

## Compartments and boundaries

Compartments have an ID, label, box, fill, boundary style and kind. Their function is to establish the scene context rather than to act as generic decorative panels. Examples include extracellular and intracellular regions, cortex and medulla, or a defined tissue region.

For `placement: inside`, the node box must lie inside its declared rectangular compartment. For `placement: boundary`, it must overlap and extend across the boundary. `unconstrained` skips that geometric condition and should be used only for a stated reason.

These checks operate on rectangles. They do not prove containment within a cell's curved silhouette, registration to a 3D surface or correct membrane insertion. Do not interpret a successful rectangle test as anatomical proof. For a membrane-bound object, inspect the actual rendered membrane and the orientation of the extracellular and intracellular domains.

## Structural relations

Structural relations express anatomical facts that generally should not become drawn arrows. Each record has an ID, subject node, predicate, object node and claim ID.

```json
{
  "id": "nucleus-in-cell",
  "subject": "nucleus",
  "predicate": "part_of",
  "object": "cell",
  "claim": "cell-organisation"
}
```

The 25 predicates are:

| Family | Predicates |
|---|---|
| Part and enclosure | `part_of`, `contains`, `encloses`, `lines` |
| Spatial relation | `adjacent_to`, `anterior_to`, `posterior_to`, `superior_to`, `inferior_to`, `medial_to`, `lateral_to`, `superficial_to`, `deep_to`, `proximal_to`, `distal_to` |
| Continuity and route | `branches_from`, `drains_into`, `passes_through`, `continuous_with` |
| Functional or attachment relation | `supplies`, `innervates`, `originates_from`, `inserts_into`, `contacts` |
| Cross-view mapping | `corresponds_to` |

A structure enclosing another is not automatically its anatomical parent. A drawn overlap is not automatically contact. A vessel supplying an organ is not the same statement as that vessel being part of the organ. Keep the predicate specific.

The validator rejects self-relations, unresolved entities or claims, cycles in normalized proper part-whole relations, and direct opposite spatial assertions. It does not convert screen x/y positions into anatomical relations. Spatial truth must be checked in the declared anatomical frame. Different projections or instances should use appropriate correspondence records rather than contradictory positions assigned to the same object pair.

## Visible relations

An edge has source and target references, a type, an ID and optional claim, polyline waypoints, text label and label position. The endpoints identify a node and a named landmark.

```json
{
  "id": "activation",
  "source": {"node": "receptor", "landmark": "intracellular-domain"},
  "target": {"node": "effector", "landmark": "left"},
  "type": "activation",
  "claim": "claim-activation",
  "via": [[503, 574], [704, 574]],
  "label": "activates",
  "label_position": [553, 540]
}
```

| Type | Visual convention | Scientific meaning |
|---|---|---|
| `activation` | Open arrow end | Positive influence in the stated model |
| `inhibition` | T-bar end | Negative influence in the stated model |
| `association` | Plain undirected line | Association or contact, not causation |
| `transport` | Filled arrow end | Directed movement of the stated material |
| `consumption` | Filled arrow into a process node | Input to the declared process |
| `production` | Filled arrow out of a process node | Output of the declared process |
| `sequence` | Filled arrow end | Order of activities or explanatory stages |
| `zoom` | Dashed line without arrowhead | Correspondence across illustrative scales |

Biological edge types require a claim. Sequence and zoom do not imply biological causation. Proposed and illustrative claims are dashed regardless of arrow type. Where multiple relation types occur, include a concise explanatory legend or caption. An arrowhead shape cannot carry every scientific distinction by itself.

This is house notation. It is not an SBGN-ML exporter or a formal SBGN conformance implementation. Use an appropriate SBGN tool and the relevant Process Description, Activity Flow or Entity Relationship specification when formal interchange is required. [sbgn; sbgn-spec]

## Labels and landmarks

A label has an ID, editable text and a box. Optional fields specify font size, alignment, role, target and leader waypoints. Alignment is `left`, `right` or `centre`; role is `label`, `heading` or `note`.

Landmarks are normalized points within an asset's view box. Their names should express the target, such as `outer-membrane`, `nucleolus`, `urinary-pole` or `basement-membrane`. The five generic landmarks supplied on every asset are useful for layout and non-anatomical connectors, but they are not substitutes for named anatomical targets. In imported assets they initially describe bounding-box positions.

The renderer wraps text using available font metrics, places editable text and draws a leader from an appropriate side of its box. It does not perform global automatic label-layout optimisation. It checks text-box overlap, but not every line crossing or obstruction by underlying anatomy. Explicit waypoints are supported when a leader needs to avoid another label or structure.

Final physical type size is calculated as:

```text
font points = font coordinate size × print width in mm × 72
              / (canvas coordinate width × 25.4)
```

Do not shrink a complete figure after checking its labels without recalculating the effective size. The default profile uses 180 mm width with a 7-point minimum label size. These are configurable house values, not universal journal requirements.

## Calibration and scale

A scale bar needs its drawing length, physical length, units per coordinate pixel, unit name and a source. The frame must be marked calibrated. The compiler checks that drawing length multiplied by calibration equals physical length. It does not establish whether the calibration source is valid or whether all elements share that scale.

Multi-scale scenes often cannot share one scale bar. Use separately calibrated views when data permit. Otherwise state that the scales are unequal and illustrative. A magnification label chosen for aesthetic balance is not calibration.

## Assets, ontology and rights

The asset schema records drawing content, view box, landmarks, category, scale class, representation, viewpoint, mirroring policy, creator, licence, reference IDs, review state, aliases and limitations. Imported assets also record source URL. Optional ontology bindings have system, identifier, label, release and URL fields.

Ontology bindings must be looked up and confirmed. FIPAT, Uberon, Cell Ontology and MeSH support different purposes; their labels are not interchangeable identifiers. Record the version, especially where terminologies have changed. [fipat; ta2; uberon; cl; mesh]

`reference_ids` can include verification targets. `schematic_unreviewed` and `imported_unreviewed` must not be renamed to `expert_reviewed` because an AI inspected the file. A verified licence also does not imply verified biology.

## Interchange and deliberate limits

SVG is the editable interchange format. PNG is a raster convenience format. PDF preserves the composed figure for viewing or publication workflows. The scene JSON preserves semantic and positional instructions. Editing a delivered SVG in another application does not automatically update the scene JSON; reconcile the edit before regenerating the figure.

No R, Blender, Figma, Illustrator, Inkscape, SBGN-ML, DICOM or molecular-coordinate round-trip adapter is claimed. Existing tools can read or supply appropriate files, but the tested local path is JSON to SVG and optional CairoSVG conversion. A broader interoperability claim requires actual round-trip tests in the target applications.
