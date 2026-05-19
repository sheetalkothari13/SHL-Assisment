from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CampaignItemCreate(BaseModel):
    assessment_name: str = Field(..., description="The name of the assessment.")
    assessment_code: str = Field(..., description="The catalog code of the assessment.")
    assessment_type: str = Field(..., description="The type: K, P, A, I.")
    assessment_url: str = Field(..., description="The product portal URL.")
    why_selected: Optional[str] = Field(None, description="Detailed recruiter fit reasoning.")


class CampaignCreate(BaseModel):
    title: str = Field(..., description="A custom title for the recruitment campaign spec sheet.")
    role_name: str = Field(..., description="The target job role.")
    seniority: str = Field(..., description="Target seniority (Entry, Mid, Senior).")
    target_skills: List[str] = Field(default_factory=list, description="Target competencies or skills.")
    notes: Optional[str] = Field(None, description="General specification markdown/text notes.")
    items: List[CampaignItemCreate] = Field(..., description="List of finalized assessment items selected in the specs.")


class CampaignResponse(BaseModel):
    id: str
    title: str
    role_name: str
    seniority: str
    target_skills: List[str]
    notes: Optional[str] = None
    created_at: str
    items: List[CampaignItemCreate]
