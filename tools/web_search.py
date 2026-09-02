from langchain.tools import tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

# Limit to 3 results to keep context small enough for Groq's free tier
_search = DuckDuckGoSearchAPIWrapper(max_results=3)

# Max characters to return from a single search call (~1 500 tokens)
_MAX_CHARS = 3000


@tool
def web_research(query: str) -> str:
    """
    Search the live web for current information.

    Use this tool when current information is required, especially:
    university programs, tuition fees, deadlines, admission requirements,
    professors, official university profiles, and official contact details.

    The query should be specific and should ask for official university
    sources whenever possible.
    """
    try:
        result = _search.run(query)
        # Truncate so a single tool call can never blow the context window
        if len(result) > _MAX_CHARS:
            result = result[:_MAX_CHARS] + "\n[...truncated for length]"
        return result
    except Exception as e:
        return f"Search failed: {e}"
