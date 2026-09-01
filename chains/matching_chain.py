from pydantic import BaseModel, Field

from prompts.matching_prompt import MATCHING_PROMPT
from services.model import get_llm


class ProgramMatch(BaseModel):
    score: int = Field(
        ge=0,
        le=100
    )

    strengths: list[str] = Field(
        default_factory=list
    )

    potential_gaps: list[str] = Field(
        default_factory=list
    )

    explanation: str


def match_candidate_to_program(
    candidate,
    program,
) -> ProgramMatch:
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        ProgramMatch
    )

    chain = MATCHING_PROMPT | structured_llm

    return chain.invoke(
        {
            "candidate": candidate.model_dump_json(
                indent=2
            ),
            "program": program.model_dump_json(
                indent=2
            ),
        }
    )
