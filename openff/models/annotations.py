from typing import Any, Callable

import numpy
from openff.units import Quantity, Unit
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from openff.models.exceptions import IncompatibleUnitError


class _IntQuantityMeta(type):
    def __getitem__(self, t):
        return type(
            "_IntQuantityPydanticAnnotation",
            (_IntQuantityPydanticAnnotation,),
            {"__unit__": t},
        )


class _FloatQuantityMeta(type):
    def __getitem__(self, t):
        return type(
            "_FloatQuantityPydanticAnnotation",
            (_FloatQuantityPydanticAnnotation,),
            {"__unit__": t},
        )


class _ArrayQuantityMeta(type):
    def __getitem__(self, t):
        return type(
            "_ArrayQuantityPydanticAnnotation",
            (_ArrayQuantityPydanticAnnotation,),
            {"__unit__": t},
        )


class _IntQuantityPydanticAnnotation(int, metaclass=_IntQuantityMeta):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """
        Return a pydantic_core.CoreSchema that behaves in the following ways:

        * ints will be converted to `Quantity`
        * floats will be converted to `Quantity` with the float cast to an int
        * `Quantity` instances will be parsed as `Quantity` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just an int
        """

        def validate_from_int(value: int) -> Quantity:
            return Quantity(value, units=getattr(cls, "__unit__", "dimensionless"))

        def validate_from_float(value: float) -> Quantity:
            return Quantity(int(value), units=getattr(cls, "__unit__", "dimensionless"))

        def validate_from_quantity(value: Quantity) -> Quantity:
            annotated_units = Unit(
                getattr(cls, "__unit__", "dimensionless"),
            )

            if value.units == annotated_units:
                return Quantity(
                    int(value.m),
                    units=annotated_units,
                )

            elif value.units.is_compatible_with(annotated_units):
                return Quantity(
                    int(value.to(annotated_units).m),
                    units=annotated_units,
                )

            else:
                raise IncompatibleUnitError(
                    f"Cannot convert `Quantity` with units {value.units} to {annotated_units}.",
                )

        from_int_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(int),
                core_schema.int_schema(),
                core_schema.no_info_plain_validator_function(validate_from_int),
            ],
        )

        from_float_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(float),
                core_schema.float_schema(),
                core_schema.no_info_plain_validator_function(validate_from_float),
            ],
        )

        from_quantity_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(Quantity),
                core_schema.no_info_plain_validator_function(validate_from_quantity),
            ],
        )

        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.int_schema(),
                    core_schema.no_info_plain_validator_function(validate_from_int),
                ],
            ),
            python_schema=core_schema.union_schema(
                [
                    from_quantity_schema,
                    from_int_schema,
                    from_float_schema,
                ],
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: int(instance.m),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return handler(core_schema.int_schema())


class _FloatQuantityPydanticAnnotation(float, metaclass=_FloatQuantityMeta):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """
        Return a pydantic_core.CoreSchema that behaves in the following ways:

        * floats will be converted to `Quantity`
        * ints will be converted to `Quantity` with the int cast to a float
        * `Quantity` instances will be parsed as `Quantity` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a float
        """

        def validate_from_int(value: int) -> Quantity:
            return Quantity(
                float(value),
                units=getattr(cls, "__unit__", "dimensionless"),
            )

        def validate_from_float(value: float) -> Quantity:
            return Quantity(value, units=getattr(cls, "__unit__", "dimensionless"))

        def validate_from_quantity(value: Quantity) -> Quantity:
            annotated_units = Unit(
                getattr(cls, "__unit__", "dimensionless"),
            )

            if value.units == annotated_units:
                return Quantity(
                    float(value.m),
                    units=annotated_units,
                )

            elif value.units.is_compatible_with(annotated_units):
                return Quantity(
                    float(value.to(annotated_units).m),
                    units=annotated_units,
                )

            else:
                raise IncompatibleUnitError(
                    f"Cannot convert `Quantity` with units {value.units} to {annotated_units}.",
                )

        from_int_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(int),
                core_schema.int_schema(),
                core_schema.no_info_plain_validator_function(validate_from_int),
            ],
        )

        from_float_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(float),
                core_schema.float_schema(),
                core_schema.no_info_plain_validator_function(validate_from_float),
            ],
        )

        from_quantity_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(Quantity),
                core_schema.no_info_plain_validator_function(validate_from_quantity),
            ],
        )

        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.float_schema(),
                    core_schema.no_info_plain_validator_function(validate_from_float),
                ],
            ),
            python_schema=core_schema.union_schema(
                [
                    from_quantity_schema,
                    from_float_schema,
                    from_int_schema,
                ],
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: float(instance.m),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return handler(core_schema.float_schema())


class _ArrayQuantityPydanticAnnotation(float, metaclass=_ArrayQuantityMeta):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """
        Return a pydantic_core.CoreSchema

        """

        def validate_from_list(value: list) -> Quantity:
            return Quantity(
                numpy.array(value),
                units=getattr(cls, "__unit__", "dimensionless"),
            )

        def validate_from_array(value: numpy.ndarray) -> Quantity:
            return Quantity(value, units=getattr(cls, "__unit__", "dimensionless"))

        def validate_from_quantity(value: Quantity) -> Quantity:
            if not isinstance(value.m, (list, numpy.ndarray)):
                raise ValueError(
                    f"Wrapped object must be a list or numpy.ndarray, not {type(value.m)}.",
                )

            annotated_units = Unit(
                getattr(cls, "__unit__", "dimensionless"),
            )

            if value.units == annotated_units:
                return value

            elif value.units.is_compatible_with(annotated_units):
                return Quantity(
                    numpy.array(value.to(annotated_units).m),
                    units=annotated_units,
                )

            else:
                raise IncompatibleUnitError(
                    f"Cannot convert `Quantity` with units {value.units} to {annotated_units}.",
                )

        from_list_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(list),
                core_schema.no_info_plain_validator_function(validate_from_list),
            ],
        )
        from_array_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(numpy.ndarray),
                core_schema.no_info_plain_validator_function(validate_from_array),
            ],
        )

        from_quantity_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(Quantity),
                core_schema.no_info_plain_validator_function(validate_from_quantity),
            ],
        )

        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.float_schema(),
                    core_schema.no_info_plain_validator_function(validate_from_list),
                ],
            ),
            python_schema=core_schema.union_schema(
                [
                    from_quantity_schema,
                    from_array_schema,
                    from_list_schema,
                ],
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: float(instance.m),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return handler(core_schema.float_schema())


# Each of these `Annotated` wrappers will be used as annotations for fields;
IntQuantity = _IntQuantityPydanticAnnotation
FloatQuantity = _FloatQuantityPydanticAnnotation
ArrayQuantity = _ArrayQuantityPydanticAnnotation
