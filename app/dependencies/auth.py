from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.user import UserModel

User = UserModel

def require_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    # Kiểm tra đúng giá trị role, tránh cấp quyền cho role gần giống ADMIN.
    if str(current_user.role) != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ Admin mới được phép thực hiện thao tác này")
    return current_user
 