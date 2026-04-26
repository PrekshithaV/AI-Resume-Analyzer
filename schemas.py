from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    job_role: str = Field(..., min_length=2, max_length=200)
    blob_url: Optional[str] = Field(None)


class SkillGap(BaseModel):
    skill: str
    importance: str
    suggestion: str


class Improvement(BaseModel):
    section: str
    issue: str
    recommendation: str


class AnalysisResult(BaseModel):
    ats_score: int
    ats_verdict: str
    job_match_percent: int
    matched_skills: list[str]
    missing_skills: list[SkillGap]
    improvements: list[Improvement]
    strengths: list[str]
    summary: str


class UploadResponse(BaseModel):
    blob_url: str
    filename: str
    size_bytes: int