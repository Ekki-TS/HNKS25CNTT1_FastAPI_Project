from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base
	
class ResearchProjectModel(Base):
	__tablename__ = "projects"

	id = Column(Integer, primary_key=True, comment="Mã dự án")
	name = Column(String(100), nullable=False, comment="Tên dự án")
	description = Column(Text, nullable=True, comment="Mô tả dự án")
	owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="Chủ sở hữu dự án")
	created_at = Column(DateTime, default=datetime.now, nullable=False, comment="Thời điểm tạo dự án")
	is_deleted = Column(Boolean, default=False, nullable=False, comment="Cờ xóa mềm: dự án bị ẩn khỏi danh sách nhưng vẫn giữ dữ liệu")
	deleted_at = Column(DateTime, nullable=True, comment="Thời điểm xóa mềm dự án")
 
	# Một user có thể sở hữu nhiều project (User 1-N Project).
	owner = relationship("UserModel", back_populates="owned_projects")
	# Bảng trung gian này biểu diễn quan hệ nhiều-nhiều giữa user và project.
	members = relationship("ResearchMemberModel", back_populates="project")
	# Một project có thể có nhiều task.
	tasks = relationship("ResearchTaskModel", back_populates="project")
	# Mỗi dự án có nhiều log hoạt động để theo dõi lịch sử thay đổi.
	activity_logs = relationship("ResearchActivityLogModel", back_populates="project")


class ResearchMemberModel(Base):
	__tablename__ = "project_members"

	project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True, comment="Mã dự án")
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, comment="Mã user thành viên")
	role = Column(String(100), nullable=False, default="MEMBER", comment="Vai trò của thành viên trong dự án")
	joined_at = Column(DateTime, default=datetime.now, nullable=False, comment="Thời điểm thêm thành viên")

	# Hai khóa ngoại ghép thành khóa chính, ngăn một user tham gia project hai lần.
	project = relationship("ResearchProjectModel", back_populates="members")
	user = relationship("UserModel", back_populates="memberships")


class ResearchActivityLogModel(Base):
	__tablename__ = "project_activity_logs"

	id = Column(Integer, primary_key=True, comment="Mã log hoạt động")
	project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="Dự án bị tác động")
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="User thực hiện thao tác")
	action = Column(String(100), nullable=False, comment="Loại thao tác: CREATE_PROJECT, UPDATE_PROJECT, ADD_MEMBER...")
	details = Column(Text, nullable=True, comment="Thông tin chi tiết bổ sung cho hành động")
	created_at = Column(DateTime, default=datetime.now, nullable=False, comment="Thời điểm ghi log")

	# Ghi nhận lịch sử cho từng project và user tương ứng.
	project = relationship("ResearchProjectModel", back_populates="activity_logs")
	user = relationship("UserModel", back_populates="activity_logs")

__all__ = ["ResearchProjectModel", "ResearchMemberModel", "ResearchActivityLogModel"]
