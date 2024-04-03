import re

import pytest
from openff.units import Quantity, Unit
from pydantic import ValidationError

from openff.models.models import DefaultModel
from openff.models.types.dimension_types import (
    LengthQuantity,
    build_dimension_type,
    has_compatible_dimensionality,
)


@pytest.mark.parametrize(
    (
        "quantity",
        "unit",
        "result",
    ),
    [
        ("1.0 angstrom", "angstrom", True),
        ("1.0 angstrom", "nanometer", True),
        ("1.0 angstrom", "kilometer", True),
        ("1.0 angstrom", "second", False),
        ("1.0 angstrom", "degree", False),
        ("1.0 angstrom", "kelvin", False),
        ("1.0 angstrom", "kilojoule_per_mole", False),
        ("1.0 angstrom", "elementary_charge", False),
        ("1.0 dalton", "amu", True),
        ("1.0 dalton", "angstrom", False),
        ("1.0 second", "angstrom", False),
        ("1.0 degree", "angstrom", False),
        ("1.0 kelvin", "angstrom", False),
        ("1.0 kilojoule_per_mole", "angstrom", False),
        ("1.0 elementary_charge", "angstrom", False),
        ("1.0 kilojoule_per_mole", "kilojoule_per_mole", True),
        ("1.0 kilocalorie_per_mole", "kilojoule_per_mole", True),
    ],
)
def test_has_compatible_dimensionality(quantity, unit, result):

    if result:
        # This function, which lives inside a validator, should return the
        # same quantity back if the dimensionality is compatible
        assert Quantity(quantity) == has_compatible_dimensionality(
            Quantity(quantity),
            unit,
        )
    else:
        # but raise an ValueError (which Pydantic will bubble up to a ValidationError)
        # if it is not
        with pytest.raises(
            ValueError, match=f"Dimensionality must be compatible with unit {unit}"
        ):
            has_compatible_dimensionality(Quantity(quantity), unit)


def test_length_quantity():
    class BondParameter(DefaultModel):
        bond_length: LengthQuantity

    bond = BondParameter(bond_length=Quantity("0.12345 nanometer"))

    assert bond.bond_length.units == Unit("nanometer")
    assert bond.bond_length.m_as(Unit("angstrom")) == pytest.approx(1.2345)

    with pytest.raises(
        ValidationError,
        match=re.compile(
            r"bond_length\n.*Dimensionality must be compatible with unit angstrom.*",
            re.DOTALL,
        ),
    ):
        BondParameter(bond_length=Quantity("1.0 degree"))


def test_build_dimension_type():
    kj_mol_nm2 = build_dimension_type("kilojoule / mole / nanometer ** 2")
    kcal_mol_a2 = build_dimension_type("kilocalorie / mole / angstrom ** 2")

    # These types only check for dimensionality, so k1 and k2 can be either SI or AKMA
    class ForceConstants(DefaultModel):
        k1: kj_mol_nm2
        k2: kcal_mol_a2

    f1 = ForceConstants(
        k1=Quantity("1.0 kilojoule / mole / nanometer ** 2"),
        k2=Quantity("1.0 kilocalorie / mole / angstrom ** 2"),
    )
    f2 = ForceConstants(
        k1=Quantity("1.0 kilocalorie / mole / angstrom ** 2"),
        k2=Quantity("1.0 kilojoule / mole / nanometer ** 2"),
    )

    assert f1.k1.units == Unit("kilojoule / mole / nanometer ** 2")

    assert f1.k2 == f2.k1
    assert f1.k1 == f2.k2

    with pytest.raises(
        ValidationError,
        match=re.compile(
            r"k1\n.*Dimensionality must be compatible with unit kilojoule . mole . nanometer.*k2\n",
            re.DOTALL,
        ),
    ):
        ForceConstants(
            k1=Quantity("1.0 kilojoule / mole"),
            k2=Quantity("1.0 nanometer"),
        )


def test_dimension_type_with_openmm():

    pytest.importorskip("openmm")

    import openmm.unit

    class Position(DefaultModel):
        x: LengthQuantity
        y: LengthQuantity
        z: LengthQuantity

    x, y, z = openmm.unit.Quantity([3, 2, 1], openmm.unit.nanometer)

    position = Position(x=x, y=y, z=z)

    assert position.x.units == Unit("nanometer")
    assert position.y.units == Unit("nanometer")
    assert position.z.units == Unit("nanometer")

    assert position.x.m == 3
    assert position.y.m == 2
    assert position.z.m == 1

    with pytest.raises(
        ValidationError,
        match=re.compile(
            r"2 validation errors for Position.*x.*nanometer\*\*2.*unit=\/nanometer",
            re.DOTALL,
        ),
    ):
        Position(x=x**2, y=y**-1, z=z)
