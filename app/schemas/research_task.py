from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# Trạng thái công việc 
class TaskStatus(str, Enum):
    # Enum giúp API chỉ nhận các trạng thái hợp lệ.
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

# Mức độ ưu tiện công việc
class TaskPriority(str, Enum):
    # Enum giúp API chỉ nhận các mức ưu tiên hợp lệ.
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

# Thông tin nhiệm vụ
class ResearchTaskBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None

# Cập nhật tiện độ nhiệm vụ
class ResearchTaskUpdate(BaseModel):
    # Các field tùy chọn vì update không nhất thiết thay đổi toàn bộ task.
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None

# Thông tin nhiệm vụ 
class ResearchTaskResponse(ResearchTaskBase):
    id: int
    project_id: int
    created_at: datetime
    
    # Cho phép tạo response từ SQLAlchemy model.
    model_config = ConfigDict(from_attributes=True)
