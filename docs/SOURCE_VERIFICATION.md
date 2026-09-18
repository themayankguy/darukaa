# Stage 5.1 Independent Scientific Source Verification

**Verification date:** 2026-09-18

## Final Status

`REQUIRES_EXTERNAL_VERIFICATION`

Internet access was available and official publisher/assessment pages were checked. This verified some publication metadata and directly contradicted or failed to establish several local bibliographic and quantitative claims. The local markdown files are curated summaries, not original extracted publication text. PDFs for the FAO sources and IPBES chapter were reachable or linked but were not text-extractable through the available page-fetch tool, and the Kuyper publisher page was blocked. No claim is marked independently verified unless the original publication itself was checked.

## A. Source Inventory

| Intended source | Local source ID | Original publication metadata found | Official URL/DOI | Local correspondence | Verification |
|---|---|---|---|---|---|
| FAO Recarbonizing Global Soils | `fao_rec_soils_2020` | Local title: “Recarbonizing Global Soils: A Technical Manual of Recommended Management Practices (Volume 3: Cropland, Grassland, Integrated Systems and Orchards)”; FAO; 2020. The official FAO PDF URL is reachable by redirect, but the DOI/record could not be independently resolved through the available metadata service. | `https://openknowledge.fao.org/3/ca9673en/ca9673en.pdf` | Three short manually curated paragraphs. Not original extracted text; no page, table, or passage identifiers. | `REQUIRES_EXTERNAL_VERIFICATION` |
| IPCC Special Report on Climate Change and Land, Chapter 3 | `ipcc_srccl_ch3_2019` | “Desertification.” Chapter 3 of the IPCC Special Report on Climate Change and Land; IPCC; 2019. Official chapter page and downloadable chapter were checked. | `https://www.ipcc.ch/srccl/chapter/chapter-3/` and `https://www.ipcc.ch/site/assets/uploads/sites/4/2022/11/SRCCL_Chapter_3.pdf` | Three short curated paragraphs. The local text is not the chapter text. The official chapter supports qualitative integrated crop-soil-water management and conservation agriculture, but not the local 30–50% wind and 2–6°C figures. | `PARTIALLY_VERIFIED` |
| IPBES Pollinators, Pollination and Food Production | `ipbes_pollination_2016` | “The assessment report of the Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services on pollinators, pollination and food production.” Editors Simon G. Potts, Vera L. Imperatriz-Fonseca, Hien T. Ngo; IPBES; 2016; 552 pages. | Correct official DOI: `https://doi.org/10.5281/zenodo.3402856`; official page: `https://www.ipbes.net/assessment-reports/pollinators` | Three curated paragraphs. Not original extracted text. The prior local DOI `10.5281/zenodo.3404766` was wrong and was corrected. | `PARTIALLY_VERIFIED` for identity; quantitative claim requires external verification |
| Kuyper et al. agroforestry meta-analysis | `kuyper_agroforestry_2020` | The local title is “Agroforestry Enhances Soil Biodiversity and Microbial Biomass in Degraded Arable Landscapes: A Global Meta-Analysis,” attributed to Kuyper et al. The supplied DOI `10.1016/j.agee.2020.106880` was checked through Crossref and resolves to a different article: “How mowing restores montane Mediterranean grasslands following cessation of traditional livestock grazing,” by Tardella et al., *Agriculture, Ecosystems & Environment* 295 (2020), article 106880. | Incorrect local DOI: `10.1016/j.agee.2020.106880`. No verified DOI or official URL for the local Kuyper title was established. | Two curated paragraphs. No original article, complete author list, journal record, or page/passage identifiers. | `REQUIRES_EXTERNAL_VERIFICATION`; incorrect DOI removed from authoritative interpretation |
| FAO Save and Grow | `fao_ca_principles_2016` | Local title: “Save and Grow in Practice: Maize, Rice, Wheat — A Guide to Sustainable Cereal Production”; FAO; 2016. The local DOI `10.4060/i5384e` does not resolve through Crossref, and the FAO handle for `i5384e` currently identifies an unrelated 2021 “Nutritional benefits of pulses” item. | Candidate official URL: `https://openknowledge.fao.org/3/i5384e/i5384e.pdf`, but identity was not independently established. | Three curated paragraphs. Not original extracted text. | `REQUIRES_EXTERNAL_VERIFICATION`; local DOI/identity is not defensible as supplied |

### Source-fidelity conclusion

All five local files are manually curated or generated knowledge-base syntheses. They are not demonstrated verbatim extracts from the cited publications. The system must describe them as “local knowledge-base synthesis based on” a source, not “according to the original publication,” unless original text and passage-level provenance are indexed.

## B. Quantitative Claim Verification

A claim is “directly supported” here only when the original publication was checked and explicitly supports the same number, metric, population, intervention, and context. A matching sentence in the local markdown is not independent verification.

| Claim | Local source/chunk | Original source | Directly supported? | Context matches? | Keep/Remove |
|---|---|---|---|---|---|
| SOC improves approximately 15–25% over 2–3 years | `fao_rec_soils_2020_chunk_2` | FAO Recarbonizing Global Soils, official PDF linked above; original text was not extractable/checked | No determination | No determination | **Remove numeric claim.** Local text downgraded to qualitative SOC support. |
| Residue cover of at least 30% reduces evaporation 20–35% | `fao_rec_soils_2020_chunk_3` | FAO Recarbonizing Global Soils | No determination | No determination | **Remove numeric claim.** Qualitative residue/moisture mechanism retained. |
| Break crop rotation increases grain yields 10–20% | `fao_ca_principles_2016_chunk_1` | FAO Save and Grow; supplied local identifier is not independently matched to the official publication | No | No | **Remove numeric claim.** Qualitative rotation/yield direction retained. |
| Native flowering margins increase wild bee species richness 50–100% within 1–2 years | `ipbes_pollination_2016_chunk_2` | IPBES Pollinators Assessment, official assessment page and chapter links checked; exact original passage was not checked | No determination | No determination | **Remove numeric claim and duration.** Qualitative habitat/species-richness support retained. |
| Bare-soil surface temperatures frequently exceed 45°C | `ipcc_srccl_ch3_2019_chunk_1` | Official IPCC Chapter 3 checked | No exact support established for this local passage/context | No | **Remove numeric threshold from corpus evidence.** Qualitative heat/moisture mechanism retained. |
| Agroforestry reduces wind speed 30–50% and surface temperature 2–6°C | `ipcc_srccl_ch3_2019_chunk_2` | Official IPCC Chapter 3 checked | No. Official chapter discusses integrated management and other quantified findings, but this exact local figure was not found in the checked chapter content. | No | **Remove numbers.** Qualitative microclimate and moisture wording retained. |
| Agroforestry increases microbial biomass carbon 35–45%; 126 field studies | `kuyper_agroforestry_2020_chunk_1` | Claimed Kuyper meta-analysis; supplied DOI resolves to an unrelated mowing article | No | No | **Remove numeric claim and study count.** Qualitative statement marked as requiring verification. |
| `SOC < 1.0%` low; `SOC >= 2.0%` adequate | `src/reasoning/thresholds.py` and former FAO local text | No source-specific original verification established for these universal classifications | No | Not applicable | **Keep only as product classification policy**, never as a publication-derived claim. |
| Annual rainfall `<500 mm` low and `>1200 mm` high | `src/reasoning/thresholds.py` | IPCC official chapter uses aridity-index concepts and location-specific precipitation, not these universal application cutoffs | No | Not applicable | **Keep only as product classification policy**, clearly labeled engineering policy. |
| Temperature `>35°C` high thermal stress | `src/reasoning/thresholds.py` | No original source identified for this universal threshold | No | Not applicable | **Keep only as product classification policy**, not scientific effect evidence. |
| Intervention time horizons such as `<1 yr`, `1–3 yrs`, `>3 yrs` | `knowledge_base/interventions.json` | No source passage supplies these durations for the recommendations as implemented | No | Not applicable | **Keep as product policy labels only.** They must not be presented as predicted ecological response times. |

### Quantitative claims found in original material but not used by this product

The official IPCC Chapter 3 page includes other numbers, including dryland carbon sequestration rates and study-specific management results. Those figures are not evidence for this product’s exact candidate/context pairs and were not imported. No replacement estimate was invented.

### Result

No user-facing quantitative ecological effect size is independently verified for the current recommendation corpus. The production corpus now contains qualitative wording for the previously numeric passages, and Chroma was rebuilt after those edits.

## C. Intervention Evidence Matrix

“Direct intervention support” means an intervention ID appears in local metadata. It does **not** mean the original publication has independently verified the exact intervention claim.

| Intervention | Evidence exists in current corpus? | Relevant local source(s) | Direct intervention support? | Safe for production? |
|---|---|---|---|---|
| `INT_LEGUME_INTERCROPPING` | Yes | FAO Recarbonizing; Kuyper local synthesis | Yes | **Qualitative only; numeric effects unavailable** |
| `INT_ALLEY_CROPPING_AGROFORESTRY` | Yes | IPCC local synthesis; Kuyper local synthesis | Yes | **Qualitative only; source fidelity requires verification** |
| `INT_COVER_CROPPING_RESIDUE` | Yes | FAO Recarbonizing; IPCC local synthesis | Yes | **Qualitative only; numeric effects removed** |
| `INT_CONSERVATION_TILLAGE` | Yes | FAO Save and Grow local synthesis | Yes | **Qualitative only; FAO identity requires verification** |
| `INT_POLLINATOR_HEDGEROWS` | Yes | IPBES local synthesis | Yes | **Qualitative only; exact effect and duration removed** |
| `INT_HABITAT_CORRIDORS` | Yes | IPCC local synthesis | Yes | **Qualitative only; original passage provenance absent** |
| `INT_RIPARIAN_BUFFER_STRIPS` | Yes | FAO Save and Grow and IPBES metadata | Yes in metadata, but no direct local passage specifically describing the intervention | **Insufficient evidence for evidence-backed production recommendation** |
| `INT_CROP_ROTATION_DIVERSIFICATION` | Yes | FAO Save and Grow and IPBES metadata | Yes in metadata; local FAO passage is qualitative after correction | **Qualitative only; source identity requires verification** |
| `INT_BIOSWALES_WATER_HARVESTING` | Yes | FAO Save and Grow metadata | Yes in metadata, but the local passage is general hydrology rather than direct bioswale evidence | **Insufficient evidence for evidence-backed production recommendation** |
| `INT_INTEGRATED_PEST_NUTRIENT_MGMT` | Yes | IPBES local synthesis | Yes | **Qualitative only; exact effectiveness evidence requires original chapter verification** |

The current metadata filter prevents unrelated chunks from validating a candidate, but metadata tagging itself is not independent scientific verification. The two interventions marked insufficient should remain excluded whenever no directly relevant passage survives retrieval.

## D. Provenance Audit

Current retrieved evidence preserves:

- `source_id`
- title
- organization/authors
- publication year
- source type
- `original_url_or_doi`
- topic
- variables supported
- interventions supported
- provenance note
- section header
- local chunk ID and excerpt

Remaining gaps:

- The local corpus has no original publication files, hashes, page numbers, table/figure IDs, or extraction manifest.
- FAO source identifiers/DOIs are not independently resolved; the Save and Grow identifier currently resolves to an unrelated FAO item.
- The IPBES DOI was corrected to the official assessment DOI, but chapter-level page provenance is absent.
- The Kuyper DOI was proven incorrect and replaced with an explicit verification-required marker; no replacement DOI was invented.
- The local author strings for IPCC, IPBES, and Kuyper are abbreviated or incomplete.
- A `source_url_or_doi` field remains structurally present, but its presence does not guarantee that it identifies the local text’s actual source.

## E. Claims Removed or Downgraded

Removed from indexed production evidence:

- `15–25% SOC over 2–3 years`
- `20–35% evaporation reduction with 30% residue cover`
- `10–20% subsequent grain-yield increase`
- `50–100% wild bee species-richness increase within 1–2 years`
- `30–50% wind-speed reduction`
- `2–6°C surface-temperature reduction`
- `35–45% microbial biomass-carbon increase`
- the Kuyper “126 comparative field studies” count
- the local `>45°C` surface-temperature statement

Downgraded to qualitative wording:

- Soil carbon and microbial/aggregate benefits of legumes, cover crops, and residue retention.
- Habitat and wild-pollinator support from flowering margins.
- Microclimate, moisture-retention, and connectivity mechanisms associated with agroforestry.
- Rotation and conservation-tillage mechanisms.

The IPBES DOI was corrected. No unsupported replacement numbers were added. ChromaDB was re-ingested after the edits.

## F. Remaining Scientific Limitations

- The knowledge base is still a curated synthesis and not a source-faithful original-publication index.
- Exact numerical effect sizes, study populations, intervention definitions, and response durations require original-PDF or publisher-text review.
- The application’s thresholds and time horizons are engineering/product policy; they are not literature-derived predictions.
- Intervention metadata can establish routing relevance but cannot prove the underlying publication claim.
- The current tests verify retrieval and anti-hallucination mechanics, not bibliographic truth or original-source fidelity.
- The local corpus should not be described as “according to the original publication.”

## G. Tests

Command requested: `python -m pytest -q`  
Environment command used: `python3 -m pytest -q`

- Passed: **31**
- Failed: **0**
- Skipped: **0**

The existing tests were not modified.

## Final Proceed Decision

The deterministic guardrail is suitable for adversarial testing of unsupported evidence and numerical hallucination behavior. The system is **not safe for scientific deployment**, and it is not safe to claim independently verified quantitative recommendations. Proceed only with adversarial testing that treats source identity, provenance, intervention tagging, and qualitative-only output as explicit limitations.
