# AI Travel Agent with Azure DocumentDB

Ever wonder what's happening when an AI agent "remembers" things? Run this travel agent, dig into the code, and watch Azure DocumentDB do the heavy lifting — vector search, document storage, and conversation history all at once!

> This workshop is based on the [Travel AI Agent React FastAPI and Cosmos DB Vector Store](https://github.com/jonathanscholtes/Travel-AI-Agent-React-FastAPI-and-Cosmos-DB-Vector-Store) project by Jonathan Scholtes.

---

## Setup

Before you begin, complete the setup instructions in the [ADMIN.md](ADMIN.md) and either save the environment variables in an `.env` file or in the **Codespaces** > **Codespace user secrets** of your GitHub account.

---

## Inspect what Azure DocumentDB is doing (2 min)

Before running the agent, take a look at the three tools it uses to read from and write to Azure DocumentDB.

1. In the **Explorer** of the editor, navigate to **lab-documentdb** > **api** > **service** > **TravelAgentTools.py**.
1. View what each tool does:

  | Tool | What it does |
  |---|---|
  | `vacation_lookup` | Runs a **vector similarity search** against the `ships` collection to find destinations & cruises |
  | `itinerary_lookup` | Retrieves cruise package details and schedules for a specific ship |
  | `book_cruise` | Writes a booking document to DocumentDB and validates passenger info |

---

## Start the API (1 min)

Spin up the FastAPI server that hosts the travel agent.

1. In the terminal, run the command: `python lab-documentdb/api/app.py`
1. In the terminal, **CTRL + Click**  `http://127.0.0.1:8000` to open the interactive API docs in your browser and add `/docs` at the end of the URL.

> 💡 Copy + pasting `http://127.0.0.1:8000` will result in an error. Be sure to **CTRL + Click** via the link in the terminal as stated. Doing so routes to the proper URL from the Codespace.

---

## Get a Session ID (30 seconds)

The agent uses a session ID to tie your conversation turns together and persist history in DocumentDB.

1. Expand the **GET /session/** endpoint.
1. Click **Try it out** > **Execute**.
1. Copy the `session ID` from the response, you'll use it in the next step.

---

## Chat with the AI Travel Agent (2 min)

Ask the agent about travel destinations and cruise ships — each response is grounded in data retrieved directly from Azure DocumentDB.

1. Expand **POST /agent/agent_chat**
1. Click **Try it out**.
1. Update the request body, substituting your session ID:

    ```json
    {
      "input": "What is there to do in Barbados?",
      "session_id": "<your-session-id>"
    }
    ```
1. Click **Execute** and review the response. The agent returns a summary of activities to do in Barbados, sourced from documents in the `travel.destinations` collection in Azure DocumentDB. If you look in the terminal, you will see output for the `vacation_lookup` tool call.
1. Update the request body, substituting your session ID:

    ```json
    {
      "input": "Recommend an itinerary for the 'Adventures of the Ocean' ship.",
      "session_id": "<your-session-id>"
    }
    ```

1. Click **Execute** and review the response. The agent returns a proposed itinerary, sourced from itinerary documents in Azure DocumentDB after looking up the named ship in the `travel.ships` collection and retrieving matching records from the `travel.itinerary` collection.

---

## Book a Cruise (1.5 min)

Put the agent to work by booking a cruise — it'll ask for the details it needs and write the booking record to DocumentDB.

1. In the browser, update the request body, substituting your session ID:

    ```json
    {
      "input": "Book me a cruise for the Adventures of the Ocean.",
      "session_id": "<your-session-id>"
    }
    ```
1. When prompted by the agent, answer all follow up questions by updating the request body `input` and clicking **Execute**.
1. Once the agent has the information needed, it'll book the cruise and provide you with a reference number.

---

## Reflection

Take a moment to connect what you just did to the Azure DocumentDB capabilities that made it possible.

- **Vector search** — the agent matched your natural language query to relevant cruises using semantic similarity over embeddings
- **Document store (reads)** — the agent retrieved itinerary details for a specific ship from a stored document
- **Document store (writes)** — the agent wrote your booking record back to DocumentDB
- **Session history** — every turn of your conversation was persisted in the `travel.history` collection, so the agent remembered context across messages

Azure DocumentDB handled all four of these without any additional infrastructure!

---

## 🎟️ Congratulations!

Let our staff know that you've completed the lab so that you can collect your swag!