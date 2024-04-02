from openff.units import Quantity

from openff.models._pydantic import BaseModel
from openff.models.types import custom_quantity_encoder, json_loader


class DefaultModel(BaseModel):
    """A custom Pydantic model used by other components."""

    model_config = {
        "json_encoders": {
            Quantity: custom_quantity_encoder,
        },
        # removed in V2, not sure where this went
        "json_loads": json_loader,  # type: ignore[typeddict-unknown-key]
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
    }
