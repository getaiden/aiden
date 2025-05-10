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
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel

from aiden.common.provider import Provider
from aiden.common.utils.response import extract_code
from aiden.config import config, prompt_templates

logger = logging.getLogger(__name__)


class TransformationCodeGenerator:
    """
    A class to generate, fix, and review transformation code.
    """

    def __init__(self, provider: Provider):
        """
        Initializes the TransformationCodeGenerator with an empty history.

        :param Provider provider: The provider to use for querying.
        """
        self.provider = provider
        self.history: List[Dict[str, str]] = []

    def generate_transformation_code(
        self,
        problem_statement: str,
        plan: str,
        transformation_datasets: List[str],
    ) -> str:
        """
        Generates transformation code based on the given problem statement and solution plan.

        :param [str] problem_statement: The description of the problem to be solved.
        :param [str] plan: The proposed solution plan.
        :return str: The generated transformation code.
        """
        return extract_code(
            self.provider.query(
                system_message=prompt_templates.transformation_system(),
                user_message=prompt_templates.transformation_generate(
                    problem_statement=problem_statement,
                    plan=plan,
                    transformation_data_files=[Path(f"{file}.parquet").as_posix() for file in transformation_datasets],
                    history=self.history,
                    allowed_packages=config.code_generation.allowed_packages,
                ),
            )
        )

    def fix_transformation_code(
        self,
        transformation_code: str,
        plan: str,
        review: str,
        problems: str = None,
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
                    ),
                    response_format=FixResponse,
                )
            )
        )
        return extract_code(response.code)

    def review_transformation_code(
        self, transformation_code: str, problem_statement: str, plan: str, problems: str = None
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
            ),
        )

    def generate_transformation_tests(self, problem_statement: str, plan: str, transformation_code: str) -> str:
        raise NotImplementedError("Generation of the transformation tests is not yet implemented.")

    def fix_transformation_tests(
        self, transformation_tests: str, transformation_code: str, review: str, problems: str = None
    ) -> str:
        raise NotImplementedError("Fixing of the transformation tests is not yet implemented.")

    def review_transformation_tests(
        self, transformation_tests: str, transformation_code: str, problem_statement: str, plan: str
    ) -> str:
        raise NotImplementedError("Review of the transformation tests is not yet implemented.")
