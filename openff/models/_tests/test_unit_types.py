import numpy
import pytest
from openff.units import Unit

from openff.models.models import DefaultModel
from openff.models.unit_types import OnlyAMUQuantity, OnlyElementaryChargeQuantity


def test_():
    class Molecule(DefaultModel):
        masses: OnlyAMUQuantity
        charges: OnlyElementaryChargeQuantity
        is_virtual_site: list[bool]

    molecule = Molecule(
        masses=[15.999, 1.008, 1.008, 0.0],
        charges=numpy.asarray([0, 0.520, 0.520, -1.040]),
        is_virtual_site=[False, False, False, True],
    )

    assert molecule.masses[-1].units == Unit("amu")
    assert molecule.charges[-1].units == Unit("elementary_charge")

    assert molecule.masses.m_as(Unit("amu")) == pytest.approx(
        [15.999, 1.008, 1.008, 0.0]
    )
    assert molecule.charges.sum().m == 0.0
