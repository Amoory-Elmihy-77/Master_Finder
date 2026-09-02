from langchain_groq import ChatGroq

from config.settings import GROQ_API_KEY, GROQ_MODEL


def get_llm():
    return ChatGroq(
        model_name=GROQ_MODEL,
        groq_api_key=GROQ_API_KEY,
        temperature=0.1,
        max_retries=2,
    )
