"""
Tools related to code execution, including running training code in isolated environments.

These tools automatically handle model artifact registration through the ArtifactRegistry,
ensuring that artifacts generated during the execution can be retrieved later in the pipeline.
"""

import logging
import uuid
from typing import Dict, List, Optional, Type

from smolagents import Tool, tool

from aiden.common.environment import Environment
from aiden.registries.objects import ObjectRegistry
from aiden.entities.code import Code
from aiden.entities.node import Node
from aiden.common.dataset import Dataset
from aiden.executors.local_executor import LocalExecutor
from aiden.callbacks import BuildStateInfo, Callback

logger = logging.getLogger(__name__)


def get_executor_tool(distributed: bool = False, environment: Optional[Environment] = None) -> Tool:
    """Get the appropriate executor tool based on the distributed flag and environment.

    Args:
        distributed: Whether to use distributed execution
        environment: The Environment object to use for execution. If None, a default local environment will be used.

    Returns:
        A callable tool function for executing code
    """

    @tool
    def execute_code(
        node_id: str,
        code: str,
        working_dir: str,
        input_dataset_names: List[str],
        output_dataset_name: str,
        timeout: int,
    ) -> Dict:
        """Executes code in an isolated environment.

        Args:
            node_id: Unique identifier for this execution
            code: The code to execute
            working_dir: Directory to use for execution
            input_dataset_names: List of dataset names to retrieve from the registry
            output_dataset_name: Name of the dataset to create
            timeout: Maximum execution time in seconds

        Returns:
            A dictionary containing execution results with model artifacts and their registry names
        """
        # Log the distributed flag
        logger.debug(f"execute_training_code called with distributed={distributed}")

        # Create default environment if none provided
        env = environment or Environment(type="local")

        # Log the environment
        logger.debug(f"execute_training_code called with environment={env}")

        object_registry = ObjectRegistry()

        execution_id = f"{node_id}-{uuid.uuid4()}"
        try:
            # Get actual datasets from registry
            input_datasets = object_registry.get_multiple(Dataset, input_dataset_names)
            output_dataset = object_registry.get(Dataset, output_dataset_name)
            # Create a node to store execution results
            node = Node(solution_plan="")  # We only need this for execute_node

            # Get callbacks from the registry and notify them
            node.training_code = code

            # Create state info once for all callbacks
            state_info = BuildStateInfo(
                intent="Unknown",  # Will be filled by agent context
                provider="Unknown",  # Will be filled by agent context
                input_datasets=[v for _, v in input_datasets.items()],
                output_dataset=output_dataset,
                iteration=0,  # Default value, no longer used for MLFlow run naming
                node=node,
            )

            # Notify all callbacks about execution start
            _notify_callbacks(object_registry.get_all(Callback), "start", state_info)

            # Import here to avoid circular imports
            from aiden.config import config

            # Get the appropriate executor class via the factory
            executor_class = _get_executor_class(distributed=distributed, environment=env)

            # Create an instance of the executor
            logger.debug(f"Creating {executor_class.__name__} for execution ID: {execution_id}")
            executor = executor_class(
                execution_id=execution_id,
                code=code,
                working_dir=working_dir,
                timeout=timeout,
                code_execution_file_name=config.execution.runfile_name,
                environment=env,
            )

            # Execute and collect results - LocalExecutor.run() handles cleanup internally
            logger.debug(f"Executing node {node} using executor {executor}")
            result = executor.run()
            logger.debug(f"Execution result: {result}")
            node.execution_time = result.exec_time
            node.execution_stdout = result.term_out
            node.exception_was_raised = result.exception is not None
            node.exception = result.exception or None

            node.training_code = code

            # Notify callbacks about the execution end with the same state_info
            # The node reference in state_info automatically reflects the updates to node
            _notify_callbacks(object_registry.get_all(Callback), "end", state_info)

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


def _get_executor_class(distributed: bool = False, environment: Environment | None = None) -> Type:
    """Get the appropriate executor class based on the distributed flag and environment.

    Args:
        distributed: Whether to use distributed execution if available
        environment: The Environment object to use for execution. If None, a default local environment will be used.

    Returns:
        Executor class (not instance) appropriate for the environment
    """
    # Log the distributed flag
    logger.debug(f"get_executor_class using distributed={distributed}")

    # Create default environment if none provided
    env = environment or Environment(type="local")

    if env.type == "local":
        if distributed:
            try:
                # Try to import Ray executor

                logger.debug("Using Ray for distributed execution")
                return LocalExecutor
            except ImportError:
                # Fall back to process executor if Ray is not available
                logger.warning("Ray not available, falling back to LocalExecutor")
                return LocalExecutor
        else:
            # Default to LocalExecutor for non-distributed execution
            logger.debug("Using LocalExecutor (non-distributed)")
            return LocalExecutor
    elif env.type == "dagster":
        return LocalExecutor
    else:
        raise ValueError(f"Unknown environment type: {env.type}")


def _notify_callbacks(callbacks: Dict, event_type: str, build_state_info) -> None:
    """Helper function to notify callbacks with consistent error handling.

    Args:
        callbacks: Dictionary of callbacks from the registry
        event_type: The event type - either "start" or "end"
        build_state_info: The state info to pass to callbacks
    """
    method_name = f"on_iteration_{event_type}"

    for callback in callbacks.values():
        try:
            getattr(callback, method_name)(build_state_info)
        except Exception as e:
            # Log full stack trace at debug level
            import traceback

            logger.debug(
                f"Error in callback {callback.__class__.__name__}.{method_name}: {e}\n{traceback.format_exc()}"
            )
            # Log a shorter message at warning level
            logger.warning(f"Error in callback {callback.__class__.__name__}.{method_name}: {str(e)[:50]}")
