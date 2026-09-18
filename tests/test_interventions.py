"""Tests verifying intervention definitions and structure."""

import json
from pathlib import Path
import pytest


@pytest.fixture
def interventions():
    path = Path(__file__).resolve().parent.parent / "knowledge_base" / "interventions.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_interventions_count_and_fields(interventions):
    """Verifies that all interventions have mandatory fields."""
    assert len(interventions) >= 8
    mandatory_fields = [
        "intervention_id", "name", "description", "applicable_conditions",
        "target_variables", "impacted_metrics", "time_horizon",
        "potential_tradeoffs", "evidence_topics"
    ]
    for item in interventions:
        for field in mandatory_fields:
            assert field in item, f"Intervention {item.get('intervention_id')} missing {field}"
        assert len(item["impacted_metrics"]) >= 1
        assert len(item["potential_tradeoffs"]) >= 1
