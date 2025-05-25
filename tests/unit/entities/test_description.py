"""
Unit tests for the description module.
"""

from aiden.entities.description import SchemaInfo, CodeInfo, TransformationDescription


def test_dataclass_creation_and_defaults():
    """Test creating dataclass objects with required and default values."""
    # SchemaInfo with required and optional fields
    schema_with_inputs = SchemaInfo(output={"result": "int"}, inputs={"data": {"type": "DataFrame"}})
    assert schema_with_inputs.output == {"result": "int"}
    assert schema_with_inputs.inputs == {"data": {"type": "DataFrame"}}

    # SchemaInfo with default empty inputs
    schema_default_inputs = SchemaInfo(output={"result": "float"})
    assert schema_default_inputs.inputs == {}

    # CodeInfo with and without transformation
    code_with_transform = CodeInfo(transformation="def transform(x): return x")
    assert code_with_transform.transformation == "def transform(x): return x"

    code_default = CodeInfo()
    assert code_default.transformation is None


def test_transformation_description():
    """Test TransformationDescription creation and attributes."""
    # Create a complete description
    desc = TransformationDescription(
        id="test-transform",
        state="ready",
        intent="Test transformation",
        schemas=SchemaInfo(output={"result": "int"}, inputs={"data": {"type": "DataFrame"}}),
        code=CodeInfo(transformation="def transform(x): return x"),
    )

    # Verify core attributes
    assert desc.id == "test-transform"
    assert desc.state == "ready"
    assert desc.intent == "Test transformation"
    assert desc.schemas.output == {"result": "int"}
    assert desc.schemas.inputs == {"data": {"type": "DataFrame"}}
    assert desc.code.transformation == "def transform(x): return x"


def test_text_representations():
    """Test text and markdown representation methods."""
    # Create a description
    desc = TransformationDescription(
        id="format-test",
        state="ready",
        intent="Test formatting",
        schemas=SchemaInfo(output={"result": "int"}, inputs={"data": {"type": "DataFrame"}}),
        code=CodeInfo(transformation="def transform(x): return x"),
    )

    # Test text format - assert the full text block
    expected_text = (
        "Transformation: format-test\n"
        "State: ready\n"
        "Intent: Test formatting\n"
        "\n"
        "Input Schema:\n"
        "  - data: {'type': 'DataFrame'}\n"
        "\n"
        "Output Schema:\n"
        "  - result: int\n"
        "\n"
        "Code:\n"
        "  - Transformation Code:\n"
        "    ```python\n"
        "def transform(x): return x\n"
        "```\n"
    )
    assert desc.as_text() == expected_text

    # Test markdown format - assert the full markdown block
    expected_markdown = (
        "# Transformation: format-test\n"
        "\n"
        "**State:** ready\n"
        "\n"
        "**Intent:** Test formatting\n"
        "\n"
        "## Input Schema\n"
        "- `data`: {'type': 'DataFrame'}\n"
        "\n"
        "## Output Schema\n"
        "- `result`: int\n"
        "\n"
        "## Code\n"
        "### Transformation Code\n"
        "```python\n"
        "def transform(x): return x\n"
        "```\n"
    )
    assert desc.as_markdown() == expected_markdown

    # Test empty code representation - assert the full text with placeholder
    desc_no_code = TransformationDescription(
        id="no-code",
        state="draft",
        intent="Test empty code",
        schemas=SchemaInfo(output={"result": "int"}),
        code=CodeInfo(),
    )
    assert "# No transformation code available" in desc_no_code.as_text()
    assert "# No transformation code available" in desc_no_code.as_markdown()


def test_json_serialization():
    """Test JSON serialization and deserialization."""
    # Create and serialize
    original = TransformationDescription(
        id="json-test",
        state="draft",
        intent="Test serialization",
        schemas=SchemaInfo(output={"result": "bool"}),
        code=CodeInfo(transformation="def transform(): pass"),
    )
    json_str = original.to_json()

    # Deserialize and verify
    deserialized = TransformationDescription.from_json(json_str)
    assert deserialized.id == original.id
    assert deserialized.state == original.state
    assert deserialized.intent == original.intent
    assert deserialized.schemas.output == original.schemas.output
    assert deserialized.code.transformation == original.code.transformation
