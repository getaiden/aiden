"""
Module: LocalExecutor for Isolated Python Code Execution

This module provides an implementation of the `Executor` interface for executing Python code snippets
in an isolated process. It captures stdout, stderr, exceptions, and stack traces, and enforces
timeout limits on execution.

Classes:
    - RedirectQueue: A helper class to redirect stdout and stderr to a multiprocessing Queue.
    - LocalExecutor: A class to execute Python code snippets in an isolated process.

Usage:
    Create an instance of `LocalExecutor`, providing the Python code, working directory, and timeout.
    Call the `run` method to execute the code and return the results in an `ExecutionResult` object.

Exceptions:
    - Raises `RuntimeError` if the child process fails unexpectedly.

"""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

from aiden.config import config
from aiden.executors.executor import ExecutionResult, Executor
from aiden.common.environment import Environment

logger = logging.getLogger(__name__)


class LocalExecutor(Executor):
    """
    Execute Python code snippets in an isolated process.

    The `LocalExecutor` class implements the `Executor` interface, allowing Python code
    snippets to be executed with strict isolation, output capture, and timeout enforcement.
    """

    def __init__(
        self,
        execution_id: str,
        code: str,
        working_dir: Path | str,
        timeout: int,
        environment: Environment,
        code_execution_file_name: str = config.execution.runfile_name,
    ):
        """
        Initialize the LocalExecutor.

        Args:
            execution_id (str): Unique identifier for this execution.
            code (str): The Python code to execute.
            working_dir (Path | str): The working directory for execution.
            datasets (Dict[str, str]): Datasets to be used for execution.
            timeout (int): The maximum allowed execution time in seconds.
            environment (Environment): The environment to use for execution.
            code_execution_file_name (str): The filename to use for the executed script.
        """
        super().__init__(code, timeout)
        # Create a unique working directory for this execution
        self.working_dir = Path(working_dir).resolve() / execution_id
        self.working_dir.mkdir(parents=True, exist_ok=True)
        # Set the file names for the code and training data
        self.code_file_name = code_execution_file_name
        # Keep track of resources for cleanup
        self.dataset_files = []
        self.code_file = None
        self.process = None
        self.environment = environment

    def run(self) -> ExecutionResult:
        """Execute code in a subprocess and return results."""
        logger.debug(f"LocalExecutor is executing code with working directory: {self.working_dir}")
        start_time = time.time()

        try:
            # Write code to file with module environment setup
            self.code_file = self.working_dir / self.code_file_name
            module_setup = "import os\nimport sys\nfrom pathlib import Path\n\n"
            with open(self.code_file, "w", encoding="utf-8") as f:
                f.write(module_setup + self.code)

            # Execute the code in a subprocess
            if self.environment.type == "local":
                self.process = subprocess.Popen(
                    [
                        sys.executable,
                        str(self.code_file),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd(),  # str(self.working_dir),
                    text=True,
                )
            elif self.environment.type == "dagster":
                self.process = subprocess.Popen(
                    [
                        "dagster",
                        "job",
                        "execute",
                        "-f",
                        str(self.code_file),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd(),  # str(self.working_dir),
                    text=True,
                )

            stdout, stderr = self.process.communicate(timeout=self.timeout)
            exec_time = time.time() - start_time

            # Collect all model artifacts created by the execution - not code or datasets
            model_artifacts = []
            model_dir = self.working_dir / "model_files"
            if model_dir.exists() and model_dir.is_dir():
                model_artifacts.append(str(model_dir))
            else:
                # If model_files directory doesn't exist, collect individual files
                for file in self.working_dir.iterdir():
                    if file != self.code_file:
                        model_artifacts.append(str(file))

            if self.process.returncode != 0:
                return ExecutionResult(
                    term_out=[stdout],
                    exec_time=exec_time,
                    exception=RuntimeError(f"Process exited with code {self.process.returncode}: {stderr}"),
                )

            # Extract performance and create result
            return ExecutionResult(
                term_out=[stdout],
                exec_time=exec_time,
            )

        except subprocess.TimeoutExpired:
            if self.process:
                self.process.kill()

            return ExecutionResult(
                term_out=[],
                exec_time=self.timeout,
                exception=TimeoutError(
                    f"Execution exceeded {self.timeout}s timeout - individual run timeout limit reached"
                ),
            )
        except Exception as e:
            stdout, stderr = "", ""

            if self.process:
                # Try to collect any output that was produced before the exception
                try:
                    if hasattr(self.process, "stdout") and self.process.stdout:
                        stdout = self.process.stdout.read() or ""
                except Exception:
                    pass  # Best effort to get output

                self.process.kill()

            return ExecutionResult(
                term_out=[stdout or f"Process failed with exception: {str(e)}"],
                exec_time=time.time() - start_time,
                exception=e,
            )
        finally:
            # Always clean up resources regardless of execution path
            self.cleanup()

    def cleanup(self):
        """
        Clean up resources after execution while preserving model artifacts.
        """
        logger.debug(f"Cleaning up resources for execution in {self.working_dir}")

        try:
            # Clean up dataset files
            for dataset_file in self.dataset_files:
                dataset_file.unlink(missing_ok=True)

            # Clean up code file
            if self.code_file:
                try:
                    self.code_file.unlink(missing_ok=True)
                except AttributeError:
                    # Python 3.7 compatibility - missing_ok not available
                    if self.code_file.exists():
                        self.code_file.unlink()

            # Terminate process if still running
            if self.process and self.process.poll() is None:
                self.process.kill()

        except Exception as e:
            logger.warning(f"Error during resource cleanup: {str(e)}")

    def __del__(self):
        """Ensure cleanup happens when the object is garbage collected."""
        try:
            self.cleanup()
        except Exception:
            # Silent failure during garbage collection - detailed logging already done in cleanup()
            pass
