from models.professor import ProfessorSearchResult
from prompts.professor_prompt import PROFESSOR_PROMPT
from services.model import get_llm
from agents.research_agent import create_research_agent

_MAX_RESEARCH_CHARS = 4000


def research_professors(
    university: str,
    field: str,
):
    agent = create_research_agent()

    query = (
        f"Find up to 5 current professors/researchers at {university} "
        f"working in {field}. For each: name, position, research areas, "
        f"official profile URL, official email if publicly listed."
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

    return result["messages"][-1].content


def extract_professors(
    university,
    field,
    research,
) -> ProfessorSearchResult:
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        ProfessorSearchResult
    )

    chain = PROFESSOR_PROMPT | structured_llm

    return chain.invoke(
        {
            "university": university,
            "field": field,
            "research": research[:_MAX_RESEARCH_CHARS],
        }
    )


def find_professors(
    university: str,
    field: str,
) -> ProfessorSearchResult:
    """
    Convenience wrapper: research + structured extraction in one call.
    """

    research = research_professors(university, field)

    return extract_professors(university, field, research)
