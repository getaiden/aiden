from typing import List, Optional, Callable
from smolagents import CodeAgent, LiteLLMModel, MultiStepAgent
from aiden.tools.response_formatting import format_final_manager_agent_response
from aiden.config import config
from aiden.common.utils.prompt import get_prompt_templates


class ManagerAgent:
    def __init__(
        self,
        model_id: str = "openai/gpt-4o",
        verbosity: int = 2,
        max_steps: int = 30,
        managed_agents: List[MultiStepAgent] = None,
        chain_of_thought_callable: Optional[Callable] = None,
    ) -> None:

        self.agent = CodeAgent(
            name="manager",
            model=LiteLLMModel(model_id=model_id),
            tools=[
                format_final_manager_agent_response,
            ],
            managed_agents=managed_agents,
            add_base_tools=False,
            verbosity_level=verbosity,
            additional_authorized_imports=config.code_generation.authorized_agent_imports,
            prompt_templates=get_prompt_templates("code_agent.yaml", "manager_prompt_templates.yaml"),
            max_steps=max_steps,
            planning_interval=7,
            step_callbacks=[chain_of_thought_callable],
        )
