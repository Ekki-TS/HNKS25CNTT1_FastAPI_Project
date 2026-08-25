from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.task import ResearchTaskModel, TaskCommentModel
from app.models.user import UserModel
from app.services.task_services import get_task_or_404, is_project_member


def require_comment_access(task_id: int, user: UserModel, db: Session) -> ResearchTaskModel:
    task = get_task_or_404(task_id, db)
    if not is_project_member(task.project_id, user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của project này",
        )
    return task


def list_comments(task_id: int, user: UserModel, db: Session) -> list[TaskCommentModel]:
    require_comment_access(task_id, user, db)
    return (
        db.query(TaskCommentModel)
        .filter(TaskCommentModel.task_id == task_id)
        .order_by(TaskCommentModel.created_at.asc(), TaskCommentModel.id.asc())
        .all()
    )


def create_comment(
    task_id: int,
    content: str,
    user: UserModel,
    db: Session,
) -> TaskCommentModel:
    require_comment_access(task_id, user, db)
    content = content.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nội dung comment không được để trống",
        )

    comment = TaskCommentModel(task_id=task_id, user_id=user.id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
