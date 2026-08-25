from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.research_project import ResearchMember, ResearchProject
from app.models.users import User
from app.schemas.research_project import MemberAdd, ResearchProjectTitleCreate, ResearchProjectTitleUpdate


def get_project_or_404(db: Session, project_id: int) -> ResearchProject:
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if project is None:
        raise NotFoundException("Không tìm thấy đề tài")
    return project


def get_membership(db: Session, project_id: int, user_id: int) -> ResearchMember | None:
    return (
        db.query(ResearchMember)
        .filter(
            ResearchMember.project_id == project_id,
            ResearchMember.user_id == user_id,
        )
        .first()
    )


def require_owner(db: Session, project_id: int, user: User) -> ResearchProject:
    project = get_project_or_404(db, project_id)
    membership = get_membership(db, project_id, user.id)
    if membership is None or membership.role != "OWNER":
        raise ForbiddenException("Chỉ OWNER mới có quyền thực hiện hành động này")
    return project


def create_project(db: Session, project_in: ResearchProjectTitleCreate, user: User) -> ResearchProject:
    project = ResearchProject(
        title=project_in.title,
        description=project_in.description,
        owner_id=user.id,
    )
    db.add(project)
    db.flush()
    db.add(ResearchMember(project_id=project.id, user_id=user.id, role="OWNER"))
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session, user: User) -> List[ResearchProject]:
    return (
        db.query(ResearchProject)
        .join(ResearchMember, ResearchMember.project_id == ResearchProject.id)
        .filter(ResearchMember.user_id == user.id)
        .all()
    )


def get_project(db: Session, project_id: int, user: User) -> ResearchProject:
    project = get_project_or_404(db, project_id)
    if get_membership(db, project_id, user.id) is None:
        raise ForbiddenException("Bạn không phải thành viên của đề tài")
    return project


def update_project(
    db: Session,
    project_id: int,
    project_in: ResearchProjectTitleUpdate,
    user: User,
) -> ResearchProject:
    project = require_owner(db, project_id, user)
    for field, value in project_in.model_dump(include=project_in.model_fields_set).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int, user: User) -> None:
    project = require_owner(db, project_id, user)
    db.delete(project)
    db.commit()


def list_members(db: Session, project_id: int, user: User) -> List[ResearchMember]:
    get_project(db, project_id, user)
    return db.query(ResearchMember).filter(ResearchMember.project_id == project_id).all()


def add_member(
    db: Session,
    project_id: int,
    member_in: MemberAdd,
    user: User,
) -> ResearchMember:
    require_owner(db, project_id, user)
    member = db.query(User).filter(User.id == member_in.user_id).first()
    if member is None:
        raise NotFoundException("Không tìm thấy người dùng")
    if get_membership(db, project_id, member_in.user_id) is not None:
        raise BadRequestException("Người dùng đã là thành viên của đề tài")

    membership = ResearchMember(
        project_id=project_id,
        user_id=member_in.user_id,
        role="MEMBER",
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def remove_member(db: Session, project_id: int, member_id: int, user: User) -> None:
    require_owner(db, project_id, user)
    membership = get_membership(db, project_id, member_id)
    if membership is None:
        raise NotFoundException("Người dùng không thuộc đề tài này")
    if membership.role == "OWNER":
        raise BadRequestException("Không thể xóa OWNER cuối cùng của đề tài")
    db.delete(membership)
    db.commit()
