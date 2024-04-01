import json

import numpy as np
import pytest
from pydantic import ValidationError

from openff.models.dimension_types import (
    AngleQuantity,
    ChargeQuantity,
    DistanceQuantity,
    LengthQuantity,
)
from openff.models.models import DefaultModel
from openff.models.unit_types import (
    OnlyAMUQuantity,
    OnlyDegreeQuantity,
    OnlyElementaryChargeQuantity,
)
from openff.units import Quantity, unit
from openff.units.openmm import from_openmm
from openff.utilities.testing import skip_if_missing


class FloatQuantity:
    pass


@pytest.mark.skip(reason="Behavior needs to be rewritten into new classes")
class TestAnnotatedTypes:
    @skip_if_missing("openmm.unit")
    def test_float_quantity_model(self):
        import openmm.unit

        class Atom(DefaultModel):
            mass: OnlyAMUQuantity
            charge: ChargeQuantity
            foo: Quantity
            fuu: Quantity
            bar: AngleQuantity
            barint: AngleQuantity
            baz: LengthQuantity
            qux: DistanceQuantity
            quix: LengthQuantity
            quux: int
            fnord: float
            fum: str
            zot: list
            fred: dict

        a = Atom(
            mass=4,
            charge=0 * unit.elementary_charge,
            foo=2.0 * unit.nanometer,
            fuu=from_openmm(2.0 * openmm.unit.nanometer),  # hack
            bar="90.0 degree",
            barint="90 degree",
            baz=0.4 * openmm.unit.nanometer,
            qux=openmm.unit.Quantity(np.float64(0.4), openmm.unit.nanometer),
            quix=openmm.unit.Quantity(2, openmm.unit.nanometer),
            quux=1,
            fnord=4.2,
            fum="fum",
            zot=["zot", 1, 4.2],
            fred={"baz": 2},
        )

        assert a.mass == 4.0 * unit.atomic_mass_constant
        assert a.charge == 0 * unit.elementary_charge  # this previously was 0.0
        assert isinstance(a.charge.m, int)  # was previously coerced to float
        assert a.foo == 2.0 * unit.nanometer
        assert a.fuu == 2.0 * unit.nanometer
        assert a.bar == 90 * unit.degree
        assert a.barint == 90 * unit.degree  # previously was 90.0
        assert isinstance(a.barint.m, int)  # was previously coerced to float
        assert a.baz == 0.4 * unit.nanometer
        assert a.qux == 0.4 * unit.nanometer
        assert a.quix == 2.0 * unit.nanometer
        assert isinstance(a.quix.m, int)
        assert a.quux == 1
        assert a.fnord == 4.2
        assert a.fum == "fum"
        assert a.zot == ["zot", 1, 4.2]
        assert a.fred == {"baz": 2}

        # TODO: Update with custom deserialization to == a.dict()
        assert json.loads(a.model_dump_json()) == {
            "mass": '{"val": 4, "unit": "unified_atomic_mass_unit"}',
            "charge": '{"val": 0, "unit": "elementary_charge"}',
            "foo": '{"val": 2.0, "unit": "nanometer"}',
            "fuu": '{"val": 2.0, "unit": "nanometer"}',
            "bar": '{"val": 90.0, "unit": "degree"}',
            "barint": '{"val": 90, "unit": "degree"}',
            "baz": '{"val": 0.4, "unit": "nanometer"}',
            "qux": '{"val": 0.4, "unit": "nanometer"}',
            "quix": '{"val": 2, "unit": "nanometer"}',
            "quux": 1,
            "fnord": 4.2,
            "fum": "fum",
            "zot": ["zot", 1, 4.2],
            "fred": {"baz": 2},
        }

        parsed = Atom.model_validate_json(a.model_dump_json())
        assert a == parsed

        assert Atom(**a.model_dump()) == a

    @pytest.mark.parametrize("val", [True, [1]])
    def test_bad_float_quantity_type(self, val):
        class Model(DefaultModel):
            a: FloatQuantity["atomic_mass_constant"]  # noqa

        with pytest.raises(
            ValidationError,
            match=r"Could not validate data of type .*[bool|list].*",
        ):
            Model(a=val)

    @skip_if_missing("openmm.unit")
    def test_array_quantity_model(self):
        import openmm.unit

        class Molecule(DefaultModel):
            masses: OnlyAMUQuantity
            charges: OnlyElementaryChargeQuantity
            other: ChargeQuantity
            foo: Quantity
            bar: OnlyDegreeQuantity
            baz: OnlyAMUQuantity

        m = Molecule(
            masses=[16, 1, 1],
            charges=np.asarray([-1, 0.5, 0.5]),
            other=[2.0, 2.0] * openmm.unit.elementary_charge,
            foo=np.array([2.0, -2.0, 0.0]) * unit.nanometer,
            bar=[0, 90, 180],
            baz=np.array([3, 2, 1]).tobytes(),
        )

        assert json.loads(m.model_dump_json()) == {
            "masses": '{"val": [16, 1, 1], "unit": "unified_atomic_mass_unit"}',
            "charges": '{"val": [-1.0, 0.5, 0.5], "unit": "elementary_charge"}',
            "other": '{"val": [2.0, 2.0], "unit": "elementary_charge"}',
            "foo": '{"val": [2.0, -2.0, 0.0], "unit": "nanometer"}',
            "bar": '{"val": [0, 90, 180], "unit": "degree"}',
            "baz": '{"val": [3, 2, 1], "unit": "unified_atomic_mass_unit"}',
        }

        parsed = Molecule.model_validate(m.model_dump())

        # TODO: Better Model __eq__; Pydantic models just looks at their .dicts, which doesn't
        # play nicely with arrays out of the box
        assert parsed.model_fields == m.model_fields

        for key in m.model_dump().keys():
            try:
                assert getattr(m, key) == getattr(parsed, key)
            except ValueError:
                assert all(getattr(m, key) == getattr(parsed, key))
