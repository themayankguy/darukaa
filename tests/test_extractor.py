from src.input_layer.extractor import EnvironmentalExtractor


def test_extracts_requested_demo_environmental_state():
    text = (
        "I manage a wheat farm in a semi-arid region. The soil organic carbon is low at 0.3%, "
        "soil moisture is low, annual rainfall is low, and the farm has been under monoculture "
        "wheat cultivation for several years. Habitat diversity and species richness are also low."
    )

    state = EnvironmentalExtractor().extract(text)

    assert state.soil_organic_carbon_pct == 0.3
    assert state.soil_moisture == "low"
    assert state.rainfall_regime == "low"
    assert state.region == "semi-arid"
    assert state.cropping_pattern == "monoculture wheat"
    assert state.habitat_diversity == "low"
    assert state.species_richness == "low"


def test_extracts_supported_explicit_field_variants():
    extractor = EnvironmentalExtractor()

    assert extractor.extract("SOC = 0.3%").soil_organic_carbon_pct == 0.3
    assert extractor.extract("organic carbon is 0.3%").soil_organic_carbon_pct == 0.3
    assert extractor.extract("soil moisture is very low").soil_moisture == "low"
    assert extractor.extract("soil moisture condition is dry").soil_moisture == "dry"
    assert extractor.extract("habitat diversity is poor").habitat_diversity == "poor"
    assert extractor.extract("species richness is poor").species_richness == "poor"