from datetime import datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.project import ResearchActivityLogModel, ResearchMemberModel, ResearchProjectModel
from app.models.user import UserModel
from app.schemas.research_project import ResearchMemberCreate, ResearchProjectCreate, ResearchProjectUpdate


def log_project_activity(db: Session, project_id: int, user_id: int, action: str, details: str | None = None) -> None:
    # Ghi log hành động của user lên project để phục vụ audit trail và tracking lịch sử.
    db.add(
        ResearchActivityLogModel(
            project_id=project_id,
            user_id=user_id,
            action=action,
            details=details,
        )
    )


def get_project_or_404(project_id: int, db: Session) -> ResearchProjectModel:
    # Chỉ lấy project chưa bị xóa mềm để tránh trả về dữ liệu đã ẩn khỏi hệ thống.
    project = db.query(ResearchProjectModel).filter(ResearchProjectModel.id == project_id,ResearchProjectModel.is_deleted.is_(False)).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay project")
    return project


def require_project_member(project_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)) -> ResearchProjectModel:
    project = get_project_or_404(project_id, db)
    if project.owner_id == current_user.id:  # type: ignore[comparison-overlap]
        return project
    membership = db.query(ResearchMemberModel).filter(ResearchMemberModel.project_id == project_id,ResearchMemberModel.user_id == current_user.id).first()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ban khong phai thanh vien project")
    return project


def require_project_owner(project_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)) -> ResearchProjectModel:
    project = get_project_or_404(project_id, db)
    if project.owner_id != current_user.id:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ owner mới được phép thao tác")
    return project

def create_project(data: ResearchProjectCreate, db: Session, current_user: UserModel) -> ResearchProjectModel:
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tên project không được để trống")
    project = ResearchProjectModel(name=name, description=data.description, owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    log_project_activity(db, project.id, current_user.id, "CREATE_PROJECT", f"Project '{name}' da duoc tao.")  # type: ignore[arg-type]
    db.commit()
    return project


def list_projects(db: Session, current_user: UserModel, search: str | None = None) -> list[ResearchProjectModel]:
    query = db.query(ResearchProjectModel).outerjoin(ResearchMemberModel,ResearchMemberModel.project_id == ResearchProjectModel.id,)
    query = query.filter(ResearchProjectModel.is_deleted.is_(False),(ResearchProjectModel.owner_id == current_user.id) | (ResearchMemberModel.user_id == current_user.id),)
    if search and search.strip():
        query = query.filter(ResearchProjectModel.name.ilike(f"%{search.strip()}%"))
    return query.order_by(ResearchProjectModel.id).distinct().all()


def list_activity_logs(db: Session, project_id: int, user_id: int | None = None) -> list[ResearchActivityLogModel]:
    # Trả về lịch sử hoạt động của project theo thời gian giảm dần để dễ theo dõi.
    query = db.query(ResearchActivityLogModel).filter(ResearchActivityLogModel.project_id == project_id)
    if user_id is not None:
        query = query.filter(ResearchActivityLogModel.user_id == user_id)
    return query.order_by(ResearchActivityLogModel.created_at.desc()).all()


def update_project(data: ResearchProjectUpdate, project: ResearchProjectModel, db: Session) -> ResearchProjectModel:
    values = data.model_dump(exclude_unset=True)
    if "name" in values:
        name = values["name"].strip()
        if not name:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ten project khong duoc de trong")
        values["name"] = name
    for field, value in values.items():
        setattr(project, field, value)
    log_project_activity(db, project.id, project.owner_id, "UPDATE_PROJECT", "Project da duoc cap nhat.")  # type: ignore[arg-type]
    db.commit()
    db.refresh(project)
    return project


def delete_project(project: ResearchProjectModel, db: Session) -> None:
    # Xóa mềm: không xóa hẳn row, chỉ đánh dấu deleted và ẩn khỏi giao diện mặc định.
    if project.is_deleted:  # type: ignore[truthy-function]
        return
    project.is_deleted = True  # type: ignore[assignment]
    project.deleted_at = datetime.now()  # type: ignore[assignment]
    log_project_activity(db, project.id, project.owner_id, "DELETE_PROJECT", "Project da duoc xoa mem.")  # type: ignore[arg-type]
    db.commit()


def list_members(project: ResearchProjectModel) -> list[ResearchMemberModel]:
    return project.members


def add_member(data: ResearchMemberCreate, project: ResearchProjectModel, db: Session) -> ResearchMemberModel:
    if data.user_id == project.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner da thuoc project")
    if db.get(UserModel, data.user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay user")
    existing = db.query(ResearchMemberModel).filter(ResearchMemberModel.project_id == project.id,ResearchMemberModel.user_id == data.user_id,).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User da la thanh vien project")
    member = ResearchMemberModel(project_id=project.id, user_id=data.user_id, role=data.role.value)
    db.add(member)
    db.commit()
    db.refresh(member)
    log_project_activity(db, project.id, project.owner_id, "ADD_MEMBER", f"Them user {data.user_id} vao project.")  # type: ignore[arg-type]
    db.commit()
    return member


def remove_member(user_id: int, project: ResearchProjectModel, db: Session) -> None:
    if user_id == project.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Khong duoc xoa owner khoi project")
    member = db.query(ResearchMemberModel).filter(
        ResearchMemberModel.project_id == project.id,
        ResearchMemberModel.user_id == user_id,
    ).first()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay thanh vien")
    db.delete(member)
    log_project_activity(db, project.id, project.owner_id, "REMOVE_MEMBER", f"Xoa user {user_id} khoi project.")  # type: ignore[arg-type]
    db.commit()
