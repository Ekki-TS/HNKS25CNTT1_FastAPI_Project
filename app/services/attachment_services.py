from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.task import ResearchTaskModel, TaskAttachmentModel
from app.models.user import UserModel
from app.services.comment_services import require_comment_access

MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/zip",
    "application/x-7z-compressed",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "image/jpeg",
    "image/png",
    "text/plain",
}
ATTACHMENT_ROOT = Path("uploads") / "tasks"


def list_attachments(task_id: int, user: UserModel, db: Session) -> list[TaskAttachmentModel]:
    require_comment_access(task_id, user, db)
    return (
        db.query(TaskAttachmentModel)
        .filter(TaskAttachmentModel.task_id == task_id)
        .order_by(TaskAttachmentModel.created_at.desc(), TaskAttachmentModel.id.desc())
        .all()
    )


def save_attachment(
    task_id: int,
    upload: UploadFile,
    user: UserModel,
    db: Session,
) -> TaskAttachmentModel:
    require_comment_access(task_id, user, db)
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Loại file không được hỗ trợ",
        )

    content = upload.file.read(MAX_ATTACHMENT_SIZE + 1)
    if len(content) > MAX_ATTACHMENT_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Kích thước file tối đa là 10 MB",
        )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File không được để trống",
        )

    original_name = Path(upload.filename or "attachment").name
    suffix = Path(original_name).suffix.lower()
    stored_name = f"{uuid4().hex}{suffix}"
    folder = ATTACHMENT_ROOT / str(task_id)
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / stored_name
    file_path.write_bytes(content)

    attachment = TaskAttachmentModel(
        task_id=task_id,
        uploader_id=user.id,
        original_name=original_name,
        stored_name=stored_name,
        content_type=upload.content_type,
        file_size=len(content),
        file_path=str(file_path),
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def get_attachment(
    task_id: int,
    attachment_id: int,
    user: UserModel,
    db: Session,
) -> TaskAttachmentModel:
    require_comment_access(task_id, user, db)
    attachment = (
        db.query(TaskAttachmentModel)
        .filter(
            TaskAttachmentModel.id == attachment_id,
            TaskAttachmentModel.task_id == task_id,
        )
        .first()
    )
    if attachment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy file")
    return attachment
