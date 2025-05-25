"""
This module defines a multi-agent ML engineering system for building machine learning models.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable

from aiden.common.environment import Environment
from aiden.registries.objects import ObjectRegistry
from aiden.entities.code import Code
from aiden.agents.manager import ManagerAgent
from aiden.agents.data_expert import DataExpertAgent
from aiden.agents.data_engineer import DataEngineerAgent

logger = logging.getLogger(__name__)


@dataclass
class AidenGenerationResult:
    transformation_source_code: str
    solution_plan: str
    metadata: Dict[str, str] = field(default_factory=dict)


class AidenAgent:
    """
    Multi-agent ML engineering system for building machine learning models.

    This class creates and manages a system of specialized agents that work together
    to analyze data, plan solutions, train models, and generate inference code.
    """

    def __init__(
        self,
        manager_model_id: str = "openai/gpt-4o",
        data_expert_model_id: str = "openai/gpt-4o",
        data_engineer_model_id: str = "openai/gpt-4o",
        tool_model_id: str = "anthropic/claude-3-7-sonnet-latest",
        environment: Environment = None,
        max_steps: int = 30,
        verbose: bool = False,
        chain_of_thought_callable: Optional[Callable] = None,
    ):
        """
        Initialize the multi-agent ML engineering system.

        Args:
            manager_model_id: Model ID for the manager agent
            data_expert_model_id: Model ID for the data expert agent
            data_engineer_model_id: Model ID for the data engineer agent
            tool_model_id: Model ID for the model used inside tool calls
            max_steps: Maximum number of steps for the manager agent
            verbose: Whether to display detailed agent logs
            chain_of_thought_callable: Callable to use for chain of thought output
        """
        self.manager_model_id = manager_model_id
        self.data_expert_model_id = data_expert_model_id
        self.data_engineer_model_id = data_engineer_model_id
        self.tool_model_id = tool_model_id
        self.environment = environment
        self.max_steps = max_steps
        self.verbose = verbose
        self.chain_of_thought_callable = chain_of_thought_callable

        # Set verbosity levels
        self.manager_verbosity = 2 if verbose else 0
        self.specialist_verbosity = 1 if verbose else 0

        # Create transformation coder agent - implements transformation code
        self.data_engineer = DataEngineerAgent(
            model_id=self.data_engineer_model_id,
            verbosity=self.specialist_verbosity,
            environment=self.environment,
            tool_model_id=self.tool_model_id,
            chain_of_thought_callable=self.chain_of_thought_callable,
        ).agent

        # Create solution planner agent - plans Data transformation approaches
        self.data_expert = DataExpertAgent(
            model_id=self.data_expert_model_id,
            verbosity=self.specialist_verbosity,
            chain_of_thought_callable=self.chain_of_thought_callable,
        ).agent

        # Create manager agent - coordinates the workflow
        self.manager_agent = ManagerAgent(
            model_id=self.manager_model_id,
            verbosity=self.manager_verbosity,
            max_steps=self.max_steps,
            managed_agents=[self.data_expert, self.data_engineer],
            chain_of_thought_callable=self.chain_of_thought_callable,
        ).agent

    def run(self, task, additional_args: dict) -> AidenGenerationResult:
        """
        Run the orchestrator agent to generate a machine learning model.

        Returns:
            AidenGenerationResult: The result of the model generation process.
        """
        object_registry = ObjectRegistry()
        result = self.manager_agent.run(task=task, additional_args=additional_args)

        try:
            # Only log the full result when in verbose mode
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Agent result: %s", result)

            # Extract data from the agent result
            transformation_code_id = result.get("transformation_code_id", "")
            transformation_code = object_registry.get(Code, transformation_code_id).code

            # Model metadata
            metadata = result.get("metadata", {"model_type": "unknown", "framework": "unknown"})

            return AidenGenerationResult(
                transformation_source_code=transformation_code,
                solution_plan=result.get("solution_plan", ""),
                metadata=metadata,
            )
        except Exception as e:
            raise RuntimeError(f"❌ Failed to process agent result: {str(e)}") from e
