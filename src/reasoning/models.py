"""Models for deterministic multi-metric ecological reasoning and candidate recommendations."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.input_layer.schemas import EnvironmentalState
from src.reasoning.condition_detector import ConditionDetectionResult


class TriggeredRelationship(BaseModel):
    """Represents an activated cross-variable ecological relationship rule."""
    relationship_id: str = Field(..., description="Unique rule identifier (e.g., REL_SEMIARID_SOC_MONOCULTURE).")
    name: str = Field(..., description="Descriptive ecological title.")
    variables_involved: List[str] = Field(..., description="Participating environmental variables (>= 3).")
    conditions_detected: List[str] = Field(..., description="Conditions that satisfied the rule.")
    mechanism: str = Field(..., description="Cross-variable ecological mechanism explaining the interaction.")
    affected_metrics: List[str] = Field(..., description="Specific metrics degraded by this interaction.")
    candidate_interventions: List[str] = Field(..., description="IDs of candidate interventions addressing this.")
    evidence_topics: List[str] = Field(..., description="Search topics to ground this interaction.")
    priority: str = Field("MEDIUM", description="Severity level: CRITICAL, HIGH, MEDIUM, LOW.")


class CandidateRecommendation(BaseModel):
    """Deterministic intermediate candidate recommendation object before evidence grounding."""
    intervention_id: str = Field(..., description="Unique intervention identifier.")
    action: str = Field(..., description="Name and direct operational practice.")
    description: str = Field(..., description="Technical agronomic description.")
    triggering_relationships: List[str] = Field(..., description="IDs of relationships that selected this practice.")
    variables_addressed: List[str] = Field(..., description="Input variables directly improved or targeted.")
    impacted_metrics: List[str] = Field(..., description="Environmental metrics targeted for improvement.")
    time_horizon: str = Field(..., description="Categorized time horizon (Short, Medium, Long term).")
    tradeoffs: List[str] = Field(default_factory=list, description="Agronomic constraints or operational trade-offs.")
    required_evidence_topics: List[str] = Field(default_factory=list, description="Literature topics required for verification.")


class MultiMetricReasoningResult(BaseModel):
    """Complete output of the deterministic multi-metric reasoning engine."""
    environmental_state: EnvironmentalState
    condition_detection: ConditionDetectionResult
    is_sufficient_for_assessment: bool = Field(
        ...,
        description="True if >= 3 environmental variables are supplied, enabling full cross-variable co-reasoning."
    )
    available_variables: List[str] = Field(default_factory=list, description="Variables supplied in state.")
    missing_variables: List[str] = Field(default_factory=list, description="Key environmental variables still needed.")
    participating_variable_count: int = Field(0, description="Total count of variables participating in diagnosis.")
    triggered_relationships: List[TriggeredRelationship] = Field(default_factory=list)
    candidate_recommendations: List[CandidateRecommendation] = Field(default_factory=list)
