"""
Environment configuration for Aiden transformations.

This module provides the Environment class for configuring different execution
environments such as local development or Dagster-based workflows.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class Environment:
    """Configuration for the execution environment of Aiden transformations.

    This class defines the environment in which a transformation will be executed,
    such as local development or a Dagster-based workflow.

    Args:
        type: The type of environment. Supported values are 'local' and 'dagster'.
        workdir: The working directory for execution.
        metadata: Additional environment-specific configuration.
    """

    type: str
    workdir: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate the environment configuration."""
        self.type = self.type.lower()

        # Validate environment type
        if self.type not in ["local", "dagster"]:
            raise ValueError(f"Unsupported environment type: {self.type}")

        # Set default workdir if not provided
        if not self.workdir:
            self.workdir = os.getenv("AIDEN_WORKDIR", "./workdir")

        # Ensure workdir exists and resolve path
        workdir_path = Path(self.workdir).expanduser()
        workdir_path.mkdir(parents=True, exist_ok=True)
        self.workdir = str(workdir_path.resolve())

        # Initialize metadata if None
        self.metadata = self.metadata or {}

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
        return {"type": self.type, "workdir": self.workdir, "metadata": self.metadata}

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "Environment":
        """Create an Environment instance from a dictionary."""
        return cls(**config)

    def __repr__(self) -> str:
        """Return a string representation of the environment."""
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
        dagster_env = get_environment('dagster')

        # Custom workdir
        custom_env = get_environment(workdir='~/custom/workdir')
    """
    # Determine environment type from env var if not provided
    if env_type is None:
        env_type = os.getenv("AIDEN_ENV", "local")

    # Set default workdir from env var if not provided
    if "workdir" not in kwargs:
        kwargs["workdir"] = os.getenv("AIDEN_WORKDIR", "./workdir")

    return Environment(type=env_type, **kwargs)
