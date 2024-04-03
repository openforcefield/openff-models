import json

import numpy
from openff.units import Quantity, Unit

from openff.models.exceptions import UnsupportedExportError


class QuantityEncoder(json.JSONEncoder):
    """
    JSON encoder for unit-wrapped floats and NumPy arrays.

    This is intended to operate on Quantity objects.
    """

    def default(self, obj):
        if isinstance(obj, Quantity):
            if isinstance(obj.magnitude, (float, int)):
                data = obj.magnitude
            elif isinstance(obj.magnitude, numpy.ndarray):
                data = obj.magnitude.tolist()
            else:
                # This shouldn't ever be hit if our object models
                # behave in ways we expect?
                raise UnsupportedExportError(
                    f"trying to serialize unsupported type {type(obj.magnitude)}"
                )
            return {
                "val": data,
                "unit": str(obj.units),
            }


def custom_quantity_encoder(v):
    """Wrap json.dump to use QuantityEncoder."""
    return json.dumps(v, cls=QuantityEncoder)


def json_loader(data: str) -> dict:
    """Load JSON containing custom unit-tagged quantities."""
    # TODO: recursively call this function for nested models
    out: dict = json.loads(data)
    for key, val in out.items():
        try:
            # Directly look for an encoded FloatQuantity/ArrayQuantity,
            # which is itself a dict
            v = json.loads(val)
        except (json.JSONDecodeError, TypeError):
            # Handles some cases of the val being a primitive type
            continue
        # TODO: More gracefully parse non-FloatQuantity/ArrayQuantity dicts
        unit_ = Unit(v["unit"])
        val = v["val"]
        out[key] = unit_ * val
    return out


def dict_to_quantity(data: dict) -> Quantity:
    """Convert a dictionary of structure like {"val": 1.0, "unit": "angstrom"} to a Quantity."""
    if len(data) == 2:
        try:
            return Quantity(data["val"], data["unit"])
        except KeyError as error:
            raise ValueError(f"bad keys {data.keys()}") from error
    else:
        raise ValueError("Dictionary must have exactly two keys 'val' and 'unit'")
