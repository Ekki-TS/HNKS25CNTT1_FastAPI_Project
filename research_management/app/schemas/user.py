from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

# Schema thông báo chung cho tất cả responses
class MessageResponse(BaseModel):
    """Schema trả về thông báo thành công/thất bại cho client"""
    message: str
    success: bool = True
    data: Optional[dict] = None 
    
# Thông tin người dùng cơ bản
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., max_length=100)
    
#  Người dùng tạo acc 
class UserCreate(UserBase):
    # Password chỉ xuất hiện ở request và được băm trước khi lưu database
    password: str = Field(..., min_length=6, max_length=72)

# Người dùng đăng nhập acc 
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)

# Người dùng cập nhật acc 
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

# Đăng nhập lấy thông tin acc
class UserResponse(UserBase):
    # Response không chứa password_hash để tránh lộ dữ liệu nhạy cảm.
    id: int
    role: str
    is_active: bool
    created_at: datetime

    # Cho phép Pydantic tạo response từ SQLAlchemy model.
    model_config = ConfigDict(from_attributes=True)

# Trả về thông tin token kèm kiểu dữ liệu Bearer 
class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
