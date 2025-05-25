"""
Unit tests for the code_generation module.
"""

from unittest.mock import Mock, patch

from aiden.tools.code_generation import get_generate_transformation_code
from aiden.common.environment import Environment


def test_get_generate_transformation_code_returns_tool():
    """Test that get_generate_transformation_code returns a tool function."""
    llm_to_use = "openai/gpt-4o"
    environment = Environment(type="local")

    tool = get_generate_transformation_code(llm_to_use, environment)

    # Check that it returns a callable tool with correct name
    assert callable(tool)
    assert hasattr(tool, "name")
    assert tool.name == "generate_transformation_code"


@patch("aiden.tools.code_generation.TransformationCodeGenerator")
@patch("aiden.tools.code_generation.Provider")
def test_generate_transformation_code_calls_generator(mock_provider_class, mock_generator_class):
    """Test that the tool function calls TransformationCodeGenerator correctly."""
    # Setup mocks
    mock_provider = Mock()
    mock_provider_class.return_value = mock_provider

    mock_generator = Mock()
    mock_generator.generate_transformation_code.return_value = "generated_code"
    mock_generator_class.return_value = mock_generator

    # Create and call the tool
    llm_to_use = "openai/gpt-4o"
    environment = Environment(type="local")
    tool = get_generate_transformation_code(llm_to_use, environment)

    result = tool(
        task="Test task",
        solution_plan="Test plan",
        input_datasets_names=["dataset1", "dataset2"],
        output_dataset_name="output_dataset",
    )

    # Verify correct calls and result
    mock_provider_class.assert_called_once_with(llm_to_use)
    mock_generator_class.assert_called_once_with(mock_provider, environment)
    mock_generator.generate_transformation_code.assert_called_once_with(
        "Test task", "Test plan", ["dataset1", "dataset2"], "output_dataset"
    )
    assert result == "generated_code"
