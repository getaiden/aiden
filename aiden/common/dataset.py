"""
Dataset definition and related utilities for handling data in Aiden.

This module provides a base Dataset class that can be used to define
input and output datasets for data transformations.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Type, get_type_hints

from pydantic import BaseModel, create_model


@dataclass
class Dataset:
    """Dataset class for defining data sources and destinations in Aiden.

    This class is used to define the location and format of datasets
    used in data transformations.

    Args:
        path: The path to the dataset. Can be a local path or S3 URI.
        format: The format of the dataset (e.g., 'csv', 'parquet', 'json').
        **kwargs: Additional dataset-specific parameters.
    """

    path: str
    format: str
    _data: Optional[Any] = None
    _metadata: Dict[str, Any] | None = None
    _name: Optional[str] = None
    schema: Optional[dict | Type[BaseModel]] = None

    def __post_init__(self):
        """Initialize metadata if not provided and set internal name and schema."""
        if self._metadata is None:
            self._metadata = {}

        # Extract name from file path (without extension)
        if self._name is None:
            path_obj = Path(self.path)
            self._name = path_obj.stem

        # Store the original schema for __repr__
        self._original_schema = self.schema

        # Process schema if provided
        if self.schema is not None and not isinstance(self.schema, BaseModel):
            # Convert the schema to a Pydantic model if it's a dictionary
            try:
                self.schema = self.map_to_basemodel(self._name or "schema", self.schema)
            except Exception as e:
                # If conversion fails, keep the original schema
                print(f"Warning: Could not convert schema to Pydantic model: {e}")
                # Keep the original schema as is

    @property
    def is_s3(self) -> bool:
        """Check if the dataset path is an S3 URI."""
        return self.path.startswith("s3://")

    @property
    def is_local(self) -> bool:
        """Check if the dataset path is a local filesystem path."""
        return not self.is_s3

    def get_metadata(self) -> Dict[str, Any]:
        """Get the dataset metadata."""
        return self._metadata

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Set the dataset metadata."""
        self._metadata = metadata

    def add_metadata(self, key: str, value: Any) -> None:
        """Add a key-value pair to the dataset metadata."""
        self._metadata[key] = value

    @property
    def name(self) -> str:
        """Get the internal name of the dataset (filename without extension)."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the internal name of the dataset."""
        self._name = value

    def get_data(self) -> Any:
        """Get the loaded dataset data."""
        return self._data

    def set_data(self, data: Any) -> None:
        """Set the dataset data."""
        self._data = data

    def __repr__(self) -> str:
        """Return a JSON string representation of the dataset with name, path, format, and schema."""
        import json

        schema_dict = {}
        if self.schema is not None:
            # Handle both dictionary schema and Pydantic model schema
            if isinstance(self.schema, dict):
                schema_dict = {k: v.__name__ if isinstance(v, type) else str(v) for k, v in self.schema.items()}
            else:
                schema_dict = self.format_schema(self.schema)

        dataset_info = {"name": self.name, "path": self.path, "format": self.format, "schema": schema_dict}

        return json.dumps(dataset_info, indent=2)

    def __len__(self) -> int:
        """Return the number of items in the dataset."""
        if self._data is None:
            return 0
        if hasattr(self._data, "__len__"):
            return len(self._data)
        return 0

    def __getitem__(self, idx: int) -> Any:
        """Get an item from the dataset by index."""
        if self._data is None:
            raise ValueError("Dataset data not loaded")
        return self._data[idx]

    def head(self, n: int = 5) -> Any:
        """Return the first n items of the dataset if available."""
        if self._data is None:
            raise ValueError("Dataset data not loaded")
        if hasattr(self._data, "head"):  # For pandas DataFrame
            return self._data.head(n)
        if hasattr(self._data, "__getitem__"):
            return self._data[:n]
        return self._data

    @staticmethod
    def map_to_basemodel(name: str, schema: dict | Type[BaseModel]) -> Type[BaseModel]:
        """
        Ensure that the schema is a Pydantic model or a dictionary, and return the model.

        :param name: the name to be given to the model class
        :param schema: the schema to be converted to a Pydantic model
        :return: the Pydantic model
        """
        # Pydantic model: return as is
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            return schema

        # Dictionary: convert to Pydantic model, if possible
        if isinstance(schema, dict):
            try:
                # Handle both Dict[str, type] and Dict[str, str] formats
                annotated_schema = {}

                for k, v in schema.items():
                    # If v is a string like "int", convert it to the actual type
                    if isinstance(v, str):
                        type_mapping = {
                            "int": int,
                            "float": float,
                            "str": str,
                            "bool": bool,
                            "list": list,
                            "dict": dict,
                        }
                        if v in type_mapping:
                            annotated_schema[k] = (type_mapping[v], ...)
                        else:
                            raise ValueError(f"Invalid type specification: {v} for field {k}")
                    # If v is already a type, use it directly
                    elif isinstance(v, type):
                        annotated_schema[k] = (v, ...)
                    else:
                        raise ValueError(f"Invalid field specification for {k}: {v}")

                # Create a model class with the given name
                model_class = create_model(name, **annotated_schema)
                return model_class
            except Exception as e:
                raise ValueError(f"Invalid schema definition: {e}")

        # All other schema types are invalid
        raise TypeError("Schema must be a Pydantic model or a dictionary of field names to types.")

    @staticmethod
    def format_schema(schema) -> Dict[str, str]:
        """
        Format a schema model into a dictionary representation of field names and types.

        :param schema: A pydantic model defining a schema or a schema instance
        :return: A dictionary representing the schema structure with field names as keys and types as values
        """
        if schema is None:
            return {}

        # If schema is a class (type) and a subclass of BaseModel
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            result = {}
            # Use model_fields which is the recommended approach in newer Pydantic versions
            for field_name, field_info in schema.model_fields.items():
                field_type = getattr(field_info.annotation, "__name__", str(field_info.annotation))
                result[field_name] = field_type
            return result

        # If schema is an instance of BaseModel
        elif isinstance(schema, BaseModel):
            result = {}
            # Use model_fields which is the recommended approach in newer Pydantic versions
            for field_name, field_info in schema.__class__.model_fields.items():
                field_type = getattr(field_info.annotation, "__name__", str(field_info.annotation))
                result[field_name] = field_type
            return result

        # If schema is a dictionary (original schema passed to constructor)
        elif isinstance(schema, dict):
            result = {}
            for field_name, field_type in schema.items():
                if isinstance(field_type, type):
                    result[field_name] = field_type.__name__
                else:
                    result[field_name] = str(field_type)
            return result

        return {}

    @staticmethod
    def convert_schema_to_type_dict(schema: Type[BaseModel] | None) -> Dict[str, type]:
        """
        Convert a Pydantic model to a dictionary mapping field names to their Python types.

        This is useful for tools that require type information without the full Pydantic field metadata.

        :param schema: A Pydantic model to convert
        :return: A dictionary with field names as keys and Python types as values
        """
        if not schema or not isinstance(schema, BaseModel):
            return {}

        result = {}

        # Get the actual type annotations, which will be Python types
        type_hints = get_type_hints(schema)

        # Extract annotations from model fields
        for field_name, field_info in schema.model_fields.items():
            # Use the type hint if available, otherwise fall back to the field annotation
            field_type = type_hints.get(field_name, field_info.annotation)
            result[field_name] = field_type

        return result
