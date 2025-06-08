"""
Unit test for the dataset module.
"""

from pydantic import BaseModel

from aiden.common.dataset import Dataset


def test_dataset():
    """Test the Dataset class core functionality."""
    # Create a dataset with schema
    schema_dict = {"id": int, "name": str, "active": bool}
    dataset = Dataset(path="/tmp/data.csv", format="csv", schema=schema_dict)

    # Test basic properties
    assert dataset.path == "/tmp/data.csv"
    assert dataset.format == "csv"
    assert dataset.name == "data"  # Name extracted from filename

    # Test schema conversion to Pydantic model
    assert isinstance(dataset.schema, type)
    assert issubclass(dataset.schema, BaseModel)
