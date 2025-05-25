"""
Unit tests for the environment module.
"""

import os
from unittest.mock import patch
from pathlib import Path

from aiden.common.environment import Environment, get_environment


@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.expanduser")
@patch("pathlib.Path.resolve")
@patch("pathlib.Path.exists")
def test_local_environment(mock_exists, mock_resolve, mock_expanduser, mock_mkdir):
    """Test the local environment configuration."""
    # Setup mocks
    mock_exists.return_value = True
    mock_resolve.return_value = Path("/resolved/test_local_dir")
    mock_expanduser.return_value = Path("/expanded/test_local_dir")

    # Create a local environment
    env = Environment(type="local", workdir="./test_local_dir")

    # Verify local environment properties
    assert env.type == "local"
    assert env.is_local is True
    assert env.is_dagster is False

    # Verify directory creation was attempted
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    # Test factory function with local environment
    with patch.dict(os.environ, {"AIDEN_ENV": "local"}):
        env = get_environment(workdir="./test_local_env_dir")
        assert env.type == "local"
        assert env.is_local is True


@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.expanduser")
@patch("pathlib.Path.resolve")
@patch("pathlib.Path.exists")
def test_dagster_environment(mock_exists, mock_resolve, mock_expanduser, mock_mkdir):
    """Test the Dagster environment configuration."""
    # Setup mocks
    mock_exists.return_value = True
    mock_resolve.return_value = Path("/resolved/test_dagster_dir")
    mock_expanduser.return_value = Path("/expanded/test_dagster_dir")

    # Create a Dagster environment
    env = Environment(type="dagster", workdir="./test_dagster_dir")

    # Verify Dagster environment properties
    assert env.type == "dagster"
    assert env.is_local is False
    assert env.is_dagster is True

    # Verify directory creation was attempted
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    # Test factory function with Dagster environment
    with patch.dict(os.environ, {"AIDEN_ENV": "dagster"}):
        env = get_environment(workdir="./test_dagster_env_dir")
        assert env.type == "dagster"
        assert env.is_dagster is True
