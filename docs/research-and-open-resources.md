# Research and open resources

## Scope and selection

This is a focused primary-source review for building a practical medical illustration toolkit, checked on 5 October 2026. It is not a systematic census of every anatomical atlas, artist, publication standard or open-source application. The source directory distinguishes reviewed material, discovery-only records, incomplete retrieval and recommended verification targets. It does not claim that every listed source has supplied an independently verified asset.

The review covers professional medical illustration, proprietary reference boundaries, open scientific artwork, terminology, anatomical and molecular reference data, diagram notation, accessibility, publication policy and vector export. Sources were chosen for the decisions they support rather than to maximise the length of a bibliography. The resulting rules distinguish published guidance from original house defaults.

## The major design decision

Separate anatomical reconstruction from explanatory schematics. Anatomical plates need reference-supported spatial truth and expert judgment. Mechanistic diagrams need explicit abstraction and relationship semantics. A general image prompt is not a substitute for either. AMI's description of the profession supports treating scientific understanding and visual communication as linked responsibilities. [ami-profession]

The toolkit consequently supplies two routes: deterministic schematic composition using original or licensed vectors, and composition of reference-supported imported anatomical geometry. It does not claim to generate a clinically reliable body from text. A separate structure-based route is required when measured molecular geometry matters. [rcsb]

## Open artwork and geometry

| Resource | Useful role | Rights boundary | Included here? |
|---|---|---|---|
| Servier Medical Art | Professional 2D medical illustrations | CC BY 4.0 with attribution and appropriate adaptation notice | Provider route only |
| NIH BioArt Source | Professional scientific assets | Read each entry; public-domain and attribution-licensed material coexist | Provider route only |
| Bioicons | Community SVG library and editor integrations | Mixed licences; preserve asset-level creator and conditions | Provider route only |
| SciDraw | Community scientific drawing discovery | Item rights were not sufficiently verified in this review | Discovery only |
| Z-Anatomy | 3D anatomical reference/model route | Repository states CC BY-SA 4.0; review redistribution/adaptation conditions | Provider route only |
| RCSB PDB | Molecular coordinate reference | Archive coordinate data and educational artwork have different rights | Reference route only |
| RCSB Goodsell Gallery | Evidence-informed molecular illustration | Gallery states CC BY 4.0 with per-image acknowledgement | Reference route only |
| Original local collection | Schematic cells, organelles, tissue and equipment | Original art offered under CC0 to the extent rights exist | 77 vector records |

Servier is a useful acquisition route when professional 2D medical artwork is needed; attribution remains part of reuse. NIH assets require per-entry licence handling rather than a blanket government-work assumption. Bioicons' repository structure itself distinguishes licence families. Z-Anatomy can support reference-based 3D work, but a downloaded mesh still requires correct viewpoint, identity and scientific use. [servier; servier-cite; nih-bioart-faq; nih-bioart-terms; bioicons; zanatomy]

External provider files were not downloaded into this distribution. Network binary acquisition was unavailable during the build. This is why the delivered library is original schematic artwork rather than a purported local copy of thousands of outside illustrations. The generic local SVG importer is implemented; provider-specific download APIs are not.

## Proprietary atlases and commercial platforms

Netter is a craft and anatomical communication reference, not an open artwork source. BioRender is a useful schematic-composition reference, but its licences do not permit extraction of standalone icons into a competing library. A published open-access article containing a licensed figure does not automatically convert the underlying platform assets into unrestricted stock artwork. [netter-rights; biorender-rights; biorender-citation]

Other major regional, dissection and sectional atlas families can be considered during a subject-specific commission, but their inclusion in a reading list is not proof that a particular edition, plate or licence has been inspected. Do not create a false catalogue of “all atlases reviewed.” Select and verify the exact source needed for the actual region and view.

## Terminology and semantic resources

FIPAT provides anatomical terminology resources, while the TA2 viewer supplies a particular versioned terminology interface. The FIPAT portal currently lists Terminologia Anatomica Humana 2024 among its resources. Record a named terminology and edition rather than assuming every anatomy label belongs to the same version. [fipat; ta2]

Uberon supports anatomical ontology work across species. Cell Ontology supports natural cell-type identity. MeSH supports indexing and discovery. None supplies a guarantee that a drawn shape, anatomical course or label endpoint is correct. Bind verified identifiers and releases; never invent an identifier because it resembles a familiar prefix. [uberon; cl; mesh]

An anatomical relation contract should remain distinct from display geometry. A `part_of` assertion, an anterior/posterior relation and a screen position express different things. Similarly, DICOM's patient and image-coordinate definitions must not be replaced with an illustrator's intuitive left/right convention. [dicom]

## Notation and existing tools

SBGN provides distinct Process Description, Activity Flow and Entity Relationship languages, with formal specifications and supporting software. The present toolkit's visible edge grammar is declared house notation. It does not export SBGN-ML or claim conformance merely because some arrowheads are familiar. Use a formal editor and validator when that exchange requirement matters. [sbgn; sbgn-spec]

Bioicons already supports vector-editor workflows, and diagrams.net documents use of biochemical clipart. Reuse those existing capabilities where they fit the task. The new code here concentrates on the specific scene specification, traceability, asset metadata, local composition and checks rather than rebuilding a general graphics editor. [bioicons; drawio-bioicons]

CairoSVG provides optional PNG and PDF conversion. It is not an anatomical renderer. Conversion fidelity, physical size and font behaviour still require inspection in the production environment. [cairosvg]

## Publication policy findings

The reviewed Elsevier policy distinguishes explanatory diagrams, data visualisations, primary research images and graphical abstracts. It permits some AI-assisted explanatory work with oversight and disclosure, while applying different restrictions to primary imagery and graphical abstracts. In particular, its graphical-abstract guidance does not allow general-purpose AI image generators. Check the exact journal and current policy before choosing a production method. [elsevier-ai]

The full current Nature Portfolio AI policy could not be retrieved in this review. The package therefore supplies a recheck requirement rather than repeating an older policy from memory or asserting universal permission. PLOS figure guidance is included as a technical preparation reference, not a guarantee that the generic house profile meets every current journal requirement. [nature-ai; plos-figures]

No journal acceptance certification is claimed. Figure type, integrity, disclosure, source rights, physical dimensions, export format and editorial requirements all remain part of the actual submission decision.

## Textbook references and licensing caution

The explanatory tissue and vessel examples use anatomical facts as references and original drawing geometry. No textbook illustration has been copied into the library. Current OpenStax page licensing must be checked for the actual item and version; this distribution does not assume that every page or edition is uniformly CC BY 4.0. Some organelle, cell and connective-tissue records are marked as verification targets rather than completed source checks. [openstax-epithelium; openstax-vessels]

The nephron example follows an unfolded conceptual route and states its omissions. The signalling specimen does not claim to represent an experimentally established named mechanism. The distinction between original schematic geometry and copied reference artwork should remain visible in future asset acquisition. [openstax-kidney; openstax-signalling]

## What is potentially distinctive, and what is not established

The proposed integration combines a machine-readable biological scene, separate structural and visible relations, source-linked claims, named anatomical landmarks, explicit abstraction limits, local vectors, guarded imports and version-bound human review records. The package implements these components within its stated limits.

That integration is not proof of a novel market category or of superiority to existing tools. No exhaustive feature census, expert-rated visual comparison or independent clinical validation has been completed. The comparative protocol explains how to test quality fairly, including open collections paired with established editors. A defensible claim should name the task set, versions, reviewers, evaluation criteria and uncertainty rather than use an unqualified “no equal.”

## Source directory

The records below preserve status and intended application. A reviewed page supports only the stated use; it is not blanket approval of every downstream illustration.

<a id="source-ami-profession"></a>

### ami-profession: AMI: Learn About Medical Illustration

**Status:** reviewed. **Type:** professional. **Checked:** 2026-10-05.

Medical illustration combines scientific research, visual communication and subject-expert collaboration. Professional competence cannot be inferred from attractive images.

[AMI: Learn About Medical Illustration](https://ami.org/medical-illustration/learn-about-it/)

<a id="source-ami-ethics"></a>

### ami-ethics: AMI Code of Ethics

**Status:** reviewed. **Type:** professional. **Checked:** 2026-10-05.

Use honest attribution, permissions and confidential handling of entrusted material. PDF and its single page were inspected.

[AMI Code of Ethics](https://ami.org/wp-content/uploads/2025/03/AMI_Code_of_Ethics.pdf)

<a id="source-netter-rights"></a>

### netter-rights: Netter Images

**Status:** reviewed. **Type:** licensing. **Checked:** 2026-10-05.

A reference for anatomical craft and licensed illustration, not an open asset collection. No Netter artwork is included.

[Netter Images](https://www.netterimages.com/)

<a id="source-biorender-rights"></a>

### biorender-rights: BioRender academic licence

**Status:** reviewed. **Type:** licensing. **Checked:** 2026-10-05.

Do not extract icons or redistribute a competing standalone library. Check the applicable account licence for each finished figure.

[BioRender academic licence](https://www.biorender.com/academic-license)

<a id="source-biorender-citation"></a>

### biorender-citation: BioRender figure citation guidance

**Status:** reviewed. **Type:** licensing. **Checked:** 2026-10-05.

Citation and reuse conditions must be checked for the actual licensed figure; a public image is not an unrestricted asset source.

[BioRender figure citation guidance](https://help.biorender.com/hc/en-gb/articles/17605511350685-How-to-cite-your-BioRender-figure)

<a id="source-servier"></a>

### servier: Servier Medical Art

**Status:** reviewed. **Type:** asset-provider. **Checked:** 2026-10-05.

Reusable professional medical drawings under CC BY 4.0; retain attribution and identify adaptations. No provider files are bundled.

[Servier Medical Art](https://smart.servier.com/)

<a id="source-servier-cite"></a>

### servier-cite: How to cite Servier Medical Art

**Status:** reviewed. **Type:** licensing. **Checked:** 2026-10-05.

Use the attribution guidance supplied by the rights holder and preserve the Creative Commons link.

[How to cite Servier Medical Art](https://smart.servier.com/how-to-cite-servier-medical-art/)

<a id="source-nih-bioart"></a>

### nih-bioart: NIH BioArt Source

**Status:** reviewed. **Type:** asset-provider. **Checked:** 2026-10-05.

Professional scientific assets searchable by subject. Read the licence of each entry.

[NIH BioArt Source](https://bioart.niaid.nih.gov/)

<a id="source-nih-bioart-faq"></a>

### nih-bioart-faq: NIH BioArt Source FAQ

**Status:** reviewed. **Type:** licensing. **Checked:** 2026-10-05.

The collection contains public-domain and attribution-licensed material. Do not infer a blanket licence from NIH hosting.

[NIH BioArt Source FAQ](https://bioart.niaid.nih.gov/faqs)

<a id="source-nih-bioart-terms"></a>

### nih-bioart-terms: NIH BioArt Source terms

**Status:** reviewed. **Type:** licensing. **Checked:** 2026-10-05.

Users must verify fitness and comply with entry-specific attribution; provider availability is not a medical endorsement of a downstream figure.

[NIH BioArt Source terms](https://bioart.niaid.nih.gov/terms)

<a id="source-bioicons"></a>

### bioicons: Bioicons repository

**Status:** reviewed. **Type:** asset-provider. **Checked:** 2026-10-05.

Open SVG collection with separate CC0, CC BY, CC BY-SA, MIT and BSD paths. Asset-level rights differ from website code rights.

[Bioicons repository](https://github.com/duerrsimon/bioicons)

<a id="source-bioicons-web"></a>

### bioicons-web: Bioicons browser

**Status:** reviewed. **Type:** asset-provider. **Checked:** 2026-10-05.

Searchable biological icons for vector editors. Do not count a link to the collection as a bundled or tested local library.

[Bioicons browser](https://bioicons.com/)

<a id="source-drawio-bioicons"></a>

### drawio-bioicons: diagrams.net: Biochemistry clipart

**Status:** reviewed. **Type:** software. **Checked:** 2026-10-05.

An existing Bioicons route for diagrams.net. Reuse it when its connector semantics are sufficient.

[diagrams.net: Biochemistry clipart](https://www.drawio.com/docs/diagram-types/use-cases/biochem-clipart-in-diagrams/)

<a id="source-scidraw"></a>

### scidraw: SciDraw

**Status:** discovery-only. **Type:** asset-provider. **Checked:** 2026-10-05.

Candidate community resource. The dynamic site did not expose sufficient licence text in this review; verify each item before use.

[SciDraw](https://scidraw.io/)

<a id="source-zanatomy"></a>

### zanatomy: Z-Anatomy anatomical models

**Status:** reviewed. **Type:** asset-provider. **Checked:** 2026-10-05.

The repository states CC BY-SA 4.0. Useful as a 3D reference route; no model is bundled, imported or validated here.

[Z-Anatomy anatomical models](https://github.com/Z-Anatomy/Models-of-human-anatomy)

<a id="source-fipat"></a>

### fipat: FIPAT terminology portal

**Status:** reviewed. **Type:** terminology. **Checked:** 2026-10-05.

Use a named terminology and version; the portal lists Terminologia Anatomica Humana 2024 and other terminologies. A terminology label does not verify geometry.

[FIPAT terminology portal](https://ifaa.unifr.ch/)

<a id="source-ta2"></a>

### ta2: TA2 viewer

**Status:** reviewed. **Type:** terminology. **Checked:** 2026-10-05.

Versioned TA2 lookup is available. Do not silently call every terminology source the newest edition.

[TA2 viewer](https://ta2viewer.openanatomy.org/)

<a id="source-uberon"></a>

### uberon: Uberon anatomy ontology

**Status:** reviewed. **Type:** terminology. **Checked:** 2026-10-05.

Use stable, verified terms for cross-species anatomy; record the ontology release and relation type.

[Uberon anatomy ontology](https://obophenotype.github.io/uberon/)

<a id="source-cl"></a>

### cl: Cell Ontology

**Status:** reviewed. **Type:** terminology. **Checked:** 2026-10-05.

Use verified natural cell-type identifiers with a pinned release; do not invent identifiers from labels.

[Cell Ontology](https://obophenotype.github.io/cell-ontology/)

<a id="source-mesh"></a>

### mesh: NLM MeSH

**Status:** reviewed. **Type:** terminology. **Checked:** 2026-10-05.

MeSH supports discovery and indexing, not spatial reconstruction or geometric validation.

[NLM MeSH](https://www.nlm.nih.gov/mesh/meshhome.html)

<a id="source-sbgn"></a>

### sbgn: Systems Biology Graphical Notation

**Status:** reviewed. **Type:** notation. **Checked:** 2026-10-05.

Process Description, Activity Flow and Entity Relationship have different semantics. This toolkit uses a declared house notation, not an SBGN certification.

[Systems Biology Graphical Notation](https://sbgn.github.io/)

<a id="source-sbgn-spec"></a>

### sbgn-spec: SBGN specifications

**Status:** reviewed. **Type:** notation. **Checked:** 2026-10-05.

Formal SBGN delivery requires the appropriate specification and a separate conformance check, not only familiar-looking arrows.

[SBGN specifications](https://sbgn.github.io/specifications)

<a id="source-dicom"></a>

### dicom: DICOM patient image coordinate definitions

**Status:** reviewed. **Type:** standard. **Checked:** 2026-10-05.

Do not confuse patient coordinates, image orientation and display convention. Preserve the coordinate frame and laterality.

[DICOM patient image coordinate definitions](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.2.html)

<a id="source-wai-complex"></a>

### wai-complex: W3C WAI: Complex images

**Status:** reviewed. **Type:** accessibility. **Checked:** 2026-10-05.

Provide a concise text alternative and the necessary extended explanation for complex scientific figures.

[W3C WAI: Complex images](https://www.w3.org/WAI/tutorials/images/complex/)

<a id="source-wai-colour"></a>

### wai-colour: WCAG: Use of Color

**Status:** reviewed. **Type:** accessibility. **Checked:** 2026-10-05.

Do not encode distinctions exclusively through colour. Pair semantic colours with text, shape, line type or pattern.

[WCAG: Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)

<a id="source-figure-design"></a>

### figure-design: Rougier et al. Ten Simple Rules for Better Figures

**Status:** reviewed. **Type:** research. **Checked:** 2026-10-05.

Make composition depend on the intended message, audience and medium. Numerical toolkit defaults are house rules, not claims of a universal journal standard.

[Rougier et al. Ten Simple Rules for Better Figures](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003833)

<a id="source-plos-figures"></a>

### plos-figures: PLOS ONE figure preparation guidance

**Status:** reviewed. **Type:** publication. **Checked:** 2026-10-05.

Check current final figure format and resolution requirements for the target journal. The generic toolkit profile is not a journal acceptance guarantee.

[PLOS ONE figure preparation guidance](https://journals.plos.org/plosone/s/figures)

<a id="source-elsevier-ai"></a>

### elsevier-ai: Elsevier generative AI policies for journals

**Status:** reviewed. **Type:** publication. **Checked:** 2026-10-05.

AI-assisted explanatory diagrams require oversight/disclosure. Primary research images and graphical abstracts have different restrictions; journal rules must be checked.

[Elsevier generative AI policies for journals](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals)

<a id="source-nature-ai"></a>

### nature-ai: Nature Portfolio AI policy

**Status:** retrieval-incomplete. **Type:** publication. **Checked:** 2026-10-05.

Full policy could not be retrieved in this review. Read the current official policy for the target journal; no pre-approved export profile is supplied.

[Nature Portfolio AI policy](https://www.nature.com/nature-portfolio/editorial-policies/ai)

<a id="source-openstax-epithelium"></a>

### openstax-epithelium: OpenStax A&P 2e, 4.2 Epithelial Tissue

**Status:** reviewed. **Type:** anatomy-reference. **Checked:** 2026-10-05.

Reference for polarity and epithelial organisation. Original geometry is not copied from its figures; verify current item/version rights before reusing textbook content.

[OpenStax A&P 2e, 4.2 Epithelial Tissue](https://openstax.org/books/anatomy-and-physiology-2e/pages/4-2-epithelial-tissue)

<a id="source-openstax-vessels"></a>

### openstax-vessels: OpenStax A&P 2e, 20.1 Blood Vessel Structure

**Status:** reviewed. **Type:** anatomy-reference. **Checked:** 2026-10-05.

Reference for schematic vessel-wall organisation. Illustrated layer widths are not measurements.

[OpenStax A&P 2e, 20.1 Blood Vessel Structure](https://openstax.org/books/anatomy-and-physiology-2e/pages/20-1-structure-and-function-of-blood-vessels)

<a id="source-openstax-kidney"></a>

### openstax-kidney: OpenStax A&P 2e, Chapter 25 review / microscopic anatomy

**Status:** reviewed. **Type:** anatomy-reference. **Checked:** 2026-10-05.

Reference for nephron segment continuity and distinction between the nephron and its collecting system. No copied textbook illustration is included.

[OpenStax A&P 2e, Chapter 25 review / microscopic anatomy](https://openstax.org/books/anatomy-and-physiology-2e/pages/25-chapter-review)

<a id="source-openstax-signalling"></a>

### openstax-signalling: OpenStax Biology 2e, Signalling Molecules and Receptors

**Status:** reviewed. **Type:** biology-reference. **Checked:** 2026-10-05.

Reference for explanatory ligand/receptor categories. The specimen is an invented abstract example, not a named experimentally established pathway.

[OpenStax Biology 2e, Signalling Molecules and Receptors](https://openstax.org/books/biology-2e/pages/9-1-signaling-molecules-and-cellular-receptors)

<a id="source-openstax-organelles"></a>

### openstax-organelles: OpenStax A&P 2e, 3.2 Cytoplasm and Organelles

**Status:** verification-target. **Type:** biology-reference. **Checked:** 2026-10-05.

Recommended verification target for generic organelle symbols; detailed asset-level review has not been performed.

[OpenStax A&P 2e, 3.2 Cytoplasm and Organelles](https://openstax.org/books/anatomy-and-physiology-2e/pages/3-2-the-cytoplasm-and-cellular-organelles)

<a id="source-openstax-connective"></a>

### openstax-connective: OpenStax A&P 2e, 4.3 Connective Tissue

**Status:** verification-target. **Type:** anatomy-reference. **Checked:** 2026-10-05.

Recommended verification target for connective-tissue cell and matrix symbols.

[OpenStax A&P 2e, 4.3 Connective Tissue](https://openstax.org/books/anatomy-and-physiology-2e/pages/4-3-connective-tissue-supports-and-protects)

<a id="source-openstax-blood"></a>

### openstax-blood: OpenStax A&P 2e, Chapter 18 Blood

**Status:** verification-target. **Type:** anatomy-reference. **Checked:** 2026-10-05.

Recommended verification target for blood-cell symbols; they are not cytology evidence or diagnostic classifiers.

[OpenStax A&P 2e, Chapter 18 Blood](https://openstax.org/books/anatomy-and-physiology-2e/pages/18-introduction)

<a id="source-openstax-immune"></a>

### openstax-immune: OpenStax A&P 2e, Chapter 21 Immunity

**Status:** verification-target. **Type:** biology-reference. **Checked:** 2026-10-05.

Recommended verification target for generic immune-cell and antibody symbols.

[OpenStax A&P 2e, Chapter 21 Immunity](https://openstax.org/books/anatomy-and-physiology-2e/pages/21-introduction)

<a id="source-rcsb"></a>

### rcsb: RCSB PDB usage policies

**Status:** reviewed. **Type:** structure-data. **Checked:** 2026-10-05.

Distinguish CC0 archive coordinate data from attribution-licensed educational images. Record structure ID, method, source paper and the rendering decisions.

[RCSB PDB usage policies](https://www.rcsb.org/pages/policies)

<a id="source-cairosvg"></a>

### cairosvg: CairoSVG documentation

**Status:** reviewed. **Type:** software. **Checked:** 2026-10-05.

CairoSVG handles the optional SVG-to-PNG/PDF export. Unsafe XML processing is never enabled.

[CairoSVG documentation](https://cairosvg.org/documentation/)

<a id="source-house-design"></a>

### house-design: Medical Illustration Studio original design rules

**Status:** reviewed. **Type:** original-design. **Checked:** 2026-10-05.

Original procedural schematic geometry and house defaults. This is not independent biological evidence.

Provenance identifier: `urn:medical-illustration-studio:house-design:1`.

<a id="source-goodsell"></a>

### goodsell: RCSB PDB-101 Goodsell Gallery

**Status:** reviewed. **Type:** scientific-art. **Checked:** 2026-10-05.

Molecular landscapes combine structural, microscopy and biophysical information with explicit omissions. The gallery states CC BY 4.0 with per-illustration acknowledgement. No artwork is bundled.

[RCSB PDB-101 Goodsell Gallery](https://pdb101.rcsb.org/sci-art/goodsell-gallery)

