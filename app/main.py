from fastapi import FastAPI

from app.core.config import register_exception_handlers
from app.db.database import Base, engine
from app.models import project, task, user
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.projects import router as project_router
from app.routers.tasks import router as tasks_router

# Import model trước để SQLAlchemy biết toàn bộ bảng khi tạo metadata.
Base.metadata.create_all(bind=engine)

app = FastAPI()

register_exception_handlers(app)
# Đăng ký các router theo từng nhóm chức năng.
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(project_router)
app.include_router(tasks_router)


@app.get("/health", tags=["health-check"])
def health_check():
    return {"status": "ok"}