"""
agent.py — Builds the ShopEasy customer-support agent.

The agent is backed by a Foundry-hosted GPT-4o model and has two tools:
  • lookup_order        — SQL query against Azure PostgreSQL
  • fetch_return_policy — vector/RAG search against Azure AI Search

Call build_agent() to get an Agent instance ready to be used in a chat loop.
"""

from __future__ import annotations

import os

from azure.identity import DefaultAzureCredential
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient

from tools import lookup_order, fetch_return_policy

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

INSTRUCTIONS = """
You are a friendly and knowledgeable customer support agent for ShopEasy,
an online retailer that sells electronics, clothing, books, and home goods.

## Your job when a customer asks about returning an order

1. Call **lookup_order** with the order ID provided by the customer to get:
   - The order date and delivery date
   - The product category
   - The order status (e.g. Delivered, Shipped)

2. Call **fetch_return_policy** with the product category from step 1 to
   retrieve the applicable return policy text.

3. Calculate eligibility and write a clear, empathetic reply:
  - Use `current_date` from **lookup_order** as today's date in Los Angeles
  - Use `days_since_delivery` from **lookup_order** for all return-window logic
  - Check if days_since_delivery <= return window (usually 30 days)
   - Include: order summary (product, delivery date, status)
  - State clearly: "Delivered X days ago" and whether that's within the window
   - The key policy rules that apply (return window, condition requirements,
     refund amount, how to initiate the return)
   - A direct recommendation: eligible or not, and the next step

## General guidelines
- If the customer has not provided an order ID, politely ask for it.
- Keep responses concise — no more than 3–4 short paragraphs.
- Always be empathetic; the customer may be frustrated.
- Do not invent policy details; use only what fetch_return_policy returns.
- CRITICAL for date calculations:
  * Do not use your own system context for today's date
  * Use `current_date` returned by **lookup_order**
  * Use `days_since_delivery` returned by **lookup_order**
  * If days_since_delivery <= 30, the item IS eligible for return
  * If days_since_delivery > 30, the item is NOT eligible for return
  * Always state the specific number of days since delivery in your response
"""

# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_agent() -> Agent:
    """
    Instantiate and return the customer-support Agent.

    The returned object is an async context manager:

        async with build_agent() as agent:
            stream = agent.run("Can I return ORD-001?", stream=True)
            ...
    """
    credential = DefaultAzureCredential()

    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4o"),
        credential=credential,
    )

    return Agent(
        client=client,
        name="ShopEasySupport",
        instructions=INSTRUCTIONS,
        tools=[lookup_order, fetch_return_policy],
    )
