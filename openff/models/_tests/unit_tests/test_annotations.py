import pytest
from openff.units import Quantity, unit
from pydantic import BaseModel

from openff.models.annotations import FloatQuantity, IntQuantity


class ImplicitUnitIntModel(BaseModel):
    int_quantity: IntQuantity


class ImplicitUnitsFloatModel(BaseModel):
    float_quantity: FloatQuantity


class TestImplicitUnitsIntQuantity:
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
        model = ImplicitUnitIntModel(int_quantity=input)

        assert isinstance(model, ImplicitUnitIntModel)
        assert isinstance(model.int_quantity, Quantity)
        assert isinstance(model.int_quantity.m, int)

        assert ImplicitUnitIntModel.model_validate_json(
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
            ImplicitUnitIntModel(int_quantity=input)


class TestImplicitUnitsFloatQuantity:
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
        model = ImplicitUnitsFloatModel(float_quantity=input)

        assert isinstance(model, ImplicitUnitsFloatModel)
        assert isinstance(model.float_quantity, Quantity)
        assert isinstance(model.float_quantity.m, float)

        assert ImplicitUnitsFloatModel.model_validate_json(
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
            ImplicitUnitsFloatModel(float_quantity=input)


class ExplicitUnitIntModel(BaseModel):
    int_quantity: IntQuantity["nanometer"]


class ExplicitUnitsFloatModel(BaseModel):
    float_quantity: FloatQuantity["nanometer"]


class TestExplicitUnitsIntQuantity:
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
        model = ExplicitUnitIntModel(int_quantity=input)

        assert isinstance(model, ExplicitUnitIntModel)
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
            ExplicitUnitIntModel(int_quantity=input)


class TestExplicitUnitsFloatQuantity:
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
        model = ExplicitUnitsFloatModel(float_quantity=input)

        assert isinstance(model, ExplicitUnitsFloatModel)
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
            ExplicitUnitsFloatModel(float_quantity=input)
