"""
Dataset definition and related utilities for handling data in Aiden.

This module provides a simplified Dataset class that can be used to define
input and output datasets for data transformations.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from aiden.common.data_source import DataSource, FileDataSource, PostgreSQLDataSource, create_data_source
from aiden.common.utils.pydantic_utils import format_schema, map_to_basemodel


@dataclass
class Dataset:
    """Dataset class for defining data sources and destinations in Aiden.

    This class is used to define the location and format of datasets
    used in data transformations. It supports both file-based and database data sources.

    Args:
        path: The path to the dataset (for file-based datasets) or None for database datasets.
        format: The format of the dataset (e.g., 'csv', 'parquet', 'json', 'sql').
        schema: Optional schema definition as a dict or Pydantic model.
        name: Optional name for the dataset. If not provided, it will be extracted from the path.
        data_source: Optional DataSource object. If provided, path and format are ignored.
    """

    path: Optional[str] = None
    format: Optional[str] = None
    schema: Optional[dict | Type[BaseModel]] = None
    name: Optional[str] = None
    data_source: Optional[DataSource] = None

    def __post_init__(self):
        """Initialize dataset based on provided parameters."""
        # If data_source is provided, use it directly
        if self.data_source is not None:
            self.name = self.data_source.get_name()
            self.format = self.data_source.get_format()
            # path is not set as it might not be applicable for all data sources
        # Otherwise, create a FileDataSource from path and format (backward compatibility)
        elif self.path is not None and self.format is not None:
            self.data_source = FileDataSource(path=self.path, format=self.format, name=self.name)
            # Update name in case it was derived from the path
            self.name = self.data_source.get_name()
        else:
            raise ValueError("Either data_source or both path and format must be provided")

        # Process schema if provided
        if self.schema is not None and not isinstance(self.schema, BaseModel):
            # Convert the schema to a Pydantic model if it's a dictionary
            try:
                self.schema = map_to_basemodel(self.name or "schema", self.schema)
            except Exception as e:
                # If conversion fails, keep the original schema
                print(f"Warning: Could not convert schema to Pydantic model: {e}")

    def __repr__(self) -> str:
        """Return a JSON string representation of the dataset with name, data source info, format, and schema."""
        import json

        schema_dict = {}
        if self.schema is not None:
            # Handle both dictionary schema and Pydantic model schema
            if isinstance(self.schema, dict):
                schema_dict = {k: v.__name__ if isinstance(v, type) else str(v) for k, v in self.schema.items()}
            else:
                schema_dict = format_schema(self.schema)

        # Start with basic dataset info
        dataset_info = {"name": self.name, "format": self.format, "schema": schema_dict}

        # Add data source specific information
        if self.data_source:
            source_info = self.data_source.to_dict()
            dataset_info["source_type"] = source_info.get("type", "unknown")

            # For file data sources, include the path for backward compatibility
            if isinstance(self.data_source, FileDataSource):
                dataset_info["path"] = self.data_source.path
            # For other data sources, include relevant connection info
            else:
                dataset_info["connection"] = source_info.get("connection", {})
                dataset_info["table"] = source_info.get("table", {})
                dataset_info["pg_schema"] = source_info.get("pg_schema", {})

        return json.dumps(dataset_info, indent=2)


def create_file_dataset(
    path: str, format: str, schema: Optional[dict | Type[BaseModel]] = None, name: Optional[str] = None
) -> Dataset:
    """Create a dataset from a file source.

    Args:
        path: The path to the file. Can be a local path or S3 URI.
        format: The format of the file (e.g., 'csv', 'parquet', 'json').
        schema: Optional schema definition as a dict or Pydantic model.
        name: Optional name for the dataset. If not provided, it will be extracted from the path.

    Returns:
        A Dataset instance with a FileDataSource.
    """
    data_source = FileDataSource(path=path, format=format, name=name)
    return Dataset(data_source=data_source, schema=schema)


def create_postgresql_dataset(
    table: str,
    connection_string: str,
    schema_name: str = "public",
    format: str = "sql",
    dataset_name: Optional[str] = None,
    dataset_schema: Optional[dict | Type[BaseModel]] = None,
) -> Dataset:
    """Create a dataset from a PostgreSQL source.

    Args:
        table: The name of the table.
        connection_string: The PostgreSQL connection string.
        schema_name: The schema name (default: 'public').
        format: The format to use when reading/writing data (default: 'sql').
        dataset_name: Optional name for the dataset. If not provided, it will be the table name.
        dataset_schema: Optional schema definition as a dict or Pydantic model.

    Returns:
        A Dataset instance with a PostgreSQLDataSource.
    """
    data_source = PostgreSQLDataSource(
        connection_string=connection_string, table=table, schema=schema_name, format=format, name=dataset_name
    )
    return Dataset(data_source=data_source, schema=dataset_schema)


def create_dataset_from_source(
    source_type: str, source_params: Dict[str, Any], schema: Optional[dict | Type[BaseModel]] = None
) -> Dataset:
    """Factory function to create a dataset from a specified data source type.

    Args:
        source_type: The type of data source ('file', 'postgresql', etc.)
        source_params: Parameters for the data source
        schema: Optional schema definition as a dict or Pydantic model

    Returns:
        A Dataset instance with the specified data source

    Raises:
        ValueError: If the specified source type is not supported
    """
    data_source = create_data_source(source_type, **source_params)
    return Dataset(data_source=data_source, schema=schema)
