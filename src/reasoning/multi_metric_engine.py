"""Deterministic Multi-Metric Ecological Reasoning Engine.

Executes the pipeline:
Environmental State
-> Condition Detection
-> Relationship Matching (>= 3 variables)
-> Cross-Variable Mechanism
-> Candidate Intervention Selection

Operates strictly deterministically with zero LLM dependence.
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

from src.input_layer.schemas import EnvironmentalState
from src.reasoning.condition_detector import ConditionDetector, ConditionDetectionResult
from src.reasoning.models import (
    TriggeredRelationship,
    CandidateRecommendation,
    MultiMetricReasoningResult,
)

# Essential environmental domains for completeness evaluation
CORE_VARIABLE_DOMAINS = {
    "soil_organic_carbon_pct": "Soil Organic Carbon (Soil Health)",
    "soil_moisture": "Soil Moisture (Soil Health)",
    "soil_ph": "Soil pH (Soil Health)",
    "rainfall_regime": "Rainfall Pattern / Precipitation (Climate)",
    "temperature_regime": "Temperature Regime (Climate)",
    "cropping_pattern": "Cropping Pattern / Crop Rotation (Land Use)",
    "land_use_type": "Land Use Classification (Land Use)",
    "habitat_diversity": "Habitat Heterogeneity / Corridors (Biodiversity)",
    "species_richness": "Species Richness / Wildlife Abundance (Biodiversity)",
    "biodiversity_condition": "Overall Biodiversity Condition (Biodiversity)",
    "pollution_pressure": "Chemical / Fertilizer / Pesticide Load (Human Impact)",
    "agricultural_pressure": "Tillage / Soil Disruption Intensity (Human Impact)",
    "deforestation_status": "Woodland Canopy & Clearing Status (Human Impact)",
}


class MultiMetricReasoningEngine:
    """Deterministic ecological co-reasoning engine."""

    def __init__(
        self,
        relationships_path: Optional[Path] = None,
        interventions_path: Optional[Path] = None,
        condition_detector: Optional[ConditionDetector] = None,
    ):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.relationships_path = relationships_path or (base_dir / "knowledge_base" / "relationships.json")
        self.interventions_path = interventions_path or (base_dir / "knowledge_base" / "interventions.json")
        self.detector = condition_detector or ConditionDetector()

        self._relationships: List[Dict[str, Any]] = self._load_json(self.relationships_path)
        self._interventions_map: Dict[str, Dict[str, Any]] = {
            item["intervention_id"]: item for item in self._load_json(self.interventions_path)
        }

    def _load_json(self, path: Path) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate(self, state: EnvironmentalState) -> MultiMetricReasoningResult:
        """Evaluates an environmental state through deterministic multi-variable coupling."""
        # 1. Condition Detection
        condition_res = self.detector.detect(state)
        supplied_vars = state.get_supplied_variables()
        var_count = len(supplied_vars)
        available_var_names = list(supplied_vars.keys())

        # 2. Minimum Multi-Variable Completeness Gate (>= 3 variables)
        if var_count < 3:
            missing = [
                desc for var_key, desc in CORE_VARIABLE_DOMAINS.items()
                if var_key not in supplied_vars
            ][:4]  # Suggest top 4 missing relevant variables
            return MultiMetricReasoningResult(
                environmental_state=state,
                condition_detection=condition_res,
                is_sufficient_for_assessment=False,
                available_variables=available_var_names,
                missing_variables=missing,
                participating_variable_count=var_count,
                triggered_relationships=[],
                candidate_recommendations=[],
            )

        # 3. Relationship Rule Matching
        detected_condition_set = set(condition_res.derived_conditions)
        triggered_relationships: List[TriggeredRelationship] = []
        triggered_intervention_ids: Dict[str, List[str]] = {}  # int_id -> [rel_id, ...]

        for rule in self._relationships:
            req_conds = set(rule["required_conditions"])
            # All conditions for this relationship rule must be satisfied
            if req_conds.issubset(detected_condition_set):
                # Ensure rule identifies participating environmental variables
                env_vars = rule.get("environmental_variables", [])
                
                triggered_rel = TriggeredRelationship(
                    relationship_id=rule["relationship_id"],
                    name=rule["name"],
                    variables_involved=env_vars,
                    conditions_detected=sorted(list(req_conds)),
                    mechanism=rule["mechanism"],
                    affected_metrics=rule.get("affected_metrics", []),
                    candidate_interventions=rule.get("candidate_interventions", []),
                    evidence_topics=rule.get("evidence_topics", []),
                    priority=rule.get("priority", "MEDIUM"),
                )
                triggered_relationships.append(triggered_rel)

                for int_id in rule.get("candidate_interventions", []):
                    if int_id not in triggered_intervention_ids:
                        triggered_intervention_ids[int_id] = []
                    triggered_intervention_ids[int_id].append(rule["relationship_id"])

        # 4. Candidate Intervention Selection
        candidate_recommendations: List[CandidateRecommendation] = []
        for int_id, rel_ids in triggered_intervention_ids.items():
            if int_id in self._interventions_map:
                int_def = self._interventions_map[int_id]
                # Collect variables addressed that are actually in the user state
                addressed = [
                    v for v in int_def.get("target_variables", [])
                    if v in supplied_vars
                ]
                if not addressed:
                    addressed = int_def.get("target_variables", [])

                candidate = CandidateRecommendation(
                    intervention_id=int_id,
                    action=int_def["name"],
                    description=int_def["description"],
                    triggering_relationships=rel_ids,
                    variables_addressed=addressed,
                    impacted_metrics=int_def.get("impacted_metrics", []),
                    time_horizon=int_def.get("time_horizon", "Medium-term (1-3 yrs)"),
                    tradeoffs=int_def.get("potential_tradeoffs", []),
                    required_evidence_topics=int_def.get("evidence_topics", []),
                )
                candidate_recommendations.append(candidate)

        return MultiMetricReasoningResult(
            environmental_state=state,
            condition_detection=condition_res,
            is_sufficient_for_assessment=True,
            available_variables=available_var_names,
            missing_variables=[],
            participating_variable_count=var_count,
            triggered_relationships=triggered_relationships,
            candidate_recommendations=candidate_recommendations,
        )
