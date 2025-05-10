"""
This module defines a multi-agent ML engineering system for building machine learning models.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict

from smolagents import CodeAgent, LiteLLMModel, ToolCallingAgent

from aiden.common.registries.objects import ObjectRegistry
from aiden.config import config
from aiden.models.entities.code import Code
from aiden.tools.execution import get_executor_tool
from aiden.tools.response_formatting import format_final_de_agent_response, format_final_manager_agent_response
from aiden.tools.transformation import get_fix_transformation_code, get_generate_transformation_code
from aiden.utils import get_prompt_templates

logger = logging.getLogger(__name__)


@dataclass
class AidenGenerationResult:
    transformation_source_code: str
    transformation_code_id: str
    metadata: Dict[str, str] = field(default_factory=dict)  # Model metadata


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
        max_steps: int = 30,
        verbose: bool = False,
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
        """
        self.manager_model_id = manager_model_id
        self.data_expert_model_id = data_expert_model_id
        self.data_engineer_model_id = data_engineer_model_id
        self.tool_model_id = tool_model_id
        self.max_steps = max_steps
        self.verbose = verbose

        # Set verbosity levels
        self.manager_verbosity = 2 if verbose else 0
        self.specialist_verbosity = 1 if verbose else 0

        # Create transformation coder agent - implements transformation code
        self.data_engineer = ToolCallingAgent(
            name="data_engineer",
            description=(
                "Data engineer that implements Data transformation code based on provided plan. "
                "To work effectively, as part of the 'task' prompt the agent STRICTLY requires:"
                "- the Data transformation task definition (i.e. 'intent' of the transformation)"
                "- input schema for the transformation"
                "- output schema for the transformation"
                "- the full solution plan that outlines how to solve this problem given by the data_expert"
                "- the dataset name"
                "- the working directory to use for transformation execution"
            ),
            model=LiteLLMModel(model_id=self.data_engineer_model_id),
            tools=[
                get_generate_transformation_code(self.tool_model_id),
                get_fix_transformation_code(self.tool_model_id),
                get_executor_tool(),
                format_final_de_agent_response,
            ],
            add_base_tools=False,
            verbosity_level=self.specialist_verbosity,
            prompt_templates=get_prompt_templates("toolcalling_agent.yaml", "de_prompt_templates.yaml"),
        )

        # Create solution planner agent - plans Data transformation approaches
        self.data_expert = ToolCallingAgent(
            name="data_expert",
            description=(
                "Data expert that develops detailed solution ideas and plan for Data transformation use case. "
                "To work effectively, as part of the 'task' prompt the agent STRICTLY requires:"
                "- the Data transformation task definition (i.e. 'intent')"
                "- input schema for the data transformation"
                "- output schema for the data transformation"
            ),
            model=LiteLLMModel(model_id=self.data_expert_model_id),
            tools=[],
            add_base_tools=False,
            verbosity_level=self.specialist_verbosity,
            prompt_templates=get_prompt_templates("toolcalling_agent.yaml", "data_expert_prompt_templates.yaml"),
        )

        # Create orchestrator agent - coordinates the workflow
        self.manager_agent = CodeAgent(
            model=LiteLLMModel(model_id=self.manager_model_id),
            tools=[
                format_final_manager_agent_response,
            ],
            managed_agents=[self.data_expert, self.data_engineer],
            add_base_tools=False,
            verbosity_level=self.manager_verbosity,
            additional_authorized_imports=config.code_generation.authorized_agent_imports,
            prompt_templates=get_prompt_templates("code_agent.yaml", "manager_prompt_templates.yaml"),
            max_steps=self.max_steps,
            planning_interval=7,
        )

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
                transformation_code_id=transformation_code_id,
                metadata=metadata,
            )
        except Exception as e:
            raise RuntimeError(f"❌ Failed to process agent result: {str(e)}") from e
