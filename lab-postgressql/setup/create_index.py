"""
setup/create_index.py — Creates the Azure AI Search index and uploads the
return-policy documents (chunked + embedded) for RAG retrieval.

Run once (before the lab):
    python setup/create_index.py

Requires the following environment variables (or a .env file in the project root):
    AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY, AZURE_SEARCH_INDEX_NAME
    AZURE_OPENAI_ENDPOINT_LAB, AZURE_OPENAI_API_KEY_LAB, AZURE_OPENAI_EMBEDDING_DEPLOYMENT_LAB
"""

from __future__ import annotations

import asyncio
import os
import sys
import textwrap
import uuid
from pathlib import Path

# Allow running from any working directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
)
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

load_dotenv(override=False)

# ---------------------------------------------------------------------------
# Index definition
# ---------------------------------------------------------------------------

INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME", "return-policies")

FIELDS = [
    SimpleField(name="id",       type=SearchFieldDataType.String, key=True),
    SearchableField(name="title",    type=SearchFieldDataType.String),
    SearchableField(name="content",  type=SearchFieldDataType.String),
    SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="default-profile",
    ),
]

VECTOR_SEARCH = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="default-hnsw")],
    profiles=[VectorSearchProfile(name="default-profile", algorithm_configuration_name="default-hnsw")],
)

# ---------------------------------------------------------------------------
# Document chunks
# Each dict has: id, title, content, category
# The content is a meaningful, self-contained chunk from the policy document.
# ---------------------------------------------------------------------------

POLICY_DIR = Path(__file__).parent.parent / "policies"

# We define fixed chunks so the lab is deterministic regardless of file edits
DOCUMENTS = [
    {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "electronics-window")),
        "title": "Electronics Return Window",
        "category": "Electronics",
        "content": textwrap.dedent("""
            Electronics Return Window

            Unopened / Sealed items: 30 days from delivery date.
            Opened items: 30 days from delivery date.
            Defective or Dead-on-Arrival (DOA) items: 90 days from delivery date.

            The return window starts on the delivery date shown in your order
            confirmation email, not the original purchase date.
        """).strip(),
    },
    {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "electronics-eligibility")),
        "title": "Electronics Return Eligibility Requirements",
        "category": "Electronics",
        "content": textwrap.dedent("""
            Electronics Return Eligibility Requirements

            To qualify for a return, the item must:
            1. Be returned within the applicable return window.
            2. Be accompanied by the original proof of purchase (order number is sufficient).
            3. Include all original contents: box, manuals, cables, chargers, and accessories.
            4. Show no signs of physical damage caused by the customer (drops, liquid damage, etc.).

            Non-returnable electronics include:
            - Software licenses and digital downloads (once the key has been revealed)
            - Items marked "Final Sale" or "Non-Returnable" on the product page
            - Prepaid gift cards and store credit
        """).strip(),
    },
    {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "electronics-refund")),
        "title": "Electronics Refund Amounts",
        "category": "Electronics",
        "content": textwrap.dedent("""
            Electronics Refund Amounts

            - Unopened, sealed in original packaging:
              Full refund of item price plus original shipping cost.

            - Opened, all contents present, no damage:
              Full refund of item price; original shipping is non-refundable.

            - Opened, missing minor accessories:
              Item price minus a 15% restocking fee.

            - Defective / Dead-on-arrival (with photo evidence):
              Full refund of item price plus original shipping cost.

            - Physical damage caused by the customer:
              Not eligible for a refund. Repair or trade-in options may be available.
        """).strip(),
    },
    {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "electronics-process")),
        "title": "How to Return an Electronics Item",
        "category": "Electronics",
        "content": textwrap.dedent("""
            How to Initiate an Electronics Return

            1. Log in to your ShopEasy account at shopease.com/myorders.
            2. Select the order and click "Return or Replace".
            3. Choose a return reason; upload photos if the item is defective.
            4. Print the prepaid return shipping label (available for orders over $25).
            5. Drop the package off at any ShopEasy partner carrier location
               within 5 days of initiating the return.
            6. Once the warehouse receives and inspects the item, the refund is
               processed within 5–7 business days to the original payment method.

            Keep the return tracking number until the refund appears in your account.
        """).strip(),
    },
    {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "electronics-warranty")),
        "title": "Electronics Warranty vs. Return Policy",
        "category": "Electronics",
        "content": textwrap.dedent("""
            Electronics Warranty vs. Return Policy

            The 30-day return window is separate from any manufacturer warranty:

            - Return window (0–30 days from delivery): Handled by ShopEasy.
              Eligible for full refund or store credit as described above.

            - Manufacturer warranty (31 days and beyond): Contact the manufacturer
              directly. ShopEasy can provide contact details on request.

            - ShopEasy Protection Plan (if purchased separately): Covers accidental
              damage and extends coverage beyond the manufacturer warranty.
              See your plan agreement for full details.
        """).strip(),
    },
    {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "clothing-return")),
        "title": "Clothing & Apparel Return Policy",
        "category": "Clothing",
        "content": textwrap.dedent("""
            Clothing & Apparel Return Policy

            Return window: 60 days from delivery date.
            Items must be unworn, unwashed, and in original packaging with tags attached.
            Final-sale and swimwear items are non-returnable.
            Refund: Full item price; original shipping non-refundable.
            Start a return at shopease.com/myorders.
        """).strip(),
    },
    {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "books-return")),
        "title": "Books Return Policy",
        "category": "Books",
        "content": textwrap.dedent("""
            Books Return Policy

            Return window: 30 days from delivery date.
            Physical books must be in original condition (no writing, highlighting, or damage).
            Digital/e-books are non-returnable once downloaded.
            Refund: Full item price; original shipping non-refundable.
        """).strip(),
    },
    {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "home-kitchen-return")),
        "title": "Home & Kitchen Return Policy",
        "category": "Home & Kitchen",
        "content": textwrap.dedent("""
            Home & Kitchen Return Policy

            Return window: 30 days from delivery date.
            Items must be unused and in original packaging.
            Large appliances may require a scheduled pickup — contact support first.
            Perishable and hazardous items are non-returnable.
            Refund: Full item price; original shipping non-refundable.
        """).strip(),
    },
]


# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------

async def embed_batch(texts: list[str]) -> list[list[float]]:
    client = AsyncAzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_LAB"],
        api_key=os.environ["AZURE_OPENAI_API_KEY_LAB"],
        api_version="2024-02-01",
    )
    resp = await client.embeddings.create(
        model=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_LAB", "text-embedding-ada-002"),
        input=texts,
    )
    await client.close()
    return [item.embedding for item in resp.data]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]

    # ── 1. Create / recreate the index ────────────────────────────────────
    print(f"Creating index '{INDEX_NAME}' …")
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    async with index_client:
        index = SearchIndex(
            name=INDEX_NAME,
            fields=FIELDS,
            vector_search=VECTOR_SEARCH,
        )
        await index_client.create_or_update_index(index)
    print("  Index ready.")

    # ── 2. Generate embeddings ─────────────────────────────────────────────
    print(f"Generating embeddings for {len(DOCUMENTS)} chunks …")
    texts = [f"{d['title']}\n\n{d['content']}" for d in DOCUMENTS]
    vectors = await embed_batch(texts)
    for doc, vec in zip(DOCUMENTS, vectors):
        doc["content_vector"] = vec
    print("  Embeddings done.")

    # ── 3. Upload documents ────────────────────────────────────────────────
    print("Uploading documents to the index …")
    search_client = SearchClient(
        endpoint=endpoint,
        index_name=INDEX_NAME,
        credential=credential,
    )
    async with search_client:
        result = await search_client.upload_documents(documents=DOCUMENTS)

    succeeded = sum(1 for r in result if r.succeeded)
    print(f"  Uploaded {succeeded}/{len(DOCUMENTS)} documents successfully.")

    # ── 4. Summary ─────────────────────────────────────────────────────────
    print("\nIndex contents:")
    for doc in DOCUMENTS:
        print(f"  [{doc['category']:<16}]  {doc['title']}")

    print(f"\nDone!  Run the chat agent with:  python chat.py")


if __name__ == "__main__":
    asyncio.run(main())
