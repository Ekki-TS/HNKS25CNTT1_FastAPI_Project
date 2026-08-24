from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.dependencies.auth import require_admin
from app.models.user import UserModel
from app.schemas.user import UserResponse
from app.services.user_service import list_users as list_users_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.get("", response_model=list[UserResponse], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db),search: str | None = Query(default=None),is_active: bool | None = None,):
    return list_users_service(db, search=search, is_active=is_active)
  