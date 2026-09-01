from typing import List, Optional

from pydantic import BaseModel


class CandidateProfile(BaseModel):
    name: Optional[str] = None
    education: List[str] = []
    gpa: Optional[str] = None
    skills: List[str] = []
    experience: List[str] = []
    projects: List[str] = []
    research_interests: List[str] = []
    languages: List[str] = []
    certifications: List[str] = []
    summary: Optional[str] = None
