import pytest
from openff.units import Quantity, unit
from pydantic import BaseModel

from openff.models.annotations import FloatQuantity, IntQuantity


class ImplicitUnitsIntModel(BaseModel):
    int_quantity: IntQuantity


class ImplicitUnitsFloatModel(BaseModel):
    float_quantity: FloatQuantity


class TestImplicitUnitsIntQuantity:
    _MODEL = ImplicitUnitsIntModel

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
        ],
    )
    def test_supported_inputs(self, input):
        model = self._MODEL(int_quantity=input)

        assert isinstance(model, self._MODEL)
        assert isinstance(model.int_quantity, Quantity)
        assert isinstance(model.int_quantity.m, int)

        assert self._MODEL.model_validate_json(
            model.model_dump_json(),
        ).int_quantity == unit.Quantity(int(input))

    @pytest.mark.parametrize(
        "input",
        [
            "test",
            None,
            Quantity,
        ],
    )
    def test_unsupported_inputs(self, input):
        with pytest.raises(
            ValueError,
            match=f"Input should be an instance.*{input.__class__.__name__}",
        ):
            self._MODEL(int_quantity=input)

    @pytest.mark.parametrize(
        "input",
        [
            unit.Quantity(4, "picosecond"),
            unit.Quantity(2, "kilojoule_per_mole"),
        ],
    )
    def test_incompatible_units(self, input):
        with pytest.raises(
            ValueError,
            match=f"Cannot convert.*{str(input.units)} to dimensionless",
        ):
            self._MODEL(int_quantity=input)


class TestImplicitUnitsFloatQuantity:
    _MODEL = ImplicitUnitsFloatModel

    @pytest.mark.parametrize(
        "input",
        [
            0,
            1,
            2,
            0.0,
            1.0,
            2.0,
            Quantity(0.0),
            Quantity(1.0),
            Quantity(2.0),
        ],
    )
    def test_supported_inputs(self, input):
        model = self._MODEL(float_quantity=input)

        assert isinstance(model, self._MODEL)
        assert isinstance(model.float_quantity, Quantity)
        assert isinstance(model.float_quantity.m, float)

        assert self._MODEL.model_validate_json(
            model.model_dump_json(),
        ).float_quantity == unit.Quantity(float(input))

    @pytest.mark.parametrize(
        "input",
        [
            "test",
            None,
            Quantity,
        ],
    )
    def test_unsupported_inputs(self, input):
        with pytest.raises(
            ValueError,
            match=f"Input should be an instance.*{input.__class__.__name__}",
        ):
            self._MODEL(float_quantity=input)


class ExplicitUnitsIntModel(BaseModel):
    int_quantity: IntQuantity["nanometer"]  # type: ignore


class ExplicitUnitsFloatModel(BaseModel):
    float_quantity: FloatQuantity["nanometer"]  # type: ignore


class TestExplicitUnitsIntQuantity:
    _MODEL = ExplicitUnitsIntModel

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
        model = self._MODEL(int_quantity=input)

        assert isinstance(model, self._MODEL)
        assert isinstance(model.int_quantity, Quantity)
        assert isinstance(model.int_quantity.m, int)

        # TODO: JSON roundtrip

    @pytest.mark.parametrize(
        "input",
        [
            "test",
            None,
            Quantity,
        ],
    )
    def test_unsupported_inputs(self, input):
        with pytest.raises(
            ValueError,
            match=f"Input should be an instance.*{input.__class__.__name__}",
        ):
            self._MODEL(int_quantity=input)

    @pytest.mark.parametrize(
        "input",
        [
            unit.Quantity(4, "picosecond"),
            unit.Quantity(2, "kilojoule_per_mole"),
        ],
    )
    def test_incompatible_units(self, input):
        with pytest.raises(
            ValueError,
            match=f"Cannot convert.*{str(input.units)} to nanometer",
        ):
            self._MODEL(int_quantity=input)

    def test_compatible_units(self):
        model = self._MODEL(int_quantity=Quantity(200, "angstrom"))
        assert model.int_quantity == Quantity(20, "nanometer")


class TestExplicitUnitsFloatQuantity:
    _MODEL = ExplicitUnitsFloatModel

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
        model = self._MODEL(float_quantity=input)

        assert isinstance(model, self._MODEL)
        assert isinstance(model.float_quantity, Quantity)
        assert isinstance(model.float_quantity.m, float)

        # TODO: JSON roundtrip

    @pytest.mark.parametrize(
        "input",
        [
            "test",
            None,
            Quantity,
        ],
    )
    def test_unsupported_inputs(self, input):
        with pytest.raises(
            ValueError,
            match=f"Input should be an instance.*{input.__class__.__name__}",
        ):
            self._MODEL(float_quantity=input)

    @pytest.mark.parametrize(
        "input",
        [
            unit.Quantity(4, "picosecond"),
            unit.Quantity(2, "kilojoule_per_mole"),
        ],
    )
    def test_incompatible_units(self, input):
        with pytest.raises(
            ValueError,
            match=f"Cannot convert.*{str(input.units)} to nanometer",
        ):
            self._MODEL(float_quantity=input)

    def test_compatible_units(self):
        model = self._MODEL(float_quantity=Quantity(200, "angstrom"))
        assert model.float_quantity == Quantity(20.0, "nanometer")
