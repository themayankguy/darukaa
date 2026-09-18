"""Tests for conversational intelligence, session memory, profile merging, and clarification."""

import pytest
import uuid
from pathlib import Path

from src.input_layer.schemas import EnvironmentalState
from src.conversation.orchestrator import ChatOrchestrator
from src.conversation.session_manager import SessionManager
from src.core.mock_client import MockLLMClient


@pytest.fixture
def orchestrator(tmp_path):
    # Use isolated SQLite DB in pytest temp directory
    db_file = tmp_path / "test_sessions.db"
    session_mgr = SessionManager(db_path=db_file)
    mock_llm = MockLLMClient()
    return ChatOrchestrator(session_manager=session_mgr, llm_client=mock_llm)


def test_clarification_on_insufficient_input(orchestrator):
    """Test 1 — Clarification: Input only 'Rainfall is low.' triggers clarification."""
    sid = str(uuid.uuid4())
    resp = orchestrator.process_chat("Rainfall is low.", session_id=sid)

    assert resp.status == "needs_clarification"
    assert resp.clarification_required is True
    assert resp.recommendations is None
    assert resp.clarification_question is not None
    assert len(resp.missing_information or []) > 0
    assert resp.session_id == sid

    # Verify session is persisted in DB
    session = orchestrator.session_manager.get_session(sid)
    assert session is not None
    assert session.cumulative_state.rainfall_regime == "low"


def test_multi_turn_memory(orchestrator):
    """Test 2 — Multi-turn memory: Turn 1 provides rainfall + wheat monoculture; Turn 2 provides SOC 0.3%."""
    sid = str(uuid.uuid4())
    
    # Turn 1
    resp1 = orchestrator.process_chat(
        "Rainfall is low and my farm is monoculture wheat.",
        session_id=sid
    )
    assert resp1.status == "needs_clarification"
    assert resp1.clarification_required is True

    # Turn 2
    resp2 = orchestrator.process_chat(
        "Soil organic carbon is 0.3%.",
        session_id=sid
    )
    # Merged profile now has: rainfall='low', cropping_pattern='monoculture wheat', land_use_type='cropland', soc=0.3
    assert resp2.status == "complete"
    assert resp2.clarification_required is False
    assert resp2.recommendations is not None
    assert len(resp2.recommendations) >= 1
    assert "REL_SEMIARID_SOC_MONOCULTURE" in [r["relationship_id"] for r in (resp2.relationships or [])]


def test_explicit_overwrite(orchestrator):
    """Test 3 — Explicit overwrite: Turn 1 sets moisture dry; Turn 2 sets moisture adequate."""
    sid = str(uuid.uuid4())

    # Turn 1
    orchestrator.process_chat("Soil moisture is dry.", session_id=sid)
    s1 = orchestrator.session_manager.get_session(sid)
    assert s1.cumulative_state.soil_moisture == "dry"

    # Turn 2
    orchestrator.process_chat("Soil moisture is now adequate.", session_id=sid)
    s2 = orchestrator.session_manager.get_session(sid)
    assert s2.cumulative_state.soil_moisture == "adequate"


def test_null_protection(orchestrator):
    """Test 4 — Null protection: 0.3% SOC is not overwritten with null on next turn."""
    sid = str(uuid.uuid4())

    # Turn 1
    orchestrator.process_chat("Soil organic carbon is 0.3%.", session_id=sid)
    s1 = orchestrator.session_manager.get_session(sid)
    assert s1.cumulative_state.soil_organic_carbon_pct == 0.3

    # Turn 2: message with no SOC information
    orchestrator.process_chat("The weather is nice today.", session_id=sid)
    s2 = orchestrator.session_manager.get_session(sid)
    assert s2.cumulative_state.soil_organic_carbon_pct == 0.3


def test_structured_json_invocation(orchestrator):
    """Test 5 — Structured JSON: Direct EnvironmentalState assessment."""
    state = EnvironmentalState(
        soil_organic_carbon_pct=0.3,
        rainfall_regime="low",
        cropping_pattern="monoculture wheat",
        land_use_type="cropland",
    )
    resp = orchestrator.process_assessment(state)
    assert resp.status == "complete"
    assert resp.recommendations is not None
    assert len(resp.recommendations) >= 1
    assert resp.reasoning_trace is not None


def test_session_isolation(orchestrator):
    """Test 6 — Session isolation: Data in Session A does not leak to Session B."""
    sid_a = str(uuid.uuid4())
    sid_b = str(uuid.uuid4())

    orchestrator.process_chat("Soil organic carbon is 0.4% and rainfall is low.", session_id=sid_a)
    orchestrator.process_chat("De-forested woodland with heavy synthetic fertilizer runoff.", session_id=sid_b)

    sess_a = orchestrator.session_manager.get_session(sid_a)
    sess_b = orchestrator.session_manager.get_session(sid_b)

    assert sess_a.cumulative_state.soil_organic_carbon_pct == 0.4
    assert sess_b.cumulative_state.soil_organic_carbon_pct is None
    assert sess_b.cumulative_state.deforestation_status == "cleared_woodland"
    assert sess_a.cumulative_state.deforestation_status is None


def test_llm_independence(orchestrator):
    """Test 7 — LLM independence: Reasoning executes deterministically with LLM disabled/mocked."""
    orchestrator.llm = None
    orchestrator.extractor.llm = None
    orchestrator.clarification_engine.llm = None

    state = EnvironmentalState(
        soil_organic_carbon_pct=0.3,
        rainfall_regime="low",
        cropping_pattern="monoculture wheat",
    )
    resp = orchestrator.process_assessment(state)
    assert resp.status == "complete"
    assert len(resp.recommendations or []) >= 1
