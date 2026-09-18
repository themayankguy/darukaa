"""Evidence Engine with strict source grounding and anti-hallucination guardrails.

Answers: 'Does the retrieved scientific evidence actually support this candidate intervention/claim?'
- Matches candidate interventions against retrieved passages
- Preserves complete bibliographic provenance
- Distinguishes qualitative mechanisms from quantitative figures
- Strictly suppresses unbacked numerical claims
- Identifies and reports insufficient evidence states
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field

from src.reasoning.models import CandidateRecommendation, TriggeredRelationship
from src.knowledge.retriever import ScientificRetriever, RetrievedEvidenceChunk


class ValidatedRecommendation(BaseModel):
    """Evidence-grounded recommendation contract matching challenge requirements."""
    intervention_id: str
    action: str
    why_it_works: str = Field(..., description="Biological/physical mechanism grounded in scientific literature.")
    impacted_metrics: List[str] = Field(..., description="Metrics directly improved by practice.")
    time_horizon: str
    confidence: str = Field(..., description="'High', 'Medium', or 'Low' based on evidence relevance.")
    evidence: List[RetrievedEvidenceChunk] = Field(..., description="Attached scientific evidence with provenance.")
    quantitative_estimate: Optional[str] = Field(
        None,
        description="Explicit quantitative projection ONLY if verified in retrieved text; otherwise null."
    )
    limitations: List[str] = Field(default_factory=list, description="Agronomic constraints or operational trade-offs.")
    is_supported: bool = True
    grounding_notes: str = ""


class EvidenceEvaluationResult(BaseModel):
    """Aggregate result of evidence grounding across all candidate recommendations."""
    is_evidence_sufficient: bool = True
    validated_recommendations: List[ValidatedRecommendation] = Field(default_factory=list)
    unsupported_candidates: List[str] = Field(default_factory=list)
    retrieved_evidence_pool: List[RetrievedEvidenceChunk] = Field(default_factory=list)
    evidence_notes: str = ""


class EvidenceEngine:
    """Deterministic scientific evidence validator and grounding engine."""

    def __init__(
        self,
        retriever: ScientificRetriever,
        min_relevance_score: float = 0.35,
    ):
        self.retriever = retriever
        self.min_relevance_score = min_relevance_score
        # Regex to detect percentages and numeric ranges in candidate claims
        self.num_pattern = re.compile(
            r"(?<!\w)\d+(?:\.\d+)?\s*(?:[-–]\s*\d+(?:\.\d+)?\s*)?(?:%|°C|years?|months?)"
        )

    def evaluate_candidates(
        self,
        candidates: List[CandidateRecommendation],
        relationships: List[TriggeredRelationship],
    ) -> EvidenceEvaluationResult:
        """Grounds candidate interventions against the scientific corpus.
        Rejects unsupported interventions and suppresses fabricated numbers.
        """
        validated_recs: List[ValidatedRecommendation] = []
        unsupported: List[str] = []
        all_retrieved: List[RetrievedEvidenceChunk] = []

        # Map relationship mechanisms by candidate
        mechanism_by_int: Dict[str, str] = {}
        for rel in relationships:
            for int_id in rel.candidate_interventions:
                if int_id not in mechanism_by_int:
                    mechanism_by_int[int_id] = rel.mechanism

        for candidate in candidates:
            # Formulate multi-topic query for this candidate
            query_parts = [candidate.action]
            if candidate.required_evidence_topics:
                query_parts.extend(candidate.required_evidence_topics[:2])
            query = " ".join(query_parts)

            # Retrieve evidence
            chunks = self.retriever.retrieve(query=query, top_k=3)
            all_retrieved.extend(chunks)

            relevant_chunks = [
                c for c in chunks
                if candidate.intervention_id in c.interventions_supported
            ]

            if not relevant_chunks or candidate.intervention_id not in mechanism_by_int:
                unsupported.append(candidate.action)
                continue

            # Check for quantitative claims in retrieved evidence
            quantitative_projection = self._extract_verified_quantitative_claim(
                relevant_chunks, candidate.intervention_id
            )

            # Determine confidence level based on top similarity and direct intervention tagging
            top_chunk = relevant_chunks[0]
            is_directly_tagged = candidate.intervention_id in top_chunk.interventions_supported
            if top_chunk.similarity_score >= 0.60 or is_directly_tagged:
                confidence = "High"
            elif top_chunk.similarity_score >= 0.45:
                confidence = "Medium"
            else:
                confidence = "Low"

            # Derive mechanistic explanation
            mech_rationale = mechanism_by_int[candidate.intervention_id]
            why_it_works = f"{mech_rationale} Supported by findings in {top_chunk.source_organization} ({top_chunk.publication_year})."

            validated = ValidatedRecommendation(
                intervention_id=candidate.intervention_id,
                action=candidate.action,
                why_it_works=why_it_works,
                impacted_metrics=candidate.impacted_metrics,
                time_horizon=candidate.time_horizon,
                confidence=confidence,
                evidence=relevant_chunks,
                quantitative_estimate=quantitative_projection,
                limitations=candidate.tradeoffs,
                is_supported=True,
                grounding_notes=f"Grounded via {len(relevant_chunks)} peer/institutional passages."
            )
            validated_recs.append(validated)

        validated_recs = self._select_strongest_recommendations(
            validated_recs,
            candidates,
        )
        is_sufficient = len(validated_recs) > 0
        notes = (
            f"Successfully grounded {len(validated_recs)} interventions in peer-reviewed scientific literature."
            if is_sufficient
            else "Insufficient relevant scientific evidence found in current corpus to ground recommendations."
        )

        return EvidenceEvaluationResult(
            is_evidence_sufficient=is_sufficient,
            validated_recommendations=validated_recs,
            unsupported_candidates=unsupported,
            retrieved_evidence_pool=all_retrieved,
            evidence_notes=notes,
        )

    def _select_strongest_recommendations(
        self,
        validated_recommendations: List[ValidatedRecommendation],
        candidates: List[CandidateRecommendation],
        limit: int = 3,
    ) -> List[ValidatedRecommendation]:
        """Selects the strongest already-validated recommendations deterministically."""
        candidate_by_id = {candidate.intervention_id: candidate for candidate in candidates}
        confidence_rank = {"High": 3, "Medium": 2, "Low": 1}

        def ranking_key(recommendation: ValidatedRecommendation) -> tuple:
            candidate = candidate_by_id[recommendation.intervention_id]
            return (
                confidence_rank.get(recommendation.confidence, 0),
                len(recommendation.evidence),
                len(candidate.variables_addressed),
                len(recommendation.impacted_metrics),
                len(candidate.triggering_relationships),
                recommendation.intervention_id,
            )

        return sorted(validated_recommendations, key=ranking_key, reverse=True)[:limit]

    def _extract_verified_quantitative_claim(
        self,
        chunks: List[RetrievedEvidenceChunk],
        intervention_id: str,
    ) -> Optional[str]:
        """Extracts numerical estimates ONLY if explicitly present in retrieved text.
        Guarantees zero invented numerical figures.
        """
        intervention_terms = {
            "INT_LEGUME_INTERCROPPING": ["legume", "intercropping", "cover cropping"],
            "INT_ALLEY_CROPPING_AGROFORESTRY": ["agroforestry", "woody", "tree", "canopy"],
            "INT_COVER_CROPPING_RESIDUE": ["cover", "residue", "surface", "evaporation"],
            "INT_CONSERVATION_TILLAGE": ["tillage", "tilled", "plowing", "drilling", "disturbance"],
            "INT_POLLINATOR_HEDGEROWS": ["hedgerow", "margin", "pollinator", "bee"],
            "INT_CROP_ROTATION_DIVERSIFICATION": ["rotation", "rotational", "break crop", "monoculture"],
            "INT_HABITAT_CORRIDORS": ["corridor", "connectivity", "habitat", "vegetation"],
            "INT_RIPARIAN_BUFFER_STRIPS": ["buffer", "riparian", "runoff", "waterway"],
        }.get(intervention_id, [])

        for chunk in chunks:
            # Look for verified percentage ranges in the chunk text
            matches = self.num_pattern.findall(chunk.excerpt)
            if matches:
                # Check for explicit sentences in chunk with metrics
                for sentence in chunk.excerpt.split("."):
                    for m in matches:
                        match_str = m[0] if isinstance(m, tuple) else m
                        if match_str in sentence:
                            # Verify relevance to this intervention topic
                            sentence_lower = sentence.lower()
                            if (
                                any(term in sentence_lower for term in ["increase", "improve", "reduce", "yield", "carbon", "soc"])
                                and any(term in sentence_lower for term in intervention_terms)
                            ):
                                return sentence.strip()
        return None

    def verify_no_hallucinated_number(self, proposed_claim: str, evidence_chunks: List[RetrievedEvidenceChunk]) -> bool:
        """Audits an arbitrary text claim to ensure all numerical percentages appear in evidence.
        Returns True if all numbers in claim are present in source text, False otherwise.
        """
        matches = self.num_pattern.findall(proposed_claim)
        if not matches:
            return True  # Pure qualitative claim passes

        combined_evidence = " ".join(c.excerpt for c in evidence_chunks)
        for m in matches:
            num_str = m[0] if isinstance(m, tuple) else m
            if num_str not in combined_evidence:
                return False  # Number was hallucinated!
        return True
