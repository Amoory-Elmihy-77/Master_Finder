from langchain.agents import create_agent

from services.model import get_llm
from tools.web_search import web_research


SYSTEM_PROMPT = """You are MasterFinder AI, an academic study-abroad research agent.

Search the web for current, accurate information about Master's programs and professors.
Prefer official university sources. Never invent URLs, emails, or facts.
Return concise, factual research notes that can be structured later."""


def create_research_agent():
    return create_agent(
        model=get_llm(),
        tools=[web_research],
        system_prompt=SYSTEM_PROMPT,
    )
