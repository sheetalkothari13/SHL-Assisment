from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import json
import uuid
from app.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    role_name = Column(String(150), nullable=False)
    seniority = Column(String(50), nullable=False)
    target_skills_json = Column(Text, nullable=True) # JSON list of competencies
    notes = Column(Text, nullable=True) # General spec sheet/markdown notes
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("CampaignItem", back_populates="campaign", cascade="all, delete-orphan", lazy="selectin")

    @property
    def target_skills(self):
        if not self.target_skills_json:
            return []
        try:
            return json.loads(self.target_skills_json)
        except Exception:
            return []

    @target_skills.setter
    def target_skills(self, value):
        self.target_skills_json = json.dumps(value) if value else None

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "role_name": self.role_name,
            "seniority": self.seniority,
            "target_skills": self.target_skills,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "items": [item.to_dict() for item in self.items]
        }


class CampaignItem(Base):
    __tablename__ = "campaign_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    assessment_name = Column(String(150), nullable=False)
    assessment_code = Column(String(50), nullable=False)
    assessment_type = Column(String(10), nullable=False) # K, P, A, I
    assessment_url = Column(Text, nullable=False)
    why_selected = Column(Text, nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="items")

    def to_dict(self):
        return {
            "assessment_name": self.assessment_name,
            "assessment_code": self.assessment_code,
            "assessment_type": self.assessment_type,
            "assessment_url": self.assessment_url,
            "why_selected": self.why_selected
        }
