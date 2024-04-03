from functools import partial
from typing import Annotated, Any

from openff.units import Quantity
from pydantic import AfterValidator
from pydantic.functional_validators import WrapValidator

from openff.models.validators import coerce_json_back_to_quantity

try:
    from openmm.unit import Quantity as OpenMMQuantity
except ImportError:
    OpenMMQuantity = Any  # type: ignore


def has_compatible_dimensionality(quantity: Quantity, unit: str) -> Quantity:
    if quantity.is_compatible_with(unit):
        return quantity
    else:
        raise ValueError(f"Dimensionality must be compatible with unit {unit}")


def build_dimension_type(unit: str) -> type[Quantity]:
    """Return an Annotated type for dimensional compatibility with a unit."""
    return Annotated[  # type: ignore[return-value]
        Quantity,
        WrapValidator(coerce_json_back_to_quantity),
        AfterValidator(partial(has_compatible_dimensionality, unit=unit)),
    ]


# TODO: Decide which dimensions to ship by default
(
    LengthQuantity,
    MassQuantity,
    TimeQuantity,
    DegreeQuantity,
    TemperatureQuantity,
    MolarEnergyQuantity,
    ChargeQuantity,
) = (
    build_dimension_type(unit)
    for unit in [
        "angstrom",
        "dalton",
        "second",
        "degree",
        "Kelvin",
        "kilojoule_per_mole",
        "elementary_charge",
    ]
)

# Aliases
DistanceQuantity = LengthQuantity
AngleQuantity = DegreeQuantity
