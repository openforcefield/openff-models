"""Custom models for dealing with unit-bearing quantities in a Pydantic-compatible manner."""

from typing import TYPE_CHECKING

import numpy
from openff.units import Quantity, Unit
from openff.utilities import has_package, requires_package

from openff.models.exceptions import UnitValidationError

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
