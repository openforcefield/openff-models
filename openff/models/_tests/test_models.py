from pydantic import BaseModel

from openff.models.models import DefaultModel


def test_mixed_models():
    """Ensure models can be created with something else that derives from BaseModel."""

    class OtherModel(BaseModel):
        name: str

    class MixedModel(DefaultModel):
        other_model: OtherModel
        index: int

    MixedModel(
        other_model=OtherModel(name="foo"),
        index=-1,
    )
