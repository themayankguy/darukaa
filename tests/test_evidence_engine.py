"""Tests for the scientific evidence engine and anti-hallucination guardrails.

Verifies:
- Test 6: Numerical guardrail (unsupported numerical claims rejected)
- Evidence grounding of candidate recommendations
- Insufficient evidence handling
"""

import pytest
from src.knowledge.retriever import ScientificRetriever, RetrievedEvidenceChunk
from src.knowledge.evidence_engine import EvidenceEngine
from src.reasoning.models import CandidateRecommendation, TriggeredRelationship


@pytest.fixture
def evidence_engine():
    retriever = ScientificRetriever()
    return EvidenceEngine(retriever=retriever)


def test_numerical_guardrail_rejection(evidence_engine):
    """Test 6: Attempt to assert a numerical claim not supported by retrieved evidence."""
    # Create fake chunks with no numbers
    chunks = [
        RetrievedEvidenceChunk(
            chunk_id="chunk_1",
            source_id="test_source",
            source_title="Qualitative Study",
            source_organization="Test Org",
            publication_year=2021,
            source_type="report",
            source_url_or_doi="https://doi.org/test",
            topic="test",
            section_header="Intro",
            excerpt="Cover crops improve soil aggregation and stimulate microbial biomass.",
            similarity_score=0.8,
            distance=0.2,
            is_quantitative=False,
        )
    ]

    # Claim asserting +45% increase when text only has qualitative improvements
    hallucinated_claim = "Cover cropping increases soil organic carbon by +45% in one year."
    assert evidence_engine.verify_no_hallucinated_number(hallucinated_claim, chunks) is False

    # Pure qualitative claim passes
    valid_qualitative_claim = "Cover cropping improves soil aggregation and stimulates microbial biomass."
    assert evidence_engine.verify_no_hallucinated_number(valid_qualitative_claim, chunks) is True


def test_verified_numerical_claim_accepted(evidence_engine):
    """When a number is actually in the source chunk, it is preserved."""
    chunks = [
        RetrievedEvidenceChunk(
            chunk_id="fao_rec_soils_2020_chunk_2",
            source_id="fao_rec_soils_2020",
            source_title="Recarbonizing Global Soils",
            source_organization="FAO",
            publication_year=2020,
            source_type="technical_report",
            source_url_or_doi="https://doi.org/10.4060/ca9673en",
            topic="soil_organic_carbon",
            section_header="Legumes",
            excerpt="Legume cover cropping in semi-arid wheat systems increases soil organic carbon by ~15–25% over 2–3 years.",
            similarity_score=0.9,
            distance=0.1,
            is_quantitative=True,
        )
    ]

    valid_claim = "Legume cover cropping increases soil organic carbon by ~15–25% over 2–3 years."
    assert evidence_engine.verify_no_hallucinated_number(valid_claim, chunks) is True


def test_evaluate_candidate_grounding(evidence_engine):
    """Verifies that candidates are properly mapped to retrieved scientific chunks."""
    candidate = CandidateRecommendation(
        intervention_id="INT_LEGUME_INTERCROPPING",
        action="Drought-Tolerant Legume-Cereal Intercropping",
        description="Cultivating alternating rows of legumes with wheat",
        triggering_relationships=["REL_SEMIARID_SOC_MONOCULTURE"],
        variables_addressed=["soil_organic_carbon_pct", "cropping_pattern"],
        impacted_metrics=["METRIC_SOIL_ORGANIC_CARBON", "METRIC_SPECIES_RICHNESS"],
        time_horizon="Short-term (<1 yr) to Medium-term (1-3 yrs)",
        tradeoffs=["Seed procurement costs"],
        required_evidence_topics=["legume intercropping", "soil organic carbon"],
    )
    relationship = TriggeredRelationship(
        relationship_id="REL_SEMIARID_SOC_MONOCULTURE",
        name="Low soil carbon under water-limited monoculture",
        variables_involved=["soil_organic_carbon_pct", "rainfall_regime", "cropping_pattern"],
        conditions_detected=["low_soil_organic_carbon", "low_rainfall", "monoculture"],
        mechanism="Low soil organic carbon impairs macro-aggregates while low rainfall exacerbates moisture deficits.",
        affected_metrics=["METRIC_SOIL_ORGANIC_CARBON"],
        candidate_interventions=["INT_LEGUME_INTERCROPPING"],
        evidence_topics=["legume intercropping"],
        priority="HIGH",
    )

    result = evidence_engine.evaluate_candidates([candidate], [relationship])
    assert result.is_evidence_sufficient is True
    assert len(result.validated_recommendations) == 1
    rec = result.validated_recommendations[0]
    assert rec.is_supported is True
    assert rec.confidence in ["High", "Medium"]
    assert len(rec.evidence) >= 1
    assert "FAO" in rec.why_it_works or "Food and Agriculture Organization" in rec.why_it_works or len(rec.evidence[0].source_organization) > 0
