from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import json
import uuid
from app.database import Base

class ConversationalSession(Base):
    __tablename__ = "conversational_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), default="New Assessment Campaign")
    status = Column(String(50), default="Requirement Gathering") # Requirement Gathering, Shortlisted, Inactive
    turn_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("SessionMessage", back_populates="session", cascade="all, delete-orphan", lazy="selectin")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "turn_count": self.turn_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [m.to_dict() for m in sorted(self.messages, key=lambda x: x.id)]
        }


class SessionMessage(Base):
    __tablename__ = "session_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("conversational_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False) # user, assistant
    content = Column(Text, nullable=False)
    recommendations_json = Column(Text, nullable=True) # JSON array of recommendations
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ConversationalSession", back_populates="messages")

    @property
    def recommendations(self):
        if not self.recommendations_json:
            return []
        try:
            return json.loads(self.recommendations_json)
        except Exception:
            return []

    @recommendations.setter
    def recommendations(self, value):
        self.recommendations_json = json.dumps(value) if value else None

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat()
        }
