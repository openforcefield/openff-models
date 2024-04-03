import numpy
import pytest
from openff.units import Quantity, Unit

from openff.models.models import DefaultModel
from openff.models.types.unit_types import (
    OnlyAMUQuantity,
    OnlyElementaryChargeQuantity,
    quack_into_unit,
)


def test_molecule_model():
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


@pytest.mark.parametrize("unit", ['nanometer', 'angstrom'])
def test_from_omm_box_vectors(unit):
    """Reproduce issue #35."""

    pytest.importorskip("openmm")

    import openmm.unit

    # mimic the output of getDefaultPeriodicBoxVectors, which returns
    # list[openmm.unit.Quantity[openmm.unit.Vec3]]
    box_vectors = [
        openmm.unit.Quantity(openmm.Vec3(x=4, y=0, z=0), openmm.unit.nanometer),
        openmm.unit.Quantity(openmm.Vec3(x=0, y=2, z=0), openmm.unit.nanometer),
        openmm.unit.Quantity(openmm.Vec3(x=0, y=0, z=5), openmm.unit.nanometer),
    ]

    validated = quack_into_unit(box_vectors, unit=unit)

    assert isinstance(validated, Quantity)

    assert validated.shape == (3, 3)
    assert validated.m.shape == (3, 3)
    assert validated.units == Unit(unit)

    for index, value in enumerate(Quantity([4.0, 2.0, 5.0], "nanometer")):
        assert validated[index][index].m_as("nanometer") == pytest.approx(value.m)
