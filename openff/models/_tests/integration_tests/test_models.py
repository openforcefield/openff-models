import pytest
from openff.units import Quantity, unit

from openff.models.models import DefaultModel
from openff.models.types.dimension_types import LengthQuantity


def test_model_pint_openmm_unit():
    pytest.importorskip("openmm")
    pytest.importorskip("unyt")

    import openmm.unit
    import unyt

    class Bagel(DefaultModel):
        x: LengthQuantity
        y: LengthQuantity
        z: LengthQuantity

    bagel = Bagel(
        x=1.0 * unit.angstrom,
        y=1.0 * openmm.unit.angstrom,
        z=1.0 * unyt.angstrom,
    )

    assert bagel.x == bagel.y == bagel.z == Quantity("1.0 angstrom")
