from aiden import Transformation, config
from aiden.common.dataset import Dataset
from aiden.common.environment import Environment
from aiden.common.provider import ProviderConfig

config.configure_logging(level="DEBUG")

# Configure AI providers for each agent
provider_config = ProviderConfig(
    manager_provider="anthropic/claude-sonnet-4-20250514",
    data_expert_provider="anthropic/claude-opus-4-20250514",
    data_engineer_provider="openai/gpt-4o",
    tool_provider="anthropic/claude-sonnet-4-20250514",
)

# Define input and output datasets
in_dev_dataset = Dataset(
    path="./tests/input_data/emails.csv",
    format="csv",
    schema={"email": str},
)
out_dev_dataset = Dataset(
    path="./tests/output_data/clean_emails.csv",
    format="csv",
    schema={"email": str},
)

# Create environment object with custom workdir
dev_env = Environment(
    type="local",
    workdir="./tests/workdir/",
)

# Define transformation with natural language intent
tr = Transformation(
    intent="clean emails column and keep only valid ones.",
    environment=dev_env,
)

# Build the transformation with specified datasets and providers
tr.build(
    input_datasets=[in_dev_dataset],
    output_dataset=out_dev_dataset,
    provider=provider_config,
    verbose=False,
    max_iterations=1,
    timeout=10,
)

# Deploy the transformation
tr.save("./tests/artifacts/email_transformation.py")
