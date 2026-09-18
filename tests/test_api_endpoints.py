"""End-to-end API tests using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_endpoint():
    """1. Health endpoint returns 200 and ok."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_chat_clarification_response():
    """2. Chat endpoint with insufficient variables returns clarification."""
    resp = client.post(
        "/api/v1/chat",
        json={"message": "Rainfall is very low on my farm."}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "needs_clarification"
    assert data["clarification_required"] is True
    assert "clarification_question" in data
    assert data["clarification_question"] is not None
    assert "session_id" in data


def test_chat_complete_recommendation_and_persistence():
    """3. Chat multi-turn workflow: turn 1 provides rainfall; turn 2 adds SOC and monoculture."""
    # Turn 1
    resp1 = client.post(
        "/api/v1/chat",
        json={"message": "Rainfall is low and the cropping pattern is monoculture wheat."}
    )
    assert resp1.status_code == 200
    d1 = resp1.json()
    session_id = d1["session_id"]
    assert d1["status"] == "needs_clarification"

    # Turn 2 with same session_id
    resp2 = client.post(
        "/api/v1/chat",
        json={
            "session_id": session_id,
            "message": "Soil organic carbon is 0.3%."
        }
    )
    assert resp2.status_code == 200
    d2 = resp2.json()
    assert d2["status"] == "complete"
    assert d2["clarification_required"] is False
    assert len(d2["recommendations"]) >= 1
    assert "reasoning_trace" in d2
    assert len(d2["reasoning_trace"]["cross_variable_relationships"]) >= 1


def test_assessment_endpoint_structured_json():
    """4. Direct structured assessment returns complete evidence-grounded response."""
    payload = {
        "soil_organic_carbon_pct": 0.3,
        "soil_moisture": "dry",
        "rainfall_regime": "low",
        "temperature_regime": "high heat stress",
        "land_use_type": "cropland",
        "cropping_pattern": "monoculture wheat"
    }
    resp = client.post("/api/v1/assessment", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "complete"
    assert len(data["recommendations"]) >= 1
    rec = data["recommendations"][0]
    assert "action" in rec
    assert "why_it_works" in rec
    assert "evidence" in rec
    assert len(rec["evidence"]) >= 1


def test_session_retrieval():
    """5. Retrieve session profile and turns."""
    # Create turn
    resp = client.post(
        "/api/v1/chat",
        json={"message": "Soil moisture is dry and rainfall is low."}
    )
    sid = resp.json()["session_id"]

    # Retrieve
    get_resp = client.get(f"/api/v1/session/{sid}")
    assert get_resp.status_code == 200
    s_data = get_resp.json()
    assert s_data["session_id"] == sid
    assert len(s_data["history"]) >= 1


def test_malformed_json_validation():
    """6. Validation rejects invalid physical bounds (e.g., pH > 14 or negative SOC)."""
    # Invalid pH > 14
    bad_payload_ph = {"soil_ph": 17.5}
    resp1 = client.post("/api/v1/assessment", json=bad_payload_ph)
    assert resp1.status_code == 422

    # Invalid negative SOC
    bad_payload_soc = {"soil_organic_carbon_pct": -5.0}
    resp2 = client.post("/api/v1/assessment", json=bad_payload_soc)
    assert resp2.status_code == 422


def test_empty_chat_message_rejected():
    """7. Rejects empty string in chat."""
    resp = client.post("/api/v1/chat", json={"message": "   "})
    assert resp.status_code == 400
