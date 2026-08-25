from fastapi import Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.project import ResearchMemberModel, ResearchProjectModel
from app.models.task import ResearchTaskModel
from app.models.user import UserModel
from app.schemas.research_task import ResearchTaskBase, ResearchTaskUpdate


def get_task_or_404(task_id: int, db: Session) -> ResearchTaskModel:
    task = db.query(ResearchTaskModel).filter(ResearchTaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy task")
    return task


def get_project_or_404(project_id: int, db: Session) -> ResearchProjectModel:
    project = db.query(ResearchProjectModel).filter(
        ResearchProjectModel.id == project_id,
        ResearchProjectModel.is_deleted.is_(False),
    ).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy project")
    return project


def is_project_member(project_id: int, user_id: int, db: Session) -> bool:
    project = db.query(ResearchProjectModel).filter(ResearchProjectModel.id == project_id).first()
    if project is None:
        return False
    if project.owner_id == user_id:
        return True
    membership = db.query(ResearchMemberModel).filter(
        ResearchMemberModel.project_id == project_id,
        ResearchMemberModel.user_id == user_id,
    ).first()
    return membership is not None


def require_task_access(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchTaskModel:
    task = get_task_or_404(task_id, db)
    if not is_project_member(task.project_id, current_user.id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không phải thành viên của project này")
    return task


def require_project_member(
    project_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchProjectModel:
    project = get_project_or_404(project_id, db)
    if not is_project_member(project_id, current_user.id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không phải thành viên của project này")
    return project


def require_task_edit_permission(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchTaskModel:
    task = get_task_or_404(task_id, db)
    if not is_project_member(task.project_id, current_user.id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không phải thành viên của project này")
    return task


def require_task_owner(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchTaskModel:
    task = get_task_or_404(task_id, db)
    project = get_project_or_404(task.project_id, db)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ owner của project mới được xóa task")
    return task


def create_task(
    project_id: int,
    data: ResearchTaskBase,
    current_user: UserModel,
    db: Session
) -> ResearchTaskModel:
    get_project_or_404(project_id, db)
    if not is_project_member(project_id, current_user.id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không phải thành viên của project này")
    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title không được để trống")
    task = ResearchTaskModel(
        project_id=project_id,
        title=title,
        description=data.description.strip() if data.description else None,
        status=data.status.value,
        priority=data.priority.value,
        due_date=data.due_date,
        assignee_id=data.assignee_id,
    )

    if data.assignee_id is not None and not is_project_member(project_id, data.assignee_id, db):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Assignee phải là thành viên của project")
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task


def list_tasks(project_id: int,current_user: UserModel,db: Session,task_status: str | None = None,priority: str | None = None,assignee_id: int | None = None,search_title: str | None = None,sort_by: str = "created_at",sort_order: str = "asc",limit: int = 10,offset: int = 0) -> tuple[list[ResearchTaskModel], int]:
    get_project_or_404(project_id, db)
    if not is_project_member(project_id, current_user.id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không phải thành viên của project này")
    query = db.query(ResearchTaskModel).filter(ResearchTaskModel.project_id == project_id)
    filters = []
    if task_status:
        filters.append(ResearchTaskModel.status == task_status)
    
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
    
    total = query.count()
    sort_columns = {
        "created_at": ResearchTaskModel.created_at,
        "due_date": ResearchTaskModel.due_date,
    }
    sort_column = sort_columns.get(sort_by, ResearchTaskModel.created_at)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    tasks = query.offset(offset).limit(limit).all()
    
    return tasks, total


def update_task(task: ResearchTaskModel,data: ResearchTaskUpdate,current_user: UserModel,db: Session) -> ResearchTaskModel:
    if data.assignee_id is not None:
        assignee = db.query(UserModel).filter(UserModel.id == data.assignee_id).first()
        
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Người dùng không tồn tại"
            )
        
        if not is_project_member(task.project_id, data.assignee_id, db):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Assignee phải là thành viên của project")
    values = data.model_dump(exclude_unset=True)
    
    for field, value in values.items():
        if value is not None or field == "assignee_id":
            if field == "title" and isinstance(value, str):
                value = value.strip()
                if not value:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title không được để trống")
            if field == "description" and value:
                value = value.strip()
            setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task


def delete_task(task: ResearchTaskModel,db: Session) -> None:
    db.delete(task)
    db.commit()

def get_assignee_name(db: Session, task: ResearchTaskModel) -> str | None:
    if task.assignee_id:
        user = db.query(UserModel).filter(UserModel.id == task.assignee_id).first()
        return user.full_name if user else None
    return None
