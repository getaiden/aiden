"""
Unit tests for the provider module.
"""

from unittest.mock import patch, MagicMock

from aiden.common.provider import ProviderConfig, Provider


def test_provider_config():
    """Test the ProviderConfig class functionality."""
    # Test with default values
    config = ProviderConfig()
    assert config.default_provider == "openai/gpt-4o-mini"
    assert config.manager_provider == config.default_provider

    # Test with custom values
    custom_config = ProviderConfig(default_provider="openai/gpt-4", manager_provider="anthropic/claude-3")
    assert custom_config.default_provider == "openai/gpt-4"
    assert custom_config.manager_provider == "anthropic/claude-3"
    assert custom_config.data_expert_provider == custom_config.default_provider


@patch("aiden.common.provider.completion")
@patch("aiden.common.provider.supports_response_schema")
@patch("aiden.common.provider.litellm.get_supported_openai_params")
def test_provider(mock_get_params, mock_supports_schema, mock_completion):
    """Test Provider class core functionality."""
    # Setup mocks
    mock_get_params.return_value = {"response_format": True}
    mock_supports_schema.return_value = True

    # Mock completion response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "Test response"
    mock_completion.return_value = mock_response

    # Create provider
    provider = Provider()

    # Test model initialization
    assert provider.model == "openai/gpt-4o-mini"

    # Test query functionality
    result = provider.query(
        system_message="System prompt", user_message="User message", backoff=False  # Disable backoff for testing
    )

    # Verify results
    assert result == "Test response"
