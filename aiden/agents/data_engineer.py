from typing import Optional, Callable
from smolagents import ToolCallingAgent, LiteLLMModel
from aiden.common.utils.prompt import get_prompt_templates
from aiden.tools.response_formatting import format_final_de_agent_response
from aiden.tools.code_generation import get_generate_transformation_code, get_fix_transformation_code
from aiden.tools.execution import get_executor_tool
from aiden.common.environment import Environment


class DataEngineerAgent:
    def __init__(
        self,
        model_id: str,
        verbosity: int,
        environment: Environment,
        tool_model_id: str,
        chain_of_thought_callable: Optional[Callable] = None,
    ):
        self.agent = ToolCallingAgent(
            name="data_engineer",
            description=(
                "Data engineer that implements Data transformation code based on provided plan. "
                "To work effectively, as part of the 'task' prompt the agent STRICTLY requires:"
                "- the Data transformation task definition (i.e. 'intent' of the transformation)"
                "- the full solution plan that outlines how to solve this problem given by the data_expert"
                "- the input datasets (containe name, path, format, schema)"
                "- the output dataset (containe name, path, format, schema)"
                "- the working directory to use for transformation execution"
            ),
            model=LiteLLMModel(model_id=model_id),
            tools=[
                get_generate_transformation_code(llm_to_use=tool_model_id, environment=environment),
                get_fix_transformation_code(llm_to_use=tool_model_id, environment=environment),
                get_executor_tool(environment=environment),
                format_final_de_agent_response,
            ],
            add_base_tools=False,
            verbosity_level=verbosity,
            prompt_templates=get_prompt_templates("toolcalling_agent.yaml", "data_engineer_prompt_templates.yaml"),
            step_callbacks=[chain_of_thought_callable],
        )
