import pytest
from openff.units import Quantity

from openff.models.types.serialization import custom_quantity_encoder


@pytest.mark.parametrize(
    ("value", "unit", "output_"),
    [
        (1.0, "angstrom", '{"val": 1.0, "unit": "angstrom"}'),
        ([2, 3], "picosecond", '{"val": [2, 3], "unit": "picosecond"}'),
    ],
)
def test_custom_quantity_encoder(value, unit, output_):
    assert custom_quantity_encoder(Quantity(value, unit)) == output_
