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
sales_clients = Dataset(
    path="./test_cases/input_data/sales_department/sales_clients.csv",
    format="csv",
    schema={
        "ClientID": str,
        "ClientName": str,
        "Industry": str,
        "Region": str,
        "AccountManager": str,
        "Email": str,
        "Phone": str,
        "Status": str,
    },
)
sales_employee_information = Dataset(
    path="./test_cases/input_data/sales_department/sales_employee_information.csv",
    format="csv",
    schema={
        "EmployeeID": str,
        "FirstName": str,
        "LastName": str,
        "JobTitle": str,
        "Region": str,
        "HireDate": str,
        "Email": str,
        "Phone": str,
        "ManagerID": str,
        "Status": str,
    },
)
sales_leads = Dataset(
    path="./test_cases/input_data/sales_department/sales_leads.csv",
    format="csv",
    schema={
        "LeadID": str,
        "EmployeeID": str,
        "ClientName": str,
        "ContactDate": str,
        "Status": str,
        "EstimatedValue": int,
        "Source": str,
    },
)
sales_performance = Dataset(
    path="./test_cases/input_data/sales_department/sales_performance.csv",
    format="csv",
    schema={"EmployeeID": str, "ReviewDate": str, "KPIs": str, "Score": float, "Comments": str},
)
sales_targets = Dataset(
    path="./test_cases/input_data/sales_department/sales_targets.csv",
    format="csv",
    schema={
        "EmployeeID": str,
        "Month": str,
        "Year": str,
        "TargetAmount": int,
        "AchievedAmount": int,
        "AchievementPercentage": float,
    },
)
sales_training = Dataset(
    path="./test_cases/input_data/sales_department/sales_training.csv",
    format="csv",
    schema={
        "SessionID": str,
        "TrainingTopic": str,
        "Trainer": str,
        "Date": str,
        "DurationHours": int,
        "EmployeeIDs": str,
    },
)
sales_transactions = Dataset(
    path="./test_cases/input_data/sales_department/sales_transactions.csv",
    format="csv",
    schema={
        "TransactionID": str,
        "EmployeeID": str,
        "ClientName": str,
        "TransactionDate": str,
        "Amount": int,
        "Product": str,
        "Status": str,
    },
)
out_dev_dataset = Dataset(
    path="./test_cases/output_data/fact_sales_performance.csv",
    format="csv",
    schema={
        "EmployeeID": str,
        "Year": str,
        "Month": int,
        "TotalSales": float,
        "TotalLeads": int,
        "LeadsWon": int,
        "LeadConversionRate": float,
        "SalesTarget": float,
        "SalesAchieved": float,
        "TargetAchievementPct": float,
    },
)

# Create environment object with custom workdir
dagster_env = Environment(
    type="dagster",
    workdir="./test_cases/workdir/",
)

# Define transformation with natural language intent
tr = Transformation(
    intent="""
    based on all data you have i want you to calculate the performance of sales per month wich means calculate the total of sales and TotalLeads made per month
    and calculate the lead conversion rate and the target achievement percentage and also calculate the sales achieved percentage        
    """,
    environment=dagster_env,
)

# Build the transformation with specified datasets and providers
tr.build(
    input_datasets=[
        sales_clients,
        sales_employee_information,
        sales_leads,
        sales_performance,
        sales_targets,
        sales_training,
        sales_transactions,
    ],
    output_dataset=out_dev_dataset,
    provider=provider_config,
    verbose=True,
)

# Deploy the transformation
tr.save("./tests/artifacts/dagster_sales_department.py")
