# agents/orchestrator/agent.py
import os
import re
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from dotenv import load_dotenv

load_dotenv()

from .prompt import ORCHESTRATOR_PROMPT
from .subagents.stock_analyst.agent import stock_analyst_agent
from .subagents.stock_screener.agent import stock_screener_agent
from .subagents.stock_info.agent import stock_info_agent
from .utils.helper import sanitize_tickers   # your helper is fine to keep using

# --- if you prefer a quick local regex (optional fallback) --------------------
_SANITIZER_RE = re.compile(r"\b([A-Za-z0-9]+)\.(NS|NSE|BSE|BO)\b", flags=re.IGNORECASE)
def _sanitize(text: str) -> str:
    """Remove .NS/.BO suffixes and upper-case the ticker code."""
    if not isinstance(text, str):
        return text
    return _SANITIZER_RE.sub(lambda m: m.group(1).upper(), text)

# --- main orchestrator agent --------------------------------------------------
orchestrator_agent = LlmAgent(
    model=os.getenv("ORCHESTRATOR_MODEL", ""),
    name="orchestrator_agent",
    instruction=ORCHESTRATOR_PROMPT,
    tools=[
        AgentTool(agent=stock_analyst_agent),   # deep judgment on named tickers
        AgentTool(agent=stock_info_agent),      # factual data for named tickers
        AgentTool(agent=stock_screener_agent),  # screening when no tickers
    ],
)

# Convenience wrapper: call this instead of orchestrator_agent.run(...)
async def run_orchestrator(user_text: str, *args, **kwargs):
    """
    Sanitize tickers like TATAMOTORS.NS -> TATAMOTORS
    and forward the cleaned text to the orchestrator agent.
    """
    clean = sanitize_tickers(user_text) if sanitize_tickers else _sanitize(user_text)
    return await orchestrator_agent.run(clean, *args, **kwargs)

# Export root_agent for compatibility if other code imports it
root_agent = orchestrator_agent

# --- quick smoke test --------------------------------------------------------
if __name__ == "__main__":
    import asyncio
    async def go():
        # call run_orchestrator() so tickers get cleaned first
        print(await run_orchestrator("Is INFY.NS a buy? Give key risks and recent catalysts."))
        # print(await run_orchestrator("EV/EBITDA and PFCF for TATAMOTORS.BO & TCS.NS"))
        # print(await run_orchestrator("Screen IT & Banks with PE <= 20 and ROE >= 15"))
    asyncio.run(go())
