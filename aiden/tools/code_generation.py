import logging
from typing import List

from smolagents import Tool, tool

from aiden.common.environment import Environment
from aiden.common.provider import Provider
from aiden.generators import TransformationCodeGenerator

logger = logging.getLogger(__name__)


def get_generate_transformation_code(llm_to_use: str, environment: Environment) -> Tool:
    """Returns a tool function to generate transformation code with the model ID pre-filled."""

    @tool
    def generate_transformation_code(
        task: str,
        solution_plan: str,
        input_datasets_names: List[str],
        output_dataset_name: str,
    ) -> str:
        """Generates transformation code based on the solution plan.

        Args:
            task: The task definition
            solution_plan: The solution plan to implement
            input_datasets_names: Names of datasets to use for transformation
            output_dataset_name: Name of the dataset to store the transformation results

        Returns:
            Generated transformation code as a string
        """
        generator = TransformationCodeGenerator(Provider(llm_to_use), environment)
        return generator.generate_transformation_code(task, solution_plan, input_datasets_names, output_dataset_name)

    return generate_transformation_code


def get_fix_transformation_code(llm_to_use: str, environment: Environment) -> Tool:
    """Returns a tool function to fix transformation code with the model ID pre-filled."""

    @tool
    def fix_transformation_code(
        transformation_code: str,
        solution_plan: str,
        review: str,
        issue: str,
    ) -> str:
        """
        Fixes issues in the transformation code based on a review.

        Args:
            transformation_code: The transformation code to fix
            solution_plan: The solution plan being implemented
            review: Review comments about the code and its issues, ideally a summary analysis of the issue
            issue: Description of the issue to address

        Returns:
            Fixed transformation code as a string
        """
        generator = TransformationCodeGenerator(Provider(llm_to_use), environment)
        return generator.fix_transformation_code(transformation_code, solution_plan, review, issue)

    return fix_transformation_code
