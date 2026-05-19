# Pre-Event Setup Instructions

**IMPORTANT:** These administrative steps must be completed before beginning the labs for the event. Please ensure all setup tasks are finished prior to the workshop start time.

## Prerequisites

- An Azure subscription
    - If you don't have an Azure subscription, create a [free account](https://azure.microsoft.com/pricing/purchase-options/azure-account?cid=msft_learn_3759bbd6-1214-e904-3317-a10e43c1a7e8)
- Visual Studio Code
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
az group create --name rg-postgreslab --location westus
```

### Provision Azure PostgreSQL Flexible Server

> 💡 **Note:** Be sure to replace the `<insert server>` and `<insert password>` placeholders.

```bash
az postgres flexible-server create --resource-group rg-postgreslab --name <insert server> --location westus --admin-user pgadmin --admin-password "<insert password>" --sku-name Standard_B1ms --tier Burstable --version 16 --public-access 0.0.0.0
```

Then create the database:

> 💡 **Note:** Be sure to replace the `<insert server>` placeholder.

```bash
az postgres flexible-server db create --resource-group rg-postgreslab --server-name <insert server> --database-name postgres
```

To mitigate firewall connection errors, add your IP.

> 💡 **Note:** Be sure to replace the `<insert server>` and `<your-ip>` placeholders. You can get our IP address by running the command: `curl ifconfig.me`.

```bash
az postgres flexible-server firewall-rule create --resource-group rg-postgreslab --name <insert server> --rule-name AllowMyIP --start-ip-address <your-ip> --end-ip-address <your-ip>
```

### Create an Azure OpenAI resource

1. Navigate to [portal.azure.com](https://portal.azure.com)
1. Select **Create a resource**.
1. On the **Create a resource** screen, search for **Azure OpenAI**.
1. On the **Azure OpenAI** screen, select your **Subscription** from the **Subscription** drop-down and click **Create**.
1. Complete the fields on the **Basics** tab. Ensure that you select the `rg-postgreslab` resource group and the `West US` region. Once done, click **Next**.
1. On the **Network** tab, select **All networks, including the internet, can access this resource.** and click **Next**.
1. Click **Next** on the **Tags** tab.
1. On the **Review + submit** tab, confirm the information you've entered is correct and click **Create**.

### Deploy the text-embedding-3-small model

1. In the Azure portal, navigate to your **Azure OpenAI Service** resource. 
1. On the resource **Overview** page, click either **Go to Foundry portal** (at the top of the page) or **Explore Foundry portal** (located at the bottom of the page).
1. In the Foundry portal, navigate to the **Model catalog**.
1. In the **Model catalog** search for `text-embedding-3-small`.
1. On the **text-embedding-3-small** page, click **Use this model** to deploy the model.
1. In the **Deploy text-embedding-3-small** window, click **Deploy**.


## Get your environment variables

| Variable | Where to find it |
|---|---|
| `AZURE_OPENAI_ENDPOINT_LAB` | Azure Portal > Azure OpenAI Resource > Resource Management > Keys and Endpoint |
| `AZURE_OPENAI_API_KEY_LAB` | Azure Portal > Azure OpenAI Resource > Resource Management > Keys and Endpoint |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_LAB` | Microsoft Foundry Portal > Project > Deployments |
| `POSTGRES_HOST` | Azure Portal > PostgreSQL Resource > Overview > Server name |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `postgres` |
| `POSTGRES_USER` | pgadmin |
| `POSTGRES_PASSWORD` | The admin password you chose |

## Data Setup

### Seed the PostgreSQL Database

```bash
python lab-postgressql/seed_database.py
```

---

##  Test the AI agent functionality

### Start the Agent

In the terminal, run the command: `python lab-postgressql/search_notes.py`

The application will:

- Send your search query to Microsoft Foundry
- Generate an embedding vector
- Compare that vector against stored note vectors
- Return the most similar notes

### Chat with the agent

In the terminal, enter: `vacation ideas`

Notice that results appear even if those exact words don't exist in the notes. The system found related concepts instead.

## Try additional searches

Try additional search queries in the termimal.

```txt
stress
focus better
health goals
```

Once you are done, enter `Quit` into the terminal to exit the app.

## Reset the lab

To only reset *this* lab, run the following command in the terminal: `./lab-postgressql/reset.sh`