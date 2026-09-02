from google import genai
from google.genai import types
from langchain.tools import tool

from config.settings import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

_grounding_tool = types.Tool(google_search=types.GoogleSearch())


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

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=query,
        config=types.GenerateContentConfig(
            tools=[_grounding_tool],
        ),
    )

    text = response.text or ""

    sources = []

    candidate = response.candidates[0] if response.candidates else None
    metadata = getattr(candidate, "grounding_metadata", None) if candidate else None

    if metadata and metadata.grounding_chunks:
        for chunk in metadata.grounding_chunks:
            web = getattr(chunk, "web", None)
            if web and getattr(web, "uri", None):
                sources.append(web.uri)

    unique_sources = list(dict.fromkeys(sources))

    if unique_sources:
        text += "\n\nSources:\n"
        text += "\n".join(f"- {url}" for url in unique_sources)

    return text
