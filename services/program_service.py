from models.program import ProgramSearchResult
from prompts.program_prompt import PROGRAM_PROMPT
from services.model import get_llm
from agents.research_agent import create_research_agent


def research_programs(
    countries: list[str],
    field: str,
    degree: str,
    language: str,
    max_tuition: str,
):
    agent = create_research_agent()

    query = f"""
Find current Master's programs.

Countries:
{", ".join(countries)}

Field:
{field}

Degree:
{degree}

Preferred language:
{language}

Maximum tuition:
{max_tuition}

Search extensively.

For each candidate program, find:
- exact university name
- exact program name
- official program URL
- tuition
- currency
- ECTS
- duration
- teaching language
- deadline
- start date
- admission requirements

Use official university sources whenever possible.
"""

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
            "research": research,
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
