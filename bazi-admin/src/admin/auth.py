import os
from typing import Optional
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from dotenv import load_dotenv

load_dotenv()

class AdminAuth(AuthenticationBackend):
    """
    管理后台标准认证后端
    """
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "123456")
        
        # 1. 验证密码
        if username == admin_username and password == admin_password:
            # 2. 登录成功，颁发统一的钥匙 "admin_user"
            request.session.update({"admin_user": username})
            print(f"✅ 管理员登录成功: {username}")
            return True
            
        print(f"❌ 管理员登录失败: {username}")
        return False
    
    async def logout(self, request: Request) -> bool:
        # 清除所有会话
        request.session.clear()
        print("✅ 管理员已登出")
        return True
    
    async def authenticate(self, request: Request) -> bool:
        """
        这里必须返回 bool 值！True代表放行，False代表踢回登录页。
        """
        # 3. 检查有没有 "admin_user" 这把钥匙
        user = request.session.get("admin_user")
        if not user:
            return False
            
        return True