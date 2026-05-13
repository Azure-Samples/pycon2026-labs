# Pre-Event Setup Instructions

**IMPORTANT:** These administrative steps must be completed before beginning the labs for the event. Please ensure all setup tasks are finished prior to the workshop start time.

## Prerequisites

- An Azure subscription
    - If you don't have an Azure subscription, create a [free account](https://azure.microsoft.com/pricing/purchase-options/azure-account?cid=msft_learn_3759bbd6-1214-e904-3317-a10e43c1a7e8)
- Visual Studio Code
- Python 3.11.4+

## Create resources & deploy models

> 💡 Ensure that all resources are created in the Azure tenant that will be used for the labs. Verify you are signed into the correct tenant before proceeding with resource creation.

### Azure DocumentDB Cluster

Follow the instructions in the [Quickstart: Create an Azure DocumentDB cluster by using the Azure portal](https://learn.microsoft.com/azure/documentdb/quickstart-portal). You will only need to complete the steps within the [Create a cluster](https://learn.microsoft.com/azure/documentdb/quickstart-portal#create-a-cluster) and [Get cluster credentials](https://learn.microsoft.com/azure/documentdb/quickstart-portal#get-cluster-credentials) sections.

### Azure OpenAI Service

1. Navigate to [portal.azure.com](https://portal.azure.com)
1. Select **Create a resource**.
1. On the **Create a resource** screen, search for **Azure OpenAI**.
1. On the **Azure OpenAI** screen, select your **Subscription** from the **Subscription** drop-down and click **Create**.
1. Complete the fields on the **Basics** tab and click **Next**.
1. On the **Network** tab, select **All networks, including the internet, can access this resource.** and click **Next**.
1. Click **Next** on the **Tags** tab.
1. On the **Review + submit** tab, confirm the information you've entered is correct and click **Create**.

## Deploy the text-embedding-3-small model

1. In the Azure portal, navigate to your **Azure OpenAI Service** resource. 
1. On the resource **Overview** page, click either **Go to Foundry portal** (at the top of the page) or **Explore Foundry portal** (located at the bottom of the page).
1. In the Foundry portal, navigate to the **Model catalog**.
1. In the **Model catalog** search for `text-embedding-3-small`.
1. On the **text-embedding-3-small** page, click **Use this model** to deploy the model.
1. In the **Deploy text-embedding-3-small** window, click **Deploy**.

## Deploy the gpt-5.4-mini model

1. In the Foundry portal, navigate to the **Model catalog**.
1. In the **Model catalog** search for `gpt-5.4-mini`.
1. On the **gpt-5.4-mini** page, click **Use this model** to deploy the model.
1. In the **Deploy gpt-5.4-mini** window, click **Deploy**.

## Get your environment variables

You will need the following environment variables:

| Variable | Where to find it |
|---|---|
| AZURE_OPENAI_ENDPOINT | Azure Portal > Azure OpenAI Resource > Resource Management > Keys and Endpoint |
| AZURE_OPENAI_API_KEY | Azure Portal > Azure OpenAI Resource > Resource Management > Keys and Endpoint |
| AZURE_OPENAI_API_VERSION | 2025-04-01-preview |
| AZURE_OPENAI_EMBEDDING_DEPLOYMENT | Microsoft Foundry Portal > Project > Deployments |
| MONGO_CONNECTION_STRING | Azure Portal > Azure DocumentDB resource > Settings > Connection strings |
| AZURE_OPENAI_CHAT_DEPLOYMENT | Microsoft Foundry Portal > Build > Models |

## Load travel documents into Azure DocumentDB

The `/loader` directory contains a Python project for loading sample travel documents into Azure DocumentDB and creating the necessary vector embeddings.

1. In the terminal, navigate to the `/loader` directory.
1. The `main.py` file serves as the central entry point for loading data. Run the command `python main.py`.
1. Verify the output shows successful completion:
    ```txt
    --build itinerary--
    --load itinerary--
    --load destinations--
    --load vectors ships--
    ```

## Build the AI travel agent API

The AI travel agent is hosted through a Python FastAPI backend that integrates with the frontend interface and processes agent requests by grounding large language model (LLM) prompts against Azure DocumentDB data.

1. In the terminal, navigate to the /api directory.
1. Run the FastAPI application from the /api directory: `python app.py`
1. The server starts at `http://127.0.0.1:8000`. Open the interactive API docs in your browser and add `/docs` at the end of the URL (ex: https://bug-free-waffle-4wq6vxg7v627jp-8000.app.github.dev/docs).

## Test the AI agent functionality

Test that the AI agent functions as expected.

1. In the Swagger interface, test the session endpoint:
    - Navigate to **/session/** and select **Try it out**
    - Execute the request to get a session ID for tracking conversation history

1. Test the agent chat functionality:
    - Navigate to **/agent/agent_chat** and select **Try it out**
    - Use this example in
    ```JSON
    {
        "input": "Recommend an itinerary for the 'Adventures of the Ocean' ship.",
        "session_id": "your-session-id-from-step-1"
    }
    ```
1. The agent should respond with a cruise itinerary based on vector similarity search, demonstrating the integration between the LLM and Azure DocumentDB.

## Starting the lab

You will need to sign-in to Azure via the Azure Resources extension. The extension should already be installed in the Codespace.

1. In VS Code, in the left Activity Bar, click the **Azure** icon.
1. In the **Azure** extension, click **Sign in to Azure...**.
1. Once you've signed in, expand **PyCon** > **Azure DocumentDB** > **pyconus2026**.
1. When prompted, enter the **username** and **password** for the **DocumentDB cluster**.
1. After you've signed in, confirm that you're able to view the **travel** database for the cluster.

## Reset the lab

To only reset *this* lab, run the following command in the terminal: `./lab-documentdb/reset.sh`