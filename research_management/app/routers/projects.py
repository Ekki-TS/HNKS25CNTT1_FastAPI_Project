from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
 
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.project import ResearchProjectModel
from app.models.user import UserModel
from app.schemas.research_project import (ResearchMemberCreate, ResearchMemberResponse, ResearchProjectCreate, ResearchProjectResponse, ResearchProjectUpdate)
from app.schemas.research_task import ResearchTaskBase, TaskListResponse, TaskPriority, TaskStatus
from app.schemas.user import MessageResponse
from app.services.project_services import (add_member, create_project, delete_project, list_activity_logs, list_members, list_projects, remove_member, require_project_member, require_project_owner, update_project)
from app.services.task_services import create_task, list_tasks

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Tạo dự án")
def create_project_(data: ResearchProjectCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Tạo project mới - trả về message thành công"""
    project = create_project(data, db, current_user)
    return MessageResponse(
        message=f"Tạo project '{project.name}' thành công",
        success=True,
        data={"project_id": project.id, "project_name": project.name}
    )


@router.get("", response_model=list[ResearchProjectResponse], summary="Tất cả danh sách dự án")
def list_projects_(search: str | None = Query(default=None), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Lấy danh sách projects của user"""
    return list_projects(db, current_user, search)


@router.get("/{project_id}", response_model=ResearchProjectResponse, summary="Danh sách dự án theo id")
def get_project(project: ResearchProjectModel = Depends(require_project_member)):
    """Lấy thông tin chi tiết project"""
    return project


@router.put("/{project_id}", response_model=MessageResponse, summary="Cập nhật dự án")
@router.patch("/{project_id}", response_model=MessageResponse, summary="Cập nhật dự án")
def update_project_(data: ResearchProjectUpdate, project: ResearchProjectModel = Depends(require_project_owner), db: Session = Depends(get_db)):
    """Cập nhật project - trả về message thành công"""
    updated_project = update_project(data, project, db)
    return MessageResponse(
        message=f"Cập nhật project '{updated_project.name}' thành công",
        success=True,
        data={"project_id": updated_project.id, "project_name": updated_project.name}
    )


@router.delete("/{project_id}", response_model=MessageResponse, summary="Xóa dự án") 
def delete_project_(project: ResearchProjectModel = Depends(require_project_owner), db: Session = Depends(get_db)):
    """Xóa project (soft delete) - trả về message thành công"""
    project_name = project.name
    delete_project(project, db)
    return MessageResponse(
        message=f"Xóa project '{project_name}' thành công",
        success=True,
        data={"project_id": project.id}
    )


@router.get("/{project_id}/members", response_model=list[ResearchMemberResponse], summary="Danh sách thành viên trong dự án")
def list_members_(project: ResearchProjectModel = Depends(require_project_member)):
    """Lấy danh sách thành viên dự án"""
    return list_members(project)


@router.post("/{project_id}/members", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Thêm thành viên vào dự án")
def add_member_(data: ResearchMemberCreate, project: ResearchProjectModel = Depends(require_project_owner), db: Session = Depends(get_db)):
    """Thêm thành viên vào dự án - trả về message thành công"""
    member = add_member(data, project, db)
    return MessageResponse(
        message=f"Thêm thành viên vào project '{project.name}' thành công",
        success=True,
        data={"user_id": member.user_id, "project_id": member.project_id}
    )


@router.delete("/{project_id}/members/{user_id}", response_model=MessageResponse, summary="Xóa thành viên khỏi dự án")
def remove_member_(user_id: int, project: ResearchProjectModel = Depends(require_project_owner), db: Session = Depends(get_db)):
    """Xóa thành viên khỏi dự án - trả về message thành công"""
    remove_member(user_id, project, db)
    return MessageResponse(
        message=f"Xóa thành viên khỏi project '{project.name}' thành công",
        success=True,
        data={"user_id": user_id, "project_id": project.id}
    )


@router.get("/{project_id}/activity-logs", summary="Log hoạt động")
def get_project_activity_logs(project: ResearchProjectModel = Depends(require_project_member), db: Session = Depends(get_db)):
    """Lấy lịch sử hoạt động của project"""
    return list_activity_logs(db, project.id)


@router.post("/{project_id}/tasks", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Tạo nhiệm vụ cho dự án")
def create_project_task(project_id: int,data: ResearchTaskBase,project: ResearchProjectModel = Depends(require_project_member),db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    """Tạo task mới trong project - chỉ thành viên project mới được tạo - trả về message thành công"""
    task = create_task(project_id, data, current_user, db)
    return MessageResponse(
        message=f"Tạo task '{task.title}' thành công",
        success=True,
        data={"task_id": task.id, "task_title": task.title}
    )


@router.get("/{project_id}/tasks", response_model=TaskListResponse, summary="Danh sách task có filter và phân trang")
def get_project_tasks(project_id: int,status: TaskStatus | None = Query(None, description="Filter theo status"),priority: TaskPriority | None = Query(None, description="Filter theo priority"),assignee_id: int | None = Query(None, description="Filter theo assignee_id"),search: str | None = Query(None, description="Tìm kiếm theo title"),sort_by: Literal["created_at", "due_date"] = Query("created_at", description="Sort field"),sort_order: Literal["asc", "desc"] = Query("asc", description="Sort order"),limit: int = Query(10, ge=1, le=100, description="Số item trên một trang"),offset: int = Query(0, ge=0, description="Số item bỏ qua"),project: ResearchProjectModel = Depends(require_project_member),db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    """Lấy danh sách task của project với filter, search, và pagination"""
    tasks, total = list_tasks(
        project_id=project_id,
        current_user=current_user,
        db=db,
        task_status=status,
        priority=priority,
        assignee_id=assignee_id,
        search_title=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    
    return {
        "items": tasks,
        "total": total,
        "limit": limit,
        "offset": offset,
        "page": offset // limit + 1 if limit > 0 else 1,
    }