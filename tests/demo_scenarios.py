"""Demonstration evaluation script showcasing 5 real-world multi-metric environmental scenarios.

Prints the complete pipeline execution trace:
ENVIRONMENTAL STATE
↓
DETECTED CONDITIONS
↓
CROSS-VARIABLE RELATIONSHIPS
↓
CANDIDATE INTERVENTIONS
↓
REQUIRED EVIDENCE TOPICS
↓
RETRIEVED SCIENTIFIC SOURCES
↓
EVIDENCE STATUS
"""

import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from src.input_layer.schemas import EnvironmentalState
from src.reasoning.condition_detector import ConditionDetector
from src.reasoning.multi_metric_engine import MultiMetricReasoningEngine
from src.knowledge.retriever import ScientificRetriever
from src.knowledge.evidence_engine import EvidenceEngine


def run_scenario(scenario_num: int, title: str, state: EnvironmentalState):
    print("=" * 80)
    print(f"SCENARIO {scenario_num}: {title.upper()}")
    print("=" * 80)

    # 1. Environmental State
    print("\n[1] ENVIRONMENTAL STATE")
    for k, v in state.get_supplied_variables().items():
        print(f"  • {k}: {v}")
    print(f"  (Total active variables: {state.count_distinct_variables()} across {state.count_distinct_domains()} domains)")

    # 2. Detected Conditions
    detector = ConditionDetector()
    cond_res = detector.detect(state)
    print("\n      ↓")
    print("\n[2] DETECTED CONDITIONS")
    for cond in cond_res.derived_conditions:
        print(f"  • [Derived Condition] {cond}")
    for d in cond_res.derivations:
        print(f"      ↳ {d.rationale}")

    # 3. Cross-Variable Relationships
    engine = MultiMetricReasoningEngine(condition_detector=detector)
    reasoning_res = engine.evaluate(state)
    print("\n      ↓")
    print("\n[3] CROSS-VARIABLE RELATIONSHIPS")
    if not reasoning_res.is_sufficient_for_assessment:
        print("  [Notice] Insufficient variables (< 3). Multi-metric reasoning gated.")
        print(f"  Missing factors: {reasoning_res.missing_variables}")
        return

    for rel in reasoning_res.triggered_relationships:
        print(f"  • {rel.relationship_id}: {rel.name} (Priority: {rel.priority})")
        print(f"    Variables Coupled ({len(rel.variables_involved)}): {', '.join(rel.variables_involved)}")
        print(f"    Mechanistic Interaction: {rel.mechanism}")

    # 4. Candidate Interventions
    print("\n      ↓")
    print("\n[4] CANDIDATE INTERVENTIONS")
    for cand in reasoning_res.candidate_recommendations:
        print(f"  • [{cand.intervention_id}] {cand.action}")
        print(f"    Impacted Metrics: {', '.join(cand.impacted_metrics)}")
        print(f"    Time Horizon: {cand.time_horizon}")
        print(f"    Trade-offs: {'; '.join(cand.tradeoffs)}")

    # 5. Required Evidence Topics
    print("\n      ↓")
    print("\n[5] REQUIRED EVIDENCE TOPICS")
    all_topics = set()
    for cand in reasoning_res.candidate_recommendations:
        all_topics.update(cand.required_evidence_topics)
    for topic in sorted(list(all_topics)):
        print(f"  • Topic: '{topic}'")

    # 6. Retrieved Scientific Sources & Grounding
    retriever = ScientificRetriever()
    evidence_engine = EvidenceEngine(retriever=retriever)
    evidence_res = evidence_engine.evaluate_candidates(
        reasoning_res.candidate_recommendations,
        reasoning_res.triggered_relationships
    )

    print("\n      ↓")
    print("\n[6] RETRIEVED SCIENTIFIC SOURCES")
    seen_sources = set()
    for rec in evidence_res.validated_recommendations:
        for chunk in rec.evidence:
            src_key = (chunk.source_id, chunk.source_title)
            if src_key not in seen_sources:
                seen_sources.add(src_key)
                print(f"  • Source ID: {chunk.source_id}")
                print(f"    Title: {chunk.source_title}")
                print(f"    Organization: {chunk.source_organization} ({chunk.publication_year})")
                print(f"    DOI / URL: {chunk.source_url_or_doi}")
                print(f"    Topic Tag: {chunk.topic}")
                print(f"    Similarity: {chunk.similarity_score:.3f}")
                print(f"    Provenance Note: {chunk.provenance_note}")

    # 7. Evidence Status & Recommendation Synthesis
    print("\n      ↓")
    print("\n[7] EVIDENCE STATUS")
    print(f"  • Grounding Status: {'SUFFICIENT & GROUNDED' if evidence_res.is_evidence_sufficient else 'INSUFFICIENT EVIDENCE'}")
    print(f"  • Notes: {evidence_res.evidence_notes}")
    print("\n  [Validated Recommendations]:")
    for rec in evidence_res.validated_recommendations:
        print(f"    ✓ {rec.action} (Confidence: {rec.confidence})")
        print(f"      Why it Works: {rec.why_it_works}")
        if rec.quantitative_estimate:
            print(f"      Quantitative Benchmark: \"{rec.quantitative_estimate}\"")
        else:
            print(f"      Quantitative Benchmark: [Qualitative Ecological Mechanism Grounded in Literature]")
    print("\n" + "=" * 80 + "\n")


def main():
    # Scenario 1: Semi-Arid Monoculture Grain Farm
    s1 = EnvironmentalState(
        soil_organic_carbon_pct=0.3,
        rainfall_regime="low",
        cropping_pattern="monoculture wheat",
        land_use_type="cropland",
        region="semi-arid drylands"
    )
    run_scenario(1, "Semi-Arid Monoculture Cropland with Depleted Carbon", s1)

    # Scenario 2: Compounded Heat and Moisture Stress
    s2 = EnvironmentalState(
        soil_moisture="dry",
        rainfall_regime="low",
        temperature_regime="high_temperature",
        temperature_celsius=38.5,
        agricultural_pressure="intensive_tillage"
    )
    run_scenario(2, "Severe Heat Stress and Extreme Moisture Deficit under Tillage", s2)

    # Scenario 3: Agricultural Landscape Biodiversity Collapse
    s3 = EnvironmentalState(
        cropping_pattern="monoculture",
        habitat_diversity="low",
        species_richness="low",
        land_use_type="cropland",
        biodiversity_indicators=["low_pollinators", "few_earthworms"]
    )
    run_scenario(3, "Agricultural Biodiversity Crash and Pollinator Deficit", s3)

    # Scenario 4: Deforestation and Ecological Corridor Fragmentation
    s4 = EnvironmentalState(
        deforestation_status="cleared_woodland",
        habitat_diversity="low",
        species_richness="low",
        land_use_type="agricultural_land"
    )
    run_scenario(4, "Forest Clearing and Habitat Fragmentation", s4)

    # Scenario 5: Chemical Runoff and Ecotoxic Pressure in Intensive Cropland
    s5 = EnvironmentalState(
        pollution_pressure="pesticides and synthetic nitrogen runoff",
        land_use_type="cropland",
        biodiversity_condition="declining",
        water_availability="waterlogged"
    )
    run_scenario(5, "Pesticide Ecotoxicity and Waterlogging Saturation", s5)


if __name__ == "__main__":
    main()
