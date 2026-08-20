"""Assembles the LangGraph StateGraph and wires in MCP tools.

This is where MCP and LangGraph actually meet: MultiServerMCPClient starts
our stock_server.py as a subprocess over stdio, discovers its tools, and
converts them into LangChain Tool objects we can call from graph nodes.
"""

import os
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END

from graph.state import ReportState
from graph.nodes import (
    get_input_node,
    make_fetch_price_node,
    make_fetch_news_node,
    generate_report_node,
)

MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "..", "mcp_server", "stock_server.py")


async def build_graph():
    client = MultiServerMCPClient(
        {
            "stock-info": {
                "command": sys.executable,
                "args": [MCP_SERVER_PATH],
                "transport": "stdio",
            }
        }
    )
    tools = await client.get_tools()
    tools_by_name = {tool.name: tool for tool in tools}

    graph = StateGraph(ReportState)
    graph.add_node("get_input", get_input_node)
    graph.add_node("fetch_price", make_fetch_price_node(tools_by_name))
    graph.add_node("fetch_news", make_fetch_news_node(tools_by_name))
    graph.add_node("generate_report", generate_report_node)

    graph.add_edge(START, "get_input")
    graph.add_edge("get_input", "fetch_price")
    graph.add_edge("fetch_price", "fetch_news")
    graph.add_edge("fetch_news", "generate_report")
    graph.add_edge("generate_report", END)

    return graph.compile()
