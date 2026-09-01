from typing import List, Optional

from pydantic import BaseModel, Field


class Professor(BaseModel):
    name: str
    university: str
    position: Optional[str] = None
    research_areas: List[str] = []
    official_profile_url: Optional[str] = None
    official_email: Optional[str] = None
    source_urls: List[str] = []
    relevance_reason: Optional[str] = None


class ProfessorSearchResult(BaseModel):
    professors: List[Professor] = Field(
        default_factory=list
    )
