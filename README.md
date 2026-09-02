# MasterFinder AI

An agentic AI study-abroad research assistant built with Python, LangChain,
Google Gemini, and Streamlit.

The system researches current Master's programs from official university
sources, extracts structured program information, finds relevant academic
researchers, analyzes a user's CV, matches candidates against programs, and
maintains conversational context for personalized study-abroad research.

## Project structure

```
masterfinder-ai/
├── app.py                    # Streamlit UI, wired to all services/agents
├── requirements.txt
├── .env.example
├── .gitignore
│
├── config/
│   └── settings.py           # env vars (GEMINI_API_KEY, GEMINI_MODEL)
│
├── models/                   # Pydantic schemas
│   ├── program.py            # Program, ProgramSearchResult
│   ├── professor.py          # Professor, ProfessorSearchResult
│   └── candidate.py          # CandidateProfile
│
├── prompts/                  # ChatPromptTemplates
│   ├── program_prompt.py
│   ├── professor_prompt.py
│   ├── cv_prompt.py
│   └── matching_prompt.py
│
├── tools/
│   └── web_search.py         # web_research: LangChain tool wrapping
│                              # Gemini Google Search grounding
│
├── agents/
│   ├── research_agent.py     # one-shot research agent (no memory)
│   └── chat_agent.py         # chat agent with InMemorySaver checkpointing
│
├── chains/
│   ├── cv_chain.py           # CV text -> CandidateProfile
│   └── matching_chain.py     # CandidateProfile + Program -> ProgramMatch
│
├── loaders/
│   └── cv_loader.py          # PDF -> LangChain Documents -> text
│
└── services/
    ├── model.py               # get_llm()
    ├── program_service.py     # research + structured extraction + find_programs()
    └── professor_service.py   # research + structured extraction + find_professors()
```

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your real GEMINI_API_KEY
```

## Run

```bash
streamlit run app.py
```

## How it fits together

```
User
 ↓
Streamlit UI (app.py)
 ↓
services.program_service.find_programs() / services.professor_service.find_professors()
 ↓
agents.research_agent (create_agent + web_research tool)
 ↓
tools.web_search.web_research()  →  Gemini Google Search grounding  →  live web
 ↓
research text
 ↓
prompts + services.model.get_llm().with_structured_output(...)
 ↓
Program / Professor Pydantic objects
 ↓
Streamlit cards

CV flow:
Upload PDF → loaders.cv_loader.load_cv() → documents_to_text()
 → chains.cv_chain.analyze_cv() → CandidateProfile
 → chains.matching_chain.match_candidate_to_program() → ProgramMatch

Chat flow:
agents.chat_agent.get_chat_agent() (same tool, + InMemorySaver checkpointer
keyed by a stable thread_id) → conversational memory across turns
```

## Engineering rules baked into the prompts

1. Never let the LLM invent university data.
2. Prefer official university sources.
3. Keep source URLs.
4. Never invent professor emails — `official_email` is `null` unless it is
   publicly listed on an official source.
5. Use structured Pydantic output everywhere instead of parsing free text.
6. Use web search for anything that changes (tuition, deadlines, professors).
7. Use `InMemorySaver` + a stable `thread_id` for conversational context
   (prototype-only; swap for a persistent checkpointer/store in production).
8. The CV is used only for extraction/matching — never as an admission
   guarantee. Fit scores are estimates, not decisions.
9. Start simple: no RAG/vector DB/FastAPI/Docker in this V1.
10. Uses the current LangChain 1.x agent API (`create_agent`) rather than
    the older `LLMChain` / `initialize_agent` / `ConversationBufferMemory`.

## Free tier notes (Gemini)

- Get a free API key at https://aistudio.google.com/apikey — no credit card
  required.
- `gemini-2.5-flash` (the default here) is on the free tier and includes a
  daily quota of free Google Search grounding requests. Check your live
  quota in AI Studio, since Google adjusts these numbers over time.
- Source links returned by grounding are Google redirect URLs
  (`vertexaisearch.cloud.google.com/...`) rather than the original site's
  URL directly. They still resolve to the real page in a browser, but if
  you need the raw destination URL you'll need to follow the redirect
  server-side.
- If you outgrow the free quota, either wait for the daily reset or switch
  `GEMINI_MODEL` to a paid-tier call — no other code changes needed.


Streamlit → Gemini → PromptTemplate → web_research tool → agent →
structured Program output → professors → CV upload/loader →
CandidateProfile → CV/program matching → agent memory → UI polish →
source validation → edge cases.

Optional next steps (not built here): RAG over saved university PDFs,
persistent user profiles, professor-outreach email drafts, multi-factor
program ranking, LangGraph for more complex workflows, and caching to
control search cost.
