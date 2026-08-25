from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.task import ResearchTaskModel
from app.models.user import UserModel
from app.schemas.research_task import (ResearchTaskResponse, ResearchTaskUpdate, TaskAttachmentResponse, TaskCommentCreate, TaskCommentResponse)
from app.schemas.user import MessageResponse
from app.services.task_services import (
    create_task, delete_task, get_task_or_404, list_tasks, 
    require_project_member, require_task_access, require_task_edit_permission, update_task
)
from app.services.task_services import require_task_owner
from app.services.comment_services import create_comment, list_comments
from app.services.attachment_services import get_attachment, list_attachments, save_attachment

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}/comments", response_model=list[TaskCommentResponse], summary="Danh sách comment của task")
def get_task_comments(task_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_comments(task_id, current_user, db)


@router.post("/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED, summary="Thêm comment cho task")
def add_task_comment(task_id: int, data: TaskCommentCreate, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_comment(task_id, data.content, current_user, db)


@router.get("/{task_id}/attachments", response_model=list[TaskAttachmentResponse], summary="Danh sách file đính kèm")
def get_task_attachments(task_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_attachments(task_id, current_user, db)


@router.post("/{task_id}/attachments", response_model=TaskAttachmentResponse, status_code=status.HTTP_201_CREATED, summary="Upload file cho task")
def add_task_attachment(task_id: int, file: UploadFile = File(...), current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return save_attachment(task_id, file, current_user, db)


@router.get("/{task_id}/attachments/{attachment_id}/download", summary="Tải file đính kèm")
def download_task_attachment(task_id: int, attachment_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    attachment = get_attachment(task_id, attachment_id, current_user, db)
    return FileResponse(attachment.file_path, media_type=attachment.content_type, filename=attachment.original_name)

@router.get("/{task_id}", response_model=ResearchTaskResponse, summary="Lấy thông tin tasks")
def get_task(task: ResearchTaskModel = Depends(require_task_access)):
    """Lấy thông tin chi tiết của một task."""
    return task


@router.patch("/{task_id}", response_model=MessageResponse, summary="Cập nhật tasks")
def update_task_(task_id: int,data: ResearchTaskUpdate,task: ResearchTaskModel = Depends(require_task_edit_permission),db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    """Cập nhật các trường của task - chỉ cập nhật field được gửi lên."""
    updated_task = update_task(task, data, current_user, db)
    return MessageResponse(
        message=f"Cập nhật task '{updated_task.title}' thành công",
        success=True,
        data={"task_id": updated_task.id, "title": updated_task.title}
    )


@router.delete("/{task_id}", response_model=MessageResponse, summary="Xóa tasks")
def delete_task_(task: ResearchTaskModel = Depends(require_task_owner),db: Session = Depends(get_db)):
    """Xóa task."""
    task_title = task.title
    delete_task(task, db)
    return MessageResponse(
        message=f"Xóa task '{task_title}' thành công",
        success=True,
        data={"task_id": task.id}
    )

