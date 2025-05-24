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
products_dataset = Dataset(
    path="./tests/input_data/product_and_sales/product.csv",
    format="csv",
    schema={"product_id": str, "name": str, "category": str, "price": int},
)
sales_dataset = Dataset(
    path="./tests/input_data/product_and_sales/sales.csv",
    format="csv",
    schema={"sale_id": str, "product_id": str, "quantity": int, "sale_date": str},
)
out_dev_dataset = Dataset(
    path="./tests/output_data/sales_revenue.csv",
    format="csv",
    schema={"sale_id": str, "total_revenue": int},
)

# Create environment object with custom workdir
dev_env = Environment(
    type="local",
    workdir="./tests/workdir/",
)

# Define transformation with natural language intent
tr = Transformation(
    intent="calculate the total revenue for each sale.",
    environment=dev_env,
)

# Build the transformation with specified datasets and providers
tr.build(
    input_datasets=[products_dataset, sales_dataset],
    output_dataset=out_dev_dataset,
    provider=provider_config,
    verbose=True,
)

# Deploy the transformation
tr.save("./tests/artifacts/sales_revenue.py")
