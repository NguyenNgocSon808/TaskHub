from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import auth, tasks, users, workspaces
from app.core.config import settings
from app.core.database import sessionmanager
from app.core.middleware import LogProcessTimeMiddleware

# 1. Khai báo Metadata cho Swagger UI
tags_metadata = [
    {"name": "Authentication", "description": "APIs cấp phát và xác thực JWT Token."},
    {"name": "Users", "description": "Quản lý thông tin cá nhân của người dùng."},
    {"name": "Workspaces", "description": "Quản lý không gian làm việc và phân quyền RBAC."},
    {"name": "Tasks", "description": "Quản lý công việc, bộ lọc và phân trang."}
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()

app = FastAPI(
    title="TaskHub API System",
    description="Hệ thống lõi quản lý công việc và phân quyền cho dự án TaskHub.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 2. Đăng ký Middleware
app.add_middleware(LogProcessTimeMiddleware)

# 3. Đăng ký các Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(workspaces.router, prefix=settings.API_V1_STR)
app.include_router(tasks.router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "Welcome to TaskHub API", "status": "Healthy"}
