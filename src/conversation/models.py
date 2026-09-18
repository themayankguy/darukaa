"""Conversation data models and cumulative session profile."""

import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from src.input_layer.schemas import EnvironmentalState


class ConversationTurn(BaseModel):
    """Represents an individual exchange in a multi-turn conversation."""
    turn_id: str
    session_id: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    role: str = Field("user", description="'user' or 'assistant'")
    input_text: str
    extracted_environmental_state: Optional[Dict[str, Any]] = None
    response: Dict[str, Any]
    clarification_required: bool = False


class SessionProfile(BaseModel):
    """Cumulative environmental profile tracking information across conversation turns."""
    session_id: str
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    cumulative_state: EnvironmentalState = Field(default_factory=EnvironmentalState)
    turn_count: int = 0
    history: List[ConversationTurn] = Field(default_factory=list)

    def merge_state(self, new_state: EnvironmentalState) -> EnvironmentalState:
        """Merges newly extracted variables with the cumulative state.
        
        Merge Policy:
        - New explicit user value overwrites previous value.
        - Previous values are preserved if not mentioned in new_state (non-destructive merge).
        - Existing values are NEVER overwritten with None or empty values.
        """
        current_dict = self.cumulative_state.model_dump(exclude_unset=False)
        new_dict = new_state.get_supplied_variables()

        for field_name, new_val in new_dict.items():
            if new_val is not None:
                # If it's a list (e.g. biodiversity_indicators, human_pressures), union elements
                if isinstance(new_val, list):
                    prev_list = current_dict.get(field_name) or []
                    combined = list(dict.fromkeys(prev_list + new_val))
                    current_dict[field_name] = combined
                else:
                    current_dict[field_name] = new_val

        self.cumulative_state = EnvironmentalState(**current_dict)
        self.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return self.cumulative_state
