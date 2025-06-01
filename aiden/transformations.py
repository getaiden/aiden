import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union


from aiden.agents import AidenAgent
from aiden.common.dataset import Dataset
from aiden.common.environment import Environment, get_environment
from aiden.common.provider import ProviderConfig
from aiden.registries.objects import ObjectRegistry
from aiden.common.utils.transformation_state import TransformationState
from aiden.common.utils.transformation_utils import format_code_snippet
from aiden.config import prompt_templates
from aiden.entities.description import CodeInfo, SchemaInfo, TransformationDescription
from aiden.callbacks import Callback, ChainOfThoughtModelCallback, BuildStateInfo
from aiden.common.utils.cot import ConsoleEmitter


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
        environment: Optional[Union[dict, "Environment"]] = None,
    ):
        self.intent: str = intent
        self.input_datasets: List["Dataset"]
        self.output_dataset: "Dataset"

        # Initialize environment
        if environment is None:
            self.environment = get_environment()
        elif isinstance(environment, Environment):
            self.environment = environment
        else:
            self.environment = get_environment(**environment)

        # The Transformation's mutable state is defined by these fields
        self.state: TransformationState = TransformationState.DRAFT
        self.transformer_source: str = ""

        # Generate a unique run ID for this transformation
        self.run_id = f"run-{datetime.now().isoformat()}".replace(":", "-").replace(".", "-")

        # Generate a unique identifier for this transformation
        self.identifier: str = f"transformation-{abs(hash(self.intent))}-{str(uuid.uuid4())}"

        # Initialize metadata dictionary
        self.metadata: Dict[str, str] = {}

        # Set working directory based on environment
        if (self.environment.is_local or self.environment.is_dagster) and self.environment.workdir:
            self.working_dir = str(Path(self.environment.workdir) / self.run_id)
            os.makedirs(self.working_dir, exist_ok=True)
        else:
            raise ValueError("A valid working directory is required in the environment configuration")

        # Registries used to make datasets, artifacts and other objects available across the system
        self.object_registry = ObjectRegistry()

    def build(
        self,
        input_datasets: List["Dataset"],
        output_dataset: "Dataset",
        provider: str | ProviderConfig = "openai/gpt-4o",
        verbose: bool = False,
        callbacks: List[Callback] = None,
        chain_of_thought: bool = True,
    ) -> None:

        # Ensure the object registry is cleared before building
        self.object_registry.clear()

        # Initialize callbacks list if not provided
        callbacks = callbacks or []

        # Add chain of thought callback if requested
        cot_callable = None
        if chain_of_thought:
            cot_model_callback = ChainOfThoughtModelCallback(emitter=ConsoleEmitter())
            callbacks.append(cot_model_callback)

            # Get the underlying callback for use with agents
            cot_callable = cot_model_callback.get_chain_of_thought_callable()

        # Register all callbacks in the object registry
        self.object_registry.register_multiple(Callback, {f"{i}": c for i, c in enumerate(callbacks)})

        try:
            # Convert string provider to config if needed
            if isinstance(provider, str):
                provider_config = ProviderConfig(default_provider=provider)
            else:
                provider_config = provider

            # We use the tool_provider for schema resolution and tool operations
            # TODO: provider_obj = Provider(model=provider_config.tool_provider)
            self.state = TransformationState.BUILDING

            # Step 1: register input/output datasets
            self.input_datasets = input_datasets
            self.output_dataset = output_dataset

            for input_dataset in input_datasets:
                self.object_registry.register(Dataset, input_dataset.name, input_dataset)
            self.object_registry.register(Dataset, output_dataset.name, output_dataset)

            # Run callbacks for build start
            for callback in self.object_registry.get_all(Callback).values():
                try:
                    # Note: callbacks still receive the actual dataset objects for backward compatibility
                    callback.on_build_start(
                        BuildStateInfo(
                            intent=self.intent,
                            provider=provider_config.tool_provider,  # Use tool_provider for callbacks
                            input_datasets=[
                                self.object_registry.get(Dataset, input_dataset.name)
                                for input_dataset in self.input_datasets
                            ],
                            output_dataset=self.object_registry.get(Dataset, self.output_dataset.name),
                        )
                    )
                except Exception as e:
                    # Log full stack trace at debug level
                    import traceback

                    logger.debug(
                        f"Error in callback {callback.__class__.__name__}.on_build_start: {e}\n{traceback.format_exc()}"
                    )

                    # Log a shorter message at warning level
                    logger.warning(f"Error in callback {callback.__class__.__name__}.on_build_start: {str(e)[:50]}")

            # Step 2: generate transformation
            # Start the transformation generation run
            agent_prompt = prompt_templates.agent_builder_prompt(
                intent=self.intent,
                input_datasets=[f"`{dataset}`" for dataset in input_datasets],
                output_dataset=f"`{output_dataset}`",
                working_dir=self.working_dir,
            )

            agent = AidenAgent(
                manager_model_id=provider_config.manager_provider,
                data_expert_model_id=provider_config.data_expert_provider,
                data_engineer_model_id=provider_config.data_engineer_provider,
                tool_model_id=provider_config.tool_provider,
                environment=self.environment,
                max_steps=30,
                verbose=verbose,
                chain_of_thought_callable=cot_callable,
            )
            generated = agent.run(
                agent_prompt,
                additional_args={
                    "intent": self.intent,
                    "working_dir": self.working_dir,
                    "input_datasets_names": [str(dataset) for dataset in input_datasets],
                    "output_dataset_name": output_dataset.name,
                },
            )

            # Run callbacks for build start
            for callback in self.object_registry.get_all(Callback).values():
                try:
                    # Note: callbacks still receive the actual dataset objects for backward compatibility
                    callback.on_build_end(
                        BuildStateInfo(
                            intent=self.intent,
                            provider=provider_config.tool_provider,  # Use tool_provider for callbacks
                            input_datasets=[
                                self.object_registry.get(Dataset, input_dataset.name)
                                for input_dataset in self.input_datasets
                            ],
                            output_dataset=self.object_registry.get(Dataset, self.output_dataset.name),
                        )
                    )
                except Exception as e:
                    # Log full stack trace at debug level
                    import traceback

                    logger.debug(
                        f"Error in callback {callback.__class__.__name__}.on_build_end: {e}\n{traceback.format_exc()}"
                    )

                    # Log a shorter message at warning level
                    logger.warning(f"Error in callback {callback.__class__.__name__}.on_build_end: {str(e)[:50]}")

            # Step 4: update model state and attributes
            self.transformer_source = generated.transformation_source_code

            # Store the model metadata from the generation process
            self.metadata.update(generated.metadata)

            # Store provider information in metadata
            self.metadata["provider"] = str(provider_config.default_provider)
            self.metadata["orchestrator_provider"] = str(provider_config.manager_provider)
            self.metadata["expert_provider"] = str(provider_config.data_expert_provider)
            self.metadata["engineer_provider"] = str(provider_config.data_engineer_provider)
            self.metadata["ops_provider"] = str(provider_config.tool_provider)
            self.metadata["tool_provider"] = str(provider_config.tool_provider)
            self.metadata["env_type"] = self.environment.type

            self.state = TransformationState.READY

        except Exception as e:
            self.state = TransformationState.ERROR
            # Log full stack trace at debug level
            import traceback

            logger.debug(f"Error during model building: {str(e)}\n{traceback.format_exc()}")

            # Log a shorter message at error level
            logger.error(f"Error during model building: {str(e)[:50]}")
            raise e

    def save(self, path: str) -> None:
        """
        Save the transformation to a file.
        :param path: path to save the transformation
        """
        with open(path, "w") as f:
            f.write(self.transformer_source)

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
        # Create schema info with all input schemas
        input_schemas_dict = {}
        for dataset in self.input_datasets:
            if dataset.schema:
                input_schemas_dict[dataset.name] = Dataset.format_schema(dataset.schema)

        schemas = SchemaInfo(
            inputs=input_schemas_dict,
            output=Dataset.format_schema(self.output_dataset.schema),
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
