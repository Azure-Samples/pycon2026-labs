# Pre-Event Setup Instructions

**IMPORTANT:** These administrative steps must be completed before beginning the labs for the event. Please ensure all setup tasks are finished prior to the workshop start time.

## Prerequisites

- An Azure subscription
    - If you don't have an Azure subscription, create a [free account](https://azure.microsoft.com/pricing/purchase-options/azure-account?cid=msft_learn_3759bbd6-1214-e904-3317-a10e43c1a7e8)
- Visual Studio Code
- Azure CLI (already installed with the Codespace)
- Python 3.11.4+

## Create resources & deploy models

> 💡 Ensure that all resources are created in the Azure tenant that will be used for the labs. Verify you are signed into the correct tenant before proceeding with resource creation.

You will create resources via the Azure CLI.

### Create an Azure Resource Group

```bash
# For BAMI tenants
az login --tenant <your BAMI tenant>.onmicrosoft.com --use-device-code

# For PyCon
az login --tenant pycondemos.onmicrosoft.com --use-device-code

# For non-BAMI tenants
az login

# Run this command for BAMI/PyCon/non-BAMI tenants
az group create --name rg-shopeasy-lab --location westus
```

### Provision Azure PostgreSQL Flexible Server

> 💡 **Note:** Be sure to replace the `<insert server>` and `<insert password>` placeholders.

```bash
az postgres flexible-server create --resource-group rg-shopeasy-lab --name shopeasy-pg --location westus --admin-user pgadmin --admin-password "<insert password>" --sku-name Standard_B1ms --tier Burstable --version 16 --public-access 0.0.0.0
```

Then create the database:

> 💡 **Note:** Be sure to replace the `<insert server>` placeholder.

```bash
az postgres flexible-server db create --resource-group rg-shopeasy-lab --server-name <insert server> --database-name shopease
```

To mitigate firewall connection errors, add your IP.

> 💡 **Note:** Be sure to replace the `<insert server>` and `<your-ip>` placeholders. You can get our IP address by running the command: `curl ifconfig.me`.

```bash
az postgres flexible-server firewall-rule create --resource-group rg-shopeasy-lab --name <insert server> --rule-name AllowMyIP --start-ip-address <your-ip> --end-ip-address <your-ip>
```

### Provision Azure AI Search

> 💡 **Note:** Be sure to replace the `<insert searcj service name>` placeholder.

```bash
az search service create --resource-group rg-shopeasy-lab --name <insert search service name> --location westus --sku basic
```

Retrieve the admin API key (you will need it for your environment variables):

> 💡 **Note:** Be sure to replace the `<insert search service name>` placeholder.

```bash
az search admin-key show --resource-group rg-shopeasy-lab --service-name <insert search service name> --query primaryKey -o tsv
```

### Create an Azure OpenAI resource

1. Navigate to [portal.azure.com](https://portal.azure.com)
1. Select **Create a resource**.
1. On the **Create a resource** screen, search for **Azure OpenAI**.
1. On the **Azure OpenAI** screen, select your **Subscription** from the **Subscription** drop-down and click **Create**.
1. Complete the fields on the **Basics** tab. Ensure that you select the `rg-shopeasy-lab` resource group and the `West US` region. Once done, click **Next**.
1. On the **Network** tab, select **All networks, including the internet, can access this resource.** and click **Next**.
1. Click **Next** on the **Tags** tab.
1. On the **Review + submit** tab, confirm the information you've entered is correct and click **Create**.

### Deploy the text-embedding-ada-002 model

1. In the Azure portal, navigate to your **Azure OpenAI Service** resource. 
1. On the resource **Overview** page, click either **Go to Foundry portal** (at the top of the page) or **Explore Foundry portal** (located at the bottom of the page).
1. In the Foundry portal, navigate to the **Model catalog**.
1. In the **Model catalog** search for `text-embedding-ada-002`.
1. On the **text-embedding-ada-002** page, click **Use this model** to deploy the model.
1. In the **Deploy text-embedding-ada-002** window, click **Deploy**.

### Create an Azure AI Foundry Project

1. Navigate to [ai.azure.com](https://ai.azure.com).
1. At the top of the page, select the **New Foundry** toggle to enable the new Foundry portal experience.
1. In the **Select a project to continue** window, click the drop-down and select **Create a new project**.
1. In the **Create a project** window, name the project `shopeasy-lab`.
1. In the **Advanced options**, replace the **Microsoft Foundry resource** name with a domain name that's available.
1. In the **Advanced options**, for **Region**, select **West US**.
1. Click **Create**.

### Deloy the gpt-4o model

1. In the **New Foundry** portal, navigate to **Discover**.
1. Select **Models**.
1. Search for `gpt-4o`.
1. On the **gpt-4o** page, click **Deploy**.
1. Select **Default settings**.

## Grant yourself the Contributor role on the Foundry project

The agent uses `DefaultAzureCredential` (your `az login` identity). Make sure your Azure AD account has the **Azure AI Developer** or **Contributor** role on the Foundry project resource:

### Get the Azure AD Object ID

```bash
az ad signed-in-user show --query id -o tsv
```

### Get the resource ID

> 💡 **Note:** Be sure to replace the `<your Microsoft Foundry resource name>` placeholders.

```bash
az resource show --resource-group rg-shopeasy-lab --resource-type "Microsoft.CognitiveServices/accounts" --name <your Microsoft Foundry resource name> --query id -o tsv
```

### Assign the role

> 💡 **Note:** Be sure to replace the `<your-azure-ad-object-id` and `<resource-id>` placeholders.

```bash
az role assignment create --assignee "<your-azure-ad-object-id>" --role "Azure AI Developer" --scope "<resource-id>"
```

## Get your environment variables

| Variable | Where to find it |
|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | New Microsoft Foundry Portal > Project > Homepage |
| `FOUNDRY_MODEL_DEPLOYMENT_NAME` | Microsoft Foundry Portal > Build > Models |
| `AZURE_OPENAI_ENDPOINT_LAB` | Azure Portal > Azure OpenAI Resource > Resource Management > Keys and Endpoint |
| `AZURE_OPENAI_API_KEY_LAB` | Azure Portal > Azure OpenAI Resource > Resource Management > Keys and Endpoint |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_LAB` | Microsoft Foundry Portal > Project > Deployments |
| `AZURE_SEARCH_ENDPOINT` | Azure Portal > Search service resource > Overview > Url |
| `AZURE_SEARCH_API_KEY` | Azure Portal > Search service resource > Settings > Keys |
| `AZURE_SEARCH_INDEX_NAME` | Leave as `return-policies` |
| `POSTGRES_HOST` | Azure Portal > PostgreSQL Resource > Overview > Server name |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `shopease` |
| `POSTGRES_USER` | pgadmin |
| `POSTGRES_PASSWORD` | The admin password you chose |

## Authenticate with Azure

This sets up `DefaultAzureCredential` used by the agent to call the Foundry model.

```bash
# For BAMI tenants
az login --tenant <your BAMI tenant>.onmicrosoft.com --use-device-code

# For PyCon
az login --tenant pycondemos.onmicrosoft.com --use-device-code

# For non-BAMI tenants
az login
```

## Data Setup

### Seed the PostgreSQL Database

```bash
python lab-postgressql/setup/seed_db.py
```

Expected output:
```
Connecting to PostgreSQL …
Creating schema …
Seeding customers …
Seeding orders …

Done!  10 order(s) in the database.

Sample rows:
  ORD-001  2025-03-23  Electronics      Sony WH-1000XM5 Wireless Noise-Cancelling H...
  ORD-002  2025-04-27  Books            Python Crash Course, 3rd Edition
  ...
```

### Create the AI Search Index & Upload Policy Documents

```bash
python lab-postgressql/setup/create_index.py
```

Expected output:
```
Creating index 'return-policies' …
  Index ready.
Generating embeddings for 8 chunks …
  Embeddings done.
Uploading documents to the index …
  Uploaded 8/8 documents successfully.

Index contents:
  [Electronics     ]  Electronics Return Window
  [Electronics     ]  Electronics Return Eligibility Requirements
  [Electronics     ]  Electronics Refund Amounts
  [Electronics     ]  How to Return an Electronics Item
  [Electronics     ]  Electronics Warranty vs. Return Policy
  [Clothing        ]  Clothing & Apparel Return Policy
  [Books           ]  Books Return Policy
  [Home & Kitchen  ]  Home & Kitchen Return Policy
```

##  Test the AI agent functionality

### Start the Agent

```bash
python lab-postgressql/chat.py
```

You will see the startup banner with a list of demo order IDs and sample questions.

### Chat with the agent

Ask the agent about an electronics order:

```
You: Can I return order ORD-007?
```

Watch the terminal output carefully. You should see **two tool calls** happen before the agent writes its answer:
- `[TOOL] lookup_order → SQL query`
- `[TOOL] fetch_return_policy → RAG / vector search`

The agent's final response synthesizes both pieces of information.

## Starting the lab

You will need to sign-in to Azure via the Azure CLI.

**For BAMI tenants**

```bash
az login --tenant <your BAMI tenant>.onmicrosoft.com --use-device-code
```

**For Pycon**

```bash
az login --tenant pycondemos.onmicrosoft.com --use-device-code
```

**For non-BAMI tenants**

```bash
az login
```

## Reset the lab

To only reset *this* lab, run the following command in the terminal: `./lab-postgressql/reset.sh`