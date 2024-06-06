import re

import pytest
from openff.units import Quantity, Unit
from pydantic import ValidationError

from openff.models.dimension_types import LengthQuantity, build_dimension_type
from openff.models.models import DefaultModel


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
    f2 = ForceConstants(k1=f1.k2, k2=f1.k1)

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
