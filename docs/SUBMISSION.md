# Darukaa AI Environmental Scientist

## Project
Darukaa combines structured environmental state, deterministic multi-metric reasoning, local scientific retrieval, evidence validation, and auditable recommendations.

## GitHub Repository
Not available in the current workspace: no Git repository or remote URL is configured.

## Live Demo
Not deployed.

## Architecture
See [docs/ARCHITECTURE.md](ARCHITECTURE.md).

User input -> environmental state -> clarification -> condition detection -> multi-metric reasoning -> candidate intervention -> scientific retrieval -> evidence validation -> recommendation.

## Requirements Traceability
See [docs/TRACEABILITY_MATRIX.md](TRACEABILITY_MATRIX.md).

## Scientific Audit
See [docs/SCIENTIFIC_AUDIT.md](SCIENTIFIC_AUDIT.md).

## Source Verification
See [docs/SOURCE_VERIFICATION.md](SOURCE_VERIFICATION.md). Final status: `REQUIRES_EXTERNAL_VERIFICATION`.

## Testing

- Backend: `python3 -m pytest -q`
- Result: **31 passed, 0 failed, 0 skipped**
- Frontend: `cd frontend && npm run build`
- Result: **PASS**

## Demo Scenario

Wheat farmland in a semi-arid region with SOC 0.3%, low rainfall, monoculture wheat, and low habitat diversity.

Smoke validation passed for incomplete input, multi-turn memory, the primary demo, unsupported numbers, and unsupported evidence. The primary demo returns 3 evidence-backed recommendations.

## Known Limitations

- The local corpus is curated synthesis, not demonstrated verbatim original-publication text.
- Independent verification of all source identities and quantitative claims is incomplete.
- Quantitative effect sizes were removed from production corpus evidence unless independently verified.
- Product thresholds and intervention time horizons are engineering policy labels, not universal scientific predictions.
- No live deployment URL is available.
- This workspace has no configured Git repository or GitHub remote.
