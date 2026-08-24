from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# Vai trò thành viên
class MemberRole(str, Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"

# Dự án 
class ResearchProjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

# Tạo dự án
class ResearchProjectCreate(ResearchProjectBase):
    pass

# Cập nhật dự án
class ResearchProjectUpdate(BaseModel):
    # Mọi field tùy chọn để hỗ trợ cập nhật từng phần.
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

# Dữ liệu dữ án trả về cho người dùng xem
class ResearchProjectResponse(ResearchProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    # Cho phép tạo response trực tiếp từ SQLAlchemy model.
    model_config = ConfigDict(from_attributes=True)

# Dữ liệu thành viên
class ResearchMemberBase(BaseModel):
    user_id: int
    role: MemberRole = MemberRole.MEMBER

# Tạo thành viên
class ResearchMemberCreate(ResearchMemberBase):
    pass

# Cập nhật thành viên
class ResearchMemberUpdate(BaseModel):
    role: Optional[MemberRole] = None

# Dữ liệu thành viên trả về cho người dùng 
class ResearchMemberResponse(ResearchMemberBase):
    project_id: int
    joined_at: datetime

    # Cho phép Pydantic đọc thuộc tính của ResearchMemberModel.
    model_config = ConfigDict(from_attributes=True)
