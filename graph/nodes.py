"""Node functions for the stock report graph.

Each node is just a function: (state) -> partial state update. Nodes that
need MCP tools receive them already loaded (see build.py), so this module
stays free of any MCP/transport plumbing.
"""

import json

from langchain_google_genai import ChatGoogleGenerativeAI

from graph.state import ReportState


def _parse_tool_result(result):
    """MCP tools return a list of content blocks (e.g. [{'type': 'text',
    'text': '<json>'}]) rather than a plain Python object. Unwrap that
    down to the actual JSON payload."""
    if isinstance(result, list) and result and isinstance(result[0], dict) and "text" in result[0]:
        return json.loads(result[0]["text"])
    return result


def get_input_node(state: ReportState) -> dict:
    """Normalize/validate the raw ticker input. No LLM needed here —
    this 'agent' is just a plain function, which is a perfectly valid
    LangGraph node."""
    ticker = state.get("ticker", "").strip().upper()
    if not ticker or not ticker.isalnum():
        return {"error": f"'{ticker}' doesn't look like a valid ticker symbol."}
    return {"ticker": ticker}


def make_fetch_price_node(tools_by_name: dict):
    async def fetch_price_node(state: ReportState) -> dict:
        if state.get("error"):
            return {}
        tool = tools_by_name["get_stock_price"]
        raw_result = await tool.ainvoke({"ticker": state["ticker"]})
        result = _parse_tool_result(raw_result)
        if isinstance(result, dict) and result.get("error"):
            return {"error": result["error"]}
        return {"price_data": result}

    return fetch_price_node


def make_fetch_news_node(tools_by_name: dict):
    async def fetch_news_node(state: ReportState) -> dict:
        if state.get("error"):
            return {}
        tool = tools_by_name["get_stock_news"]
        raw_result = await tool.ainvoke({"ticker": state["ticker"]})
        return {"news_data": _parse_tool_result(raw_result)}

    return fetch_news_node


REPORT_PROMPT = """You are a financial analyst assistant. Write a short, \
clear report for the stock ticker {ticker} using the data below.

Price data:
{price_data}

Recent news:
{news_data}

Write 3-5 concise paragraphs: current price/performance snapshot, \
what's driving it based on the news, and a neutral summary. Do not give \
investment advice."""


async def generate_report_node(state: ReportState) -> dict:
    if state.get("error"):
        return {"report": f"Could not generate report: {state['error']}"}

    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.3)
    prompt = REPORT_PROMPT.format(
        ticker=state["ticker"],
        price_data=state.get("price_data"),
        news_data=state.get("news_data"),
    )
    response = await llm.ainvoke(prompt)

    content = response.content
    if isinstance(content, list):
        content = "".join(
            block.get("text", "") for block in content if isinstance(block, dict)
        )
    return {"report": content}
