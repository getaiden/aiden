"""
Unit tests for the response_formatting module.
"""

from aiden.tools.response_formatting import format_final_manager_agent_response, format_final_de_agent_response


def test_format_final_manager_agent_response():
    """Test basic functionality of format_final_manager_agent_response."""
    task_description = "Transform customer data from CSV to JSON format"
    solution_plan = "Read CSV file, validate data, convert to JSON structure"
    transformation_code_id = "transform_001"

    result = format_final_manager_agent_response(
        task_description=task_description,
        solution_plan=solution_plan,
        transformation_code_id=transformation_code_id,
    )

    expected = {
        "task_description": task_description,
        "solution_plan": solution_plan,
        "transformation_code_id": transformation_code_id,
    }

    assert result == expected


def test_format_final_de_agent_response():
    """Test basic functionality of format_final_de_agent_response."""
    transformation_code_id = "transform_001"
    execution_success = True
    exception = None

    result = format_final_de_agent_response(
        transformation_code_id=transformation_code_id,
        execution_success=execution_success,
        exception=exception,
    )

    expected = {
        "transformation_code_id": transformation_code_id,
        "execution_success": execution_success,
        "exception": exception,
    }

    assert result == expected
