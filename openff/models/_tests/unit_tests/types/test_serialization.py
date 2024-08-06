import pytest
from openff.units import Quantity

from openff.models.types.serialization import custom_quantity_encoder, dict_to_quantity


@pytest.mark.parametrize(
    ("value", "unit", "output_"),
    [
        (1.0, "angstrom", '{"val": 1.0, "unit": "angstrom"}'),
        ([2, 3], "picosecond", '{"val": [2, 3], "unit": "picosecond"}'),
    ],
)
def test_custom_quantity_encoder(value, unit, output_):
    assert custom_quantity_encoder(Quantity(value, unit)) == output_


def test_dict_to_quantity():
    assert dict_to_quantity({"val": 1.0, "unit": "angstrom"}) == Quantity(
        1.0, "angstrom"
    )


def test_bad_dict_to_quantity():
    with pytest.raises(ValueError, match="must have exactly two keys"):
        dict_to_quantity({"val": 1.0, "unit": "angstrom", "extra": "extra"})
    with pytest.raises(ValueError, match="must have exactly two keys"):
        dict_to_quantity({"val": 1.0})

    with pytest.raises(ValueError, match="bad keys.*data"):
        dict_to_quantity({"data": [1, 2], "unit": "angstrom"})
