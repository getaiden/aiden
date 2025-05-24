"""
This module provides tools for forcing an agent to return its response in a specific format.
"""

from typing import Optional

from smolagents import tool


@tool
def format_final_manager_agent_response(
    task_description: str,
    solution_plan: str,
    transformation_code_id: str,
) -> dict:
    """
    Returns a dictionary containing the exact fields that the agent must return in its final response. The purpose
    of this tool is to 'package' the final deliverables of the Data Engineering task. The 'solution_plan' has to be
    the plan returned by the data_expert agent, while 'transformation_code_id' must be
    the identifier returned by the data_engineer agent for the transformation code.

    Args:
        task_description: The description of the task
        solution_plan: The solution plan explanation for the the transformation
        transformation_code_id: The transformation code id returned by the data_engineer agent for the selected plan

    Returns:
        Dictionary containing the fields that must be returned by the agent in its final response
    """

    return {
        "task_description": task_description,
        "solution_plan": solution_plan,
        "transformation_code_id": transformation_code_id,
    }


@tool
def format_final_de_agent_response(
    transformation_code_id: str,
    execution_success: bool,
    exception: Optional[str] = None,
) -> dict:
    """
    Returns a dictionary containing the exact fields that the agent must return in its final response. The fields
    'exception' is optional. It MUST be included if it is available, but can be omitted if it is not available.

    Args:
        transformation_code_id: The transformation code id returned by the code execution tool after executing the transformation code
        execution_success: Boolean indicating if the transformation code executed successfully
        exception: Exception message if the code execution failed, if any

    Returns:
        Dictionary containing the fields that must be returned by the agent in its final response
    """

    return {
        "transformation_code_id": transformation_code_id,
        "execution_success": execution_success,
        "exception": exception,
    }
