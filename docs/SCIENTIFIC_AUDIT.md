# Darukaa.Earth Scientific Corpus and Evidence Audit

**Audit date:** 2026-09-18  
**Scope:** local corpus, ingestion, ChromaDB, retrieval, evidence validation, deterministic reasoning, LLM boundary, and backend tests.

## Executive Finding

The intended five sources are represented locally as four markdown files plus a fifth file whose title is the intended FAO Save and Grow source. The corpus contains 14 indexed chunks and complete field-level provenance in the chunk and retrieved-evidence models. It is not a local copy of the original reports: the markdown files describe themselves as curated or extracted syntheses, and no source PDFs or extraction manifests were found. Therefore, the local text can support only the claims written in those passages; it does not independently establish that the passages faithfully reproduce the cited publications.

Before this audit, semantic similarity alone could validate an intervention even when the chunk was not tagged for that intervention. A generic mechanism fallback could also produce scientific prose without a relationship mechanism. Those paths were corrected. Unsupported evidence now yields no validated recommendation and the API reports `status="insufficient_evidence"`.

**Deployment verdict:** not ready for scientific deployment.  
**Adversarial-testing verdict:** ready for adversarial testing of the guarded pipeline, with the corpus-fidelity and source-verification limitations below treated as expected attack surfaces.

## 1. Actual Local Corpus

`knowledge_base/documents/` does not exist. The ingest script reads only `knowledge_base/corpus/*.md`. Each markdown file has YAML frontmatter and local extracted body text. The current Chroma collection is `biodiversity_knowledge` at `data/chroma_db`, with 14 records, one per chunk.

| Intended source | Source ID | Exact local title | Organization/authors | Year | DOI or URL | Type | Topics | Variables supported | Interventions supported | Text present | Chunks | Provenance |
|---|---|---|---|---:|---|---|---|---|---|---|---:|---|
| FAO Recarbonizing Global Soils | `fao_rec_soils_2020` | Recarbonizing Global Soils: A Technical Manual of Recommended Management Practices (Volume 3: Cropland, Grassland, Integrated Systems and Orchards) | Food and Agriculture Organization of the United Nations (FAO) | 2020 | `https://doi.org/10.4060/ca9673en` | Institutional technical report | Soil organic carbon and dryland management | SOC, soil moisture, agricultural pressure, cropping pattern | Legume intercropping, cover cropping/residue, conservation tillage | Yes | 3 | Complete required fields; curated synthesis, not original-report extraction proof |
| IPCC SRCCL Chapter 3 | `ipcc_srccl_ch3_2019` | IPCC Special Report on Climate Change and Land (SRCCL): Chapter 3 — Desertification & Land Degradation | IPCC (Mirzabaev, Wu, Evans, et al.) | 2019 | `https://doi.org/10.1017/9781009157988.005` | Intergovernmental assessment report | Dryland degradation, agroforestry, microclimate | Rainfall, temperature, SOC, deforestation | Alley-cropping agroforestry, habitat corridors, cover cropping/residue | Yes | 3 | URL and fields present; author list is abbreviated |
| IPBES Pollinators | `ipbes_pollination_2016` | The Assessment Report of the Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services on Pollinators, Pollination and Food Production | IPBES (Potts, Imperatriz-Fonseca, et al.) | 2016 | `https://doi.org/10.5281/zenodo.3404766` | Intergovernmental assessment report | Pollinator forage, hedgerows, pesticide impact | Biodiversity indicators, habitat diversity, species richness, pollution pressure | Pollinator hedgerows, integrated pest/nutrient management, crop rotation | Yes | 3 | URL and fields present; author list is abbreviated |
| Kuyper et al. agroforestry meta-analysis | `kuyper_agroforestry_2020` | Agroforestry Enhances Soil Biodiversity and Microbial Biomass in Degraded Arable Landscapes: A Global Meta-Analysis | Kuyper, T.W., et al.; journal text names Agriculture, Ecosystems & Environment / Journal of Applied Ecology | 2020 | `https://doi.org/10.1016/j.agee.2020.106880` | Peer-reviewed journal meta-analysis | Agroforestry, soil microbiology, biodiversity | SOC, habitat diversity, species richness, cropping pattern | Alley-cropping agroforestry, legume intercropping | Yes | 2 | URL and fields present, but author/journal attribution is not complete |
| FAO Save and Grow | `fao_ca_principles_2016` | Save and Grow in Practice: Maize, Rice, Wheat — A Guide to Sustainable Cereal Production | Food and Agriculture Organization of the United Nations (FAO) | 2016 | `https://doi.org/10.4060/i5384e` | Institutional technical guideline | Cereal diversification, waterlogging, conservation agriculture | Cropping pattern, agricultural pressure, water availability, rainfall | Crop rotation, conservation tillage, bioswales/water harvesting, riparian buffers | Yes | 3 | Complete required fields; filename is `fao_conservation_agriculture_2016.md`, not a literal `save_and_grow` filename |

### Corpus integrity observations

- All five intended source titles are represented in the local frontmatter; the fifth is the FAO file named `fao_conservation_agriculture_2016.md`.
- The chunker preserves `source_id`, title, organization, year, URL/DOI, topic, variables, interventions, provenance note, section, and quantitative flag.
- Chroma metadata contains all evidence fields except `chunk_id`; the Chroma record ID itself is the chunk ID.
- The local body text is present for every indexed source. The files are short curated syntheses: 14 chunks total, with no local original document archive, page numbers, table identifiers, or extraction manifest.
- `provenance_note` is present but does not identify exact pages or passages in the cited originals. Source fidelity remains unverified.

## 2. Quantitative Claim Audit

The chunker detected five quantitative corpus chunks. The following claims are distinct quantitative statements found in the local corpus or production rules. Documentation examples and test fixtures are listed separately from production output.

| Claim | Location and exact local support | Source/context support | Time horizon | Generalization risk | Audit result |
|---|---|---|---|---|---|
| SOC increases approximately 15–25% over 2–3 years | `knowledge_base/corpus/fao_recarbonization_soils_2020.md`, chunk `fao_rec_soils_2020_chunk_2`: “legume cover cropping and residue retention in semi-arid wheat systems increase soil organic carbon by ~15–25% over 2–3 years under conservation management” | Directly present in local text; attributed only to “Studies synthesize,” with no study list or page | Directly stated locally as 2–3 years | Applies specifically to semi-arid wheat systems under conservation management, not all soils, crops, climates, or legume practices | **Conditionally supported locally; not independently source-verifiable** |
| Wild bee richness increases 50–100% within 1–2 years | `ipbes_pollination_2016_chunk_2`: “native flowering margins increase wild bee species richness by 50–100% within 1–2 years” | Directly present in local text; field population, sites, design, and study citation are absent | Directly stated locally as 1–2 years | Wild bee species richness is not pollinator abundance, total biodiversity, or every landscape | **Conditionally supported locally; not independently source-verifiable** |
| Residue cover of at least 30% reduces evaporation losses by 20–35% | `fao_rec_soils_2020_chunk_3` | Directly present in local text; comparison and study details are absent | No duration stated | Dryland clean-tilled comparison cannot be generalized to all soils or seasons | **Conditionally supported locally** |
| Break crop rotation increases subsequent grain yields by 10–20% | `fao_conservation_agriculture_2016.md`, chunk `fao_ca_principles_2016_chunk_1` | Directly present in local text | Three-year rotational cycle is stated; effect timing is not otherwise specified | Yield effect is not an SOC or biodiversity effect and should not be presented as one | **Supported only for the stated local context** |
| Tree canopies reduce wind speed by 30–50% and surface temperature by 2–6°C | `ipcc_srccl_land_degradation_2019.md`, chunk `ipcc_srccl_ch3_2019_chunk_2` | Directly present in local text | No duration stated | Applies to the described agroforestry microclimate context, not all tree systems | **Conditionally supported locally** |
| Agroforestry increases soil microbial biomass carbon by 35–45% | `kuyper_agroforestry_biodiversity_2020.md`, chunk `kuyper_agroforestry_2020_chunk_1`; passage says 126 comparative field studies | Directly present in local text | No duration stated | Meta-analysis population and moderator/context details are absent from local extraction | **Conditionally supported locally; citation details incomplete** |
| `SOC < 1.0%`, `SOC >= 2.0%`, rainfall `<500 mm`, rainfall `>1200 mm`, temperature `>35°C` | `src/reasoning/thresholds.py` | These are deterministic classification thresholds, not retrieved effect estimates; only the `<1.0%` SOC statement is also present in the FAO local passage | Not applicable | They are applied as universal operational rules without source-specific calibration | **Operational assumptions, not scientific effect claims; must not be presented as literature estimates** |
| Surface temperature `>50°C` in degraded bare soil | `knowledge_base/relationships.json`, `REL_THERMAL_DEGRADED_SOIL` | No matching `>50°C` local passage; IPCC local text says surface temperatures “frequently exceed 45°C” | No duration stated | Unsupported exact threshold | **UNSUPPORTED; removed from generated mechanism prose and replaced with qualitative wording** |
| Pollinator abundance `+40%` | `docs/REQUIREMENTS.md` benchmark example | No local passage supports 40% pollinator abundance. The local IPBES number is 50–100% wild bee species richness, a different metric | Not supported | Metric and context mismatch | **UNSUPPORTED; documentation example changed to qualitative wording** |

### Claim propagation

- The SOC 15–25% and bee richness 50–100% examples also appeared in `docs/ARCHITECTURE.md`, `docs/MVP_SCOPE.md`, and test fixtures. The tests use synthetic/fake chunks to exercise the guardrail; they are not evidence that the external claims are true.
- Recommendation time horizons in `knowledge_base/interventions.json` such as “Short-term (<1 yr) to Medium-term (1-3 yrs)” are intervention metadata, not source-supported effect estimates. They remain visible as operational planning labels and must not be interpreted as guaranteed ecological response times.
- The production evidence engine now returns a quantitative estimate only when a matching numeric passage is present in a chunk explicitly tagged for the candidate intervention and the sentence contains intervention-relevant terms. It does not invent replacement numbers.
- If the user asks “How much will this improve biodiversity?” and no relevant tagged passage contains a supported numeric estimate, `quantitative_estimate` is null. The system has no LLM path that generates a substitute number.

## 3. EvidenceItem Provenance Audit

`RetrievedEvidenceChunk` contains:

- `chunk_id` (the Chroma record ID)
- `source_id`
- `source_title`
- `source_organization`
- `publication_year`
- `source_type`
- `source_url_or_doi`
- `topic`
- `variables_supported`
- `interventions_supported`
- `provenance_note`
- section header and excerpt
- similarity score, distance, and quantitative flag

The ingestion metadata builder writes all of these fields except `chunk_id`, which is retained as the Chroma ID and reconstructed by retrieval. The Pydantic evidence model therefore has enough fields to trace an item to a local source and chunk. No page-level citation, source-file hash, original-document location, or extraction version is available. Kuyper’s author/journal metadata and the abbreviated author lists for IPCC/IPBES are incomplete. Provenance is therefore **field-complete for the current local contract, but not publication-complete**.

## 4. Retrieval Audit

Current flow:

1. `knowledge_base/ingestion/ingest_corpus.py` reads markdown files from `knowledge_base/corpus/`.
2. `chunker.py` parses frontmatter, creates paragraph chunks, and writes provenance into Chroma metadata.
3. `ScientificRetriever` opens the persistent local Chroma client at `data/chroma_db`, queries the `biodiversity_knowledge` collection, converts cosine distance to a displayed similarity score, and reconstructs provenance.
4. Retrieval supports configurable `top_k` and an optional topic filter.
5. Candidate evaluation queries using the deterministic candidate action plus required evidence topics.
6. Candidate evidence is filtered by exact `intervention_id` membership in `interventions_supported`.

Before correction, the evidence engine accepted `(similarity >= 0.35) OR intervention metadata`, so an unrelated but semantically similar source could validate a candidate. The retriever also ignored its `intervention_id` argument. The correction retrieves a wider ranked window, filters by explicit intervention metadata, and returns at most `top_k`; no universal cosine threshold is required for acceptance. Similarity still determines confidence ordering, but it no longer establishes scientific relevance by itself.

## 5. Evidence Guardrail Trace

The deterministic path is:

`EnvironmentalState` -> `ConditionDetector` -> `MultiMetricReasoningEngine` relationship rules -> candidate intervention IDs -> Chroma retrieval -> exact intervention metadata filter -> evidence validation -> `RecommendationResponseItem`.

Guardrail findings:

- Condition detection and relationship matching are deterministic.
- Candidate interventions come from `knowledge_base/relationships.json` and `knowledge_base/interventions.json`, not the LLM.
- A candidate is validated only when at least one retrieved chunk explicitly lists its intervention ID and a relationship supplies its mechanism.
- A generic fallback mechanism was removed. Missing deterministic mechanism evidence now makes the candidate unsupported.
- Unsupported candidates are recorded in `unsupported_candidates` and are excluded from recommendations.
- When no candidate survives, the orchestrator returns `status="insufficient_evidence"`, an empty recommendation list, and an explicit limitation rather than presenting a citation-backed recommendation.
- Evidence excerpts and provenance are passed directly into the response; the LLM is not used to fabricate citations or evidence.

## 6. Numerical Hallucination Protection

`EvidenceEngine._extract_verified_quantitative_claim` scans retrieved excerpts for percentages, temperature values, and year/month durations. It returns a sentence only when the numeric text occurs in the excerpt, the chunk is explicitly tagged for the candidate, and the sentence includes both an effect term and intervention-specific terms. `verify_no_hallucinated_number` rejects detected numeric expressions absent from the evidence excerpts.

The existing tests cover an unsupported `+45%` claim and a locally present `~15–25% over 2–3 years` claim. The full suite passes. Residual limitation: the detector is a lexical guardrail, not a statistical or causal interpretation system. It cannot prove that a source’s number is valid beyond the local text, and raw unlabelled counts are not treated as effect estimates.

## 7. LLM Boundary Audit

- `src/input_layer/extractor.py` performs deterministic regex/pattern extraction and does not ask the LLM to supply missing measurements.
- `ClarificationEngine` may use an injected LLM only to rephrase a deterministic clarification question. Its system instruction prohibits answering the query.
- `MultiMetricReasoningEngine` is deterministic and loads candidate interventions and relationships from JSON.
- `EvidenceEngine` is deterministic and does not call an LLM.
- `GeminiClient` and `MockLLMClient` implement text generation only. The mock’s synthesis response is generic and is not used to create recommendations, numbers, citations, or evidence in the current orchestration path.
- `ChatOrchestrator` stores an LLM reference but recommendation assembly is deterministic; there is no final LLM synthesis call in the audited path.

The boundary therefore passes for the current implementation. The API should continue treating any future prose-synthesis LLM as presentation-only and never as an authority for relationships, interventions, evidence, citations, or estimates.

## 8. Tests

Command: `python3 -m pytest -q`

- Total: **31**
- Passed: **31**
- Failed: **0**
- Skipped: **0**
- Relevant scientific/evidence tests: `tests/test_evidence_engine.py` and `tests/test_knowledge_rag.py`; both pass.
- Additional coverage includes condition detection, deterministic multi-metric reasoning, relationship rules, conversation flow, API endpoints, and intervention loading.

The suite does not yet test the new explicit `insufficient_evidence` response status, an unrelated high-similarity chunk being rejected, or source-fidelity against original publications. Those remain adversarial test targets; tests were not changed to manufacture a pass.

## 9. Corrections Made During Audit

- `src/knowledge/retriever.py`: honored intervention-specific filtering by retrieving a wider ranked window and retaining only chunks whose metadata explicitly lists the candidate intervention.
- `src/knowledge/evidence_engine.py`: removed similarity-only acceptance and the generic mechanism fallback; restricted numeric extraction to intervention-relevant sentences; expanded numeric detection to percentages, temperatures, and durations.
- `src/conversation/orchestrator.py`: returns `insufficient_evidence` with an explicit limitation when no recommendation is validated.
- `knowledge_base/relationships.json`: removed the unsupported `>50°C` figure from `REL_THERMAL_DEGRADED_SOIL` without inventing a replacement number.
- `docs/REQUIREMENTS.md`: removed the unsupported `+40% pollinator abundance` benchmark and replaced it with qualitative evidence-bounded wording.

No datasets, models, external LLM APIs, or architecture components were added. Tests were not modified.

## 10. Audit Table

| Check | Status | Evidence | Required action |
|---|---|---|---|
| Local corpus exists | PASS | Five intended source titles are represented in `knowledge_base/corpus/`; 14 local chunks are indexed in Chroma. | Preserve the corpus manifest and add original-document/page traceability before deployment. |
| DOI/URL metadata | PASS | Every local frontmatter record has `original_url_or_doi`; retrieved evidence preserves it. | Complete author, journal, page, and extraction metadata. |
| Quantitative claims | FAIL | Several figures are present only in curated local syntheses; `>50°C` and `+40% pollinator abundance` were unsupported. | Independently verify every effect size or keep it qualitative; do not generalize local contexts. |
| Retrieval provenance | PASS | Chroma metadata and `RetrievedEvidenceChunk` preserve source and chunk provenance. | Add immutable document/version identifiers for production auditability. |
| Evidence relevance | PASS | Candidate acceptance now requires exact intervention metadata, not similarity alone. | Add adversarial tests for near-match and cross-intervention retrieval. |
| Numerical guardrail | PASS | Numeric output is excerpt-grounded, intervention-filtered, and absent when unsupported; tests pass. | Add tests for `°C`, durations, and metric/context mismatch. |
| LLM boundary | PASS | LLM use is limited to optional clarification wording; reasoning and evidence are deterministic. | Keep future synthesis calls presentation-only. |
| Tests | PASS | 31 passed, 0 failed, 0 skipped. | Add tests for the newly corrected insufficient-evidence and filtering paths. |

## Stage 5.1 Verification Addendum

The independent source-verification pass is documented in [docs/SOURCE_VERIFICATION.md](SOURCE_VERIFICATION.md) and is currently `REQUIRES_EXTERNAL_VERIFICATION`. The quantitative effect sizes previously present in the curated corpus were removed or downgraded to qualitative wording, the IPBES DOI was corrected, the incorrect Kuyper DOI was marked for verification, and the Chroma collection was re-ingested. The current corpus must not be treated as original publication text.
