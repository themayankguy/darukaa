"""Thresholds and classification rules for environmental condition detection.

Configurable values for converting quantitative measurements and qualitative terms
into normalized condition tokens across the 5 ecological domains.
"""

from typing import Dict, Any, List

# Threshold configurations (adjustable without modifying detection logic)
THRESHOLDS: Dict[str, Any] = {
    # Soil Health
    "soc_low_threshold_pct": 1.0,           # SOC < 1.0% is classified as depleted/low
    "soc_adequate_threshold_pct": 2.0,      # SOC >= 2.0% is considered adequate/healthy
    "ph_acidic_threshold": 6.0,             # pH < 6.0 is acidic
    "ph_alkaline_threshold": 7.8,           # pH > 7.8 is alkaline
    
    # Climate & Hydrology
    "rainfall_low_annual_mm": 500.0,        # Annual precipitation < 500mm is low / semi-arid
    "rainfall_high_annual_mm": 1200.0,      # Annual precipitation > 1200mm is high
    "temp_high_celsius": 35.0,              # Temperature > 35°C represents high thermal stress
}

# Lexical mapping for qualitative inputs to condition tokens
QUALITATIVE_MAPPINGS: Dict[str, Dict[str, List[str]]] = {
    "soil_moisture": {
        "low_soil_moisture": ["dry", "very_dry", "arid", "severely_depleted", "low", "drought_stressed"],
        "waterlogging": ["waterlogged", "saturated", "flooded", "poorly_drained", "standing_water"],
    },
    "soil_condition_qualitative": {
        "degraded_soil": ["degraded", "eroded", "compacted", "crusted", "salinized", "nutrient_depleted"],
        "soil_health_adequate": ["fertile", "healthy", "high_organic_matter", "loamy", "adequate"],
    },
    "rainfall_regime": {
        "low_rainfall": ["low", "arid", "semi-arid", "dry", "semi_arid", "drought_prone", "scanty"],
        "high_rainfall": ["high", "heavy", "excessive", "monsoonal", "very_high"],
    },
    "temperature_regime": {
        "high_temperature": ["high", "hot", "extreme_heat", "heat_stress", "high_temperature", "scorching"],
    },
    "cropping_pattern": {
        "monoculture": ["monoculture", "monoculture wheat", "continuous wheat", "single crop", "wheat monoculture", "monoculture maize"],
        "diversified_rotation": ["rotation", "intercropping", "polyculture", "strip_cropping", "diverse"],
    },
    "land_use_type": {
        "cropland": ["cropland", "arable", "field", "farm", "crop", "agricultural_land"],
        "pasture": ["pasture", "rangeland", "grassland"],
    },
    "species_richness": {
        "low_species_richness": ["low", "very_low", "poor", "depleted", "few", "scarce"],
        "high_species_richness": ["high", "diverse", "abundant", "rich"],
    },
    "habitat_diversity": {
        "low_habitat_diversity": ["low", "fragmented", "poor", "simple", "homogenous", "homogeneous", "no_corridors"],
        "high_habitat_diversity": ["high", "complex", "diverse", "heterogeneous"],
    },
    "biodiversity_condition": {
        "biodiversity_decline": ["declining", "poor", "degraded", "dropping", "threatened", "collapse", "loss"],
    },
    "agricultural_pressure": {
        "intensive_tillage": ["intensive_tillage", "deep_tillage", "deep_plowing", "conventional_tillage", "inversion_tillage", "heavy_tillage"],
    },
    "pollution_pressure": {
        "pollution_pressure": ["high", "pesticides", "fertilizers", "heavy_pesticides", "synthetic_fertilizer_overuse", "runoff", "chemical_pollution"],
    },
    "deforestation_status": {
        "deforestation": ["cleared", "deforested", "recent_clearing", "fragmented_forest", "loss_of_trees"],
    },
}
