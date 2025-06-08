"""
Unit test for the dataset module.
"""

import json
import pytest
from pydantic import BaseModel

from aiden.common.dataset import Dataset, create_file_dataset, create_postgresql_dataset, create_dataset_from_source
from aiden.common.data_source import FileDataSource, PostgreSQLDataSource


def test_dataset_file_backward_compatibility():
    """Test the Dataset class backward compatibility with file-based datasets."""
    # Create a dataset with schema using the original constructor
    schema_dict = {"id": int, "name": str, "active": bool}
    dataset = Dataset(path="/tmp/data.csv", format="csv", schema=schema_dict)

    # Test basic properties
    assert dataset.format == "csv"
    assert dataset.name == "data"  # Name extracted from filename

    # Test schema conversion to Pydantic model
    assert isinstance(dataset.schema, type)
    assert issubclass(dataset.schema, BaseModel)

    # Test that data_source was created automatically
    assert dataset.data_source is not None
    assert isinstance(dataset.data_source, FileDataSource)
    assert dataset.data_source.path == "/tmp/data.csv"
    assert dataset.data_source.format == "csv"


def test_dataset_with_file_data_source():
    """Test creating a Dataset with an explicit FileDataSource."""
    # Create a data source
    file_source = FileDataSource(path="/tmp/data.parquet", format="parquet")

    # Create a dataset with the data source
    dataset = Dataset(data_source=file_source)

    # Test basic properties
    assert dataset.format == "parquet"
    assert dataset.name == "data"  # Name extracted from filename
    assert dataset.data_source is file_source

    # Test the string representation
    repr_dict = json.loads(dataset.__repr__())
    assert repr_dict["name"] == "data"
    assert repr_dict["format"] == "parquet"
    assert repr_dict["path"] == "/tmp/data.parquet"
    assert repr_dict["source_type"] == "file"


def test_dataset_with_postgresql_data_source():
    """Test creating a Dataset with a PostgreSQLDataSource."""
    # Create a data source
    pg_source = PostgreSQLDataSource(
        connection_string="postgresql://postgres:secret@localhost:5432/testdb", table="users"
    )

    # Create a dataset with the data source and a schema
    schema_dict = {"id": int, "username": str, "email": str}
    dataset = Dataset(data_source=pg_source, schema=schema_dict)

    # Test basic properties
    assert dataset.name == "users"  # Should default to table name
    assert dataset.format == "sql"  # Default format
    assert dataset.data_source == pg_source

    # Test schema conversion
    assert isinstance(dataset.schema, type)
    assert issubclass(dataset.schema, BaseModel)
    repr_dict = json.loads(dataset.__repr__())
    assert repr_dict["name"] == "users"
    assert repr_dict["format"] == "sql"
    assert repr_dict["source_type"] == "postgresql"
    assert "connection" in repr_dict
    # Connection is now a string with the connection string
    assert "postgresql://" in repr_dict["connection"]
    # Password is included in the connection string
    assert "secret" in repr_dict["connection"]


def test_create_file_dataset_helper():
    """Test the create_file_dataset helper function."""
    # Create a dataset using the helper
    dataset = create_file_dataset(
        path="/tmp/data.json", format="json", schema={"id": int, "data": dict}, name="custom_name"
    )

    # Test basic properties
    assert dataset.format == "json"
    assert dataset.name == "custom_name"  # Custom name used
    assert isinstance(dataset.data_source, FileDataSource)
    assert dataset.data_source.path == "/tmp/data.json"

    # Test schema conversion
    assert isinstance(dataset.schema, type)
    assert issubclass(dataset.schema, BaseModel)


def test_create_postgresql_dataset_helper():
    """Test the create_postgresql_dataset helper function."""
    # Create a dataset using the helper with connection string
    dataset = create_postgresql_dataset(
        connection_string="postgresql://analyst:secret123@db.example.com:5432/analytics",
        table="events",
        schema_name="raw_data",
        format="jdbc",
        dataset_name="event_data",
        dataset_schema={"event_id": str, "timestamp": str, "data": dict},
    )

    # Test basic properties
    assert dataset.format == "jdbc"
    assert dataset.name == "event_data"
    assert isinstance(dataset.data_source, PostgreSQLDataSource)

    # Test data source properties
    assert dataset.data_source.connection_string == "postgresql://analyst:secret123@db.example.com:5432/analytics"
    assert dataset.data_source.table == "events"
    assert dataset.data_source.schema == "raw_data"


def test_create_postgresql_dataset_with_connection_string():
    """Test the create_postgresql_dataset helper function with connection string only."""
    # Create a dataset using the helper with just a connection string
    dataset = create_postgresql_dataset(
        connection_string="postgresql://user:pass@host:5432/mydb",
        table="customers",
        dataset_schema={"id": int, "name": str, "email": str},
    )

    # Test basic properties
    assert dataset.format == "sql"  # Default format
    assert dataset.name == "customers"  # From table name
    assert isinstance(dataset.data_source, PostgreSQLDataSource)

    # Test that connection string was set correctly
    assert dataset.data_source.connection_string == "postgresql://user:pass@host:5432/mydb"

    # Test schema conversion
    assert isinstance(dataset.schema, type)
    assert issubclass(dataset.schema, BaseModel)

    # Test schema conversion
    assert isinstance(dataset.schema, type)
    assert issubclass(dataset.schema, BaseModel)


def test_create_dataset_from_source_factory():
    """Test the create_dataset_from_source factory function."""
    # Create a file dataset using the factory
    file_dataset = create_dataset_from_source(
        source_type="file",
        source_params={"path": "/tmp/data.csv", "format": "csv", "name": "file_data"},
        schema={"col1": str, "col2": int},
    )

    assert file_dataset.name == "file_data"
    assert file_dataset.format == "csv"
    assert isinstance(file_dataset.data_source, FileDataSource)

    # Create a PostgreSQL dataset using the factory
    pg_dataset = create_dataset_from_source(
        source_type="postgresql",
        source_params={
            "connection_string": "postgresql://postgres:secret@localhost:5432/testdb",
            "table": "products",
            "name": "product_data",
        },
        schema={"id": int, "name": str, "price": float},
    )

    assert pg_dataset.name == "product_data"
    assert pg_dataset.format == "sql"  # Default format
    assert isinstance(pg_dataset.data_source, PostgreSQLDataSource)


def test_dataset_invalid_initialization():
    """Test that Dataset initialization fails when required parameters are missing."""
    # Neither path+format nor data_source provided
    with pytest.raises(ValueError):
        Dataset(schema={"id": int})

    # Only path provided, format missing
    with pytest.raises(ValueError):
        Dataset(path="/tmp/data.csv")

    # Only format provided, path missing
    with pytest.raises(ValueError):
        Dataset(format="csv")
