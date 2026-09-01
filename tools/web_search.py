from openai import OpenAI
from langchain.tools import tool

from config.settings import OPENAI_MODEL

client = OpenAI()


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

    response = client.responses.create(
        model=OPENAI_MODEL,
        tools=[
            {
                "type": "web_search",
            }
        ],
        input=query,
    )

    text = response.output_text

    sources = []

    for item in response.output:
        if getattr(item, "type", None) != "web_search_call":
            continue

        action = getattr(item, "action", None)

        if not action:
            continue

        for source in getattr(action, "sources", []) or []:
            url = getattr(source, "url", None)
            if url:
                sources.append(url)

    unique_sources = list(dict.fromkeys(sources))

    if unique_sources:
        text += "\n\nSources:\n"
        text += "\n".join(f"- {url}" for url in unique_sources)

    return text
