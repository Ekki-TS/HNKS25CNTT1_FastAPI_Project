from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import UserModel
from app.schemas.user import LoginRequest, Token, UserCreate

# hàm đăng ký tài khoản trả về dict với id 
def register_user(data: UserCreate, db: Session) -> dict:
    existing_user = db.query(UserModel).filter(UserModel.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email đã được đăng ký")

    user = UserModel(
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Trả về dict chứa id và message
    return {
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name
    }


def login_user(data: LoginRequest, db: Session) -> Token:
    user = db.query(UserModel).filter(UserModel.email == data.email).first()
    if user is None or not verify_password(data.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not bool(user.is_active):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản đã bị khóa")

    return Token(access_token=create_access_token(str(user.id)))
