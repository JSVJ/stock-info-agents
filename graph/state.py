"""Shared state definition for the stock report graph.

LangGraph passes one shared dict-like object between nodes. Each node reads
whatever keys it needs and returns a dict of the keys it wants to update —
LangGraph merges that into the running state automatically.
"""

from typing import TypedDict


class ReportState(TypedDict, total=False):
    ticker: str
    error: str
    price_data: dict
    news_data: list[dict]
    report: str
