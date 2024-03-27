from typing import Any, Callable

from openff.units import Quantity

from openff.models._pydantic import BaseModel
from openff.models.types import custom_quantity_encoder, json_loader


class DefaultModel(BaseModel):
    """A custom Pydantic model used by other components."""

    class Config:
        """Custom Pydantic configuration."""

        json_encoders: dict[Any, Callable] = {
            Quantity: custom_quantity_encoder,
        }
        json_loads: Callable = json_loader
        validate_assignment: bool = True
        arbitrary_types_allowed: bool = True
