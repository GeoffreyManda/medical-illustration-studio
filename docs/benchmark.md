# Comparative evaluation: protocol, not results

## What would justify a quality claim?

A claim of Netter-level anatomical communication requires much more than attractive example images. It needs expert assessment of spatial anatomy, labels, informative exposure, completeness for the brief and visual explanation. A claim of BioRender-level schematic capability needs assessment of coherent scientific scenes, relation semantics, asset adequacy, editing, export and reliability. A claim of market superiority requires a defined comparison set and a study, not a feature list.

No such evaluation has been completed for this package. The provided 24 task briefs are a reusable benchmark specification. The eight specimens are demonstrations, not blinded evaluation outputs. No performance scores or human approvals are supplied.

## Compare complete workflows fairly

Compare tools at the level at which people actually use them. An icon collection should not be treated as a failed illustration application because it does not draw arrows or place labels. A general vector editor paired with an open asset collection is a legitimate workflow comparator. An anatomical 3D source paired with an illustrator's vector or painting workflow is another.

A suitable comparison set could include Bioicons plus an SVG editor, Servier artwork plus an editor, NIH BioArt Source plus an editor, Z-Anatomy plus a compatible 3D/2D workflow, a formal SBGN editor for pathways, and this toolkit with the same permitted source access. Include licensed commercial workflows only where permission allows the evaluation and use of resulting figures. Document tool versions, asset licences, operator experience and model/backend settings. [bioicons; servier; nih-bioart; zanatomy; sbgn]

Do not penalise a comparator for refusing to fabricate research data, missing copyrighted artwork or lack of access to the same references. Conversely, do not quietly give one system an expert-produced finished anatomical drawing while asking another to infer it from text.

## Tasks and reference answers

The task file covers anatomy, tissue sections, tubular continuity, membranes, cellular organisation, matched views, workflows, multi-scale scenes, cutaways, exploded layers, section registration, procedure explanation, innervation, vascular routes, topography, histology schemata, molecular binding, reaction networks, feedback, cell interfaces, development, pathology and device context.

For each task, prepare a fixed brief, source package, required structures or relations, important omissions, permitted assets, final dimensions and reference answer. An independent specialist should approve the reference answer and the critical-error list. Do not use the model's own output as the reference against which its correctness is scored.

The 24 supplied briefs are generic. They become an evaluation dataset only after those task-specific materials have been supplied. Keep some tasks and references out of development so that repeated tuning does not turn the test into a memory exercise.

## Scoring

Rate each domain from 0 to 4 using explicit definitions: 0 is unusable or materially wrong; 1 has major failures; 2 is usable only after substantial correction; 3 meets the defined requirement with limited correction; 4 meets it well without a material identified defect.

| Domain | Weight | Evaluation question |
|---|---:|---|
| Scientific accuracy | 30 | Are structures, claims, labels and evidence interpretations correct? |
| Spatial topology | 20 | Are continuity, adjacency, laterality, layers and orientation correct? |
| Communication | 20 | Does the intended reader understand the intended distinction? |
| Visual craft | 15 | Does the composition use form, hierarchy and detail effectively? |
| Accessibility | 5 | Does meaning survive the required viewing and accessibility conditions? |
| Editability and reproducibility | 5 | Can the result be edited and regenerated without losing its meaning? |
| Licensing and traceability | 5 | Are rights, sources and adaptations appropriately recorded? |

The total is the sum of weight multiplied by domain rating, divided by four. It ranges from 0 to 100. A critical scientific or integrity error fails the task irrespective of the total. An aesthetically excellent figure with wrong laterality must not pass because its other scores are high.

## Critical errors

Predefine critical errors for each task. Examples include wrong anatomical identity or laterality, impossible connections, a label identifying the wrong structure, unsupported causal interpretation, a fabricated primary research image, a materially false scale, an invented result or impermissible redistribution of proprietary artwork.

Define borderline errors in advance as well. A deliberate omission disclosed in the brief is not the same as a missing required structure. A schematic enlargement declared as not to scale is not the same as a false quantitative scale. These distinctions need consistent reviewer guidance.

## Human evaluation

Use at least two independent qualified reviewers for scientific judgments and appropriate visual reviewers for craft and communication. Randomise output order and remove tool branding where lawful and feasible. Do not blind reviewers to scientific context needed for a valid judgment. Record individual ratings before adjudicating disagreements.

Report task-level scores, critical failures, disagreements, uncertainty and time to a usable reviewed figure. Account for the paired design because the tools receive the same tasks. A bootstrap across tasks can describe uncertainty in paired performance differences, provided its assumptions and limitations are clear. Do not turn a small task set with wide uncertainty into a universal claim of superiority.

Record time spent on source preparation, initial generation, corrections and human review separately. A system that generates quickly but requires extensive anatomical correction has not necessarily improved the production workflow.

## Using the scorer

The CLI calculates a weighted score from a single submitted human rating. It does not run the comparative study, recruit reviewers or infer medical quality from pixels.

```json
{
  "task_id": "MED-01",
  "candidate_id": "candidate-a",
  "reviewer_id": "actual-reviewer-identifier",
  "scores": {
    "scientific_accuracy": 3,
    "spatial_topology": 3,
    "communication": 3,
    "visual_craft": 3,
    "accessibility": 3,
    "editability_reproducibility": 3,
    "licensing_traceability": 3
  },
  "critical_errors": []
}
```

These values demonstrate the input format; they are not ratings of this package or any competing tool. Replace them with an actual review before making a performance statement.

```bash
python -m medillustrate benchmark --ratings actual-rating.json
```

## What the software tests establish

The executable tests exercise schemas, passive SVG handling, asset rendering, layout slots, scene reproduction, references, relation constraints, text and box checks, import behaviour, export limits and review-record binding. They establish software behaviour under those test cases. They do not establish anatomical completeness, medical validity, clinician comprehension, publication acceptance or superiority to another product.

Keep those two forms of evidence separate. An honest evaluation can report strong software reliability while also finding insufficient anatomical coverage or requiring further expert review.
