import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

load_dotenv()

# Đọc cấu hình từ .env để không ghi thông tin nhạy cảm trực tiếp trong code.
DATABASE_URL: str = os.getenv("DATABASE_URL", "")
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

class AppException(Exception):
    def __init__(self, status_code: int, message: str, error_code: str = "APP_ERROR"):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code

class NotFoundException(AppException):
    def __init__(self, message: str = "Không tìm thấy dữ liệu"):
        super().__init__(status.HTTP_404_NOT_FOUND, message, "NOT_FOUND")

class BadRequestException(AppException):
    def __init__(self, message: str = "Yêu cầu không hợp lệ"):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, "BAD_REQUEST")

class ForbiddenException(AppException):
    def __init__(self, message: str = "Bạn không có quyền thực hiện hành động này"):
        super().__init__(status.HTTP_403_FORBIDDEN, message, "FORBIDDEN")


def register_exception_handlers(app: FastAPI) -> None:
    # Chuẩn hóa lỗi về cùng một cấu trúc JSON để client dễ xử lý.
    @app.exception_handler(AppException)
    def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": "HTTP_ERROR",
                "message": str(exc.detail),
            },
        )

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Dữ liệu gửi lên không hợp lệ",
            },
        )

    @app.exception_handler(Exception)
    def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "Đã có lỗi xảy ra, vui lòng thử lại sau",
            },
        )
