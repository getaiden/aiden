import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, Type

from pandas import DataFrame
from pydantic import BaseModel

from aiden.agents import AidenAgent
from aiden.common.provider import ProviderConfig
from aiden.common.registries.objects import ObjectRegistry
from aiden.common.utils.pydantic_utils import format_schema, map_to_basemodel
from aiden.common.utils.transformation_state import TransformationState
from aiden.config import prompt_templates
from aiden.models.entities.description import TransformationDescription, SchemaInfo, CodeInfo
from aiden.common.utils.transformation_utils import format_code_snippet

# Define placeholders for classes that will be implemented later
# This allows the code to type-check while maintaining the intended structure

logger = logging.getLogger(__name__)


class Transformation:
    """
    Represents a transformation that transforms inputs to outputs according to a specified intent.

    A `Transformation` is defined by a human-readable description of its expected intent, as well as structured
    definitions of its input schema and output schema.

    Attributes:
        intent (str): A human-readable, natural language description of the model's expected intent.
        output_schema (dict): A mapping of output key names to their types.
        input_schema (dict): A mapping of input key names to their types.

    Example:
        model = Transformation(
            intent="Clean emails column and keep only valide ones.",
            output_schema=create_model("output_schema", **{"price": float}),
            input_schema=create_model("input_schema", **{
                "bedrooms": int,
                "bathrooms": int,
                "square_footage": float,
            })
        )
    """

    def __init__(
        self,
        intent: str,
        input_schema: Type[BaseModel] | Dict[str, type] = None,
        output_schema: Type[BaseModel] | Dict[str, type] = None,
    ):
        self.intent: str = intent
        self.input_schema: Type[BaseModel] = map_to_basemodel("in", input_schema) if input_schema else None
        self.output_schema: Type[BaseModel] = map_to_basemodel("out", output_schema) if output_schema else None
        self.validation_dataset: Dict[str, DataFrame] = dict()

        # The model's mutable state is defined by these fields
        self.state: TransformationState = TransformationState.DRAFT
        self.transformer_source: str | None = None
        self.metadata: Dict[str, str] = dict()  # todo: initialise metadata, etc

        # Registries used to make datasets, artifacts and other objects available across the system
        self.object_registry = ObjectRegistry()

        # Setup the working directory and unique identifiers
        self.identifier: str = f"transformation-{abs(hash(self.intent))}-{str(uuid.uuid4())}"
        self.run_id = f"run-{datetime.now().isoformat()}".replace(":", "-").replace(".", "-")
        self.working_dir = f"./workdir/{self.run_id}/"
        os.makedirs(self.working_dir, exist_ok=True)

    def build(
        self,
        validation_dataset: DataFrame,
        provider: str | ProviderConfig = "openai/gpt-4o",
        timeout: int = None,
        verbose: bool = False,
    ) -> None:
        # Ensure the object registry is cleared before building
        self.object_registry.clear()

        try:
            # Convert string provider to config if needed
            if isinstance(provider, str):
                provider_config = ProviderConfig(default_provider=provider)
            else:
                provider_config = provider

            # We use the tool_provider for schema resolution and tool operations
            # TODO: provider_obj = Provider(model=provider_config.tool_provider)
            self.state = TransformationState.BUILDING

            # Step 1: register validation dataset
            self.validation_dataset["validation_dataset"] = validation_dataset
            self.object_registry.register(DataFrame, "validation_dataset", validation_dataset)

            # Step 2: resolve schemas
            self.object_registry.register(dict, "input_schema", format_schema(self.input_schema))
            self.object_registry.register(dict, "output_schema", format_schema(self.output_schema))

            # Step 3: generate model
            # Start the model generation run
            agent_prompt = prompt_templates.agent_builder_prompt(
                intent=self.intent,
                input_schema=json.dumps(format_schema(self.input_schema), indent=4),
                output_schema=json.dumps(format_schema(self.output_schema), indent=4),
                datasets=["`validation_dataset`"],
                working_dir=self.working_dir,
            )

            agent = AidenAgent(
                manager_model_id=provider_config.manager_provider,
                data_expert_model_id=provider_config.data_expert_provider,
                data_engineer_model_id=provider_config.data_engineer_provider,
                tool_model_id=provider_config.tool_provider,
                max_steps=30,
                verbose=verbose,
            )
            generated = agent.run(
                agent_prompt,
                additional_args={
                    "intent": self.intent,
                    "working_dir": self.working_dir,
                    "input_schema": format_schema(self.input_schema),
                    "output_schema": format_schema(self.output_schema),
                    "timeout": timeout,
                },
            )

            # Step 4: update model state and attributes
            self.transformer_source = generated.transformation_source_code

            # Store the model metadata from the generation process
            self.metadata.update(generated.metadata)

            # # Store provider information in metadata
            # self.metadata["provider"] = str(provider_config.default_provider)
            # self.metadata["orchestrator_provider"] = str(provider_config.orchestrator_provider)
            # self.metadata["expert_provider"] = str(provider_config.expert_provider)
            # self.metadata["engineer_provider"] = str(provider_config.engineer_provider)
            # self.metadata["ops_provider"] = str(provider_config.ops_provider)
            # self.metadata["tool_provider"] = str(provider_config.tool_provider)

            self.state = TransformationState.READY

        except Exception as e:
            self.state = TransformationState.ERROR
            # Log full stack trace at debug level
            import traceback

            logger.debug(f"Error during model building: {str(e)}\n{traceback.format_exc()}")

            # Log a shorter message at error level
            logger.error(f"Error during model building: {str(e)[:50]}")
            raise e

    def get_state(self) -> TransformationState:
        """
        Return the current state of the model.
        :return: the current state of the model
        """
        return self.state

    def get_metadata(self) -> dict:
        """
        Return metadata about the model.
        :return: metadata about the model
        """
        return self.metadata

    def describe(self) -> TransformationDescription:
        """
        Return a structured description of the model.

        :return: A TransformationDescription object with various methods like to_dict(), as_text(),
                as_markdown(), to_json() for different output formats
        """
        # Create schema info
        schemas = SchemaInfo(
            input=format_schema(self.input_schema),
            output=format_schema(self.output_schema),
        )

        # Create code info
        code = CodeInfo(
            transformation=format_code_snippet(self.transformer_source),
        )

        # Assemble and return the complete model description
        return TransformationDescription(
            id=self.identifier,
            state=self.state.value,
            intent=self.intent,
            schemas=schemas,
            code=code,
        )
