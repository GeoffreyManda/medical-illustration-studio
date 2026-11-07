# Layout atlas

Each recipe starts from a reader's question rather than a decorative arrangement. Slots are executable normalized `[x, y, width, height]` positions within the full canvas. They are starting positions, not automatic anatomical composition or finished artwork. Asset aspect ratio is preserved; author and review the geometry, labels and relationships separately.

Choose the recipe that reveals the required relationship. Retain its invariants when refining the composition. A multiscale view, a matched comparison and a regional plate make different promises to the reader. Do not switch between them simply because an asset fits a convenient box.

## 1. Single anatomical plate

**Identifier:** `anatomical-plate`.

**Reader question:** What is present and where?

**Reading order:** orientation → dominant structure → named landmarks.

**Preserve:** One documented viewpoint; Accurate adjacency and depth; Label endpoints on named structures.

**Do not substitute:** Icon collage; Invented branching; Mirroring for convenience.

**Required inputs:** Reviewed geometry; View and laterality; Required and omitted structures.

```json
{
  "hero": [
    0.24,
    0.2,
    0.53,
    0.61
  ]
}
```

## 2. Polarised epithelial section

**Identifier:** `epithelial-section`.

**Reader question:** How are the luminal and basal sides organised?

**Reading order:** lumen → epithelium → basal interface.

**Preserve:** Apical-basal order; Contiguous epithelial row; Basement membrane position.

**Do not substitute:** Random nuclei outside cells; Confusing a section with a surface view.

**Required inputs:** Cell classes; Junction detail; Tissue context.

```json
{
  "tissue": [
    0.12,
    0.35,
    0.72,
    0.4
  ]
}
```

Complete schematic specimen: `examples/epithelial-barrier.scene.json`.

## 3. Vessel-wall cross-section

**Identifier:** `vascular-cross-section`.

**Reader question:** Which layer is being explained?

**Reading order:** lumen → inner lining → wall layers.

**Preserve:** Concentric layer order; Cut-plane declaration; No quantitative thickness claim without data.

**Do not substitute:** Red equals artery as a universal rule; Identical layer widths presented as measurements.

**Required inputs:** Vessel class; Layer terminology; Cut plane.

```json
{
  "hero": [
    0.24,
    0.2,
    0.53,
    0.61
  ]
}
```

Complete schematic specimen: `examples/vascular-wall.scene.json`.

## 4. Unfolded tubular system

**Identifier:** `unfolded-tubule`.

**Reader question:** Which compartments are connected?

**Reading order:** entry → continuous tubular route → exit.

**Preserve:** Lumen continuity; Separate blood and filtrate; Not-to-scale disclosure.

**Do not substitute:** Crossing lines interpreted as anastomoses; Claiming collecting duct is part of nephron.

**Required inputs:** Segment list; Connectivity; Regional boundary.

```json
{
  "system": [
    0.2,
    0.2,
    0.6,
    0.66
  ]
}
```

Complete schematic specimen: `examples/renal-nephron.scene.json`.

## 5. Membrane-centred signalling

**Identifier:** `membrane-signalling`.

**Reader question:** How does a signal cross a compartment boundary?

**Reading order:** extracellular signal → boundary interaction → intracellular effect.

**Preserve:** Compartment assignments; Biological edge type; Hypotheses visibly distinguished.

**Do not substitute:** All arrows meaning the same thing; Signal arrows called transport.

**Required inputs:** Evidence for each claim; Receptor class; Mechanism scope.

```json
{
  "ligand": [
    0.2,
    0.19,
    0.12,
    0.17
  ],
  "receptor": [
    0.38,
    0.32,
    0.13,
    0.29
  ],
  "effector": [
    0.58,
    0.66,
    0.14,
    0.2
  ]
}
```

Complete schematic specimen: `examples/cell-signalling.scene.json`.

## 6. Cell interior with selective detail

**Identifier:** `cell-interior`.

**Reader question:** Where are the named cellular structures?

**Reading order:** cell boundary → nucleus → selected organelles.

**Preserve:** Organelle containment; No arbitrary copy counts treated as data; Shared abstraction level.

**Do not substitute:** Every organelle given equal emphasis; False measured size relationships.

**Required inputs:** Cell type; Organelle subset; Scale policy.

```json
{
  "cell": [
    0.12,
    0.21,
    0.64,
    0.62
  ]
}
```

Complete schematic specimen: `examples/cell-interior.scene.json`.

## 7. Matched structural comparison

**Identifier:** `paired-state`.

**Reader question:** What precisely differs between the two states?

**Reading order:** state A → state B → single declared difference.

**Preserve:** Same viewpoint; Same dimensions and scale; Only named changes.

**Do not substitute:** Treatment efficacy implied by invented improvement; Changing every visual variable.

**Required inputs:** State definitions; Evidence or explicit hypothetical status; Locked comparison settings.

```json
{
  "before": [
    0.08,
    0.3,
    0.38,
    0.4
  ],
  "after": [
    0.54,
    0.3,
    0.38,
    0.4
  ]
}
```

Complete schematic specimen: `examples/paired-epithelium.scene.json`.

## 8. Research workflow

**Identifier:** `study-workflow`.

**Reader question:** What material or information passes between stages?

**Reading order:** material → activity → measurement or information.

**Preserve:** Differentiate sample from data; Traceable stage order; No fabricated outputs.

**Do not substitute:** Fictional plots as results; Decorative dashboard cards.

**Required inputs:** Actual workflow scope; Stage definitions; Output type.

```json
{
  "input": [
    0.08,
    0.34,
    0.17,
    0.27
  ],
  "process": [
    0.4,
    0.34,
    0.17,
    0.27
  ],
  "output": [
    0.73,
    0.34,
    0.17,
    0.27
  ]
}
```

Complete schematic specimen: `examples/study-workflow.scene.json`.

## 9. Nested biological scales

**Identifier:** `multiscale-zoom`.

**Reader question:** How does local structure relate to the larger context?

**Reading order:** context → selected region → magnified feature.

**Preserve:** Zoom is not causation; Parent region explicitly selected; Independent scale or not-to-scale.

**Do not substitute:** Uniform scale bars on unequal magnification; Floating inset without origin.

**Required inputs:** Source region; Local feature; Scale evidence.

```json
{
  "context": [
    0.04,
    0.34,
    0.25,
    0.3
  ],
  "cell": [
    0.36,
    0.25,
    0.27,
    0.44
  ],
  "detail": [
    0.74,
    0.37,
    0.23,
    0.28
  ]
}
```

Complete schematic specimen: `examples/multi-scale-tissue.scene.json`.

## 10. Selective cutaway

**Identifier:** `cutaway`.

**Reader question:** What is hidden beneath an intact surface?

**Reading order:** intact surface → cut edge → exposed contents.

**Preserve:** Cut surfaces distinct from intact tissue; Layer occlusion; One documented lighting convention.

**Do not substitute:** Transparency that erases structures; Implausible resection.

**Required inputs:** Reference anatomy; Cut plane; Removed structures.

```json
{
  "hero": [
    0.18,
    0.2,
    0.64,
    0.61
  ]
}
```

## 11. Exploded laminar anatomy

**Identifier:** `exploded-layers`.

**Reader question:** What is the order of normally apposed layers?

**Reading order:** outer → intermediate → inner.

**Preserve:** Original adjacency retained; Displacement explicitly conceptual; No displacement called anatomical distance.

**Do not substitute:** Rearranging layers to fit labels; Artificial gaps interpreted as pathology.

**Required inputs:** Layer order; Displacement direction; Attachment information.

```json
{
  "outer": [
    0.25,
    0.19,
    0.5,
    0.18
  ],
  "middle": [
    0.25,
    0.42,
    0.5,
    0.18
  ],
  "inner": [
    0.25,
    0.65,
    0.5,
    0.18
  ]
}
```

## 12. Plane-to-section registration

**Identifier:** `section-registration`.

**Reader question:** Where was this section taken?

**Reading order:** whole → plane indicator → registered section.

**Preserve:** Plane orientation; Patient laterality; One-to-one landmarks.

**Do not substitute:** Radiological display silently reflected; Section from a different level.

**Required inputs:** Source volume or reviewed plate; Plane normal; Registration landmarks.

```json
{
  "locator": [
    0.07,
    0.25,
    0.35,
    0.46
  ],
  "section": [
    0.52,
    0.25,
    0.41,
    0.46
  ]
}
```

## 13. Reviewed procedural sequence

**Identifier:** `surgical-sequence`.

**Reader question:** How do exposures and relationships change over time?

**Reading order:** exposure → intermediate state → resulting state.

**Preserve:** Same operative orientation; Tissue continuity; Qualified procedural review.

**Do not substitute:** Invented operative steps; Unsafe instructions without clinical context.

**Required inputs:** Approved step list; Clinical specialist; Reference anatomy.

```json
{
  "step1": [
    0.06,
    0.31,
    0.27,
    0.37
  ],
  "step2": [
    0.37,
    0.31,
    0.27,
    0.37
  ],
  "step3": [
    0.68,
    0.31,
    0.27,
    0.37
  ]
}
```

## 14. Innervation territory map

**Identifier:** `innervation-map`.

**Reader question:** Which route reaches which territory?

**Reading order:** origin → route → territory.

**Preserve:** Tract/nerve/branch distinction; Branch continuity; Territory uncertainty.

**Do not substitute:** Curves added as decorative nerves; Branch names attached to wrong level.

**Required inputs:** Verified course; Landmarks; Variant policy.

```json
{
  "trunk": [
    0.29,
    0.22,
    0.37,
    0.62
  ],
  "territory": [
    0.72,
    0.3,
    0.22,
    0.45
  ]
}
```

## 15. Directed circulation route

**Identifier:** `vascular-route`.

**Reader question:** Which named vessels connect these regions?

**Reading order:** source → exchange region → return.

**Preserve:** Flow direction; Named connections; Oxygenation distinct from vessel identity.

**Do not substitute:** Impossible anastomosis; Generic red/blue meaning unexplained.

**Required inputs:** Connectivity table; Flow scope; Included/excluded beds.

```json
{
  "source": [
    0.09,
    0.28,
    0.25,
    0.4
  ],
  "bed": [
    0.38,
    0.28,
    0.25,
    0.4
  ],
  "return": [
    0.69,
    0.28,
    0.25,
    0.4
  ]
}
```

## 16. Organ topography

**Identifier:** `organ-topography`.

**Reader question:** Which neighbouring structures determine location?

**Reading order:** orientation → target → neighbours.

**Preserve:** Laterality; Position relative to landmarks; Depth and cavity relationships.

**Do not substitute:** Independent icons placed in a silhouette; Patient variation erased.

**Required inputs:** Species and life stage; Reviewed regional anatomy; Depth plan.

```json
{
  "region": [
    0.17,
    0.19,
    0.66,
    0.63
  ]
}
```

## 17. Histology-derived explanatory schema

**Identifier:** `histology-schema`.

**Reader question:** Which tissue organisation should the reader recognise?

**Reading order:** tissue pattern → cell relationships → selected feature.

**Preserve:** Schematic label; No fabricated microscope evidence; Stain/colour semantics declared.

**Do not substitute:** Invented histology passed as observed; Cytology diagnosis from illustrative texture.

**Required inputs:** Actual reference material; Structural thesis; Schematic disclosure.

```json
{
  "field": [
    0.1,
    0.24,
    0.63,
    0.52
  ],
  "detail": [
    0.78,
    0.34,
    0.18,
    0.29
  ]
}
```

## 18. Structure-based binding view

**Identifier:** `structure-binding`.

**Reader question:** Where is a supported molecular interaction located?

**Reading order:** assembly → selected site → observed or proposed interaction.

**Preserve:** Structure identifiers; Chain/assembly definition; Missing regions acknowledged.

**Do not substitute:** Invented atom contacts; Random protein blob called crystal structure.

**Required inputs:** PDB/source file; Source paper; Representation and ligand state.

```json
{
  "complex": [
    0.12,
    0.23,
    0.57,
    0.55
  ],
  "site": [
    0.76,
    0.33,
    0.19,
    0.31
  ]
}
```

## 19. Reaction-centred network

**Identifier:** `reaction-network`.

**Reader question:** What is consumed, produced or regulates a process?

**Reading order:** inputs → process → outputs and modifiers.

**Preserve:** Process node; Material vs modulation edges; Stoichiometry only when supported.

**Do not substitute:** Activation arrow used as mass flow; Mixed SBGN dialects.

**Required inputs:** Reaction definitions; Evidence; Named notation.

```json
{
  "substrate": [
    0.1,
    0.35,
    0.2,
    0.28
  ],
  "process": [
    0.4,
    0.4,
    0.15,
    0.18
  ],
  "product": [
    0.68,
    0.35,
    0.22,
    0.28
  ]
}
```

## 20. Feedback organisation

**Identifier:** `feedback-loop`.

**Reader question:** What returns to regulate an earlier process?

**Reading order:** forward route → response → return regulation.

**Preserve:** Feedback sign; Endpoint identity; No unsupported closed-loop causation.

**Do not substitute:** Circular layout treated as temporal proof; Inhibition confused with absence.

**Required inputs:** Edge claims; Mechanism boundary; Feedback evidence.

```json
{
  "input": [
    0.08,
    0.32,
    0.22,
    0.27
  ],
  "response": [
    0.4,
    0.32,
    0.22,
    0.27
  ],
  "feedback": [
    0.73,
    0.32,
    0.2,
    0.27
  ]
}
```

## 21. Two-cell interface

**Identifier:** `cell-interaction`.

**Reader question:** What changes at a specific contact?

**Reading order:** cell identities → contact region → local interaction.

**Preserve:** Membrane adjacency; Side-specific proteins; Contact vs soluble signalling.

**Do not substitute:** Receptor on wrong cell; Cells fused unintentionally.

**Required inputs:** Cell types; Molecular sides; Interaction evidence.

```json
{
  "cellA": [
    0.11,
    0.23,
    0.31,
    0.51
  ],
  "cellB": [
    0.57,
    0.23,
    0.31,
    0.51
  ]
}
```

## 22. Developmental sequence

**Identifier:** `developmental-series`.

**Reader question:** Which changes are attributable to developmental stage?

**Reading order:** earlier stage → intermediate stage → later stage.

**Preserve:** Species; Stage rather than arbitrary age; Homologous landmarks.

**Do not substitute:** Adult proportions shrunk to represent children; Cross-species stage mixing.

**Required inputs:** Stage references; Scale policy; Landmark correspondences.

```json
{
  "early": [
    0.07,
    0.29,
    0.25,
    0.42
  ],
  "mid": [
    0.38,
    0.29,
    0.25,
    0.42
  ],
  "late": [
    0.69,
    0.29,
    0.25,
    0.42
  ]
}
```

## 23. Localised pathological change

**Identifier:** `pathology-localisation`.

**Reader question:** Where does the supported change occur?

**Reading order:** normal context → lesion boundary → mechanism or morphology.

**Preserve:** Lesion location; Evidence vs stylisation; No diagnostic specificity from invented colour.

**Do not substitute:** Impossible invasion routes; Disease severity inferred without data.

**Required inputs:** Disease context; Reference material; Clinical reviewer.

```json
{
  "context": [
    0.07,
    0.24,
    0.53,
    0.52
  ],
  "lesion": [
    0.69,
    0.28,
    0.24,
    0.43
  ]
}
```

## 24. Device in anatomical context

**Identifier:** `device-anatomy`.

**Reader question:** How does a device relate to the surrounding structure?

**Reading order:** anatomical route → device position → contact or functional region.

**Preserve:** Correct scale/placement; Manufacturer version; No instruction inferred from decoration.

**Do not substitute:** Device floating through tissue; Off-label use implied without context.

**Required inputs:** Reviewed device geometry; Anatomical references; Intended-use statement.

```json
{
  "anatomy": [
    0.13,
    0.2,
    0.63,
    0.6
  ],
  "detail": [
    0.79,
    0.35,
    0.17,
    0.26
  ]
}
```

## 25. Patient educational explanation

**Identifier:** `patient-explanation`.

**Reader question:** What should a non-specialist understand or do?

**Reading order:** plain-language question → essential visual → clear explanation.

**Preserve:** Limited jargon; Respectful representation; Comprehension testing.

**Do not substitute:** Graphic detail unrelated to purpose; Treatment recommendation without source.

**Required inputs:** Audience needs; Approved clinical message; Accessibility plan.

```json
{
  "hero": [
    0.23,
    0.23,
    0.54,
    0.52
  ]
}
```

## 26. Editorial graphical abstract

**Identifier:** `graphical-abstract`.

**Reader question:** What is the single supported finding and its scope?

**Reading order:** question → supported result → bounded interpretation.

**Preserve:** Actual findings; Publisher-specific AI policy; No invented study quantities.

**Do not substitute:** Dashboard of every method; General-purpose AI imagery where disallowed.

**Required inputs:** Manuscript; Real result; Journal policy.

```json
{
  "premise": [
    0.06,
    0.31,
    0.22,
    0.38
  ],
  "finding": [
    0.34,
    0.22,
    0.37,
    0.52
  ],
  "implication": [
    0.77,
    0.35,
    0.17,
    0.3
  ]
}
```

## 27. Respectful representation comparison

**Identifier:** `equity-comparison`.

**Reader question:** Does the explanation remain true across represented groups?

**Reading order:** common anatomy → relevant difference → limits of comparison.

**Preserve:** Variation is evidence-based; Shared scientific detail; No default group coded as normal.

**Do not substitute:** Skin tone as pathology code; Unsupported group biology.

**Required inputs:** Purpose of comparison; Evidence; Representation brief.

```json
{
  "groupA": [
    0.09,
    0.3,
    0.36,
    0.4
  ],
  "groupB": [
    0.55,
    0.3,
    0.36,
    0.4
  ]
}
```

## 28. Evidence-linked mechanism

**Identifier:** `evidence-mechanism`.

**Reader question:** Which portions are established and which are proposed?

**Reading order:** observed or established → proposed bridge → outcome.

**Preserve:** Visible uncertainty; Claim-specific evidence; Association is not a causal edge.

**Do not substitute:** A solid arrow laundering speculation; Source lists without claim mapping.

**Required inputs:** Claim ledger; Evidence status; Scope of inference.

```json
{
  "known": [
    0.08,
    0.31,
    0.3,
    0.4
  ],
  "uncertain": [
    0.45,
    0.31,
    0.2,
    0.4
  ],
  "outcome": [
    0.72,
    0.31,
    0.2,
    0.4
  ]
}
```

## Selecting a layout without overcomplicating the scene

Use one main view when it can answer the question. Add a locator when spatial context is otherwise unclear. Add a registered section when an internal relationship is hidden. Add an inset when local detail is necessary, and identify its parent region. Use a paired view when the purpose is comparison, with common geometry and scale. Use a sequence only when the order of stages matters.

A recipe does not require every available slot to be filled. Empty space can protect the reading path and label clarity. Conversely, a required anatomical structure cannot be omitted merely because a slot is full. Adjust the composition while preserving the scientific contract.
