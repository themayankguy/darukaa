"""Unit tests for condition detector and thresholds."""

import pytest
from src.input_layer.schemas import EnvironmentalState
from src.reasoning.condition_detector import ConditionDetector


def test_detect_quantitative_soc_and_rainfall():
    detector = ConditionDetector()
    state = EnvironmentalState(
        soil_organic_carbon_pct=0.3,
        rainfall_annual_mm=380.0,
        cropping_pattern="monoculture wheat",
    )
    result = detector.detect(state)

    assert result.has_condition("low_soil_organic_carbon")
    assert result.has_condition("low_rainfall")
    assert result.has_condition("monoculture")
    assert len(result.derivations) >= 3

    # Verify user facts are strictly distinguished from derived conditions
    assert "soil_organic_carbon_pct" in result.user_provided_facts
    assert result.user_provided_facts["soil_organic_carbon_pct"] == 0.3
    assert "low_soil_organic_carbon" not in result.user_provided_facts


def test_detect_qualitative_classifications():
    detector = ConditionDetector()
    state = EnvironmentalState(
        soil_moisture="dry",
        temperature_regime="high_temperature",
        habitat_diversity="low",
        species_richness="poor",
    )
    result = detector.detect(state)

    assert result.has_condition("low_soil_moisture")
    assert result.has_condition("high_temperature")
    assert result.has_condition("low_habitat_diversity")
    assert result.has_condition("low_species_richness")


def test_detect_healthy_conditions():
    detector = ConditionDetector()
    state = EnvironmentalState(
        soil_organic_carbon_pct=2.4,
        cropping_pattern="monoculture",
        habitat_diversity="low",
    )
    result = detector.detect(state)

    assert result.has_condition("soil_health_adequate")
    assert not result.has_condition("low_soil_organic_carbon")
