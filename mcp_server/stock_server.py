"""MCP server exposing stock price and news tools, backed by yfinance.

Run standalone for testing:
    python mcp_server/stock_server.py

An MCP *server* is just a process that advertises a set of "tools" (functions
with typed inputs/outputs) over a protocol (here, stdio). Any MCP-aware
client — including LangGraph via langchain-mcp-adapters — can discover and
call these tools without knowing anything about yfinance.
"""

from mcp.server.fastmcp import FastMCP
import yfinance as yf

mcp = FastMCP("stock-info")


@mcp.tool()
def get_stock_price(ticker: str) -> dict:
    """Get the latest price and key stats for a stock ticker.

    Args:
        ticker: Stock ticker symbol, e.g. "AAPL".
    """
    t = yf.Ticker(ticker)
    info = t.info

    if not info or info.get("regularMarketPrice") is None:
        return {"error": f"No price data found for ticker '{ticker}'"}

    return {
        "ticker": ticker.upper(),
        "price": info.get("regularMarketPrice"),
        "previous_close": info.get("previousClose"),
        "change_percent": info.get("regularMarketChangePercent"),
        "volume": info.get("volume"),
        "market_cap": info.get("marketCap"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "short_name": info.get("shortName"),
    }


@mcp.tool()
def get_stock_news(ticker: str, limit: int = 5) -> list[dict]:
    """Get recent news headlines for a stock ticker.

    Args:
        ticker: Stock ticker symbol, e.g. "AAPL".
        limit: Max number of news items to return.
    """
    t = yf.Ticker(ticker)
    raw_news = t.news or []

    items = []
    for item in raw_news[:limit]:
        content = item.get("content", item)
        items.append(
            {
                "title": content.get("title"),
                "publisher": (content.get("provider") or {}).get("displayName"),
                "link": (content.get("canonicalUrl") or {}).get("url"),
                "published": content.get("pubDate"),
            }
        )
    return items


if __name__ == "__main__":
    mcp.run(transport="stdio")
