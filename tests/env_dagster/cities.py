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
    path="./tests/input_data/cities.csv",
    format="csv",
    schema={"City": str, "Population": int, "GDP (USD)": int, "Area (sq mi)": int, "Median Household Income ($)": int, "County": str},
)
out_dev_dataset = Dataset(
    path="./tests/output_data/cities_ranking.csv",
    format="csv",
    schema={"City": str, "rank": int},
)

# Create environment object with custom workdir
dev_env = Environment(
    type="dagster",
    workdir="./tests/workdir/",
)

# Define transformation with natural language intent
tr = Transformation(
    intent="rank me those cities by the richest one taking into account all the information provided.",
    environment=dev_env,
)

# Build the transformation with specified datasets and providers
tr.build(
    input_datasets=[in_dev_dataset],
    output_dataset=out_dev_dataset,
    provider=provider_config,
    verbose=False,
)

# Deploy the transformation
tr.save("./tests/artifacts/dagster_cities_ranking.py")