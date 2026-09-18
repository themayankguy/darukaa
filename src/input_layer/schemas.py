"""Environmental State and Input Schemas for Darukaa.Earth AI Biodiversity System.

Covers the 5 core environmental domains:
1. Soil Health (pH, organic carbon %, moisture)
2. Land Use / Land Cover (land use type, land cover, cropping pattern)
3. Biodiversity (species richness, habitat diversity, general biodiversity condition)
4. Climate & Hydrology (temperature, rainfall regime, water availability)
5. Human Impact (pollution, deforestation, agricultural pressure / tillage / pesticides)
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator


class EnvironmentalState(BaseModel):
    """Normalized environmental state representation.
    Supports both quantitative measurements and qualitative classifications.
    All fields are optional to allow incremental conversational slot filling.
    """
    
    # -------------------------------------------------------------
    # 1. Soil Health
    # -------------------------------------------------------------
    soil_ph: Optional[float] = Field(
        None,
        ge=0.0,
        le=14.0,
        description="Soil pH on standard 0-14 scale."
    )
    soil_organic_carbon_pct: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Soil organic carbon percentage (SOC %)."
    )
    soil_moisture: Optional[str] = Field(
        None,
        description="Qualitative or categorical soil moisture status (e.g., 'dry', 'adequate', 'waterlogged', 'severely_depleted')."
    )
    soil_condition_qualitative: Optional[str] = Field(
        None,
        description="General qualitative description of soil status (e.g., 'degraded', 'eroded', 'fertile')."
    )

    # -------------------------------------------------------------
    # 2. Land Use / Land Cover
    # -------------------------------------------------------------
    land_use_type: Optional[str] = Field(
        None,
        description="Classification of land use (e.g., 'cropland', 'pasture', 'agroforestry', 'fallow', 'orchard')."
    )
    land_cover: Optional[str] = Field(
        None,
        description="Vegetative/surface cover (e.g., 'bare_soil', 'herbaceous', 'forest_canopy', 'sparse_cover')."
    )
    cropping_pattern: Optional[str] = Field(
        None,
        description="Cropping regime (e.g., 'monoculture', 'monoculture wheat', 'intercropping', 'crop_rotation', 'agroforestry')."
    )

    # -------------------------------------------------------------
    # 3. Biodiversity
    # -------------------------------------------------------------
    species_richness: Optional[str] = Field(
        None,
        description="Species richness status (e.g., 'low', 'moderate', 'high', or estimated count)."
    )
    habitat_diversity: Optional[str] = Field(
        None,
        description="Habitat heterogeneity (e.g., 'low', 'fragmented', 'moderate', 'high_structural_diversity')."
    )
    biodiversity_indicators: Optional[List[str]] = Field(
        default_factory=list,
        description="Observed indicator groups (e.g., ['low_pollinators', 'few_earthworms', 'pest_outbreak'])."
    )
    biodiversity_condition: Optional[str] = Field(
        None,
        description="Overall qualitative biodiversity status when exact measurements are unavailable (e.g., 'declining', 'poor', 'stable')."
    )

    # -------------------------------------------------------------
    # 4. Climate & Hydrology
    # -------------------------------------------------------------
    temperature_regime: Optional[str] = Field(
        None,
        description="Thermal regime (e.g., 'high_temperature', 'extreme_heat', 'temperate', 'subtropical')."
    )
    temperature_celsius: Optional[float] = Field(
        None,
        ge=-50.0,
        le=65.0,
        description="Mean or peak temperature in Celsius if measured."
    )
    rainfall_regime: Optional[str] = Field(
        None,
        description="Precipitation pattern (e.g., 'low', 'semi-arid', 'arid', 'high', 'seasonal', 'bimodal')."
    )
    rainfall_annual_mm: Optional[float] = Field(
        None,
        ge=0.0,
        le=12000.0,
        description="Annual precipitation in millimeters if measured."
    )
    water_availability: Optional[str] = Field(
        None,
        description="Water availability / drainage condition (e.g., 'scarce', 'waterlogged', 'drought_prone', 'adequate')."
    )

    # -------------------------------------------------------------
    # 5. Human Impact
    # -------------------------------------------------------------
    pollution_pressure: Optional[str] = Field(
        None,
        description="Presence or severity of pollution (e.g., 'synthetic_fertilizer_overuse', 'pesticide_runoff', 'industrial_waste')."
    )
    deforestation_status: Optional[str] = Field(
        None,
        description="Deforestation or land-clearing status (e.g., 'cleared_woodland', 'recent_deforestation', 'intact')."
    )
    agricultural_pressure: Optional[str] = Field(
        None,
        description="Management intensity (e.g., 'intensive_tillage', 'deep_plowing', 'heavy_machinery_compaction', 'low_input')."
    )
    human_pressures: Optional[List[str]] = Field(
        default_factory=list,
        description="Tags of explicit human pressures (e.g., ['deep_tillage', 'pesticides', 'deforestation'])."
    )

    # -------------------------------------------------------------
    # Spatial / Geographic Context (Bonus)
    # -------------------------------------------------------------
    region: Optional[str] = Field(
        None,
        description="Geographic region or biome (e.g., 'semi-arid drylands', 'sub-humid tropics', 'temperate plains')."
    )
    coordinates: Optional[Dict[str, float]] = Field(
        None,
        description="Latitude and longitude coordinates, e.g. {'lat': 26.91, 'lng': 75.78}."
    )

    @field_validator("soil_ph")
    @classmethod
    def validate_ph(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 14.0):
            raise ValueError("Soil pH must be between 0.0 and 14.0.")
        return v

    @field_validator("soil_organic_carbon_pct")
    @classmethod
    def validate_soc(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("Soil organic carbon percentage must be between 0.0 and 100.0.")
        return v

    def get_supplied_variables(self) -> Dict[str, Any]:
        """Returns a dictionary of all explicitly populated fields (non-None, non-empty list)."""
        supplied = {}
        for field_name, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, list) and len(value) == 0:
                    continue
                if isinstance(value, dict) and len(value) == 0:
                    continue
                supplied[field_name] = value
        return supplied

    def get_supplied_domains(self) -> Dict[str, List[str]]:
        """Maps supplied variables to their parent ecological domain."""
        domain_mapping = {
            "soil_health": ["soil_ph", "soil_organic_carbon_pct", "soil_moisture", "soil_condition_qualitative"],
            "land_use_cover": ["land_use_type", "land_cover", "cropping_pattern"],
            "biodiversity": ["species_richness", "habitat_diversity", "biodiversity_indicators", "biodiversity_condition"],
            "climate": ["temperature_regime", "temperature_celsius", "rainfall_regime", "rainfall_annual_mm", "water_availability"],
            "human_impact": ["pollution_pressure", "deforestation_status", "agricultural_pressure", "human_pressures"],
        }
        active_domains: Dict[str, List[str]] = {}
        supplied_vars = self.get_supplied_variables()
        for domain, fields in domain_mapping.items():
            active_fields = [f for f in fields if f in supplied_vars]
            if active_fields:
                active_domains[domain] = active_fields
        return active_domains

    def count_distinct_variables(self) -> int:
        """Counts the number of distinct environmental variables supplied."""
        return len(self.get_supplied_variables())

    def count_distinct_domains(self) -> int:
        """Counts the number of active ecological domains with data."""
        return len(self.get_supplied_domains())


class StructuredInputPayload(BaseModel):
    """Wrapper payload for direct JSON ingestion."""
    session_id: Optional[str] = Field(None, description="Optional persistent session identifier.")
    environmental_state: EnvironmentalState
    notes: Optional[str] = Field(None, description="Additional context or user observation.")
