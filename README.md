# Aiden

An agentic framework for building data transformations from natural language.

## Overview

Aiden is a Python framework that enables you to build data transformations using natural language. It leverages AI agents to simplify data engineering tasks, making them more accessible and efficient.

## Installation

You can install Aiden using pip:

```bash
pip install aiden-ai
```

Or using Poetry:

```bash
poetry add aiden-ai
```

For development installation:

```bash
git clone https://github.com/getaiden/aiden.git
cd aiden
poetry install
source .venv/bin/activate
```


## Example Usage

Aiden makes it easy to transform data using natural language instructions. Here's a comprehensive example showing how to clean email addresses with custom configuration:

```python
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
    path="./emails.csv",
    format="csv",
    schema={"email": str},
)
out_dev_dataset = Dataset(
    path="./clean_emails.csv",
    format="csv",
    schema={"email": str},
)

# Create environment object with custom workdir
dev_env = Environment(
    type="local",
    workdir="./custom_workdir/",
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
tr.save("./artifact.py")
```

This example demonstrates how to:
1. Configure specific AI providers for each agent
2. Define input and output datasets with schemas
3. Set up a custom environment
4. Build a transformation with natural language intent
5. Deploy the transformation to a Python file

## Advanced Features

Aiden provides several advanced features:
- **Custom Environments**: Configure where transformations run
- **Provider Configuration**: Specify which AI models power each agent
- **Dataset Definitions**: Explicitly define input/output datasets with schemas
- **Deployment**: Save transformations as standalone Python files

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.