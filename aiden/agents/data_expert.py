from typing import Optional, Callable
from smolagents import ToolCallingAgent, LiteLLMModel
from aiden.common.utils.prompt import get_prompt_templates


class DataExpertAgent:
    def __init__(
        self,
        model_id: str,
        verbosity: int,
        chain_of_thought_callable: Optional[Callable] = None,
    ):
        self.agent = ToolCallingAgent(
            name="data_expert",
            description=(
                "Data expert that develops detailed solution ideas and plan for Data transformation use case. "
                "To work effectively, as part of the 'task' prompt the agent STRICTLY requires:"
                "- the Data transformation task definition (i.e. 'intent')"
                "- the input datasets (containe name, path, format, schema)"
                "- the output dataset (containe name, path, format, schema)"
            ),
            model=LiteLLMModel(model_id=model_id),
            tools=[],
            add_base_tools=False,
            verbosity_level=verbosity,
            prompt_templates=get_prompt_templates("toolcalling_agent.yaml", "data_expert_prompt_templates.yaml"),
            step_callbacks=[chain_of_thought_callable],
        )
