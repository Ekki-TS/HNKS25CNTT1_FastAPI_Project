from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class ResearchTaskModel(Base):
	__tablename__ = "tasks"

	id: Any = Column(Integer, primary_key=True)
	project_id: Any = Column(Integer, ForeignKey("projects.id"), nullable=False)
	title: Any = Column(String(100), nullable=False)
	description: Any = Column(Text, nullable=True)
	assignee_id: Any = Column(Integer, ForeignKey("users.id"), nullable=True)
	status: Any = Column(String(100), nullable=False, default="TODO")
	priority: Any = Column(String(100), nullable=False, default="MEDIUM")
	due_date: Any = Column(DateTime, nullable=True)
	created_at: Any = Column(DateTime, default=datetime.now, nullable=False)

	# Task luôn thuộc một project; project có thể có nhiều task.
	project = relationship("ResearchProjectModel", back_populates="tasks")
	# assignee có thể rỗng vì task chưa nhất thiết được giao cho ai.
	assignee = relationship("UserModel", back_populates="assigned_tasks")
	comments = relationship("TaskCommentModel", back_populates="task", cascade="all, delete-orphan")
	attachments = relationship("TaskAttachmentModel", back_populates="task", cascade="all, delete-orphan")


class TaskCommentModel(Base):
	__tablename__ = "task_comments"

	id: Any = Column(Integer, primary_key=True)
	task_id: Any = Column(Integer, ForeignKey("tasks.id"), nullable=False)
	user_id: Any = Column(Integer, ForeignKey("users.id"), nullable=False)
	content: Any = Column(Text, nullable=False)
	created_at: Any = Column(DateTime, default=datetime.now, nullable=False)

	task = relationship("ResearchTaskModel", back_populates="comments")
	user = relationship("UserModel", back_populates="task_comments")


class TaskAttachmentModel(Base):
	__tablename__ = "task_attachments"

	id: Any = Column(Integer, primary_key=True)
	task_id: Any = Column(Integer, ForeignKey("tasks.id"), nullable=False)
	uploader_id: Any = Column(Integer, ForeignKey("users.id"), nullable=False)
	original_name: Any = Column(String(255), nullable=False)
	stored_name: Any = Column(String(255), nullable=False, unique=True)
	content_type: Any = Column(String(100), nullable=False)
	file_size: Any = Column(Integer, nullable=False)
	file_path: Any = Column(String(500), nullable=False)
	created_at: Any = Column(DateTime, default=datetime.now, nullable=False)

	task = relationship("ResearchTaskModel", back_populates="attachments")
	uploader = relationship("UserModel", back_populates="task_attachments")

__all__ = ["ResearchTaskModel", "TaskCommentModel", "TaskAttachmentModel"]
 