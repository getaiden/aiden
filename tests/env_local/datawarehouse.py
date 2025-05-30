from aiden import Transformation
from aiden.common.dataset import Dataset
from aiden.common.environment import Environment
from aiden.common.provider import ProviderConfig

# Configure AI providers for each agent
provider_config = ProviderConfig(
    manager_provider="anthropic/claude-3-7-sonnet-latest",
    data_expert_provider="anthropic/claude-3-7-sonnet-latest",
    data_engineer_provider="anthropic/claude-3-7-sonnet-latest",
    tool_provider="anthropic/claude-3-7-sonnet-latest",
)

# Define input and output datasets
sales_clients = Dataset(
    path="./tests/input_data/sales_department/sales_clients.csv",
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
    path="./tests/input_data/sales_department/sales_employee_information.csv",
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
    path="./tests/input_data/sales_department/sales_leads.csv",
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
    path="./tests/input_data/sales_department/sales_performance.csv",
    format="csv",
    schema={"EmployeeID": str, "ReviewDate": str, "KPIs": str, "Score": float, "Comments": str},
)
sales_targets = Dataset(
    path="./tests/input_data/sales_department/sales_targets.csv",
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
    path="./tests/input_data/sales_department/sales_training.csv",
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
    path="./tests/input_data/sales_department/sales_transactions.csv",
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
fact_sales_performance = Dataset(
    path="./tests/output_data/fact_sales_performance.csv",
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

fact_lead_status = Dataset(
    path="./tests/output_data/fact_lead_status.csv",
    format="csv",
    schema={
        "EmployeeID": str,
        "Year": int,
        "Month": int,
        "TotalLeads": int,
        "LeadsWon": int,
        "LeadsLost": int,
        "ConversionRate": float,
    },
)

fact_sales_commissions = Dataset(
    path="./tests/output_data/fact_sales_commissions.csv",
    format="csv",
    schema={
        "EmployeeID": str,
        "Year": int,
        "Month": int,
        "TotalSales": float,
        "CommissionRate": float,
        "CommissionEarned": float,
    },
)

dim_employee = Dataset(
    path="./tests/output_data/dim_employee.csv",
    format="csv",
    schema={
        "EmployeeID": str,
        "FullName": str,
        "JobTitle": str,
        "Region": str,
        "ManagerID": str,
        "HireDate": str,
        "Status": str,
    },
)

input_datasets = [
    sales_clients,
    sales_employee_information,
    sales_leads,
    sales_performance,
    sales_targets,
    sales_training,
    sales_transactions,
]

dev_env = Environment(
    type="dagster",
    workdir="./tests/workdir/",
)

# Define transformation with natural language intent
fact_sales_performance_transformation = Transformation(
    intent="""
    ## Based on all data you have i want you to calculate the performance of sales per month per employee for all the year even if there is no sales, leads, conversion rate, target achievement percentage, sales achieved percentage for a month put it with 0. wich means:
    - calculate the total of sales per month per employee
    - calculate the total of leads made per month per employee
    - calculate the lead conversion rate per month per employee
    - calculate the target achievement percentage per month per employee
    - calculate the sales achieved percentage per month per employee

    ## data pre-processing:
    - pre-process these dataset sales_leads, sales_transactions, sales_training, and sales_performance. Each dataset contains a date column (ContactDate, TransactionDate, Date, and ReviewDate, respectively). These columns are in standard date format (e.g., 2023-05-12), and your objective is:
    - For each table, extract the month component from the date field
    - Convert this month into a string format such as "May", "June", etc., rather than using numeric month values (e.g., "05", "06").

    ## Additional information on transformation output:
    - i want you to include all month of the year even if there is no sales, leads, conversion rate, target achievement percentage, sales achieved percentage for a month put it with 0.
    - i want you to put a string value in month column like may, june, july, etc and not 1, 2, 3, etc.
    """,
    environment=dev_env,
)

fact_lead_status_transformation = Transformation(
    intent="""
    based on all data you have calculate the total leads, the number of leads won, the number of leads lost and the conversion rate for each employee per month even for the months where there is no leads.
    """,
    environment=dev_env,
)

fact_sales_commissions_transformation = Transformation(
    intent="""
    based on all data you have calculate the commission earned by each employee per month, even for the months where there is no sales.
    """,
    environment=dev_env,
)

dim_employee_transformation = Transformation(
    intent="""
    based on all data you have create a dimension table for employees
    """,
    environment=dev_env,
)

fact_sales_performance_transformation.build(
    input_datasets=input_datasets,
    output_dataset=fact_sales_performance,
    provider=provider_config,
    verbose=True,
)

fact_lead_status_transformation.build(
    input_datasets=input_datasets,
    output_dataset=fact_lead_status,
    provider=provider_config,
    verbose=True,
)

fact_sales_commissions_transformation.build(
    input_datasets=input_datasets,
    output_dataset=fact_sales_commissions,
    provider=provider_config,
    verbose=True,
)

dim_employee_transformation.build(
    input_datasets=input_datasets,
    output_dataset=dim_employee,
    provider=provider_config,
    verbose=True,
)

fact_sales_performance_transformation.save("./tests/artifacts/fact_sales_performance_transformation.py")
fact_lead_status_transformation.save("./tests/artifacts/fact_lead_status_transformation.py")
fact_sales_commissions_transformation.save("./tests/artifacts/fact_sales_commissions_transformation.py")
dim_employee_transformation.save("./tests/artifacts/dim_employee_transformation.py")
