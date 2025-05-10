"""
Tools related to code execution, including running training code in isolated environments.

These tools automatically handle model artifact registration through the ArtifactRegistry,
ensuring that artifacts generated during the execution can be retrieved later in the pipeline.
"""

import logging
import uuid
from typing import Callable, Dict, List, Type

from pandas import DataFrame
from smolagents import tool

from aiden.common.registries.objects import ObjectRegistry
from aiden.models.entities.code import Code
from aiden.models.entities.node import Node
from aiden.models.execution.process_executor import ProcessExecutor

logger = logging.getLogger(__name__)


def get_executor_tool(distributed: bool = False) -> Callable:
    """Get the appropriate executor tool based on the distributed flag."""

    @tool
    def execute_code(
        node_id: str,
        code: str,
        working_dir: str,
        dataset_names: List[str],
        timeout: int,
    ) -> Dict:
        """Executes code in an isolated environment.

        Args:
            node_id: Unique identifier for this execution
            code: The code to execute
            working_dir: Directory to use for execution
            dataset_names: List of dataset names to retrieve from the registry
            timeout: Maximum execution time in seconds

        Returns:
            A dictionary containing execution results with model artifacts and their registry names
        """
        # Log the distributed flag
        logger.debug(f"execute_training_code called with distributed={distributed}")

        object_registry = ObjectRegistry()

        execution_id = f"{node_id}-{uuid.uuid4()}"
        try:
            # Get actual datasets from registry
            datasets = object_registry.get_multiple(DataFrame, dataset_names)

            # Create a node to store execution results
            node = Node(solution_plan="")  # We only need this for execute_node

            # Get callbacks from the registry and notify them
            node.training_code = code

            # Import here to avoid circular imports
            from aiden.config import config

            # Get the appropriate executor class via the factory
            executor_class = _get_executor_class(distributed=distributed)

            # Create an instance of the executor
            logger.debug(f"Creating {executor_class.__name__} for execution ID: {execution_id}")
            executor = executor_class(
                execution_id=execution_id,
                code=code,
                working_dir=working_dir,
                datasets=datasets,
                timeout=timeout,
                code_execution_file_name=config.execution.runfile_name,
            )

            # Execute and collect results - ProcessExecutor.run() handles cleanup internally
            logger.debug(f"Executing node {node} using executor {executor}")
            result = executor.run()
            logger.debug(f"Execution result: {result}")
            node.execution_time = result.exec_time
            node.execution_stdout = result.term_out
            node.exception_was_raised = result.exception is not None
            node.exception = result.exception or None

            node.training_code = code

            # Check if the execution failed in any way
            if node.exception is not None:
                raise RuntimeError(f"Execution failed with exception: {node.exception}")

            # Register code and artifacts
            object_registry.register(Code, execution_id, Code(node.training_code))

            # Return results
            return {
                "success": not node.exception_was_raised,
                "exception": str(node.exception) if node.exception else None,
                "transformation_code_id": execution_id,
            }
        except Exception as e:
            # Log full stack trace at debug level
            import traceback

            logger.debug(f"Error executing training code: {str(e)}\n{traceback.format_exc()}")

            return {
                "success": False,
                "exception": str(e),
            }

    return execute_code


def _get_executor_class(distributed: bool = False) -> Type:
    """Get the appropriate executor class based on the distributed flag.

    Args:
        distributed: Whether to use distributed execution if available

    Returns:
        Executor class (not instance) appropriate for the environment
    """
    # Log the distributed flag
    logger.debug(f"get_executor_class using distributed={distributed}")
    if distributed:
        try:
            # Try to import Ray executor
            from aiden.models.execution.ray_executor import RayExecutor

            logger.debug("Using Ray for distributed execution")
            return RayExecutor
        except ImportError:
            # Fall back to process executor if Ray is not available
            logger.warning("Ray not available, falling back to ProcessExecutor")
            return ProcessExecutor

    # Default to ProcessExecutor for non-distributed execution
    logger.debug("Using ProcessExecutor (non-distributed)")
    return ProcessExecutor
