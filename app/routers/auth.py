from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import UserModel
from app.schemas.user import LoginRequest, MessageResponse, Token, UserCreate, UserResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["AuthN"])

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Đăng ký tài khoản mới - trả về message thành công với id"""
    user_info = register_user(data, db)
    return MessageResponse(
        message=f"Bạn đã tạo tài khoản thành công với id là {user_info['user_id']}",
        success=True,
        data={
            "user_id": user_info['user_id'],
            "email": user_info['email'],
            "full_name": user_info['full_name']
        }
    )


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Đăng nhập - trả về access token"""
    return login_user(data, db)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    """Lấy thông tin người dùng hiện tại"""
    return current_user

