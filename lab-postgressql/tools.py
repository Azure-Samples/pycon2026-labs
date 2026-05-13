"""
tools.py — The two core tools the agent can call:

  1. lookup_order      → runs a SQL query against Azure PostgreSQL
  2. fetch_return_policy → runs a vector (RAG) search against Azure AI Search

Both functions print what they are doing so you can watch the flow in the
terminal during the lab.
"""

from __future__ import annotations

import json
import os

import asyncpg
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AsyncAzureOpenAI

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_pool: asyncpg.Pool | None = None


async def init_pool() -> None:
    """Create the shared asyncpg connection pool (called once at startup)."""
    global _pool
    _pool = await asyncpg.create_pool(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        ssl="require",
        min_size=1,
        max_size=5,
    )


async def close_pool() -> None:
    """Close the connection pool on shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def _embed(text: str) -> list[float]:
    """Return an embedding vector for *text* using Azure OpenAI."""
    client = AsyncAzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_LAB"],
        api_key=os.environ["AZURE_OPENAI_API_KEY_LAB"],
        api_version="2024-02-01",
    )
    resp = await client.embeddings.create(
        model=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_LAB", "text-embedding-ada-002"),
        input=text,
    )
    await client.close()
    return resp.data[0].embedding


# ---------------------------------------------------------------------------
# Tool 1 — SQL Query
# ---------------------------------------------------------------------------

async def lookup_order(order_id: str) -> str:
    """
    Look up an order's dates and product category from the PostgreSQL orders
    database.  Always call this first when a customer mentions an order ID.

    Args:
        order_id: The customer's order identifier, for example 'ORD-001'.

    Returns:
        A JSON string with order_id, customer_name, product_name,
        product_category, order_date, delivery_date, status, and total_amount.
        Returns an error JSON if the order is not found.
    """
    oid = order_id.strip().upper()

    # ── visible trace for the lab ──────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  [TOOL] lookup_order  →  SQL query")
    print(f"{'─'*60}")
    print(f"  Query : SELECT order_date, delivery_date, product_category, ...")
    print(f"          FROM orders JOIN customers")
    print(f"          WHERE order_id = '{oid}'")
    # ───────────────────────────────────────────────────────────────────────

    if _pool is None:
        await init_pool()

    row = await _pool.fetchrow(  # type: ignore[union-attr]
        """
        SELECT o.order_id,
               o.order_date,
               o.delivery_date,
               o.product_name,
               o.product_category,
               o.status,
               o.total_amount,
               c.name AS customer_name
        FROM   orders    o
        JOIN   customers c ON o.customer_id = c.customer_id
        WHERE  o.order_id = $1
        """,
        oid,
    )

    if row is None:
        result: dict = {"error": f"No order found with ID '{oid}'."}
    else:
        result = {
            "order_id":         row["order_id"],
            "customer_name":    row["customer_name"],
            "product_name":     row["product_name"],
            "product_category": row["product_category"],
            "order_date":       str(row["order_date"]),
            "delivery_date":    str(row["delivery_date"]),
            "status":           row["status"],
            "total_amount":     float(row["total_amount"]),
        }

    print(f"  Result: {json.dumps(result, indent=4)}")
    print(f"{'─'*60}")
    return json.dumps(result)


# ---------------------------------------------------------------------------
# Tool 2 — RAG / Vector Search
# ---------------------------------------------------------------------------

async def fetch_return_policy(product_category: str) -> str:
    """
    Search the return-policy knowledge base using vector (RAG) retrieval to
    find policy text relevant to a given product category.  Call this after
    lookup_order to retrieve the applicable policy for the order's category.

    Args:
        product_category: The product category returned by lookup_order,
                          e.g. 'Electronics' or 'Clothing'.

    Returns:
        One or more policy document chunks most relevant to the category.
        Returns an explanatory string if nothing is found.
    """
    search_text = f"{product_category} return policy refund"

    # ── visible trace for the lab ──────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  [TOOL] fetch_return_policy  →  RAG / vector search")
    print(f"{'─'*60}")
    print(f"  Index : {os.environ.get('AZURE_SEARCH_INDEX_NAME', 'return-policies')}")
    print(f"  Query : '{search_text}'")
    print(f"  Mode  : hybrid (keyword + vector embedding)")
    # ───────────────────────────────────────────────────────────────────────

    embedding = await _embed(search_text)

    search_client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=os.environ.get("AZURE_SEARCH_INDEX_NAME", "return-policies"),
        credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
    )

    vector_query = VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=3,
        fields="content_vector",
    )

    chunks: list[str] = []
    async with search_client:
        results = await search_client.search(
            search_text=search_text,
            vector_queries=[vector_query],
            select=["title", "content", "category"],
            top=3,
        )
        async for doc in results:
            chunks.append(f"[{doc['title']}]\n{doc['content']}")

    if not chunks:
        policy_text = (
            f"No return policy document found for category '{product_category}'. "
            "Please advise the customer to contact support directly."
        )
    else:
        policy_text = "\n\n---\n\n".join(chunks)

    print(f"  Found : {len(chunks)} chunk(s) retrieved")
    print(f"{'─'*60}")
    return policy_text
