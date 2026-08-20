---
title: Stock Report Agent
emoji: 📈
sdk: gradio
app_file: app.py
---

# Stock Report Agent

A LangGraph pipeline that fetches stock price and news data via a custom
MCP server (wrapping `yfinance`) and generates a short report using Google
Gemini (free tier).

## Architecture

One LangGraph `StateGraph` with four nodes:

1. `get_input` — validates/normalizes the ticker symbol.
2. `fetch_price` — calls the `get_stock_price` MCP tool.
3. `fetch_news` — calls the `get_stock_news` MCP tool.
4. `generate_report` — asks Gemini to synthesize a report from the data.

The MCP server (`mcp_server/stock_server.py`) is launched as a local
subprocess over stdio by `langchain-mcp-adapters`, and its tools are loaded
into the graph as regular LangChain tools.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then fill in GOOGLE_API_KEY
```

## Run (CLI)

```bash
python main.py
```

## Run (web UI)

```bash
python app.py
```
