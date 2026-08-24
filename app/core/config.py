import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.core.exceptions import register_exception_handlers

load_dotenv()

# Đọc cấu hình từ .env để không ghi thông tin nhạy cảm trực tiếp trong code.
DATABASE_URL: str = os.getenv("DATABASE_URL", "")
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

