"""Condition Detector for the Darukaa.Earth Environmental Reasoning Engine.

Converts an EnvironmentalState into normalized condition tokens across the 5 ecological domains.
Maintains strict separation between user-provided facts and derived conditions.
"""

from typing import Dict, List, Set, Any, Optional
from pydantic import BaseModel, Field

from src.input_layer.schemas import EnvironmentalState
from src.reasoning.thresholds import THRESHOLDS, QUALITATIVE_MAPPINGS


class ConditionDerivation(BaseModel):
    """Explains how a specific condition was derived from an underlying variable."""
    condition: str
    source_variable: str
    source_value: Any
    rationale: str


class ConditionDetectionResult(BaseModel):
    """Structured output from condition detection.
    Strictly preserves provenance of user facts vs derived conditions.
    """
    user_provided_facts: Dict[str, Any] = Field(
        default_factory=dict,
        description="Immutable snapshot of variables explicitly provided by the user."
    )
    derived_conditions: List[str] = Field(
        default_factory=list,
        description="Normalized condition tokens derived by the engine."
    )
    derivations: List[ConditionDerivation] = Field(
        default_factory=list,
        description="Audit trail explaining every derived condition."
    )

    def has_condition(self, condition: str) -> bool:
        return condition in self.derived_conditions


class ConditionDetector:
    """Deterministic ecological condition detector."""

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        self.thresholds = thresholds or THRESHOLDS
        self.mappings = QUALITATIVE_MAPPINGS

    def detect(self, state: EnvironmentalState) -> ConditionDetectionResult:
        """Evaluates an EnvironmentalState and returns user facts, derived conditions, and derivations."""
        user_facts = state.get_supplied_variables()
        derived_conditions: Set[str] = set()
        derivations: List[ConditionDerivation] = []

        # 1. Soil Health Evaluation
        self._detect_soil_conditions(state, derived_conditions, derivations)

        # 2. Land Use & Cropping Evaluation
        self._detect_land_conditions(state, derived_conditions, derivations)

        # 3. Biodiversity Evaluation
        self._detect_biodiversity_conditions(state, derived_conditions, derivations)

        # 4. Climate & Hydrology Evaluation
        self._detect_climate_conditions(state, derived_conditions, derivations)

        # 5. Human Pressure Evaluation
        self._detect_human_pressure_conditions(state, derived_conditions, derivations)

        return ConditionDetectionResult(
            user_provided_facts=user_facts,
            derived_conditions=sorted(list(derived_conditions)),
            derivations=derivations
        )

    def _detect_soil_conditions(
        self,
        state: EnvironmentalState,
        conditions: Set[str],
        derivations: List[ConditionDerivation]
    ) -> None:
        # Quantitative SOC %
        if state.soil_organic_carbon_pct is not None:
            val = state.soil_organic_carbon_pct
            low_thresh = self.thresholds["soc_low_threshold_pct"]
            adequate_thresh = self.thresholds["soc_adequate_threshold_pct"]
            if val < low_thresh:
                conditions.add("low_soil_organic_carbon")
                derivations.append(ConditionDerivation(
                    condition="low_soil_organic_carbon",
                    source_variable="soil_organic_carbon_pct",
                    source_value=val,
                    rationale=f"Measured SOC of {val}% is below the critical depletion threshold of {low_thresh}%."
                ))
            elif val >= adequate_thresh:
                conditions.add("soil_health_adequate")
                derivations.append(ConditionDerivation(
                    condition="soil_health_adequate",
                    source_variable="soil_organic_carbon_pct",
                    source_value=val,
                    rationale=f"Measured SOC of {val}% meets or exceeds the adequacy threshold of {adequate_thresh}%."
                ))

        # Qualitative Soil Condition
        if state.soil_condition_qualitative:
            val_str = state.soil_condition_qualitative.lower().strip()
            for cond_token, keywords in self.mappings["soil_condition_qualitative"].items():
                if any(k in val_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="soil_condition_qualitative",
                        source_value=state.soil_condition_qualitative,
                        rationale=f"Qualitative soil status '{state.soil_condition_qualitative}' matches '{cond_token}'."
                    ))

        # Soil Moisture
        if state.soil_moisture:
            moist_str = state.soil_moisture.lower().strip()
            for cond_token, keywords in self.mappings["soil_moisture"].items():
                if any(k in moist_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="soil_moisture",
                        source_value=state.soil_moisture,
                        rationale=f"Soil moisture classification '{state.soil_moisture}' indicates '{cond_token}'."
                    ))

    def _detect_land_conditions(
        self,
        state: EnvironmentalState,
        conditions: Set[str],
        derivations: List[ConditionDerivation]
    ) -> None:
        if state.cropping_pattern:
            crop_str = state.cropping_pattern.lower().strip()
            for cond_token, keywords in self.mappings["cropping_pattern"].items():
                if any(k in crop_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="cropping_pattern",
                        source_value=state.cropping_pattern,
                        rationale=f"Cropping pattern '{state.cropping_pattern}' matches '{cond_token}'."
                    ))

        if state.land_use_type:
            lut_str = state.land_use_type.lower().strip()
            for cond_token, keywords in self.mappings["land_use_type"].items():
                if any(k in lut_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="land_use_type",
                        source_value=state.land_use_type,
                        rationale=f"Land use classification '{state.land_use_type}' classified as '{cond_token}'."
                    ))

        if state.land_cover:
            cover_str = state.land_cover.lower().strip()
            if "bare" in cover_str or "uncovered" in cover_str:
                conditions.add("bare_soil")
                derivations.append(ConditionDerivation(
                    condition="bare_soil",
                    source_variable="land_cover",
                    source_value=state.land_cover,
                    rationale=f"Land cover '{state.land_cover}' indicates absent surface protective cover."
                ))

    def _detect_biodiversity_conditions(
        self,
        state: EnvironmentalState,
        conditions: Set[str],
        derivations: List[ConditionDerivation]
    ) -> None:
        if state.species_richness:
            sr_str = state.species_richness.lower().strip()
            for cond_token, keywords in self.mappings["species_richness"].items():
                if any(k in sr_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="species_richness",
                        source_value=state.species_richness,
                        rationale=f"Species richness '{state.species_richness}' classified as '{cond_token}'."
                    ))

        if state.habitat_diversity:
            hd_str = state.habitat_diversity.lower().strip()
            for cond_token, keywords in self.mappings["habitat_diversity"].items():
                if any(k in hd_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="habitat_diversity",
                        source_value=state.habitat_diversity,
                        rationale=f"Habitat diversity '{state.habitat_diversity}' classified as '{cond_token}'."
                    ))

        if state.biodiversity_condition:
            bc_str = state.biodiversity_condition.lower().strip()
            for cond_token, keywords in self.mappings["biodiversity_condition"].items():
                if any(k in bc_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="biodiversity_condition",
                        source_value=state.biodiversity_condition,
                        rationale=f"General biodiversity status '{state.biodiversity_condition}' mapped to '{cond_token}'."
                    ))

        if state.biodiversity_indicators:
            for ind in state.biodiversity_indicators:
                ind_str = ind.lower().strip()
                if any(term in ind_str for term in ["pollinator", "bee", "butterfly", "low_pollinators"]):
                    conditions.add("low_pollinator_indicators")
                    derivations.append(ConditionDerivation(
                        condition="low_pollinator_indicators",
                        source_variable="biodiversity_indicators",
                        source_value=ind,
                        rationale=f"Indicator '{ind}' signals pollinator habitat deficit."
                    ))

    def _detect_climate_conditions(
        self,
        state: EnvironmentalState,
        conditions: Set[str],
        derivations: List[ConditionDerivation]
    ) -> None:
        # Rainfall regime
        if state.rainfall_regime:
            rf_str = state.rainfall_regime.lower().strip()
            for cond_token, keywords in self.mappings["rainfall_regime"].items():
                if any(k in rf_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="rainfall_regime",
                        source_value=state.rainfall_regime,
                        rationale=f"Rainfall regime '{state.rainfall_regime}' classified as '{cond_token}'."
                    ))

        if state.rainfall_annual_mm is not None:
            val = state.rainfall_annual_mm
            if val < self.thresholds["rainfall_low_annual_mm"]:
                conditions.add("low_rainfall")
                derivations.append(ConditionDerivation(
                    condition="low_rainfall",
                    source_variable="rainfall_annual_mm",
                    source_value=val,
                    rationale=f"Annual rainfall {val}mm is below the dryland threshold ({self.thresholds['rainfall_low_annual_mm']}mm)."
                ))
            elif val > self.thresholds["rainfall_high_annual_mm"]:
                conditions.add("high_rainfall")
                derivations.append(ConditionDerivation(
                    condition="high_rainfall",
                    source_variable="rainfall_annual_mm",
                    source_value=val,
                    rationale=f"Annual rainfall {val}mm exceeds the high precipitation threshold ({self.thresholds['rainfall_high_annual_mm']}mm)."
                ))

        # Temperature
        if state.temperature_regime:
            tr_str = state.temperature_regime.lower().strip()
            for cond_token, keywords in self.mappings["temperature_regime"].items():
                if any(k in tr_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="temperature_regime",
                        source_value=state.temperature_regime,
                        rationale=f"Temperature regime '{state.temperature_regime}' indicates '{cond_token}'."
                    ))

        if state.temperature_celsius is not None:
            if state.temperature_celsius >= self.thresholds["temp_high_celsius"]:
                conditions.add("high_temperature")
                derivations.append(ConditionDerivation(
                    condition="high_temperature",
                    source_variable="temperature_celsius",
                    source_value=state.temperature_celsius,
                    rationale=f"Temperature {state.temperature_celsius}°C exceeds the thermal stress threshold ({self.thresholds['temp_high_celsius']}°C)."
                ))

        # Water availability
        if state.water_availability:
            wa_str = state.water_availability.lower().strip()
            if any(term in wa_str for term in ["waterlogged", "flooded", "saturation", "poor_drainage"]):
                conditions.add("waterlogging")
                derivations.append(ConditionDerivation(
                    condition="waterlogging",
                    source_variable="water_availability",
                    source_value=state.water_availability,
                    rationale=f"Water availability description '{state.water_availability}' indicates saturation/waterlogging."
                ))

    def _detect_human_pressure_conditions(
        self,
        state: EnvironmentalState,
        conditions: Set[str],
        derivations: List[ConditionDerivation]
    ) -> None:
        if state.agricultural_pressure:
            ap_str = state.agricultural_pressure.lower().strip()
            for cond_token, keywords in self.mappings["agricultural_pressure"].items():
                if any(k in ap_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="agricultural_pressure",
                        source_value=state.agricultural_pressure,
                        rationale=f"Agricultural pressure '{state.agricultural_pressure}' matches '{cond_token}'."
                    ))

        if state.pollution_pressure:
            pp_str = state.pollution_pressure.lower().strip()
            for cond_token, keywords in self.mappings["pollution_pressure"].items():
                if any(k in pp_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="pollution_pressure",
                        source_value=state.pollution_pressure,
                        rationale=f"Pollution status '{state.pollution_pressure}' matches '{cond_token}'."
                    ))

        if state.deforestation_status:
            df_str = state.deforestation_status.lower().strip()
            for cond_token, keywords in self.mappings["deforestation_status"].items():
                if any(k in df_str for k in keywords):
                    conditions.add(cond_token)
                    derivations.append(ConditionDerivation(
                        condition=cond_token,
                        source_variable="deforestation_status",
                        source_value=state.deforestation_status,
                        rationale=f"Deforestation status '{state.deforestation_status}' matches '{cond_token}'."
                    ))

        if state.human_pressures:
            for p in state.human_pressures:
                p_str = p.lower().strip()
                if "tillage" in p_str or "plowing" in p_str:
                    conditions.add("intensive_tillage")
                if "pesticide" in p_str or "fertilizer" in p_str or "chemical" in p_str:
                    conditions.add("pollution_pressure")
                if "deforestation" in p_str or "clearing" in p_str:
                    conditions.add("deforestation")
