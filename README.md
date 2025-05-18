<div align="center">

# Aiden

[![PyPI version](https://img.shields.io/pypi/v/aiden-ai.svg)](https://pypi.org/project/aiden-ai/)
[![Python Version](https://img.shields.io/pypi/pyversions/aiden-ai.svg)](https://pypi.org/project/aiden-ai/)
[![License](https://img.shields.io/github/license/getaiden/aiden.svg)](LICENSE)

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
  - [Deployment](#deployment)
- [Examples](#examples)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Community](#community)
- [Roadmap](#roadmap)
- [License](#license)

## 🔍 Overview

Aiden is a Python framework that enables you to build data transformations using natural language. It leverages a multi-agent AI architecture to simplify data engineering tasks, making them more accessible and efficient. With Aiden, you can describe your data transformation requirements in plain English, and the framework will generate the necessary code to implement them.

## 💻 Installation

### Using pip

```bash
pip install aiden-ai
```

### Using Poetry

```bash
poetry add aiden-ai
```

### Optional Dependencies

For Dagster integration:

```bash
pip install aiden-ai[dagster]
# or with poetry
poetry install --extras dagster
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/getaiden/aiden.git
cd aiden

# Install dependencies with Poetry
poetry install

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
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

- **Local Environment**: For development and testing
  ```python
  from aiden.common.environment import Environment
  
  local_env = Environment(type="local", workdir="./local_workdir/")
  ```

- **Dagster Environment**: For production-grade data orchestration
  ```python
  dagster_env = Environment(
      type="dagster",
      workdir="./dagster_workdir/"
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
```

### Dataset Definitions

Explicitly define input and output datasets with schemas for validation and transformation:

```python
from aiden.common.dataset import Dataset

dataset = Dataset(
    path="./data.csv",
    format="csv",
    schema={"column1": str, "column2": int}
)
```

### Deployment

Save transformations as standalone Python files that can be executed in various environments:

```python
transformation.save("./artifact.py")
```

#### Testing Artifacts

Once you've saved your transformation, you can test it in different environments:

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

Check out the [examples](./examples) directory for more use cases.

## 📚 Documentation

For detailed documentation, visit our [documentation site](https://docs.getaiden.ai) or check the [docs](./docs) directory in this repository.

## 🤝 Contributing

We welcome contributions to Aiden! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `poetry run pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## 👥 Community

- [Discord](https://discord.gg/getaiden)
- [Twitter](https://twitter.com/getaiden)
- [GitHub Discussions](https://github.com/getaiden/aiden/discussions)

## 🗺️ Roadmap

See our [public roadmap](https://github.com/getaiden/aiden/projects) to learn about upcoming features and improvements.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.