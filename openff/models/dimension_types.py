from functools import partial
from typing import Annotated, Any

from openff.units import Quantity
from pydantic import AfterValidator, BeforeValidator

try:
    from openmm.unit import Quantity as OpenMMQuantity
except ImportError:
    OpenMMQuantity = Any  # type: ignore


def to_quantity(quantity: Quantity | str | OpenMMQuantity) -> Quantity:
    if "openmm" in quantity.__class__.__module__:
        from openff.units.openmm import from_openmm

        return from_openmm(quantity)
    try:
        return Quantity(quantity)
    except Exception as error:
        raise ValueError from error


def has_compatible_dimensionality(quantity: Quantity, unit: str) -> Quantity:
    if quantity.is_compatible_with(unit):
        return quantity
    else:
        raise ValueError(f"Dimensionality must be compatible with unit {unit}")


def build_dimension_type(unit: str) -> type[Quantity]:
    """Return an Annotated type for dimensnional compatibility with a unit."""
    return Annotated[  # type: ignore[return-value]
        Quantity,
        BeforeValidator(to_quantity),
        AfterValidator(partial(has_compatible_dimensionality, unit=unit)),
    ]


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
