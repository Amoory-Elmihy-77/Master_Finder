import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
    raise RuntimeError(
        "GROQ_API_KEY is missing. Add it to your .env file. "
        "Get a free key at https://console.groq.com/keys"
    )
