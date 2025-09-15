# agents/orchestrator/agent.py
import os

# agents/orchestrator/agent.py
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from dotenv import load_dotenv
load_dotenv()

from .prompt import ORCHESTRATOR_PROMPT
from .subagents.stock_analyst.agent import stock_analyst_agent
from .subagents.stock_screener.agent import stock_screener_agent
from .subagents.stock_info.agent import stock_info_agent

from .utils.helper import sanitize_tickers

_base_orchestrator = LlmAgent(
    model=os.getenv("ORCHESTRATOR_MODEL"),
    name="orchestrator_agent",
    instruction=ORCHESTRATOR_PROMPT,
    tools=[
        # Deep judgment questions about named tickers
        AgentTool(agent=stock_analyst_agent),
        # Specific fact/table for named tickers (fast path) → stock_info_agent
        AgentTool(agent=stock_info_agent),
        # Find/screen with no explicit tickers
        AgentTool(agent=stock_screener_agent),
    ],
)

# ---- wrapper to sanitize before delegation -----------------------------------
class SanitizingOrchestrator(LlmAgent):
    async def run(self, text: str, *args, **kwargs):
        clean = sanitize_tickers(text)
        return await super().run(clean, *args, **kwargs)

orchestrator_agent = SanitizingOrchestrator.clone_from(_base_orchestrator)

root_agent = orchestrator_agent

# quick smoke
if __name__ == "__main__":
    import asyncio
    async def go():
        print(await root_agent.run("Is INFY a buy? Give key risks and recent catalysts."))
        # print(await root_agent.run("EV/EBITDA and PFCF for INFY & TCS"))
        # print(await root_agent.run("Screen IT & Banks with PE <= 20 and ROE >= 15"))
    asyncio.run(go())
