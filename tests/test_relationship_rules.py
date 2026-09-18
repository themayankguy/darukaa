"""Tests verifying structural integrity and multi-variable participation across relationship rules."""

import json
from pathlib import Path
import pytest


@pytest.fixture
def relationships():
    path = Path(__file__).resolve().parent.parent / "knowledge_base" / "relationships.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_minimum_ten_rules(relationships):
    """Verifies at least 10 meaningful cross-variable relationships exist."""
    assert len(relationships) >= 10


def test_each_rule_has_at_least_three_variables(relationships):
    """Verifies that every single rule explicitly identifies >= 3 environmental variables."""
    for rule in relationships:
        rule_id = rule.get("relationship_id")
        vars_involved = rule.get("environmental_variables", [])
        assert len(vars_involved) >= 3, f"Rule {rule_id} does not have >= 3 environmental variables."
        assert len(rule.get("required_conditions", [])) >= 2
        assert len(rule.get("candidate_interventions", [])) >= 1
        assert len(rule.get("affected_metrics", [])) >= 1
        assert rule.get("mechanism") is not None
