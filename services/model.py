from langchain_openai import ChatOpenAI

from config.settings import OPENAI_MODEL


def get_llm():
    return ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=0.1,
    )
