"""
chat.py — Terminal chat loop for the ShopEasy customer-support agent.

Usage:
    python chat.py

The agent streams its response token-by-token.  Tool calls (SQL query and
RAG search) are printed inline so you can see exactly what is happening.
"""

from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv

load_dotenv(override=False)  # local .env < environment variables already set

import tools as tool_module  # noqa: E402  (after dotenv)
from agent import build_agent  # noqa: E402

# ---------------------------------------------------------------------------
# Banner & sample prompts shown at startup
# ---------------------------------------------------------------------------

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║          ShopEasy Customer Support Agent                     ║
║          Powered by Azure AI Foundry + PostgreSQL            ║
╚══════════════════════════════════════════════════════════════╝

Type your question and press Enter.  Type 'exit' or press Ctrl+C to quit.

Sample questions to try
───────────────────────
  • Can I return order ORD-001?
  • I bought a TV (order ORD-003). Is it too late to return it?
  • What is the return policy for electronics?
  • I received a damaged laptop in order ORD-007. What are my options?

Order IDs in the demo database
───────────────────────────────
{order_lines}
"""


def _format_order_line(order: dict[str, str]) -> str:
    name = order["product_name"]
    if len(name) > 38:
        name = f"{name[:35]}..."

    return (
        f"  {order['order_id']:<8} {name:<38} "
        f"({order['product_category']}) — delivered {order['delivery_date']}"
    )


async def build_banner() -> str:
    orders = await tool_module.list_demo_orders()
    order_lines = "\n".join(_format_order_line(order) for order in orders)
    return BANNER.format(order_lines=order_lines)


# ---------------------------------------------------------------------------
# Main chat loop
# ---------------------------------------------------------------------------


async def chat_loop() -> None:
    await tool_module.init_pool()

    try:
        async with build_agent() as agent:
            thread_id: str | None = None
            print(await build_banner())

            while True:
                # ── read user input ────────────────────────────────────────
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n\nGoodbye!")
                    break

                if not user_input:
                    continue

                if user_input.lower() in ("exit", "quit", "q"):
                    print("Goodbye!")
                    break

                # ── stream the agent response ──────────────────────────────
                print("\nAgent: ", end="", flush=True)

                try:
                    run_kwargs: dict = {"stream": True}
                    if thread_id:
                        run_kwargs["thread_id"] = thread_id

                    stream = agent.run(user_input, **run_kwargs)

                    async for chunk in stream:
                        if chunk.text:
                            print(chunk.text, end="", flush=True)

                    response = await stream.get_final_response()

                    # Preserve thread_id for multi-turn memory (if supported)
                    thread_id = getattr(response, "thread_id", thread_id)

                except Exception as exc:
                    print(
                        f"\n\n[ERROR] The agent encountered a problem: {exc}",
                        file=sys.stderr,
                    )
                    print("Please try again.", file=sys.stderr)

                print("\n")  # blank line between turns

    finally:
        await tool_module.close_pool()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(chat_loop())
