from openff.units import Quantity, Unit
from openff.units.openmm import from_openmm
from typing import Annotated, TYPE_CHECKING, Any
from pydantic import BeforeValidator, AfterValidator, BaseModel, ValidationError
from functools import partial
from pint import DimensionalityError

try:
    from openmm.unit import Quantity as OpenMMQuantity
except ImportError:
    OpenMMQuantity = Any
if TYPE_CHECKING:
    import openmm.unit


def to_quantity(quantity: Quantity | str | OpenMMQuantity) -> Quantity:
    if "openmm" in quantity.__class__.__module__:
        return from_openmm(quantity)
    try:
        return Quantity(quantity)
    except Exception as error:
        raise ValueError from error


def has_compatible_dimensionality(quantity: Quantity, unit: str) -> Quantity:
    if quantity.is_compatible_with(unit):
        return quantity
    else:
        raise ValueError(
            f"Dimensionality must be compatible with 'unit'",
        )


(
    is_compatible_with_length,
    is_compatible_with_mass,
    is_compatible_with_time,
    is_compatible_with_degree,
    is_compatible_with_temperature,
    is_compatible_with_molar_energy,
    is_compatible_with_charge,
) = (
    partial(has_compatible_dimensionality, unit=unit)
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

(
    LengthQuantity,
    MassQuantity,
    TimeQuantity,
    DegreeQuantity,
    TemperatureQuantity,
    MolarEnergyQuantity,
    ChargeQuantity,
) = (
    Annotated[
        Quantity,
        BeforeValidator(to_quantity),
        AfterValidator(validator),
    ]
    for validator in [
        is_compatible_with_length,
        is_compatible_with_mass,
        is_compatible_with_time,
        is_compatible_with_degree,
        is_compatible_with_temperature,
        is_compatible_with_molar_energy,
        is_compatible_with_charge,
    ]
)

DistanceQuantity = LengthQuantity
AngleQuantity = DegreeQuantity


def quack_into_unit(quantity: float | int | str | Quantity | OpenMMQuantity, unit: str):
    """Like to_quantity, but takes raw numbers and tacks on amu units."""
    if "openmm" in quantity.__class__.__module__:
        return from_openmm(quantity)
    elif isinstance(quantity, Quantity):
        try:
            return quantity.to(Unit(unit))
        except DimensionalityError as error:
            raise ValueError from error
    elif isinstance(quantity, str):
        try:
            return Quantity(quantity).to(Unit(unit))
        except DimensionalityError as error: 
            # should catch other errors here, too, since a lot of stuff can error out
            # from being passed to the Quantity constructor
            raise ValueError from error
    elif isinstance(quantity, (float, int)):
        return Quantity(quantity, unit)
    else:
        raise ValueError


(
    OnlyAMUQuantity,
    OnlyElementaryChargeQuantity,
) = (
    Annotated[
        Quantity,
        BeforeValidator(partial(quack_into_unit, unit=unit)),
    ]
    for unit in [
        "amu",
        "elementary_charge",
    ]
)
