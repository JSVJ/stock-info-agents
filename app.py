"""Gradio UI entrypoint for Hugging Face Spaces.

Wraps the same compiled LangGraph graph used by main.py behind a small
web form: ticker in, report out. Spaces runs this file directly.

Runs on ZeroGPU hardware: @spaces.GPU only supports sync functions and
routes each call to an isolated worker, so the graph is rebuilt fresh
per request instead of cached across calls.
"""

import asyncio

import gradio as gr
import spaces
from dotenv import load_dotenv

from graph.build import build_graph

load_dotenv()


async def _run_report_async(ticker: str) -> str:
    app = await build_graph()
    result = await app.ainvoke({"ticker": ticker})
    return result.get("report", "(no report generated)")


@spaces.GPU
def run_report(ticker: str) -> str:
    if not ticker or not ticker.strip():
        return "Please enter a ticker symbol."
    return asyncio.run(_run_report_async(ticker))


demo = gr.Interface(
    fn=run_report,
    inputs=gr.Textbox(label="Stock ticker", placeholder="e.g. AAPL"),
    outputs=gr.Textbox(label="Report", lines=15),
    title="Stock Report Agent",
    description="LangGraph + MCP powered stock price & news report generator.",
)

if __name__ == "__main__":
    demo.launch(ssr_mode=False)
