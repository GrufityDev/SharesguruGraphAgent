# agents/subagents/stock_screener/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
)
from dotenv import load_dotenv

from .prompt import SCREENER_PROMPT

load_dotenv()

# ── MCP server (Streamable HTTP) ─────────────────────────────────────────────
MCP_URL = os.getenv("MCP_GRAPH_BASE")
MCP_TOKEN = os.getenv("MCP_TOKEN")  # optional bearer

json_mcp_params = StreamableHTTPConnectionParams(
    url=MCP_URL,
    # headers={"Authorization": f"Bearer {MCP_TOKEN}"} if MCP_TOKEN else None,
    timeout=60.0,
)

mcp_tools = MCPToolset(
    connection_params=json_mcp_params,
    tool_filter=[
        "screenerGlossary", 
        "screenerQuery", 
        "screenerFields"
    ]
)

stock_screener_agent = LlmAgent(
    model=os.getenv("STOCK_SCREENER_MODEL"),
    name="stock_screener_agent",
    instruction=SCREENER_PROMPT,
    tools=[mcp_tools],
)

# Quick smoke test
if __name__ == "__main__":
    import asyncio
    async def go():
        print(await stock_screener_agent.run("Find auto stocks with low PE and ROE >= 15; return top 50"))
    asyncio.run(go())