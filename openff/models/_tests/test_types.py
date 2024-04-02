import json

import numpy
import pytest
from openff.units import Quantity, unit
from openff.utilities.testing import skip_if_missing
from pydantic import ValidationError

from openff.models.dimension_types import LengthQuantity, MassQuantity, TimeQuantity
from openff.models.models import DefaultModel


class TestQuantityTypes:
    @skip_if_missing("openmm.unit")
    def test_array_quantity_tuples(self):
        """Test that nested tuples are processed. This is relevant for how OpenMM stores
        periodic box vectors as a tuple of tuples."""
        import openmm.unit

        class BoxModel(DefaultModel):
            box_vectors: LengthQuantity

        as_tuple = ((4, 0, 0), (0, 4, 0), (0, 0, 4)) * openmm.unit.nanometer
        as_array = numpy.eye(3) * 4 * openmm.unit.nanometer

        assert numpy.allclose(
            BoxModel(box_vectors=as_tuple).box_vectors,
            BoxModel(box_vectors=as_array).box_vectors,
        )

    @skip_if_missing("unyt")
    def test_unyt_quantities(self):
        import unyt

        class Subject(DefaultModel):
            age: TimeQuantity
            height: LengthQuantity
            weight: MassQuantity

        subject = Subject(
            age=Quantity(20.0, "year"),
            height=170.0 * unyt.cm,
            weight=[100, 110, 80] * unyt.kilogram,
        )

        # Ensure unyt scalars (unyt.unyt_quantity) are stored as floats
        assert type(subject.age.m) is float
        assert type(subject.height.m) is float
        assert type(subject.weight.m) is numpy.ndarray

    @skip_if_missing("unyt")
    @skip_if_missing("openmm.unit")
    def test_setters(self):
        import openmm.unit
        import unyt

        class SimpleModel(DefaultModel):
            data: TimeQuantity

        reference = SimpleModel(data=Quantity([3, 2, 1], "second"))
        model = SimpleModel(**reference.model_dump())

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
            scalar_data: LengthQuantity
            array_data: LengthQuantity
            name: str

        m = MixedModel(
            scalar_data=1.0 * unit.meter, array_data=[-1, 0] * unit.second, name="foo"
        )

        assert json.loads(m.model_dump_json()) == {
            "scalar_data": '{"val": 1.0, "unit": "meter"}',
            "array_data": '{"val": [-1, 0], "unit": "second"}',
            "name": "foo",
        }

        parsed = MixedModel.model_validate_json(m.model_dump_json())

        for key in m.dict().keys():
            try:
                assert getattr(m, key) == getattr(parsed, key)
            except ValueError:
                assert all(getattr(m, key) == getattr(parsed, key))

    def test_model_mutability(self):
        class Model(DefaultModel):
            time: TimeQuantity
            lengths: LengthQuantity

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

    validated = LengthQuantity.validate_type(box_vectors)

    assert isinstance(validated, Quantity)

    assert validated.shape == (3, 3)
    assert validated.m.shape == (3, 3)
    assert validated.units == unit.nanometer

    for index, value in enumerate([4, 2, 5]):
        assert validated.m[index][index] == value
