from app.db.database import Base
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, comment="Mã người dùng")
    email = Column(String(250), unique=True, nullable=False, comment="Email đăng nhập")
    password_hash = Column(String(255), nullable=False, comment="Mật khẩu đã hash")
    full_name = Column(String(100), nullable=False, comment="Họ tên")
    role = Column(String(100), default="USER", nullable=False, comment="Vai trò tài khoản")
    is_active = Column(Boolean, default=True, nullable=False, comment="Trạng thái tài khoản")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="Ngày tạo")
    
    # Các quan hệ này cho phép truy cập project/member/task từ user.
    owned_projects = relationship("ResearchProjectModel", back_populates="owner")
    memberships = relationship("ResearchMemberModel", back_populates="user")
    assigned_tasks = relationship("ResearchTaskModel", back_populates="assignee")
    # Mỗi user có thể tạo ra nhiều log hoạt động trong project để phục vụ audit trail.
    activity_logs = relationship("ResearchActivityLogModel", back_populates="user")
