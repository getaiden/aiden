from aiden import Transformation
from aiden.common.dataset import Dataset
from aiden.common.environment import Environment
from aiden.common.provider import ProviderConfig

# Configure AI providers for each agent
provider_config = ProviderConfig(
    manager_provider="openai/gpt-4o",
    data_expert_provider="openai/gpt-4o",
    data_engineer_provider="openai/gpt-4o",
    tool_provider="anthropic/claude-3-7-sonnet-latest",
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
    verbose=True,
)

# Deploy the transformation
tr.save("./tests/artifacts/emails_transformation.py")