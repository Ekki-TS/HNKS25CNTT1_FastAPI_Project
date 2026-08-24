from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import UserModel

# Hàm trả về một danh sách các obj usermodel từ sqlalchemy 
def list_users(db: Session,search: Optional[str] = None,is_active: Optional[bool] = None) -> list[UserModel]:
    query = db.query(UserModel).order_by(UserModel.id)
    if search:
        find = f"%{search}%"
        query = query.filter(
            UserModel.email.ilike(find) | UserModel.full_name.ilike(find)
        )
    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)
    return query.all()
    