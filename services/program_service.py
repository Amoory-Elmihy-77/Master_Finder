from models.program import ProgramSearchResult
from prompts.program_prompt import PROGRAM_PROMPT
from services.model import get_llm
from agents.research_agent import create_research_agent

# Truncate research text to keep extraction calls within Groq's free-tier limits
_MAX_RESEARCH_CHARS = 4000


def research_programs(
    countries: list[str],
    field: str,
    degree: str,
    language: str,
    max_tuition: str,
):
    agent = create_research_agent()

    query = (
        f"Find current {degree} programs in {field} at universities in "
        f"{', '.join(countries)}. Language: {language}. Max tuition: {max_tuition}. "
        f"For each program find: university name, program name, official URL, "
        f"tuition, ECTS, duration, language, deadline, admission requirements."
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )

    messages = result["messages"]

    final_message = messages[-1]

    return final_message.content


def extract_programs(
    countries,
    field,
    degree,
    language,
    max_tuition,
    research,
) -> ProgramSearchResult:
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        ProgramSearchResult
    )

    chain = PROGRAM_PROMPT | structured_llm

    result = chain.invoke(
        {
            "countries": ", ".join(countries),
            "field": field,
            "degree": degree,
            "language": language,
            "max_tuition": max_tuition,
            "research": research[:_MAX_RESEARCH_CHARS],
        }
    )

    return result


def find_programs(
    countries: list[str],
    field: str,
    degree: str,
    language: str,
    max_tuition: str,
) -> ProgramSearchResult:
    """
    Convenience wrapper: research + structured extraction in one call.
    """

    research = research_programs(
        countries,
        field,
        degree,
        language,
        max_tuition,
    )

    return extract_programs(
        countries,
        field,
        degree,
        language,
        max_tuition,
        research,
    )
