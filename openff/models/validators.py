from typing import Any

from openff.units import Quantity, Unit
from pydantic import ValidationInfo, ValidatorFunctionWrapHandler

from openff.models.types.serialization import dict_to_quantity, json_loader

try:
    from openmm.unit import Quantity as OpenMMQuantity
except ImportError:
    OpenMMQuantity = Any  # type: ignore

try:
    from unyt import unyt_quantity as UnytQuantity
except ImportError:
    UnytQuantity = Any  # type: ignore


def from_unyt(unyt_quantity: Any) -> Quantity:
    return Quantity(unyt_quantity.to_value(), Unit(str(unyt_quantity.units)))


def to_quantity(quantity: Quantity | str | OpenMMQuantity) -> Quantity:
    if "openmm" in quantity.__class__.__module__:
        from openff.units.openmm import from_openmm

        return from_openmm(quantity)
    try:
        return Quantity(quantity)
    except Exception as error:
        raise ValueError from error


def coerce_json_back_to_quantity(
    v: dict | str | Quantity | OpenMMQuantity | UnytQuantity,
    handler: ValidatorFunctionWrapHandler,
    info: ValidationInfo,
) -> Quantity:
    if info.mode == "json":
        if isinstance(v, str):

            return Quantity(*json_loader(v).values())
        else:
            raise ValueError("In JSON mode the input must be a string!")

    if info.mode == "python":
        if isinstance(v, dict):
            return dict_to_quantity(v)
        elif isinstance(v, Quantity):
            return to_quantity(v)
        elif "openmm" in v.__class__.__module__:
            from openff.units.openmm import from_openmm

            return from_openmm(v)

        elif "unyt" in v.__class__.__module__:
            return from_unyt(v)

        else:
            raise ValueError(
                f"In Python mode the input must be a dict! Found {type(v)}"
            )

    return v
