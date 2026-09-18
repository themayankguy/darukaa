"""Central Chat and Assessment Orchestrator.

Coordinates input parsing, session persistence, profile memory, completeness checking,
deterministic reasoning, scientific evidence retrieval, and structured response synthesis.
"""

import uuid
import datetime
from typing import Optional, Dict, Any, List

from src.input_layer.schemas import EnvironmentalState
from src.input_layer.response_schemas import (
    SystemResponse,
    RecommendationResponseItem,
    ReasoningTraceResponse,
)
from src.input_layer.extractor import EnvironmentalExtractor
from src.conversation.models import ConversationTurn, SessionProfile
from src.conversation.session_manager import SessionManager
from src.conversation.clarification import ClarificationEngine
from src.reasoning.multi_metric_engine import MultiMetricReasoningEngine
from src.knowledge.retriever import ScientificRetriever
from src.knowledge.evidence_engine import EvidenceEngine
from src.core.llm_interface import LLMClient


class ChatOrchestrator:
    """End-to-end conversational and assessment pipeline orchestrator."""

    def __init__(
        self,
        session_manager: Optional[SessionManager] = None,
        extractor: Optional[EnvironmentalExtractor] = None,
        clarification_engine: Optional[ClarificationEngine] = None,
        reasoning_engine: Optional[MultiMetricReasoningEngine] = None,
        retriever: Optional[ScientificRetriever] = None,
        evidence_engine: Optional[EvidenceEngine] = None,
        llm_client: Optional[LLMClient] = None,
    ):
        self.session_manager = session_manager or SessionManager()
        self.extractor = extractor or EnvironmentalExtractor(llm_client=llm_client)
        self.clarification_engine = clarification_engine or ClarificationEngine(llm_client=llm_client)
        self.reasoning_engine = reasoning_engine or MultiMetricReasoningEngine()
        self.retriever = retriever or ScientificRetriever()
        self.evidence_engine = evidence_engine or EvidenceEngine(retriever=self.retriever)
        self.llm = llm_client

    def process_chat(self, message: str, session_id: Optional[str] = None) -> SystemResponse:
        """Processes natural language chat input."""
        sid = session_id or str(uuid.uuid4())
        
        # 1. Parse natural language into EnvironmentalState
        extracted_state = self.extractor.extract(message)

        # 2. Update cumulative profile memory in SQLite
        session = self.session_manager.update_profile(sid, extracted_state)
        cumulative_state = session.cumulative_state

        # 3. Process the merged cumulative state
        response = self._run_pipeline(
            state=cumulative_state,
            session_id=sid,
            input_text=message,
            extracted_state_dict=extracted_state.get_supplied_variables(),
        )
        return response

    def process_assessment(
        self,
        state: EnvironmentalState,
        session_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> SystemResponse:
        """Processes directly supplied structured JSON EnvironmentalState."""
        sid = session_id or str(uuid.uuid4())
        session = self.session_manager.update_profile(sid, state)
        cumulative_state = session.cumulative_state

        response = self._run_pipeline(
            state=cumulative_state,
            session_id=sid,
            input_text=notes or "Direct structured assessment payload",
            extracted_state_dict=state.get_supplied_variables(),
        )
        return response

    def _run_pipeline(
        self,
        state: EnvironmentalState,
        session_id: str,
        input_text: str,
        extracted_state_dict: Dict[str, Any],
    ) -> SystemResponse:
        """Executes the core assessment pipeline and logs the turn."""
        turn_id = str(uuid.uuid4())

        # 1. Check Completeness Gate (Gated Multi-Variable Reasoning)
        is_complete, missing_vars, clarification_q = self.clarification_engine.evaluate_completeness(state)

        if not is_complete:
            resp = SystemResponse(
                status="needs_clarification",
                session_id=session_id,
                environmental_state=state.get_supplied_variables(),
                clarification_required=True,
                missing_information=missing_vars,
                clarification_question=clarification_q,
            )
            self.session_manager.store_turn(
                ConversationTurn(
                    turn_id=turn_id,
                    session_id=session_id,
                    role="assistant",
                    input_text=input_text,
                    extracted_environmental_state=extracted_state_dict,
                    response=resp.model_dump(),
                    clarification_required=True,
                )
            )
            return resp

        # 2. Deterministic Ecological Reasoning
        reasoning_res = self.reasoning_engine.evaluate(state)

        # If no cross-variable ecological relationships were triggered, request complementary variables
        if not reasoning_res.triggered_relationships:
            _, missing_supp, clarif_prompt = self.clarification_engine.evaluate_completeness(
                # Force missing factors identification
                EnvironmentalState(**{k: v for k, v in state.get_supplied_variables().items() if k in ["rainfall_regime", "cropping_pattern"]})
            )
            resp = SystemResponse(
                status="needs_clarification",
                session_id=session_id,
                environmental_state=state.get_supplied_variables(),
                clarification_required=True,
                missing_information=missing_supp or ["soil organic carbon %", "soil moisture", "biodiversity status"],
                clarification_question=(
                    f"I have recorded your parameters ({', '.join([f'{k}={v}' for k, v in state.get_supplied_variables().items()])}), "
                    f"but I need an additional factor to establish the ecological interaction. "
                    f"What is your soil organic carbon %, soil moisture condition, or current habitat/biodiversity status?"
                ),
            )
            self.session_manager.store_turn(
                ConversationTurn(
                    turn_id=turn_id,
                    session_id=session_id,
                    role="assistant",
                    input_text=input_text,
                    extracted_environmental_state=extracted_state_dict,
                    response=resp.model_dump(),
                    clarification_required=True,
                )
            )
            return resp

        # 3. Scientific Evidence Retrieval and Grounding
        evidence_res = self.evidence_engine.evaluate_candidates(
            reasoning_res.candidate_recommendations,
            reasoning_res.triggered_relationships,
        )

        # 4. Assemble Validated Recommendations
        rec_items: List[RecommendationResponseItem] = []
        for v_rec in evidence_res.validated_recommendations:
            rec_items.append(
                RecommendationResponseItem(
                    action=v_rec.action,
                    why_it_works=v_rec.why_it_works,
                    impacted_metrics=v_rec.impacted_metrics,
                    time_horizon=v_rec.time_horizon,
                    confidence=v_rec.confidence,
                    evidence=v_rec.evidence,
                    quantitative_estimate=v_rec.quantitative_estimate,
                    limitations=v_rec.limitations,
                )
            )

        # 5. Build Transparent Reasoning Trace
        input_factors = [f"{k} = {v}" for k, v in state.get_supplied_variables().items()]
        conditions = reasoning_res.condition_detection.derived_conditions
        rel_names = [f"{r.relationship_id}: {r.name}" for r in reasoning_res.triggered_relationships]
        cand_names = [c.action for c in reasoning_res.candidate_recommendations]
        validated_claims = [
            f"Intervention '{r.action}' supported by {len(r.evidence)} sources with {r.confidence} confidence."
            for r in rec_items
        ]
        decision_rationale = (
            f"Identified {len(conditions)} ecological deficits across {state.count_distinct_domains()} domains. "
            f"Triggered {len(rel_names)} multi-variable relationship rules. "
            f"Selected {len(rec_items)} candidate interventions verified against {len(evidence_res.retrieved_evidence_pool)} scientific passages."
        )

        trace = ReasoningTraceResponse(
            input_factors=input_factors,
            detected_conditions=conditions,
            cross_variable_relationships=rel_names,
            candidate_interventions=cand_names,
            retrieved_evidence=evidence_res.retrieved_evidence_pool,
            validated_claims=validated_claims,
            decision_rationale=decision_rationale,
        )

        # Aggregate limitations
        all_limitations = []
        for r in rec_items:
            all_limitations.extend(r.limitations)
        all_limitations = list(dict.fromkeys(all_limitations))

        evidence_status = "complete" if evidence_res.validated_recommendations else "insufficient_evidence"
        resp = SystemResponse(
            status=evidence_status,
            session_id=session_id,
            environmental_state=state.get_supplied_variables(),
            clarification_required=False,
            detected_conditions=conditions,
            relationships=[r.model_dump() for r in reasoning_res.triggered_relationships],
            recommendations=rec_items,
            reasoning_trace=trace,
            limitations=all_limitations or [evidence_res.evidence_notes],
        )

        # Store turn in SQLite
        self.session_manager.store_turn(
            ConversationTurn(
                turn_id=turn_id,
                session_id=session_id,
                role="assistant",
                input_text=input_text,
                extracted_environmental_state=extracted_state_dict,
                response=resp.model_dump(),
                clarification_required=False,
            )
        )

        return resp
