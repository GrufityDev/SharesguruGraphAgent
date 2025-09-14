# agents/subagents/stock_info/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
)
from dotenv import load_dotenv

from .prompt import STOCK_INFO_PROMPT

load_dotenv()

# ── MCP server (Streamable HTTP) ─────────────────────────────────────────────
MCP_URL = os.getenv("MCP_BASE","")
MCP_TOKEN = os.getenv("MCP_TOKEN")  # optional bearer

print(MCP_URL)
json_mcp_params = StreamableHTTPConnectionParams(
    url=MCP_URL,
    # headers={"Authorization": f"Bearer {MCP_TOKEN}"} if MCP_TOKEN else None,
    timeout=60.0,
)

mcp_tools = MCPToolset(
    connection_params=json_mcp_params,
    tool_filter=[
        "screenerGlossary", 
        "watchlistMetrics", 
        "shareholding", 
        "tickerNews",
        "financialStatements", 
        "tickerTranscripts"
    ]
)

stock_info_agent = LlmAgent(
    model=os.getenv("STOCK_INFO_MODEL"),
    name="stock_info_agent",
    instruction=STOCK_INFO_PROMPT,
    tools=[mcp_tools],
)


# Quick smoke test
if __name__ == "__main__":
    import asyncio
    async def go():
        # Example: deep question → the prompt should guide calling multiple tools
        print(await stock_info_agent.run("EV/EBITDA and PFCF for INFY & TCS"))
    asyncio.run(go())