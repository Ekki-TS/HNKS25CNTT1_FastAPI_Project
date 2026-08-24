from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class ResearchTaskModel(Base):
	__tablename__ = "tasks"

	id = Column(Integer, primary_key=True)
	project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
	title = Column(String(100), nullable=False)
	description = Column(Text, nullable=True)
	assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
	status = Column(String(100), nullable=False, default="TODO")
	priority = Column(String(100), nullable=False, default="MEDIUM")
	due_date = Column(DateTime, nullable=True)
	created_at = Column(DateTime, default=datetime.now, nullable=False)

	# Task luôn thuộc một project; project có thể có nhiều task.
	project = relationship("ResearchProjectModel", back_populates="tasks")
	# assignee có thể rỗng vì task chưa nhất thiết được giao cho ai.
	assignee = relationship("UserModel", back_populates="assigned_tasks")

__all__ = ["ResearchTaskModel"]
