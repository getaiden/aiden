"""
This module defines dataclasses for structured model descriptions.

These classes provide a comprehensive representation of a model's
characteristics, including schemas, implementation details, performance
metrics, and source code, organized in a structured format suitable
for various output formats and visualization purposes.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from dataclasses_json import DataClassJsonMixin


@dataclass
class SchemaInfo(DataClassJsonMixin):
    """Information about the model's input and output schemas."""

    output: Dict[str, Any]
    inputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class CodeInfo(DataClassJsonMixin):
    """Information about the model's source code."""

    transformation: Optional[str] = None


@dataclass
class TransformationDescription(DataClassJsonMixin):
    """A comprehensive description of a model."""

    id: str
    state: str
    intent: str
    schemas: SchemaInfo
    code: CodeInfo

    def as_text(self) -> str:
        """Convert the model description to a formatted text string."""
        # Simple text representation
        lines = [
            f"Transformation: {self.id}",
            f"State: {self.state}",
            f"Intent: {self.intent}",
            "",
            "Input Schema:",
            "\n".join(f"  - {k}: {v}" for k, v in self.schemas.inputs.items()),
            "",
            "Output Schema:",
            "\n".join(f"  - {k}: {v}" for k, v in self.schemas.output.items()),
            "",
            "Code:",
            "  - Transformation Code:",
            f"    ```python\n{self.code.transformation or '# No transformation code available'}\n```",
            "",
        ]
        return "\n".join(lines)

    def as_markdown(self) -> str:
        """Convert the model description to a markdown string."""
        # Markdown representation with formatting
        lines = [
            f"# Transformation: {self.id}",
            "",
            f"**State:** {self.state}",
            "",
            f"**Intent:** {self.intent}",
            "",
            "## Input Schema",
            "\n".join(f"- `{k}`: {v}" for k, v in self.schemas.inputs.items()),
            "",
            "## Output Schema",
            "\n".join(f"- `{k}`: {v}" for k, v in self.schemas.output.items()),
            "",
            "## Code",
            "### Transformation Code",
            "```python",
            self.code.transformation or "# No transformation code available",
            "```",
            "",
        ]
        return "\n".join(lines)
