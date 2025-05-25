"""
Unit tests for the LocalExecutor class.
"""

import tempfile
import pytest
from pathlib import Path
import shutil

from aiden.executors.local_executor import LocalExecutor
from aiden.common.environment import Environment


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for testing and clean it up afterward."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Clean up after the test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def local_env():
    """Create a local environment for testing."""
    return Environment(type="local")


def test_local_executor_success(temp_test_dir, local_env):
    """Test successful execution of Python code."""
    executor = LocalExecutor(
        execution_id="test-success",
        code="print('Hello from test script')",
        working_dir=temp_test_dir,
        timeout=10,
        environment=local_env,
    )

    result = executor.run()

    # Verify successful execution
    assert result.exception is None
    assert "Hello from test script" in result.term_out[0]


def test_local_executor_error(temp_test_dir, local_env):
    """Test error handling during Python code execution."""
    executor = LocalExecutor(
        execution_id="test-error",
        code="import sys\nprint('Error output', file=sys.stdout)\nraise ValueError('Test error message')",
        working_dir=temp_test_dir,
        timeout=10,
        environment=local_env,
    )

    result = executor.run()

    # Verify error handling
    assert result.exception is not None
    assert "Test error message" in str(result.exception) or "ValueError" in str(result.exception)
    assert "Error output" in result.term_out[0]


def test_local_executor_timeout(temp_test_dir, local_env):
    """Test timeout handling during Python code execution."""
    executor = LocalExecutor(
        execution_id="test-timeout",
        code="import time\nwhile True: time.sleep(0.1)",
        working_dir=temp_test_dir,
        timeout=1,  # Short timeout to ensure it triggers
        environment=local_env,
    )

    result = executor.run()

    # Verify timeout handling
    assert isinstance(result.exception, TimeoutError)
