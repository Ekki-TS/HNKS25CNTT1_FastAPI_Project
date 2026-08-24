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

# Tạo thành viên, role luôn mặc định là MEMBER và không cho client lựa chọn.
class ResearchMemberCreate(BaseModel):
    user_id: int

# Cập nhật thành viên
class ResearchMemberUpdate(BaseModel):
    role: Optional[MemberRole] = None

# Dữ liệu thành viên trả về cho người dùng 
class ResearchMemberResponse(ResearchMemberBase):
    project_id: int
    joined_at: datetime

    # Cho phép Pydantic đọc thuộc tính của ResearchMemberModel.
    model_config = ConfigDict(from_attributes=True)


class ResearchProjectTitleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ResearchProjectTitleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberAdd(BaseModel):
    user_id: int


class MemberResponse(BaseModel):
    project_id: int
    user_id: int
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
