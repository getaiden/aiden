"""
Unit test for the prompt utility module.
"""

from unittest.mock import patch

from aiden.common.utils.prompt import get_prompt_templates


@patch("aiden.common.utils.prompt.yaml.safe_load")
@patch("importlib.resources.files")
def test_get_prompt_templates(mock_files, mock_yaml_load):
    """Test merging of prompt templates with overrides."""
    # Setup mock returns
    mock_yaml_load.side_effect = [
        # Base template
        {"managed_agent": {"task": "Base task", "context": "Base context"}},
        # Override template
        {"managed_agent": {"task": "Override task"}},
    ]

    # Mock file paths
    mock_files.return_value.joinpath.return_value.read_text.return_value = "mock content"

    # Call the function
    result = get_prompt_templates("base.yaml", "override.yaml")

    # Verify the result - override should take precedence
    assert result["managed_agent"]["task"] == "Override task"
    assert result["managed_agent"]["context"] == "Base context"
