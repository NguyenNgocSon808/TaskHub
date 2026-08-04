import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Cấu hình logging cơ bản
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Ghi nhận thời gian bắt đầu
        start_time = time.time()
        
        # Đẩy request đi tiếp vào các Router xử lý
        response = await call_next(request)
        
        # Tính toán thời gian xử lý xong
        process_time = time.time() - start_time
        
        # Lấy IP của Client
        client_ip = request.client.host if request.client else "Unknown"
        
        # Ghi log ra màn hình console
        logger.info(f"[{request.method}] {request.url.path} - IP: {client_ip} - Time: {process_time:.4f}s")
        
        # Đính kèm thời gian xử lý vào Header của Response trả về cho Client
        response.headers["X-Process-Time"] = str(process_time)
        return response
