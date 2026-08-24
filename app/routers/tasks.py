from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.task import ResearchTaskModel
from app.models.user import UserModel
from app.schemas.research_task import (ResearchTaskBase, ResearchTaskResponse, ResearchTaskUpdate)
from app.schemas.user import MessageResponse
from app.services.task_services import (
    create_task, delete_task, get_task_or_404, list_tasks, 
    require_project_member, require_task_access, require_task_edit_permission, update_task
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ============ TASK-SPECIFIC ENDPOINTS ============
# GET /tasks/{id}: Lấy thông tin task
@router.get("/{task_id}", response_model=ResearchTaskResponse)
def get_task(task: ResearchTaskModel = Depends(require_task_access)):
    """Lấy thông tin chi tiết của một task."""
    return task


# PATCH /tasks/{id}: Cập nhật task
@router.patch("/{task_id}", response_model=MessageResponse)
def update_task_(
    task_id: int,
    data: ResearchTaskUpdate,
    task: ResearchTaskModel = Depends(require_task_edit_permission),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Cập nhật các trường của task - chỉ cập nhật field được gửi lên."""
    updated_task = update_task(task, data, current_user, db)
    return MessageResponse(
        message=f"Cập nhật task '{updated_task.title}' thành công",
        success=True,
        data={"task_id": updated_task.id, "title": updated_task.title}
    )


# DELETE /tasks/{id}: Xóa task
@router.delete("/{task_id}", response_model=MessageResponse)
def delete_task_(
    task: ResearchTaskModel = Depends(require_task_edit_permission),
    db: Session = Depends(get_db),
):
    """Xóa task."""
    task_title = task.title
    delete_task(task, db)
    return MessageResponse(
        message=f"Xóa task '{task_title}' thành công",
        success=True,
        data={"task_id": task.id}
    )

