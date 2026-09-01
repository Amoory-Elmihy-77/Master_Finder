from typing import List, Optional

from pydantic import BaseModel, Field


class Program(BaseModel):
    university: str
    country: str
    program_name: str
    degree: str

    tuition: Optional[str] = None
    currency: Optional[str] = None

    ects: Optional[int] = None
    duration: Optional[str] = None
    language: Optional[str] = None

    deadline: Optional[str] = None
    start_date: Optional[str] = None

    admission_requirements: List[str] = Field(
        default_factory=list
    )

    official_program_url: Optional[str] = None

    source_urls: List[str] = Field(
        default_factory=list
    )

    notes: Optional[str] = None


class ProgramSearchResult(BaseModel):
    programs: List[Program] = Field(
        default_factory=list
    )
