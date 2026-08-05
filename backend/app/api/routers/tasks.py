import json

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db_session
from app.core.redis import redis_client
from app.models.schema import TaskPriority, TaskStatus, User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.email_service import send_task_assignment_email
from app.services.task_service import TaskService

router = APIRouter(tags=["Tasks"])

def get_task_service(session: AsyncSession = Depends(get_db_session)) -> TaskService:
    return TaskService(session)

# Endpoint lấy danh sách Task có phân trang và lọc
@router.get("/projects/{project_id}/tasks")
async def get_tasks_in_project(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee_id: int | None = None,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    # 1. Tạo khóa (key) định danh cho cache này
    cache_key = f"cache:project:{project_id}:tasks:skip:{skip}:limit:{limit}:status:{status}:priority:{priority}:assignee:{assignee_id}"
    
    # 2. Kiểm tra xem trong Redis có data chưa
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data) # Nếu có, trả về ngay lập tức, bỏ qua DB

    # 3. Nếu chưa có (Cache miss), lấy từ Database
    tasks = await service.get_tasks(project_id, skip, limit, status, priority, assignee_id)
    
    # 4. Chuyển list object thành dict để lưu vào JSON
    # Dùng model_dump() của Pydantic để serialize dữ liệu (datetime sẽ tự thành chuỗi ISO)
    task_dicts = [TaskResponse.model_validate(task).model_dump(mode='json') for task in tasks]
    
    # 5. Lưu vào Redis, cấu hình tự động xóa sau 5 phút (300 giây)
    await redis_client.set(cache_key, json.dumps(task_dicts), ex=300)
    
    return tasks

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    project_id: int,
    data: TaskCreate,
    background_tasks: BackgroundTasks, # Inject BackgroundTasks vào đây
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    new_task = await service.create_task(current_user, project_id, data)
    
    # Nếu có người được gán, đẩy việc gửi email vào hàng đợi nền
    if new_task.assignee_id:
        # Trong thực tế, bạn cần query lấy email của assignee_id này
        fake_email = f"user_{new_task.assignee_id}@taskhub.local" 
        background_tasks.add_task(send_task_assignment_email, fake_email, new_task.title)
    
    # Xóa cache cũ của project này để lần tới gọi GET sẽ có data mới nhất
    # Dùng pattern matching để xóa toàn bộ phân trang của project này
    keys_to_delete = await redis_client.keys(f"cache:project:{project_id}:tasks:*")
    if keys_to_delete:
        await redis_client.delete(*keys_to_delete)

    return new_task

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    # Khi update task cũng cần xóa cache tương tự. Tuy nhiên, chúng ta chỉ có task_id.
    # Trong thực tế, bạn cần lấy project_id từ task hiện tại trước khi xóa cache.
    # Đoạn này giản lược việc lấy project_id.
    task = await service.update_task(task_id, data)
    
    # Xóa cache
    keys_to_delete = await redis_client.keys(f"cache:project:{task.project_id}:tasks:*")
    if keys_to_delete:
        await redis_client.delete(*keys_to_delete)
        
    return task

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    # Tương tự cho delete
    # Cần query project_id của task trước khi xóa (hoặc dùng cache pattern khác)
    # Ở đây chúng ta chỉ gọi service
    return await service.delete_task(task_id)
