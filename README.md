# TaskHub API System

TaskHub là một hệ thống quản lý công việc và phân quyền nâng cao, được thiết kế theo tiêu chuẩn Production-Ready với mô hình **Layered Architecture** (Routers $\rightarrow$ Services $\rightarrow$ Repositories). Hệ thống được tối ưu hóa cho môi trường chịu tải cao nhờ tích hợp Redis Caching, FastAPI Background Tasks và triển khai đồng bộ qua Docker.

---

## Tính Năng Chính
1. **Authentication (Xác thực)**:
   - Đăng ký và đăng nhập bảo mật (mật khẩu băm với Passlib).
   - JWT (JSON Web Tokens) cho phân quyền Access/Refresh Tokens.
2. **Workspaces & Projects (Không gian & Dự án)**:
   - Quản lý Workspace với RBAC (Role-Based Access Control): `OWNER`, `EDITOR`, `VIEWER`.
   - Quản lý Projects thuộc Workspace và phân quyền thao tác chi tiết.
3. **Tasks (Công việc)**:
   - CRUD thao tác với công việc.
   - Filter mạnh mẽ ngay trên Database (Lọc theo Status, Priority, Assignee).
   - Tối ưu hóa hiệu năng **(Redis Caching)** giúp API đạt tốc độ truy xuất siêu tốc (~2ms/request).
   - Xóa Cache tự động (Cache Invalidation) khi dữ liệu cập nhật.
4. **Performance & Monitoring**:
   - Background Tasks cho các luồng mất thời gian (ví dụ: Gửi Email).
   - Middleware ghi nhận và trả về Header `X-Process-Time` đo đạc tốc độ API, đồng thời ghi log IP của client.
5. **Chất lượng Mã nguồn**:
   - Type-hinted hoàn hảo (Zero `mypy` errors).
   - PEP-8 format chặt chẽ (Zero `ruff` issues).

---

## Yêu Cầu Hệ Thống
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Hỗ trợ tốt nhất)
- Python 3.10+ (Nếu bạn muốn chạy server trực tiếp không qua Docker)
- PostgreSQL & Redis (Nếu chạy trực tiếp)

---

## Cấu Hình Môi Trường (.env)
Tại thư mục `backend`, hãy tạo một file tên là `.env` với nội dung sau:
```env
PROJECT_NAME="TaskHub API"
ENVIRONMENT="development"
API_V1_STR="/api/v1"
SECRET_KEY="cuc-ky-bao-mat-hay-doi-chuoi-nay-trong-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

DATABASE_URL="postgresql+asyncpg://postgres:123456@db:5432/taskhub"
REDIS_URL="redis://redis:6379/0"
```
*(Lưu ý: Nếu bạn không chạy qua Docker, hãy thay đổi `db:5432` thành `localhost:5432` và `redis:6379` thành `localhost:6379`)*

---

## Triển Khai Nhanh bằng Docker
Đây là phương thức được khuyến nghị để có được môi trường đồng nhất và ổn định.

Mở Terminal tại thư mục `backend` và chạy:
```bash
docker-compose up -d --build
```
Hệ thống sẽ tự động build image và khởi động 3 container:
1. **db**: PostgreSQL Server
2. **redis**: Redis Cache Server
3. **api**: FastAPI Application Server (Cổng 8000)

---

## Khởi Chạy Tự Hướng (Chạy trực tiếp)
Nếu máy bạn chưa có Docker, bạn có thể thiết lập ảo hóa Python:
```bash
python -m venv .venv
# Window: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt
```
(Hãy chắc chắn rằng máy bạn đang chạy PostgreSQL và Redis).

Sau đó, khởi chạy server:
```bash
uvicorn app.main:app --reload
```

---

## Sử Dụng Hệ Thống & Tài liệu Swagger UI
Một khi hệ thống (Docker hoặc Uvicorn) đã báo sẵn sàng, hãy mở trình duyệt và truy cập:

- **Tài liệu API (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Tài liệu ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Kịch Bản E2E Khuyên Dùng
1. Truy cập Swagger UI.
2. Tìm thẻ `Authentication` và dùng API `POST /api/v1/auth/register` để tạo tài khoản.
3. Kéo lên góc trên bên phải trang Swagger, bấm nút **Authorize**, nhập `username` (email vừa tạo) và `password` để nhận Token.
4. Gọi API tạo Workspace trong thẻ `Workspaces`.
5. Tạo một Project trong Workspace đó.
6. Thử gọi API tạo Task trong thẻ `Tasks` (Hãy chú ý xem Log hệ thống báo Background task "Sending email" chạy ngầm ra sao).
7. Tận hưởng việc Refresh API Fetch Tasks và chứng kiến sự vi diệu của Redis Caching ở tốc độ 2ms!

---
*Dự án TaskHub - Chuẩn mực Backend Engineering.*
