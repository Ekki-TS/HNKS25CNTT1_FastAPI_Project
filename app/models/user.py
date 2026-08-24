from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base

class UserModel(Base):
    __tablename__ = "users"
    
    id: Any = Column(Integer, primary_key=True, comment="Mã người dùng")
    email: Any = Column(String(250), unique=True, nullable=False, comment="Email đăng nhập")
    password_hash: Any = Column(String(255), nullable=False, comment="Mật khẩu đã hash")
    full_name: Any = Column(String(100), nullable=False, comment="Họ tên")
    role: Any = Column(String(100), default="USER", nullable=False, comment="Vai trò tài khoản")
    is_active: Any = Column(Boolean, default=True, nullable=False, comment="Trạng thái tài khoản")
    created_at: Any = Column(DateTime, default=datetime.now, nullable=False, comment="Ngày tạo")
    
    # Các quan hệ này cho phép truy cập project/member/task từ user.
    owned_projects = relationship("ResearchProjectModel", back_populates="owner")
    memberships = relationship("ResearchMemberModel", back_populates="user")
    assigned_tasks = relationship("ResearchTaskModel", back_populates="assignee")
    task_comments = relationship("TaskCommentModel", back_populates="user")
    task_attachments = relationship("TaskAttachmentModel", back_populates="uploader")
    # Mỗi user có thể tạo ra nhiều log hoạt động trong project để phục vụ audit trail.
    activity_logs = relationship("ResearchActivityLogModel", back_populates="user")
