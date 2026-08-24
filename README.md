# Research Management API

API quản lý người dùng, project nghiên cứu và task được xây dựng bằng FastAPI, SQLAlchemy và MySQL.

## Yêu cầu

- Python 3.10 trở lên
- MySQL 8 trở lên (hoặc MariaDB tương thích)

## Cài đặt

Mở terminal tại thư mục gốc của project:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Nếu PowerShell không cho phép kích hoạt môi trường ảo, chạy lệnh sau một lần trong PowerShell hiện tại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Tạo database MySQL, ví dụ:

```sql
CREATE DATABASE research_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Tạo file `.env` ở thư mục gốc:

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/research_management
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Thay `root`, `your_password` và các giá trị cấu hình cho phù hợp với máy local. Không commit file `.env` hoặc secret thật lên repository.

## Chạy ứng dụng

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

API chạy tại <http://127.0.0.1:8000>.

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Health check: <http://127.0.0.1:8000/health>

Khi ứng dụng khởi động, các bảng được tạo tự động qua `Base.metadata.create_all`. Database phải tồn tại trước khi chạy ứng dụng.

## Demo nhanh

Các lệnh dưới đây chạy trong PowerShell. Lưu token từ response đăng nhập vào biến `$token`:

### 1. Kiểm tra health check

```powershell
curl.exe http://127.0.0.1:8000/health
```

### 2. Đăng ký tài khoản

```powershell
curl.exe -X POST http://127.0.0.1:8000/auth/register `
	-H "Content-Type: application/json" `
	-d '{"email":"demo@example.com","full_name":"Demo User","password":"password123"}'
```

### 3. Đăng nhập lấy JWT

```powershell
$login = curl.exe -s -X POST http://127.0.0.1:8000/auth/login `
	-H "Content-Type: application/json" `
	-d '{"email":"demo@example.com","password":"password123"}' | ConvertFrom-Json
$token = $login.access_token
```

### 4. Tạo project

```powershell
$project = curl.exe -s -X POST http://127.0.0.1:8000/projects `
	-H "Authorization: Bearer $token" `
	-H "Content-Type: application/json" `
	-d '{"name":"Nghiên cứu FastAPI","description":"Project demo"}' | ConvertFrom-Json
$projectId = $project.id
```

### 5. Tạo task trong project

```powershell
curl.exe -X POST "http://127.0.0.1:8000/projects/$projectId/tasks" `
	-H "Authorization: Bearer $token" `
	-H "Content-Type: application/json" `
	-d '{"title":"Viết tài liệu API","description":"Bổ sung README và Swagger","status":"TODO","priority":"HIGH"}'
```

### 6. Xem danh sách project và task

```powershell
curl.exe -H "Authorization: Bearer $token" http://127.0.0.1:8000/projects
curl.exe -H "Authorization: Bearer $token" "http://127.0.0.1:8000/projects/$projectId/tasks"
```

## Các nhóm endpoint chính

| Nhóm | Endpoint tiêu biểu | Yêu cầu xác thực |
| --- | --- | --- |
| Health | `GET /health` | Không |
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` | Tùy endpoint |
| Users | `/users` | JWT, một số thao tác cần quyền phù hợp |
| Projects | `/projects` | JWT |
| Tasks | `/projects/{project_id}/tasks` | JWT và thành viên project |

Có thể xem đầy đủ schema request/response và thử API trực tiếp trên Swagger UI tại `/docs`.

## Chạy kiểm tra

```powershell
pytest
```
