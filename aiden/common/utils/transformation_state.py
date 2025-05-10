"""
Model state definitions for Plexe.

This module defines the possible states a model can be in during its lifecycle.
"""

from enum import Enum


class TransformationState(Enum):
    """States a transformation can be in during its lifecycle."""

    DRAFT = "draft"
    """Transformation is in draft state, not yet built."""

    BUILDING = "building"
    """Transformation is currently being built."""

    READY = "ready"
    """Transformation is built and ready to use."""

    ERROR = "error"
    """Transformation encountered an error during building."""
