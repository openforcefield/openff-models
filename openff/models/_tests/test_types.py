import json

import numpy
import pytest
from pydantic import ValidationError

from openff.models.models import DefaultModel
from openff.units import Quantity, unit
from openff.utilities.testing import skip_if_missing


class ArrayQuantity:
    pass


class FloatQuantity:
    pass


@pytest.mark.skip(reason="Behavior needs to be rewritten into new classes")
class TestQuantityTypes:
    @skip_if_missing("openmm.unit")
    def test_array_quantity_tuples(self):
        """Test that nested tuples are processed. This is relevant for how OpenMM stores
        periodic box vectors as a tuple of tuples."""
        import openmm.unit

        class BoxModel(DefaultModel):
            box_vectors: ArrayQuantity["nanometer"]

        as_tuple = ((4, 0, 0), (0, 4, 0), (0, 0, 4)) * openmm.unit.nanometer
        as_array = numpy.eye(3) * 4 * openmm.unit.nanometer

        assert numpy.allclose(
            BoxModel(box_vectors=as_tuple).box_vectors,
            BoxModel(box_vectors=as_array).box_vectors,
        )

    @pytest.mark.parametrize("val", [True, 1])
    def test_bad_array_quantity_type(self, val):

        class Model(DefaultModel):
            a: ArrayQuantity["atomic_mass_constant"]

        with pytest.raises(
            ValidationError, match=r"Could not validate data of type .*[bool|int].*"
        ):
            Model(a=val)

    @skip_if_missing("unyt")
    def test_unyt_quantities(self):
        import unyt

        class Subject(DefaultModel):
            age: FloatQuantity["year"]
            height: FloatQuantity["centimeter"]
            doses: ArrayQuantity["milligram"]

        subject = Subject(
            age=20.0,  # here would be a good place to test IntQuantity if it ever exists
            height=170.0 * unyt.cm,
            doses=[2, 1, 1] * unyt.gram,
        )

        # Ensure unyt scalars (unyt.unyt_quantity) are stored as floats
        assert type(subject.age.m) is float
        assert type(subject.height.m) is float
        assert type(subject.doses.m) is numpy.ndarray

    @skip_if_missing("unyt")
    @skip_if_missing("openmm.unit")
    def test_setters(self):
        import openmm.unit
        import unyt

        class SimpleModel(DefaultModel):
            data: ArrayQuantity["second"]

        reference = SimpleModel(data=[3, 2, 1])
        model = SimpleModel(**reference.dict())

        for new_data in [
            [3, 2, 1] * unit.second,
            [3, 2, 1] * openmm.unit.second,
            numpy.asarray([3, 2, 1]) * openmm.unit.second,
            [3, 2, 1] * unyt.second,
        ]:
            model.data = new_data
            assert all(model.data == reference.data)

    def test_float_and_quantity_type(self):
        class MixedModel(DefaultModel):
            scalar_data: FloatQuantity
            array_data: ArrayQuantity
            name: str

        m = MixedModel(
            scalar_data=1.0 * unit.meter, array_data=[-1, 0] * unit.second, name="foo"
        )

        assert json.loads(m.json()) == {
            "scalar_data": '{"val": 1.0, "unit": "meter"}',
            "array_data": '{"val": [-1, 0], "unit": "second"}',
            "name": "foo",
        }

        parsed = MixedModel.parse_raw(m.json())

        for key in m.dict().keys():
            try:
                assert getattr(m, key) == getattr(parsed, key)
            except ValueError:
                assert all(getattr(m, key) == getattr(parsed, key))

    def test_model_missing_units(self):
        class ImplicitModel(DefaultModel):
            implicit_float: FloatQuantity = None
            implicit_array: ArrayQuantity = None
            explicit_float: FloatQuantity["dimensionless"] = None
            explicit_array: ArrayQuantity["dimensionless"] = None

        # Ensure the model can be constructed with units passed to implicit-unit fields
        m = ImplicitModel(
            implicit_float=4 * unit.dimensionless,
            implicit_array=[4] * unit.dimensionless,
            explicit_float=4,
            explicit_array=[4],
        )

        assert m.implicit_float == m.explicit_float
        assert m.implicit_array[0] == m.implicit_array

        with pytest.raises(ValidationError, match=r"Value 4.0 .*a unit.*"):
            ImplicitModel(implicit_float=4.0)

        with pytest.raises(ValidationError, match=r".*Value \[4.0\].*a unit.*"):
            ImplicitModel(implicit_array=[4.0])

    def test_model_mutability(self):
        class Model(DefaultModel):
            time: FloatQuantity["second"]
            lengths: ArrayQuantity["nanometer"]

        m = Model(time=10 * unit.second, lengths=[0.3, 0.5] * unit.nanometer)

        m.time = 0.5 * unit.minute
        m.lengths = [4.0, 1.0] * unit.angstrom

        assert m.time == 30 * unit.second
        assert (numpy.isclose(m.lengths, [0.4, 0.1] * unit.nanometer)).all()

        with pytest.raises(ValidationError, match="1 validation error for Model"):
            m.time = 1 * unit.gram

        with pytest.raises(ValidationError, match="1 validation error for Model"):
            m.lengths = 1 * unit.joule


@pytest.mark.skip(reason="Behavior needs to be rewritten into new classes")
@skip_if_missing("openmm.unit")
def test_is_openmm_quantity():
    import openmm.unit

    from openff.models.types import _is_openmm_quantity

    assert _is_openmm_quantity(openmm.unit.Quantity(1, openmm.unit.nanometer))
    assert not _is_openmm_quantity(unit.Quantity(1, unit.nanometer))


@pytest.mark.skip(reason="Behavior needs to be rewritten into new classes")
@skip_if_missing("openmm.unit")
def test_from_omm_quantity():
    import openmm.unit

    from openff.models.types import _from_omm_quantity

    from_list = _from_omm_quantity([1, 0] * openmm.unit.second)
    from_array = _from_omm_quantity(numpy.asarray([1, 0]) * openmm.unit.second)
    assert all(from_array == from_list)

    with pytest.raises(UnitValidationError):
        _from_omm_quantity(True * openmm.unit.femtosecond)


@pytest.mark.skip(reason="Behavior needs to be rewritten into new classes")
@skip_if_missing("openmm.unit")
def test_from_omm_box_vectors():
    """Reproduce issue #35."""
    import openmm
    import openmm.unit

    # mimic the output of getDefaultPeriodicBoxVectors, which returns
    # list[openmm.unit.Quantity[openmm.unit.Vec3]]
    box_vectors = [
        openmm.unit.Quantity(openmm.Vec3(x=4, y=0, z=0), openmm.unit.nanometer),
        openmm.unit.Quantity(openmm.Vec3(x=0, y=2, z=0), openmm.unit.nanometer),
        openmm.unit.Quantity(openmm.Vec3(x=0, y=0, z=5), openmm.unit.nanometer),
    ]

    validated = ArrayQuantity.validate_type(box_vectors)

    assert isinstance(validated, Quantity)

    assert validated.shape == (3, 3)
    assert validated.m.shape == (3, 3)
    assert validated.units == unit.nanometer

    for index, value in enumerate([4, 2, 5]):
        assert validated.m[index][index] == value
