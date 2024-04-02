from functools import partial
from typing import Annotated, Any

from openff.units import Quantity
from pydantic import AfterValidator, BeforeValidator

from openff.models.types import json_loader

from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
)
from pydantic.functional_validators import WrapValidator

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


def coerce_json_back_to_quantity(
    v: Any,
    handler: ValidatorFunctionWrapHandler,
    info: ValidationInfo
) -> dict:
    if info.mode == 'json':
        if isinstance(v, str):

            return Quantity(*json_loader(v).values())
        else:
            raise ValueError('In JSON mode the input must be a string!')

    if info.mode == 'python':
        if isinstance(v, dict):
            return Quantity(*v.values())
        elif isinstance(v, Quantity):
            return v
        else:
            raise ValueError(f'In Python mode the input must be a dict! Found {type(v)}')

    # maybe what is currently to_quantity should simply be wrapped into here?

    return v


def build_dimension_type(unit: str) -> type[Quantity]:
    """Return an Annotated type for dimensnional compatibility with a unit."""
    return Annotated[  # type: ignore[return-value]
        Quantity,
        BeforeValidator(to_quantity),
        AfterValidator(partial(has_compatible_dimensionality, unit=unit)),
        WrapValidator(coerce_json_back_to_quantity)

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
