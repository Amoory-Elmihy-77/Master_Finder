from langchain_core.prompts import ChatPromptTemplate


CV_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a CV information extraction assistant.

Extract only information present in the CV.

Do not invent:
- degrees
- GPA
- skills
- work experience
- projects
- research interests
- certifications

If a field is not present, leave it empty or null.
""",
        ),
        (
            "human",
            """
Extract the candidate profile from this CV:

{cv_text}
""",
        ),
    ]
)
