"""Custom models for dealing with unit-bearing quantities in a Pydantic-compatible manner."""

import json
from typing import TYPE_CHECKING

import numpy
from openff.units import Quantity, Unit
from openff.utilities import has_package, requires_package

from openff.models.exceptions import UnitValidationError, UnsupportedExportError

if TYPE_CHECKING:
    import openmm.unit


def _is_openmm_quantity(obj: object) -> bool:
    if has_package("openmm"):
        import openmm.unit

        return isinstance(obj, openmm.unit.Quantity)

    else:
        return "openmm.unit.quantity.Quantity" in str(type(object))


@requires_package("openmm.unit")
def _from_omm_quantity(val: "openmm.unit.Quantity") -> Quantity:
    """
    Convert float or array quantities tagged with SimTK/OpenMM units to a Pint-compatible quantity.
    """
    unit_: openmm.unit.Unit = val.unit
    val_ = val.value_in_unit(unit_)
    if type(val_) in {float, int}:
        unit_ = val.unit
        return float(val_) * Unit(str(unit_))
    # Here is where the toolkit's ValidatedList could go, if present in the environment
    elif (type(val_) in {tuple, list, numpy.ndarray}) or (
        type(val_).__module__ == "openmm.vec3"
    ):
        array = numpy.asarray(val_)
        return array * Unit(str(unit_))
    elif isinstance(val_, (float, int)) and type(val_).__module__ == "numpy":
        return val_ * Unit(str(unit_))
    else:
        raise UnitValidationError(
            "Found a openmm.unit.Unit wrapped around something other than a float-like "
            f"or numpy.ndarray-like. Found a unit wrapped around type {type(val_)}."
        )


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
