# Sử dụng Python 3.11/3.12 bản nhẹ nhất
FROM python:3.12-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Khắc phục lỗi in log bị chậm của Python
ENV PYTHONUNBUFFERED=1

# Copy file requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào trong container
COPY . .

# Lệnh khởi chạy server (Lắng nghe mọi IP trên cổng 8000)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
