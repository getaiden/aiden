<div align="center">

# Aiden

[![PyPI version](https://img.shields.io/pypi/v/aiden-ai.svg)](https://pypi.org/project/aiden-ai/)
[![Python Version](https://img.shields.io/pypi/pyversions/aiden-ai.svg)](https://pypi.org/project/aiden-ai/)
[![License](https://img.shields.io/github/license/getaiden/aiden.svg)](LICENSE.md)

**An agentic framework for building data transformations from natural language**

[Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Examples](#examples) • [Contributing](#contributing)

</div>

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
  - [Environment Types](#environment-types)
  - [Provider Configuration](#provider-configuration)
  - [Dataset Definitions](#dataset-definitions)
  - [Save result artifact](#save-result-artifact)
- [Examples](#examples)
- [Contributing](#contributing)
- [Community](#community)
- [License](#license)

## 🔍 Overview

Aiden is a Python framework that enables you to build data transformations using natural language. It leverages a multi-agent AI architecture to simplify data engineering tasks, making them more accessible and efficient. With Aiden, you can describe your data transformation requirements in plain text, and the framework will generate the necessary code to implement them.

## 💻 Installation

### Using pip or poetry

```bash
pip install aiden-ai
# or with poetry
poetry add aiden-ai
```

### SET environment variables
The environment variables are used to configure the AI providers.
We use litellm to manage the providers. You can find the list of supported providers [here](https://github.com/BerriAI/litellm/blob/main/.env.example).

```bash
export OPENAI_API_KEY="your-openai-api-key"
# or
export ANTHROPIC_API_KEY="your-anthropic-api-key"
# or
export GEMINI_API_KEY="your-google-api-key"
# or ...
```

### Optional Dependencies

For Dagster integration:

```bash
pip install aiden-ai[dagster]
# or with poetry
poetry add 'aiden-ai[dagster]'
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/getaiden/aiden-ai.git
cd aiden

# Install dependencies with Poetry
poetry install

# Activate the virtual environment
source .venv/bin/activate
```

## 🚀 Quick Start

Here's a simple example to get you started with Aiden:

```python
from aiden import Transformation
from aiden.common.dataset import Dataset

# Define input and output datasets with schemas
input_data = Dataset(
    path="./data.csv", 
    format="csv",
    schema={"email": str, "name": str, "signup_date": str}
)
output_data = Dataset(
    path="./transformed_data.csv", 
    format="csv",
    schema={"email": str, "name": str, "signup_date": str}
)

# Create a transformation with natural language intent
transformation = Transformation(
    intent="Clean the 'email' column and remove invalid entries"
)

# Build and save the transformation
transformation.build(
    input_datasets=[input_data],
    output_dataset=output_data
)
transformation.save("./email_cleaner.py")
```

## ✨ Features

### Environment Types

Aiden supports multiple execution environments:

The `workdir` is the directory where Aiden will store temporary files.

- **Local Environment**: Will generate a python artifact that can be executed locally.
  ```python
  from aiden.common.environment import Environment
  
  local_env = Environment(type="local", workdir="./local_workdir/")

  transformation = Transformation(
    intent="Clean the 'email' column and remove invalid entries",
    environment=local_env,
  )
  ```

- **Dagster Environment**: Will generate a python dagster artifact that can be executed in a dagster environment.
  ```python
  dagster_env = Environment(
      type="dagster",
      workdir="./dagster_workdir/"
  )

  transformation = Transformation(
    intent="Clean the 'email' column and remove invalid entries",
    environment=dagster_env,
  )
  ```

### Provider Configuration

Customize which AI models power each agent in the multi-agent system:

```python
from aiden.common.provider import ProviderConfig

provider_config = ProviderConfig(
    manager_provider="openai/gpt-4o",
    data_expert_provider="openai/gpt-4o",
    data_engineer_provider="openai/gpt-4o",
    tool_provider="anthropic/claude-3-7-sonnet-latest",
)

transformation = Transformation(
    intent="Clean the 'email' column and remove invalid entries",
)
transformation.build(
    input_datasets=[input_data],
    output_dataset=output_data,
    provider=provider_config,
    verbose=True,
)
```

### Dataset Definitions

Explicitly define input and output datasets with schema for transformation:

```python
from aiden.common.dataset import Dataset

dataset = Dataset(
    path="./data.csv",
    format="csv",
    schema={"column1": str, "column2": int}
)
```

### Save result artifact

Save transformations as standalone Python files that can be executed in various environments:

```python
transformation.save("./artifact.py")
```

#### Testing Artifacts

Once you've saved your transformation, you can test it in the environment you built with:

- **Local Environment**:
  ```bash
  # Run the artifact directly with Python
  python artifact.py
  ```

- **Dagster Environment**:
  ```bash
  # Start the Dagster development server
  dagster dev -f artifact.py
  
  # Then execute the artifact from the Dagster UI
  ```

## 📊 Examples

Here's a comprehensive example showing how to clean email addresses with custom configuration:

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

# Create local environment with custom workdir
local_env = Environment(
    type="local",
    workdir="./local_workdir/",
)

# Define transformation with natural language intent using local environment
tr = Transformation(
    intent="clean emails column and keep only valid ones.",
    environment=local_env,
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

Check out the [examples](./tests) directory for more use cases.

## 🤝 Contributing

We welcome contributions to Aiden! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `poetry run pytest tests/unit`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 👥 Community

- [Discord](https://discord.gg/getaiden)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
