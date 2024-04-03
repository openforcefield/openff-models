from openff.units import Quantity, Unit
from packaging.version import Version
from pydantic import BaseModel, __version__

from openff.models.models import DefaultModel


def test_mixed_models():
    """Ensure models can be created with something else that derives from BaseModel."""

    assert Version(__version__).major == 2

    class OtherModel(BaseModel):
        name: str

    class MixedModel(DefaultModel):
        other_model: OtherModel
        index: int

    mixed_model = MixedModel(
        other_model=OtherModel(name="foo"),
        index=-1,
    )

    class AnotherMixedModel(DefaultModel):
        mixed_model: MixedModel
        energy: Quantity

    assert AnotherMixedModel(
        mixed_model=mixed_model,
        energy=Quantity("1.0 kilojoule_per_mole"),
    ).energy.units == Unit("kilojoule_per_mole")
