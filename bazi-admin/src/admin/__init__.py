"""
管理后台模块
"""
from src.admin.views import UserAdmin, ArchiveAdmin, RecordAdmin
from src.admin.auth import AdminAuth

__all__ = ['UserAdmin', 'ArchiveAdmin', 'RecordAdmin', 'AdminAuth']
