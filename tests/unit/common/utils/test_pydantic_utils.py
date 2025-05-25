"""
Unit test for the pydantic_utils module.
"""

from pydantic import BaseModel

from aiden.common.utils.pydantic_utils import merge_models


def test_merge_models():
    """Test merging of Pydantic models."""

    # Define simple test models
    class Model1(BaseModel):
        a: str
        common: int = 1

    class Model2(BaseModel):
        b: str
        common: int = 2

    # Merge models and test the result
    Combined = merge_models("Combined", [Model1, Model2])
    instance = Combined(a="test", b="test")

    # Verify fields and precedence
    assert instance.a == "test" and instance.b == "test"
    assert instance.common == 2  # Model2's value should override Model1's
