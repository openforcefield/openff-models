from openff.units import Quantity

from openff.models._pydantic import BaseModel
from openff.models.types.serialization import custom_quantity_encoder


class DefaultModel(BaseModel):
    """A custom Pydantic model used by other components."""

    model_config = {
        "json_encoders": {
            Quantity: custom_quantity_encoder,
        },
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
    }
