"""
Routers 包初始化文件
统一导出所有路由
"""
from src.routers.archive import router as archive_router
from src.routers.fortune import router as fortune_router

__all__ = ["archive_router", "fortune_router"]
