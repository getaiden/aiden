"""
This module provides functions and classes for generating, fixing, and reviewing machine learning model training code.

Functions:
    generate_training_code: Generates machine learning model training code based on a problem statement and solution plan.
    generate_training_tests: Generates tests for the machine learning model training code.
    fix_training_code: Fixes the machine learning model training code based on review and identified problems.
    fix_training_tests: Fixes the tests for the machine learning model training code based on review and identified problems.
    review_training_code: Reviews the machine learning model training code to identify improvements and fix issues.
    review_training_tests: Reviews the tests for the machine learning model training code to identify improvements and fix issues.

Classes:
    TrainingCodeGenerator: A class to generate, fix, and review machine learning model training code.
"""

import json
import logging
from typing import Dict, List

from pydantic import BaseModel

from aiden.common.dataset import Dataset
from aiden.common.environment import Environment
from aiden.common.provider import Provider
from aiden.registries.objects import ObjectRegistry
from aiden.common.utils.response import extract_code
from aiden.config import config, prompt_templates

logger = logging.getLogger(__name__)


class TransformationCodeGenerator:
    """
    A class to generate, fix, and review transformation code.
    """

    def __init__(self, provider: Provider, environment: Environment):
        """
        Initializes the TransformationCodeGenerator with an empty history.

        :param Provider provider: The provider to use for querying.
        """
        self.provider = provider
        self.environment = environment
        self.history: List[Dict[str, str]] = []

    def generate_transformation_code(
        self,
        problem_statement: str,
        plan: str,
        input_datasets_names: List[str],
        output_dataset_name: str,
    ) -> str:
        """
        Generates transformation code based on the given problem statement and solution plan.

        :param [str] problem_statement: The description of the problem to be solved.
        :param [str] plan: The proposed solution plan.
        :param [List[str]] input_datasets_names: The names of the datasets to use for transformation.
        :param [str] output_dataset_name: The name of the dataset to store the transformation results.
        :return str: The generated transformation code.
        """
        registry = ObjectRegistry()
        input_datasets = registry.get_multiple(Dataset, input_datasets_names)
        output_dataset = registry.get(Dataset, output_dataset_name)

        return extract_code(
            self.provider.query(
                system_message=prompt_templates.transformation_system(),
                user_message=prompt_templates.transformation_generate(
                    problem_statement=problem_statement,
                    plan=plan,
                    input_datasets=[str(v) for _, v in input_datasets.items()],
                    output_dataset=str(output_dataset),
                    history=self.history,
                    allowed_packages=config.code_generation.allowed_packages,
                    environment_type=self.environment.type,
                ),
            )
        )

    def fix_transformation_code(
        self,
        transformation_code: str,
        plan: str,
        review: str,
        problems: str | None = None,
    ) -> str:
        """
        Fixes the transformation code based on the review and identified problems.

        :param [str] transformation_code: The previously generated transformation code.
        :param [str] plan: The proposed solution plan.
        :param [str] review: The review of the previous solution.
        :param [str] problems: Specific errors or bugs identified.
        :return str: The fixed transformation code.
        """

        class FixResponse(BaseModel):
            plan: str
            code: str

        response: FixResponse = FixResponse(
            **json.loads(
                self.provider.query(
                    system_message=prompt_templates.transformation_system(),
                    user_message=prompt_templates.transformation_fix(
                        plan=plan,
                        transformation_code=transformation_code,
                        review=review,
                        problems=problems,
                        allowed_packages=config.code_generation.allowed_packages,
                        environment_type=self.environment.type,
                    ),
                    response_format=FixResponse,
                )
            )
        )
        return extract_code(response.code)

    def review_transformation_code(
        self, transformation_code: str, problem_statement: str, plan: str, problems: str | None = None
    ) -> str:
        """
        Reviews the transformation code to identify improvements and fix issues.

        :param [str] transformation_code: The previously generated transformation code.
        :param [str] problem_statement: The description of the problem to be solved.
        :param [str] plan: The proposed solution plan.
        :param [str] problems: Specific errors or bugs identified.
        :return str: The review of the training code with suggestions for improvements.
        """
        return self.provider.query(
            system_message=prompt_templates.transformation_system(),
            user_message=prompt_templates.transformation_review(
                problem_statement=problem_statement,
                plan=plan,
                transformation_code=transformation_code,
                problems=problems,
                allowed_packages=config.code_generation.allowed_packages,
                environment_type=self.environment.type,
            ),
        )

    def generate_transformation_tests(self, problem_statement: str, plan: str, transformation_code: str) -> str:
        raise NotImplementedError("Generation of the transformation tests is not yet implemented.")

    def fix_transformation_tests(
        self, transformation_tests: str, transformation_code: str, review: str, problems: str | None = None
    ) -> str:
        raise NotImplementedError("Fixing of the transformation tests is not yet implemented.")

    def review_transformation_tests(
        self, transformation_tests: str, transformation_code: str, problem_statement: str, plan: str
    ) -> str:
        raise NotImplementedError("Review of the transformation tests is not yet implemented.")
