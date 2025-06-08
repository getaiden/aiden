"""
Unit tests for the data_source module.
"""

import pytest

from aiden.common.data_source import FileDataSource, PostgreSQLDataSource, create_data_source


def test_file_data_source_initialization():
    """Test the initialization of FileDataSource."""
    # Basic initialization
    source = FileDataSource(path="/tmp/data.csv", format="csv")
    assert source.path == "/tmp/data.csv"
    assert source.format == "csv"
    assert source.name == "data"  # Name extracted from path

    # Initialization with custom name
    source = FileDataSource(path="/tmp/data.csv", format="csv", name="custom_name")
    assert source.name == "custom_name"

    # Test get methods
    assert source.get_name() == "custom_name"
    assert source.get_format() == "csv"
    assert source.get_connection_info() == {"path": "/tmp/data.csv"}

    # Test to_dict method
    source_dict = source.to_dict()
    assert source_dict["type"] == "file"
    assert source_dict["name"] == "custom_name"
    assert source_dict["path"] == "/tmp/data.csv"
    assert source_dict["format"] == "csv"


def test_postgresql_data_source_initialization():
    """Test the initialization of PostgreSQLDataSource."""
    # Basic initialization
    source = PostgreSQLDataSource(connection_string="postgresql://postgres:secret@localhost:5432/testdb", table="users")

    assert source.connection_string == "postgresql://postgres:secret@localhost:5432/testdb"
    assert source.table == "users"
    assert source.schema == "public"  # Default schema
    assert source.format == "sql"  # Default format
    assert source.name == "users"  # Name from table

    # Initialization with custom name and schema
    source = PostgreSQLDataSource(
        connection_string="postgresql://analyst:secret123@db.example.com:5432/analytics",
        table="events",
        schema="raw_data",
        format="jdbc",
        name="event_data",
    )

    assert source.schema == "raw_data"
    assert source.format == "jdbc"
    assert source.name == "event_data"

    # Test get methods
    assert source.get_name() == "event_data"
    assert source.get_format() == "jdbc"

    # Test get_connection_info method
    conn_info = source.get_connection_info()
    assert "connection_string" in conn_info
    assert "postgresql://" in conn_info["connection_string"]
    assert "secret123" in conn_info["connection_string"]  # Password is not masked
    assert "table" in conn_info
    assert "schema" in conn_info

    # Test to_dict method
    source_dict = source.to_dict()
    assert source_dict["type"] == "postgresql"
    assert source_dict["name"] == "event_data"
    assert source_dict["format"] == "jdbc"

    # Connection info in dict should contain the connection string
    assert "connection" in source_dict
    assert "postgresql://" in source_dict["connection"]
    assert "secret123" in source_dict["connection"]  # Password is included


def test_postgresql_data_source_with_connection_string():
    """Test PostgreSQLDataSource with a connection string."""
    # Initialize with connection string
    conn_string = "postgresql://user:pass@localhost:5432/mydb"
    source = PostgreSQLDataSource(connection_string=conn_string, table="mytable")

    # Test connection info
    conn_info = source.get_connection_info()
    assert "connection_string" in conn_info
    assert "table" in conn_info
    assert "schema" in conn_info

    # Test to_dict method
    source_dict = source.to_dict()
    assert "connection" in source_dict
    # Connection string should include password
    assert "pass" in str(source_dict["connection"])


def test_create_data_source_factory():
    """Test the create_data_source factory function."""
    # Create file data source
    source = create_data_source(source_type="file", path="/tmp/data.csv", format="csv", name="file_data")

    assert isinstance(source, FileDataSource)
    assert source.path == "/tmp/data.csv"
    assert source.format == "csv"
    assert source.name == "file_data"

    # Create PostgreSQL data source
    source = create_data_source(
        source_type="postgresql",
        connection_string="postgresql://postgres:secret@localhost:5432/testdb",
        table="products",
        name="product_data",
    )

    assert isinstance(source, PostgreSQLDataSource)
    assert source.connection_string == "postgresql://postgres:secret@localhost:5432/testdb"
    assert source.table == "products"
    assert source.name == "product_data"

    # Test with unsupported source type
    with pytest.raises(ValueError, match="Unsupported data source type"):
        create_data_source(source_type="unknown")
