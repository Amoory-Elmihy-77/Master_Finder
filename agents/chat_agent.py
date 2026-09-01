import os
import sqlite3

from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver

from services.model import get_llm
from tools.web_search import web_research


SYSTEM_PROMPT = """
You are MasterFinder AI.

You help users find Master's programs abroad.

You can:
- search current university programs
- research tuition and fees
- find deadlines
- find admission requirements
- research professors
- explain program fit
- discuss the user's CV when provided

Rules:
1. Use web research for current factual information.
2. Prefer official university sources.
3. Never invent facts.
4. Never invent professor emails.
5. Clearly state when information is unavailable.
6. Cite or expose source URLs when reporting researched information.
7. Remember the user's conversation context.
"""


DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
)
os.makedirs(DB_DIR, exist_ok=True)

CHECKPOINT_DB_PATH = os.path.join(DB_DIR, "chat_checkpoints.sqlite")

# A single shared connection persists conversation state (including
# across app restarts) instead of the in-memory checkpointer, which
# used to lose everything on refresh.
_connection = sqlite3.connect(
    CHECKPOINT_DB_PATH,
    check_same_thread=False,
)

checkpointer = SqliteSaver(_connection)


def get_chat_agent():
    return create_agent(
        model=get_llm(),
        tools=[web_research],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
