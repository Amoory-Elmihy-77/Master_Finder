from models.professor import ProfessorSearchResult
from prompts.professor_prompt import PROFESSOR_PROMPT
from services.model import get_llm
from agents.research_agent import create_research_agent


def research_professors(
    university: str,
    field: str,
):
    agent = create_research_agent()

    query = f"""
Find up to 10 current professors/researchers at:

University:
{university}

Field:
{field}

Prioritize researchers whose work is directly relevant.

For every researcher find:
- name
- current position
- research areas
- official university profile URL
- official university email if publicly listed
- source URL

Never guess or construct an email address.
If no public official email is found, say:
"Not publicly listed."

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
            "research": research,
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
