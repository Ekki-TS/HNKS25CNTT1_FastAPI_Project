from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.db.database import get_db
from app.models.user import UserModel

# Đọc Bearer token từ header Authorization; tắt lỗi tự động để get_current_user tự xử lý phản hồi 401.
bearer_scheme = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
	# Không lưu mật khẩu gốc; chỉ lưu chuỗi đã được bcrypt băm.
	return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
	return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(subject: str) -> str:
	# sub định danh user; exp buộc token tự hết hạn theo cấu hình.
	expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	payload = {"sub": subject, "exp": expires_at}
	return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),db: Session = Depends(get_db)) -> UserModel:
	# Xác thực cả token lẫn trạng thái database trước khi cho endpoint sử dụng user.
	if credentials is None or credentials.scheme.lower() != "bearer":
		raise HTTPException(status_code=401, detail="Token không hợp lệ")

	token = credentials.credentials

	try:
		payload = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM],
			options={"verify_exp": True},
		)
		subject = payload.get("sub")
		if not isinstance(subject, str):
			raise ValueError("JWT thiếu user id")
		user_id = int(subject)
	except jwt.ExpiredSignatureError:
		raise HTTPException(status_code=401, detail="Token đã hết hạn")
	except (jwt.InvalidTokenError, TypeError, ValueError):
		raise HTTPException(status_code=401, detail="Token không hợp lệ")

	user = db.get(UserModel, user_id)
	if user is None or not bool(getattr(user, "is_active", False)):
		raise HTTPException(status_code=401, detail="Tài khoản không tồn tại hoặc đã bị khóa")

	return user
 