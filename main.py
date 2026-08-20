"""CLI entrypoint: ask for a ticker, run the graph, print the report."""

import asyncio

from dotenv import load_dotenv

from graph.build import build_graph

load_dotenv()


async def main():
    ticker = input("Enter a stock ticker symbol: ").strip()

    app = await build_graph()

    print("\nRunning graph...\n")
    result = {}
    async for update in app.astream({"ticker": ticker}, stream_mode="updates"):
        for node_name, partial_state in update.items():
            print(f"  -> node '{node_name}' finished")
            if partial_state:
                result.update(partial_state)

    print("\n=== Report ===\n")
    print(result.get("report", "(no report generated)"))


if __name__ == "__main__":
    asyncio.run(main())
