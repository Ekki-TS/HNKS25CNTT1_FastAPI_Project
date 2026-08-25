from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.users import User
from app.schemas.research_project import MemberAdd, MemberResponse, ProjectResponse, ResearchProjectTitleCreate, ResearchProjectTitleUpdate
from app.services import research_project as project_service

router = APIRouter(tags=["Research Projects"])

@router.post("/research-projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ResearchProjectTitleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.create_project(db, project_in, current_user)


@router.get("/research-projects", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.list_projects(db, current_user)


@router.get("/research-projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.get_project(db, project_id, current_user)


@router.patch("/research-projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_in: ResearchProjectTitleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.update_project(db, project_id, project_in, current_user)


@router.delete("/research-projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_service.delete_project(db, project_id, current_user)


@router.get("/research-projects/{project_id}/members", response_model=List[MemberResponse])
def list_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.list_members(db, project_id, current_user)


@router.post("/research-projects/{project_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: int,
    member_in: MemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.add_member(db, project_id, member_in, current_user)


@router.delete("/research-projects/{project_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_service.remove_member(db, project_id, member_id, current_user)
