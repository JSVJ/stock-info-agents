"""Gradio UI entrypoint for Hugging Face Spaces.

Wraps the same compiled LangGraph graph used by main.py behind a small
web form: ticker in, report out. Spaces runs this file directly.
"""

import asyncio

import gradio as gr
from dotenv import load_dotenv

from graph.build import build_graph

load_dotenv()

_app = None
_app_lock = asyncio.Lock()


async def get_app():
    global _app
    async with _app_lock:
        if _app is None:
            _app = await build_graph()
    return _app


async def run_report(ticker: str) -> str:
    if not ticker or not ticker.strip():
        return "Please enter a ticker symbol."
    app = await get_app()
    result = await app.ainvoke({"ticker": ticker})
    return result.get("report", "(no report generated)")


demo = gr.Interface(
    fn=run_report,
    inputs=gr.Textbox(label="Stock ticker", placeholder="e.g. AAPL"),
    outputs=gr.Textbox(label="Report", lines=15),
    title="Stock Report Agent",
    description="LangGraph + MCP powered stock price & news report generator.",
)

if __name__ == "__main__":
    demo.launch(ssr_mode=False)
