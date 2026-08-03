import asyncio
import logging

logger = logging.getLogger(__name__)

async def send_task_assignment_email(user_email: str, task_title: str):
    # Giả lập thời gian kết nối tới SMTP Server (Google/SendGrid)
    await asyncio.sleep(2) 
    logger.info(f"Đã gửi email tới {user_email}: Bạn được giao task '{task_title}'")
