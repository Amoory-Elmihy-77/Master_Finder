from models.candidate import CandidateProfile
from prompts.cv_prompt import CV_PROMPT
from services.model import get_llm


def analyze_cv(cv_text: str) -> CandidateProfile:
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        CandidateProfile
    )

    chain = CV_PROMPT | structured_llm

    return chain.invoke(
        {
            "cv_text": cv_text,
        }
    )
