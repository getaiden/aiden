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
```

## Example Usage

Aiden makes it easy to transform data using natural language instructions. Here's a simple example of cleaning email addresses:

```python
from aiden import Transformation
from pandas import DataFrame

# Create a validation dataset
validation_df = DataFrame(
    {
        "email":
        ["test", "test2", "test@test.com", "test@test.com"]
    }
)

# Define your transformation with natural language intent
tr = Transformation(
    intent="""Clean the email column by:
    1. Removing any leading or trailing whitespace
    2. Converting all emails to lowercase
    3. Validating email format (must contain @ and a valid domain)
    4. Removing duplicate email addresses
    5. Filtering out emails from disposable domains
    Return only the valid, cleaned email addresses.""",
    input_schema={"email": str},
    output_schema={"email": str},
)

# Build the transformation with the validation dataset
tr.build(validation_dataset=validation_df)

# Print the transformation description
print(tr.describe().as_markdown())
```

This example demonstrates how to create a transformation that cleans email addresses, validates the transformation with sample data, and then applies it to your actual dataset.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.