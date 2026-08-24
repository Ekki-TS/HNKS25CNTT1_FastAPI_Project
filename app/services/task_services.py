from datetime import datetime
from fastapi import Depends, HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.project import ResearchMemberModel, ResearchProjectModel
from app.models.task import ResearchTaskModel
from app.models.user import UserModel
from app.schemas.research_task import ResearchTaskUpdate


def get_task_or_404(task_id: int, db: Session) -> ResearchTaskModel:
    """Lấy task, trả 404 nếu không tìm thấy."""
    task = db.query(ResearchTaskModel).filter(ResearchTaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy task"
        )
    return task


def get_project_or_404(project_id: int, db: Session) -> ResearchProjectModel:
    """Lấy project chưa xóa, trả 404 nếu không tìm thấy."""
    project = db.query(ResearchProjectModel).filter(ResearchProjectModel.id == project_id,ResearchProjectModel.is_deleted.is_(False)).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy project"
        )
    return project


def is_project_member(project_id: int, user_id: int, db: Session) -> bool:
    """Kiểm tra user có phải thành viên hoặc chủ sở hữu project."""
    project = db.query(ResearchProjectModel).filter(ResearchProjectModel.id == project_id).first()
    
    if project is None:
        return False
    
    # Check if user is owner
    if bool(project.owner_id) == user_id:
        return True
    
    # Check if user is member
    membership = db.query(ResearchMemberModel).filter(ResearchMemberModel.project_id == project_id,ResearchMemberModel.user_id == user_id).first()
    
    return membership is not None


def require_task_access(task_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)) -> ResearchTaskModel:
    """Kiểm tra user có thể truy cập task (phải là thành viên project)."""
    task = get_task_or_404(task_id, db)
    
    if not is_project_member(task.project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của project này"
        )
    
    return task


def require_project_member(project_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)) -> ResearchProjectModel:
    """Kiểm tra user có phải thành viên project."""
    project = get_project_or_404(project_id, db)
    
    if not is_project_member(project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của project này"
        )
    
    return project


def require_task_edit_permission(task_id: int,current_user: UserModel = Depends(get_current_user),db: Session = Depends(get_db)) -> ResearchTaskModel:
    """Kiểm tra user có quyền chỉnh sửa task (owner/member/assignee)."""
    task = get_task_or_404(task_id, db)
    
    # Kiểm tra user là thành viên project
    if not is_project_member(task.project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của project này"
        )
    
    return task


def create_task(
    project_id: int,
    title: str,
    description: str | None,
    current_user: UserModel,
    db: Session
) -> ResearchTaskModel:
    """Tạo task mới - chỉ thành viên project mới được tạo."""
    # Kiểm tra project tồn tại
    project = get_project_or_404(project_id, db)
    
    # Kiểm tra user là thành viên project
    if not is_project_member(project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của project này"
        )
    
    # Validate title
    title = title.strip()
    if not title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title không được để trống"
        )
    
    task = ResearchTaskModel(
        project_id=project_id,
        title=title,
        description=description.strip() if description else None
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task


def list_tasks(
    project_id: int,
    current_user: UserModel,
    db: Session,
    status: str | None = None,
    priority: str | None = None,
    assignee_id: int | None = None,
    search_title: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "asc",
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[ResearchTaskModel], int]:
    """Lấy danh sách task của project với filtering."""
    # Kiểm tra project tồn tại
    project = get_project_or_404(project_id, db)
    
    # Kiểm tra user là thành viên project
    if not is_project_member(project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của project này"
        )
    
    # Base query
    query = db.query(ResearchTaskModel).filter(
        ResearchTaskModel.project_id == project_id
    )
    
    # Apply filters
    filters = []
    
    if status:
        filters.append(ResearchTaskModel.status == status)
    
    if priority:
        filters.append(ResearchTaskModel.priority == priority)
    
    if assignee_id:
        filters.append(ResearchTaskModel.assignee_id == assignee_id)
    
    if search_title and search_title.strip():
        filters.append(
            ResearchTaskModel.title.ilike(f"%{search_title.strip()}%")
        )
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Get total count
    total = query.count()
    
    # Apply sorting
    sort_column = getattr(ResearchTaskModel, sort_by, ResearchTaskModel.created_at)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Apply pagination
    tasks = query.offset(offset).limit(limit).all()
    
    return tasks, total


def update_task(
    task: ResearchTaskModel,
    data: ResearchTaskUpdate,
    current_user: UserModel,
    db: Session
) -> ResearchTaskModel:
    """Cập nhật task - chỉ cập nhật các field được cung cấp."""
    # Validate assignee nếu được cung cấp
    if data.assignee_id is not None:
        if data.assignee_id != 0:  # 0 means remove assignee
            assignee = db.query(UserModel).filter(
                UserModel.id == data.assignee_id
            ).first()
            
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Người dùng không tồn tại"
                )
            
            # Kiểm tra assignee có phải thành viên project
            if not is_project_member(task.project_id, data.assignee_id, db):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Assignee phải là thành viên của project"
                )
    
    # Update only provided fields
    values = data.model_dump(exclude_unset=True)
    
    for field, value in values.items():
        if value is not None or field == "assignee_id":
            if field == "title" and value:
                value = value.strip()
            if field == "description" and value:
                value = value.strip()
            setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task


def delete_task(
    task: ResearchTaskModel,
    db: Session
) -> None:
    """Xóa task."""
    db.delete(task)
    db.commit()


def get_assignee_name(db: Session, task: ResearchTaskModel) -> str | None:
    """Lấy tên assignee nếu có."""
    if task.assignee_id:
        user = db.query(UserModel).filter(UserModel.id == task.assignee_id).first()
        return user.full_name if user else None
    return None
