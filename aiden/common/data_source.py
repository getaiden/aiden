"""
Data source definitions for Aiden.

This module provides the base DataSource class and implementations
for different data source types (files, databases, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class DataSource(ABC):
    """Base abstract class for all data sources in Aiden.

    This class defines the interface that all data sources must implement.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the data source."""
        pass

    @abstractmethod
    def get_format(self) -> str:
        """Get the format of the data source."""
        pass

    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """Get the connection information for the data source."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the data source to a dictionary representation."""
        pass


@dataclass
class FileDataSource(DataSource):
    """File-based data source implementation.

    This class represents data sources that are stored in files,
    such as CSV, Parquet, or JSON files.

    Args:
        path: The path to the file. Can be a local path or S3 URI.
        format: The format of the file (e.g., 'csv', 'parquet', 'json').
        name: Optional name for the data source. If not provided, it will be extracted from the path.
    """

    path: str
    format: str
    name: Optional[str] = None

    def __post_init__(self):
        """Initialize file data source name if not provided."""
        if self.name is None:
            # Extract name from file path (without extension)
            from pathlib import Path

            path_obj = Path(self.path)
            self.name = path_obj.stem

    def get_name(self) -> str:
        """Get the name of the file data source."""
        return self.name

    def get_format(self) -> str:
        """Get the format of the file data source."""
        return self.format

    def get_connection_info(self) -> Dict[str, Any]:
        """Get the connection information for the file data source."""
        return {"path": self.path}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the file data source to a dictionary representation."""
        return {
            "type": "file",
            "name": self.name,
            "path": self.path,
            "format": self.format,
        }


@dataclass
class PostgreSQLDataSource(DataSource):
    """PostgreSQL database data source implementation.

    This class represents data sources that are stored in PostgreSQL databases.

    Args:
        connection_string: The PostgreSQL connection string.
        table: The name of the table.
        schema: The schema name (default: 'public').
        format: The format to use when reading/writing data (e.g., 'sql', 'jdbc').
        name: Optional name for the data source. If not provided, it will be the table name.
    """

    connection_string: str
    table: str
    schema: str = "public"
    format: str = "sql"
    name: Optional[str] = None

    def __post_init__(self):
        """Initialize PostgreSQL data source name if not provided."""
        if self.name is None:
            self.name = self.table

    def get_name(self) -> str:
        """Get the name of the PostgreSQL data source."""
        return self.name

    def get_format(self) -> str:
        """Get the format of the PostgreSQL data source."""
        return self.format

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for the PostgreSQL data source."""
        return {"connection_string": self.connection_string, "table": self.table, "schema": self.schema}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the PostgreSQL data source to a dictionary representation."""
        return {
            "type": "postgresql",
            "name": self.name,
            "format": self.format,
            "connection": self.connection_string,
            "table": self.table,
            "pg_schema": self.schema,
        }


def create_data_source(source_type: str, **kwargs) -> DataSource:
    """Factory function to create a data source of the specified type.

    Args:
        source_type: The type of data source to create ('file', 'postgresql', etc.)
        **kwargs: Arguments to pass to the data source constructor

    Returns:
        A DataSource instance of the specified type

    Raises:
        ValueError: If the specified source type is not supported
        ValueError: If PostgreSQL data source is missing required parameters
    """
    source_types = {
        "file": FileDataSource,
        "postgresql": PostgreSQLDataSource,
    }

    if source_type not in source_types:
        raise ValueError(
            f"Unsupported data source type: {source_type}. Supported types are: {', '.join(source_types.keys())}"
        )

    # For PostgreSQL, ensure connection_string is provided
    if source_type == "postgresql" and "connection_string" not in kwargs:
        raise ValueError("PostgreSQL data source requires a connection_string parameter")

    return source_types[source_type](**kwargs)
