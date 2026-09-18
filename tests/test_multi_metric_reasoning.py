"""Tests for the deterministic multi-metric ecological reasoning engine.

Verifies:
- Test 1: Semi-arid monoculture (>= 3 variables participating, low SOC, low rainfall, monoculture, agroforestry/intercropping candidates)
- Test 2: Water stress (dry moisture, high temp, low rainfall)
- Test 3: Biodiversity/habitat (monoculture, low habitat diversity, low species richness)
- Test 4: Insufficient state (only low rainfall -> no full assessment, missing info identified)
- Test 7: Determinism (identical state produces identical conditions, relationships, and candidates)
"""

import pytest
from src.input_layer.schemas import EnvironmentalState
from src.reasoning.multi_metric_engine import MultiMetricReasoningEngine


@pytest.fixture
def engine():
    return MultiMetricReasoningEngine()


def test_scenario_1_semi_arid_monoculture(engine):
    """Test 1: SOC = 0.3%, rainfall = low, cropping = monoculture, land use = cropland."""
    state = EnvironmentalState(
        soil_organic_carbon_pct=0.3,
        rainfall_regime="low",
        cropping_pattern="monoculture wheat",
        land_use_type="cropland",
    )
    res = engine.evaluate(state)

    assert res.is_sufficient_for_assessment is True
    assert res.participating_variable_count >= 3
    assert "low_soil_organic_carbon" in res.condition_detection.derived_conditions
    assert "low_rainfall" in res.condition_detection.derived_conditions
    assert "monoculture" in res.condition_detection.derived_conditions

    # Must trigger REL_SEMIARID_SOC_MONOCULTURE
    rel_ids = [r.relationship_id for r in res.triggered_relationships]
    assert "REL_SEMIARID_SOC_MONOCULTURE" in rel_ids

    # Candidate interventions must include legume intercropping or agroforestry
    int_ids = [c.intervention_id for c in res.candidate_recommendations]
    assert "INT_LEGUME_INTERCROPPING" in int_ids or "INT_ALLEY_CROPPING_AGROFORESTRY" in int_ids


def test_scenario_2_water_thermal_stress(engine):
    """Test 2: soil moisture = dry, rainfall = low, temperature = high."""
    state = EnvironmentalState(
        soil_moisture="dry",
        rainfall_regime="low",
        temperature_regime="high_temperature",
    )
    res = engine.evaluate(state)

    assert res.is_sufficient_for_assessment is True
    assert res.participating_variable_count == 3
    rel_ids = [r.relationship_id for r in res.triggered_relationships]
    assert "REL_THERMAL_DROUGHT_STRESS" in rel_ids


def test_scenario_3_biodiversity_collapse(engine):
    """Test 3: monoculture, low habitat diversity, low species richness."""
    state = EnvironmentalState(
        cropping_pattern="monoculture",
        habitat_diversity="low",
        species_richness="low",
    )
    res = engine.evaluate(state)

    assert res.is_sufficient_for_assessment is True
    rel_ids = [r.relationship_id for r in res.triggered_relationships]
    assert "REL_MONOCULTURE_BIODIVERSITY_COLLAPSE" in rel_ids
    int_ids = [c.intervention_id for c in res.candidate_recommendations]
    assert "INT_POLLINATOR_HEDGEROWS" in int_ids


def test_scenario_4_insufficient_state(engine):
    """Test 4: only low rainfall provided (< 3 variables)."""
    state = EnvironmentalState(rainfall_regime="low")
    res = engine.evaluate(state)

    # Must NOT run full assessment or make unsupported recommendations
    assert res.is_sufficient_for_assessment is False
    assert len(res.triggered_relationships) == 0
    assert len(res.candidate_recommendations) == 0
    assert len(res.missing_variables) > 0
    assert "rainfall_regime" in res.available_variables


def test_scenario_7_determinism(engine):
    """Test 7: Same environmental state run twice produces identical outputs."""
    state = EnvironmentalState(
        soil_organic_carbon_pct=0.3,
        rainfall_regime="low",
        cropping_pattern="monoculture",
    )
    res1 = engine.evaluate(state)
    res2 = engine.evaluate(state)

    assert res1.condition_detection.derived_conditions == res2.condition_detection.derived_conditions
    assert [r.relationship_id for r in res1.triggered_relationships] == [r.relationship_id for r in res2.triggered_relationships]
    assert [c.intervention_id for c in res1.candidate_recommendations] == [c.intervention_id for c in res2.candidate_recommendations]
