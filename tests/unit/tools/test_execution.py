"""
Unit tests for the execution module.
"""

import tempfile
import os

from aiden.tools.execution import _get_executor_class, get_executor_tool
from aiden.common.environment import Environment
from aiden.executors.local_executor import LocalExecutor
from aiden.registries.objects import ObjectRegistry
from aiden.common.dataset import Dataset


def test_get_executor_class_default():
    """Test _get_executor_class with default parameters."""
    result = _get_executor_class()

    assert result == LocalExecutor


def test_get_executor_class_local_environment():
    """Test _get_executor_class with local environment."""
    env = Environment(type="local")
    result = _get_executor_class(environment=env)

    assert result == LocalExecutor


def test_get_executor_class_dagster_environment():
    """Test _get_executor_class with dagster environment."""
    env = Environment(type="dagster")
    result = _get_executor_class(environment=env)

    assert result == LocalExecutor


def test_get_executor_tool():
    """Test get_executor_tool returns a callable tool."""
    tool = get_executor_tool()

    assert callable(tool)
    assert hasattr(tool, "name")
    assert tool.name == "execute_code"


def test_execute_code_success():
    """Test execute_code function with successful execution."""
    # Create a temporary working directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create minimal CSV files for the datasets
        input_file_path = os.path.join(temp_dir, "success_input.csv")
        output_file_path = os.path.join(temp_dir, "success_output.csv")

        # Create a simple CSV file
        with open(input_file_path, "w") as f:
            f.write("name,age\nAlice,25\nBob,30\n")

        input_dataset = Dataset(path=input_file_path, format="csv")
        output_dataset = Dataset(path=output_file_path, format="csv")

        # Register datasets
        registry = ObjectRegistry()
        registry.clear()  # Clear any existing registrations
        registry.register(Dataset, "success_input", input_dataset)
        registry.register(Dataset, "success_output", output_dataset)

        # Very simple Python code
        code = 'print("hello")'

        # Get the tool and execute
        tool = get_executor_tool()

        result = tool(
            node_id="test_simple",
            code=code,
            working_dir=temp_dir,
            input_dataset_names=["success_input"],
            output_dataset_name="success_output",
            timeout=10,
        )

        # Assert success is True and exception is None
        assert result["success"] is True
        assert result["exception"] is None


def test_execute_code_exception():
    """Test execute_code function with code that raises an exception."""
    # Create a temporary working directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create minimal CSV files for the datasets
        input_file_path = os.path.join(temp_dir, "exception_input.csv")
        output_file_path = os.path.join(temp_dir, "exception_output.csv")

        # Create a simple CSV file
        with open(input_file_path, "w") as f:
            f.write("name,age\nAlice,25\nBob,30\n")

        input_dataset = Dataset(path=input_file_path, format="csv")
        output_dataset = Dataset(path=output_file_path, format="csv")

        # Register datasets
        registry = ObjectRegistry()
        registry.clear()  # Clear any existing registrations
        registry.register(Dataset, "exception_input", input_dataset)
        registry.register(Dataset, "exception_output", output_dataset)

        # Code that will raise an exception
        code = 'raise ValueError("Test exception")'

        # Get the tool and execute
        tool = get_executor_tool()

        result = tool(
            node_id="test_exception",
            code=code,
            working_dir=temp_dir,
            input_dataset_names=["exception_input"],
            output_dataset_name="exception_output",
            timeout=10,
        )

        # Assert success is False and exception is not None
        assert result["success"] is False
        assert result["exception"] is not None
        assert "Test exception" in result["exception"]
