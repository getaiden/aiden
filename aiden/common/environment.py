"""
Environment configuration for Aiden transformations.

This module provides the Environment class for configuring different execution
environments such as local development or Dagster-based workflows.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class Environment:
    """Configuration for the execution environment of Aiden transformations.

    This class defines the environment in which a transformation will be executed,
    such as local development or a Dagster-based workflow.

    Args:
        type: The type of environment. Supported values are 'local' and 'dagster'.
        url: The base URL for the environment (required for 'dagster' type).
        workdir: The working directory for local execution (required for 'local' type).
        metadata: Additional environment-specific configuration.
    """

    type: str
    url: Optional[str] = None
    workdir: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate the environment configuration."""
        self.type = self.type.lower()

        if self.type not in ["local", "dagster"]:
            raise ValueError(f"Unsupported environment type: {self.type}")

        if self.type == "dagster" and not self.url:
            raise ValueError("URL is required for 'dagster' environment type")

        if self.type == "local":
            # Set default workdir if not provided
            if not self.workdir:
                self.workdir = os.getenv("AIDEN_WORKDIR", "./workdir")

            # Ensure workdir is a Path object and create if it doesn't exist
            workdir_path = Path(self.workdir).expanduser()
            workdir_path.mkdir(parents=True, exist_ok=True)
            self.workdir = str(workdir_path.resolve())

        if self.metadata is None:
            self.metadata = {}

    @property
    def is_local(self) -> bool:
        """Check if this is a local environment."""
        return self.type == "local"

    @property
    def is_dagster(self) -> bool:
        """Check if this is a Dagster environment."""
        return self.type == "dagster"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the environment configuration to a dictionary."""
        return {"type": self.type, "url": self.url, "workdir": self.workdir, "metadata": self.metadata}

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "Environment":
        """Create an Environment instance from a dictionary."""
        return cls(**config)

    def __repr__(self) -> str:
        """Return a string representation of the environment."""
        if self.type == "dagster":
            return f"Environment(type='{self.type}', url='{self.url}')"
        return f"Environment(type='{self.type}', workdir='{self.workdir}')"


def get_environment(env_type: Optional[str] = None, **kwargs) -> Environment:
    """Get an environment configuration based on type and environment variables.

    Args:
        env_type: The type of environment ('local' or 'dagster'). If not provided,
                 will try to get from AIDEN_ENV environment variable, defaulting to 'local'.
        **kwargs: Additional arguments to pass to the Environment constructor.

    Returns:
        Environment: Configured environment instance.

    Example:
        # Get default local environment
        env = get_environment()

        # Get specific environment type
        dagster_env = get_environment('dagster', url='http://dagster:3000')

        # Custom workdir
        custom_env = get_environment(workdir='~/custom/workdir')
    """
    # Determine environment type
    if env_type is None:
        env_type = os.getenv("AIDEN_ENV", "local")

    # For local environment, set default workdir if not provided
    if env_type == "local" and "workdir" not in kwargs:
        kwargs["workdir"] = os.getenv("AIDEN_WORKDIR")

    # For dagster environment, get URL from environment if not provided
    if env_type == "dagster" and "url" not in kwargs:
        dagster_url = os.getenv("DAGSTER_URL")
        if dagster_url:
            kwargs["url"] = dagster_url

    return Environment(type=env_type, **kwargs)

    @property
    def is_local(self) -> bool:
        """Check if this is a local environment."""
        return self.type == "local"

    @property
    def is_dagster(self) -> bool:
        """Check if this is a Dagster environment."""
        return self.type == "dagster"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the environment configuration to a dictionary."""
        return {"type": self.type, "url": self.url, "workdir": self.workdir, "metadata": self.metadata}

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "Environment":
        """Create an Environment instance from a dictionary."""
        return cls(**config)

    def __repr__(self) -> str:
        """Return a string representation of the environment."""
        if self.type == "dagster":
            return f"Environment(type='{self.type}', url='{self.url}')"
        return f"Environment(type='{self.type}', workdir='{self.workdir}')"
