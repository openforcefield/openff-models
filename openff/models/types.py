"""Custom models for dealing with unit-bearing quantities in a Pydantic-compatible manner."""
import collections
import json
from typing import TYPE_CHECKING, Any, Dict

import numpy as np
from openff.units import unit
from openff.utilities.utilities import has_package, requires_package
from openmm import unit as openmm_unit

from openff.models.exceptions import (
    MissingUnitError,
    UnitValidationError,
    UnsupportedExportError,
)


class _FloatQuantityMeta(type):
    def __getitem__(self, t):
        return type("FloatQuantity", (FloatQuantity,), {"__unit__": t})


if TYPE_CHECKING:
    FloatQuantity = unit.Quantity  # np.ndarray
else:

    class FloatQuantity(float, metaclass=_FloatQuantityMeta):
        """A model for unit-bearing floats."""

        @classmethod
        def __get_validators__(cls):
            yield cls.validate_type

        @classmethod
        def validate_type(cls, val):
            """Process a value tagged with units into one tagged with "OpenFF" style units."""
            unit_ = getattr(cls, "__unit__", Any)
            if unit_ is Any:
                if isinstance(val, (float, int)):
                    # TODO: Can this exception be raised with knowledge of the field it's in?
                    raise MissingUnitError(
                        f"Value {val} needs to be tagged with a unit"
                    )
                elif isinstance(val, unit.Quantity):
                    return unit.Quantity(val)
                elif isinstance(val, openmm_unit.Quantity):
                    return _from_omm_quantity(val)
                else:
                    raise UnitValidationError(
                        f"Could not validate data of type {type(val)}"
                    )
            else:
                unit_ = unit(unit_)
                if isinstance(val, unit.Quantity):
                    # some custom behavior could go here
                    assert unit_.dimensionality == val.dimensionality
                    # return through converting to some intended default units (taken from the class)
                    return val.to(unit_)
                    # could return here, without converting
                    # (could be inconsistent with data model - heteregenous but compatible units)
                    # return val
                if isinstance(val, openmm_unit.Quantity):
                    return _from_omm_quantity(val).to(unit_)
                if isinstance(val, (float, int)) and not isinstance(val, bool):
                    return val * unit_
                if isinstance(val, str):
                    # could do custom deserialization here?
                    return unit.Quantity(val).to(unit_)
                raise UnitValidationError(
                    f"Could not validate data of type {type(val)}"
                )


def _from_omm_quantity(val: openmm_unit.Quantity):
    """
    Convert float or array quantities tagged with SimTK/OpenMM units to a Pint-compatible quantity.
    """
    unit_ = val.unit
    val_ = val.value_in_unit(unit_)
    if type(val_) in {float, int}:
        unit_ = val.unit
        return val_ * unit.Unit(str(unit_))
    # Here is where the toolkit's ValidatedList could go, if present in the environment
    elif type(val_) in {tuple, list, np.ndarray}:
        array = np.asarray(val_)
        return array * unit.Unit(str(unit_))
    elif isinstance(val_, (float, int)) and type(val_).__module__ == "numpy":
        return val_ * unit.Unit(str(unit_))
    else:
        raise UnitValidationError(
            "Found a openmm.unit.Unit wrapped around something other than a float-like "
            f"or np.ndarray-like. Found a unit wrapped around type {type(val_)}."
        )



class QuantityEncoder(json.JSONEncoder):
    """
    JSON encoder for unit-wrapped floats and NumPy arrays.

    This is intended to operate on FloatQuantity and ArrayQuantity objects.
    """

    def default(self, obj):  # noqa
        if isinstance(obj, unit.Quantity):
            if isinstance(obj.magnitude, (float, int)):
                data = obj.magnitude
            elif isinstance(obj.magnitude, np.ndarray):
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


# Inspired from https://stackoverflow.com/a/47049015/2525806
def dict_from_string(data):

    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = dict_from_string(value)

    elif isinstance(data, list):
        result = []
        for item in data:
            result.append(dict_from_string(item))

    elif isinstance(data, tuple):
        aux = []
        for item in data:
            aux.append(dict_from_string(item))
        result = tuple(aux)

    elif isinstance(data, str):
        try:
            result = dict_from_string(json.loads(data))
        except(json.JSONDecodeError):
            result = data

    elif isinstance(data, (int, float, type(None), bool)):
        result = data

    else:
        raise ValueError("unexpected type")

    return result


def unitfy_dict(data):
    for key, value in data.items():
        if isinstance(value, dict):
            if "val" in value:
                unit_ = unit(value["unit"])
                val = value["val"]
                data[key] = unit_ * val
            else:
                data[key] = unitfy_dict(value)
    return data


def json_loader(data: str) -> dict:
    """Load JSON containing custom unit-tagged quantities."""
    out = dict_from_string(data)
    unitfy_dict(out)
    return out


class _ArrayQuantityMeta(type):
    def __getitem__(self, t):
        return type("ArrayQuantity", (ArrayQuantity,), {"__unit__": t})


if TYPE_CHECKING:
    ArrayQuantity = unit.Quantity  # np.ndarray
else:

    class ArrayQuantity(float, metaclass=_ArrayQuantityMeta):
        """A model for unit-bearing arrays."""

        @classmethod
        def __get_validators__(cls):
            yield cls.validate_type

        @classmethod
        def validate_type(cls, val):
            """Process an array tagged with units into one tagged with "OpenFF" style units."""
            unit_ = getattr(cls, "__unit__", Any)
            if unit_ is Any:
                if isinstance(val, (list, np.ndarray)):
                    # TODO: Can this exception be raised with knowledge of the field it's in?
                    raise MissingUnitError(
                        f"Value {val} needs to be tagged with a unit"
                    )
                elif isinstance(val, unit.Quantity):
                    # TODO: This might be a redundant cast causing wasted CPU time.
                    #       But maybe it handles pint vs openff.units.unit?
                    return unit.Quantity(val)
                elif isinstance(val, openmm_unit.Quantity):
                    return _from_omm_quantity(val)
                else:
                    raise UnitValidationError(
                        f"Could not validate data of type {type(val)}"
                    )
            else:
                unit_ = unit(unit_)
                if isinstance(val, unit.Quantity):
                    assert unit_.dimensionality == val.dimensionality
                    return val.to(unit_)
                if isinstance(val, openmm_unit.Quantity):
                    return _from_omm_quantity(val).to(unit_)
                if isinstance(val, (np.ndarray, list)):
                    return val * unit_
                if isinstance(val, bytes):
                    # Define outside loop
                    dt = np.dtype(int).newbyteorder("<")
                    return np.frombuffer(val, dtype=dt) * unit_
                if isinstance(val, str):
                    # could do custom deserialization here?
                    raise NotImplementedError
                    #  return unit.Quantity(val).to(unit_)
                raise UnitValidationError(
                    f"Could not validate data of type {type(val)}"
                )
