"""
Dataset definition and related utilities for handling data in Aiden.

This module provides a simplified Dataset class that can be used to define
input and output datasets for data transformations.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Type

from pydantic import BaseModel
from aiden.common.utils.pydantic_utils import map_to_basemodel, format_schema


@dataclass
class Dataset:
    """Dataset class for defining data sources and destinations in Aiden.

    This class is used to define the location and format of datasets
    used in data transformations.

    Args:
        path: The path to the dataset. Can be a local path or S3 URI.
        format: The format of the dataset (e.g., 'csv', 'parquet', 'json').
        schema: Optional schema definition as a dict or Pydantic model.
    """

    path: str
    format: str
    schema: Optional[dict | Type[BaseModel]] = None
    name: Optional[str] = None

    def __post_init__(self):
        """Initialize dataset name and process schema if provided."""
        # Extract name from file path (without extension)
        if self.name is None:
            path_obj = Path(self.path)
            self.name = path_obj.stem

        # Process schema if provided
        if self.schema is not None and not isinstance(self.schema, BaseModel):
            # Convert the schema to a Pydantic model if it's a dictionary
            try:
                self.schema = map_to_basemodel(self.name or "schema", self.schema)
            except Exception as e:
                # If conversion fails, keep the original schema
                print(f"Warning: Could not convert schema to Pydantic model: {e}")

    def __repr__(self) -> str:
        """Return a JSON string representation of the dataset with name, path, format, and schema."""
        import json

        schema_dict = {}
        if self.schema is not None:
            # Handle both dictionary schema and Pydantic model schema
            if isinstance(self.schema, dict):
                schema_dict = {k: v.__name__ if isinstance(v, type) else str(v) for k, v in self.schema.items()}
            else:
                schema_dict = format_schema(self.schema)

        dataset_info = {"name": self.name, "path": self.path, "format": self.format, "schema": schema_dict}

        return json.dumps(dataset_info, indent=2)
