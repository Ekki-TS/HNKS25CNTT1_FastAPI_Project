from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base

class ResearchProject(Base):
    __tablename__ = "research_projects"

    id: Any = Column(Integer, primary_key=True, index=True)
    title: Any = Column(String(255), nullable=False)
    description: Any = Column(Text, nullable=True)
    owner_id: Any = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Any = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("UserModel", foreign_keys=[owner_id])
    members = relationship("ResearchMember", back_populates="project")
    tasks = relationship("ResearchTask", back_populates="project")


class ResearchMember(Base):
    __tablename__ = "research_members"

    project_id: Any = Column(Integer, ForeignKey("research_projects.id"), primary_key=True)
    user_id: Any = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role: Any = Column(String(50), nullable=False, default="MEMBER")
    joined_at: Any = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("ResearchProject", back_populates="members")
    user = relationship("UserModel", foreign_keys=[user_id])