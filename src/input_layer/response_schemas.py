"""Response schemas for the Darukaa.Earth API and Conversational Interface."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from src.input_layer.schemas import EnvironmentalState
from src.knowledge.retriever import RetrievedEvidenceChunk


class RecommendationResponseItem(BaseModel):
    """Evidence-backed recommendation item."""
    action: str
    why_it_works: str
    impacted_metrics: List[str]
    time_horizon: str
    confidence: str
    evidence: List[RetrievedEvidenceChunk]
    quantitative_estimate: Optional[str] = None
    limitations: List[str] = Field(default_factory=list)


class ReasoningTraceResponse(BaseModel):
    """Transparent audit trace of the system's reasoning pipeline."""
    input_factors: List[str]
    detected_conditions: List[str]
    cross_variable_relationships: List[str]
    candidate_interventions: List[str]
    retrieved_evidence: List[RetrievedEvidenceChunk]
    validated_claims: List[str]
    decision_rationale: str


class ChatRequest(BaseModel):
    """Request payload for /api/v1/chat endpoint."""
    session_id: Optional[str] = None
    message: str


class SystemResponse(BaseModel):
    """Unified response schema supporting both complete assessments and targeted clarifications."""
    status: str = Field(..., description="'complete' or 'needs_clarification'")
    session_id: str
    environmental_state: Dict[str, Any]
    clarification_required: bool = False

    # Populated when status == 'needs_clarification'
    missing_information: Optional[List[str]] = None
    clarification_question: Optional[str] = None

    # Populated when status == 'complete'
    detected_conditions: Optional[List[str]] = None
    relationships: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[RecommendationResponseItem]] = None
    reasoning_trace: Optional[ReasoningTraceResponse] = None
    limitations: Optional[List[str]] = None
