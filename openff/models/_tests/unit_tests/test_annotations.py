import numpy
import pytest
from openff.units import Quantity, Unit
from pydantic import BaseModel

from openff.models.annotations import ArrayQuantity, FloatQuantity, IntQuantity


class ImplicitUnitsIntModel(BaseModel):
    quantity: IntQuantity


class ImplicitUnitsFloatModel(BaseModel):
    quantity: FloatQuantity


class ImplicitUnitsArrayModel(BaseModel):
    quantity: ArrayQuantity


class ExplicitUnitsIntModel(BaseModel):
    quantity: IntQuantity["nanometer"]  # type: ignore


class ExplicitUnitsFloatModel(BaseModel):
    quantity: FloatQuantity["nanometer"]  # type: ignore


class ExplicitUnitsArrayModel(BaseModel):
    quantity: ArrayQuantity["nanometer"]  # type: ignore


class _BaseMixin:
    @pytest.mark.parametrize(
        "input",
        [
            "test",
            str,
            None,
            Quantity,
        ],
    )
    def test_unsupported_inputs(self, input):
        with pytest.raises(
            ValueError,
            match=f"Input should be an instance.*{input.__class__.__name__}",
        ):
            self._MODEL(quantity=input)

    @pytest.mark.parametrize(
        "input",
        [
            Quantity(4, "picosecond"),
            Quantity(2, "kilojoule_per_mole"),
        ],
    )
    def test_incompatible_units(self, input):
        with pytest.raises(
            ValueError,
            match=f"Cannot convert.*{str(input.units)} to {self._UNIT}",
        ):
            self._MODEL(quantity=input)


class _ImplicitModelsMixin(_BaseMixin):
    _UNIT = "dimensionless"

    @pytest.mark.parametrize(
        "input",
        [
            0,
            1,
            2,
            0.0,
            1.0,
            2.0,
            Quantity(0),
            Quantity(1),
            Quantity(2),
            Quantity(0.0),
            Quantity(1.0),
            Quantity(2.0),
        ],
    )
    def test_supported_inputs(self, input):
        model = self._MODEL(quantity=input)

        assert isinstance(model, self._MODEL)
        assert isinstance(model.quantity, Quantity)
        assert isinstance(model.quantity.m, self._TYPE)

        assert self._MODEL.model_validate_json(
            model.model_dump_json(),
        ).quantity == Quantity(self._TYPE(input))


class TestImplicitUnitsIntQuantity(_ImplicitModelsMixin):
    _MODEL = ImplicitUnitsIntModel
    _TYPE = int


class TestImplicitUnitsFloatQuantity(_ImplicitModelsMixin):
    _MODEL = ImplicitUnitsFloatModel
    _TYPE = float


class _ExplicitModelsMixin(_BaseMixin):
    _UNIT = "nanometer"

    @pytest.mark.parametrize(
        "input",
        [
            0,
            1,
            2,
            0.0,
            1.0,
            2.0,
            Quantity(0, "nanometer"),
            Quantity(1, "nanometer"),
            Quantity(2, "nanometer"),
        ],
    )
    def test_supported_inputs(self, input):
        model = self._MODEL(quantity=input)

        assert isinstance(model, self._MODEL)
        assert isinstance(model.quantity, Quantity)
        assert isinstance(model.quantity.m, self._TYPE)
        assert model.quantity.units == Unit(self._UNIT)

        # TODO: JSON roundtrip

    def test_compatible_units(self):
        model = self._MODEL(quantity=Quantity(200.0, "angstrom"))
        assert model.quantity == Quantity(self._TYPE(20), "nanometer")


class TestExplicitUnitsIntQuantity(_ExplicitModelsMixin):
    _MODEL = ExplicitUnitsIntModel
    _TYPE = int


class TestExplicitUnitsFloatQuantity(_ExplicitModelsMixin):
    _MODEL = ExplicitUnitsFloatModel
    _TYPE = float


class TestImplicitUnitsArrayQuantity:
    _MODEL = ImplicitUnitsArrayModel
    _TYPE = numpy.ndarray

    @pytest.mark.parametrize(
        "input",
        [
            [0.0],
            [2.0, 1.0],
            numpy.array([0.0]),
            numpy.array([2.0, 1.0]),
            Quantity([0.0]),
            Quantity([2.0, 1.0]),
            Quantity(numpy.array([0.0])),
            Quantity(numpy.array([2.0, 1.0])),
        ],
    )
    def test_supported_inputs(self, input):
        model = self._MODEL(quantity=input)

        assert isinstance(model, self._MODEL)
        assert isinstance(model.quantity, Quantity)
        assert isinstance(model.quantity.m, self._TYPE)

        # TODO: JSON roundtrip


class _ArrayModelsMixin:
    @pytest.mark.parametrize(
        "input",
        [
            Quantity("test", "second"),
            Quantity(str),
            Quantity(type(None), "femtojoule"),
            Quantity(Quantity),
        ],
    )
    def test_unsupported_wrapped_inputs(self, input):
        with pytest.raises(
            ValueError,
            match=f"Input should be an instance.*{input.__class__.__name__}",
        ):
            self._MODEL(quantity=input)

    @pytest.mark.parametrize(
        "input",
        [
            Quantity([2], "picosecond"),
            Quantity([3], "kilojoule_per_mole"),
        ],
    )
    def test_incompatible_units(self, input):
        with pytest.raises(
            ValueError,
            match=f"Cannot convert.*{str(input.units)} to {self._UNIT}",
        ):
            self._MODEL(quantity=input)


class TestImplicitUnits(_ArrayModelsMixin):
    _MODEL = ImplicitUnitsArrayModel
    _TYPE = numpy.ndarray
    _UNIT = "dimensionless"

    @pytest.mark.parametrize(
        "input",
        [
            [0.0],
            [2.0, 1.0],
            numpy.array([0.0]),
            numpy.array([2.0, 1.0]),
            Quantity([0.0]),
            Quantity([2.0, 1.0]),
            Quantity(numpy.array([0.0])),
            Quantity(numpy.array([2.0, 1.0])),
        ],
    )
    def test_supported_inputs(self, input):
        model = self._MODEL(quantity=input)

        assert isinstance(model, self._MODEL)
        assert isinstance(model.quantity, Quantity)
        assert isinstance(model.quantity.m, self._TYPE)

        # TODO: JSON roundtrip


class TestExplicitUnitsArrayQuantity(_ArrayModelsMixin):
    _MODEL = ExplicitUnitsArrayModel
    _TYPE = numpy.ndarray
    _UNIT = "nanometer"

    @pytest.mark.parametrize(
        "input",
        [
            [0.0],
            [2.0, 1.0],
            numpy.array([0.0]),
            numpy.array([2.0, 1.0]),
            Quantity([0.0], "nanometer"),
            Quantity([2.0, 1.0], "nanometer"),
            Quantity(numpy.array([0.0]), "nanometer"),
            Quantity(numpy.array([2.0, 1.0]), "nanometer"),
        ],
    )
    def test_supported_inputs(self, input):
        model = self._MODEL(quantity=input)

        assert isinstance(model, self._MODEL)
        assert isinstance(model.quantity, Quantity)
        assert isinstance(model.quantity.m, self._TYPE)

        # TODO: JSON roundtrip

    def test_compatible_units(self):
        model = self._MODEL(quantity=Quantity([200.0, 100.0], "angstrom"))
        numpy.testing.assert_equal(model.quantity.m, [20.0, 10.0])
