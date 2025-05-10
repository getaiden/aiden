import logging
from typing import Callable, List

from smolagents import tool

from aiden.common.provider import Provider
from aiden.generation.transformation import TransformationCodeGenerator

logger = logging.getLogger(__name__)


def get_generate_transformation_code(llm_to_use: str) -> Callable:
    """Returns a tool function to generate transformation code with the model ID pre-filled."""

    @tool
    def generate_transformation_code(task: str, solution_plan: str, transformation_datasets: List[str]) -> str:
        """Generates transformation code based on the solution plan.

        Args:
            task: The task definition
            solution_plan: The solution plan to implement
            transformation_datasets: Keys of datasets to use for transformation

        Returns:
            Generated transformation code as a string
        """
        generator = TransformationCodeGenerator(Provider(llm_to_use))
        return generator.generate_transformation_code(task, solution_plan, transformation_datasets)

    return generate_transformation_code


def get_fix_transformation_code(llm_to_use: str) -> Callable:
    """Returns a tool function to fix transformation code with the model ID pre-filled."""

    @tool
    def fix_transformation_code(
        transformation_code: str,
        solution_plan: str,
        review: str,
        issue: str,
    ) -> str:
        """
        Fixes issues in the training code based on a review.

        Args:
            transformation_code: The transformation code to fix
            solution_plan: The solution plan being implemented
            review: Review comments about the code and its issues, ideally a summary analysis of the issue
            issue: Description of the issue to address

        Returns:
            Fixed training code as a string
        """
        generator = TransformationCodeGenerator(Provider(llm_to_use))
        return generator.fix_transformation_code(transformation_code, solution_plan, review, issue)

    return fix_transformation_code
