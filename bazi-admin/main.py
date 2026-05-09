from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.database import init_db, close_db, engine
from src.core.redis import init_redis, close_redis
from src.routers import archive_router, fortune_router, ai_router
from src.routers.auth import router as auth_router
from src.routers.upload import router as upload_router

# 导入管理后台
from sqladmin import Admin
from src.admin import UserAdmin, ArchiveAdmin, RecordAdmin, AdminAuth
from src.admin.views import SMSMonitorView


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库和 Redis，关闭时清理资源
    """
    # 启动时执行
    print("🚀 正在启动应用...")
    try:
        await init_db()
        print("✅ 数据库初始化完成")
    except Exception as e:
        print(f"⚠️ 数据库初始化失败: {e}")
    
    try:
        await init_redis()
        print("✅ Redis 初始化完成")
    except Exception as e:
        print(f"⚠️ Redis 初始化失败: {e}")
    
    yield
    
    # 关闭时执行
    print("🛑 正在关闭应用...")
    await close_db()
    await close_redis()


# 创建 FastAPI 应用实例
app = FastAPI(
    title="八字后端服务",
    description="基于 FastAPI 的八字应用后端 API",
    version="1.0.0",
    lifespan=lifespan
)


# 配置 CORS 跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载静态文件目录
# 前端可以通过 http://localhost:9000/static/xxx.png 访问静态资源
app.mount("/static", StaticFiles(directory="static"), name="static")



authentication_backend = AdminAuth(secret_key=os.getenv("SECRET_KEY_ADMIN", "a-very-secret-key"))

# 挂载后台，增加中文标题栏
admin = Admin(
    app,
    engine,
    authentication_backend=authentication_backend,
    title="云水禅心 · 管理后台",
    base_url="/admin",
    templates_dir="src/admin/templates", # 开启模板目录
)

# 注册管理后台视图
admin.add_view(UserAdmin)
admin.add_view(ArchiveAdmin)
admin.add_view(RecordAdmin)

# 注册开发工具
admin.add_view(SMSMonitorView)

print("✅ 管理后台已挂载到 /admin")

# 注册路由
app.include_router(auth_router)      # 认证路由
app.include_router(upload_router)    # 文件上传路由
app.include_router(archive_router)
app.include_router(fortune_router)
app.include_router(ai_router)


# ==================== 数据模型 ====================

class BaziAnalyzeRequest(BaseModel):
    """八字分析请求模型"""
    bazi_string: str  # 八字字符串，例如：'甲子 乙丑 丙寅 丁卯'
    
    class Config:
        json_schema_extra = {
            "example": {
                "bazi_string": "甲子 乙丑 丙寅 丁卯"
            }
        }


class BaziAnalyzeResponse(BaseModel):
    """八字分析响应模型"""
    success: bool
    bazi_string: str
    analysis: str
    message: str


# ==================== 路由接口 ====================

# 健康检查接口
@app.get("/api/health")
async def health_check():
    """
    健康检查接口
    返回服务运行状态
    """
    return {
        "status": "ok",
        "message": "Python 后端服务运行正常"
    }


# 根路径接口
@app.get("/")
async def root():
    """
    根路径接口
    返回欢迎信息
    """
    return {
        "message": "欢迎使用八字后端服务",
        "docs": "/docs",  # Swagger 文档地址
        "health": "/api/health"  # 健康检查地址
    }


# 八字分析接口
@app.post("/api/analyze", response_model=BaziAnalyzeResponse)
async def analyze_bazi(request: BaziAnalyzeRequest):
    """
    八字深度分析接口
    
    接收前端传来的八字字符串，调用 AI 大模型生成深度解析报告
    
    Args:
        request: 包含八字字符串的请求体
        
    Returns:
        包含分析结果的响应
    """
    try:
        bazi_string = request.bazi_string
        
        # TODO: 这里预留调用大模型的代码位置
        # 未来将在此处：
        # 1. 使用 lunar-python 库解析八字
        # 2. 调用 AI 大模型（如 OpenAI、Claude 等）生成深度分析
        # 3. 返回详细的八字解析报告
        
        # 当前返回 Mock 数据
        mock_analysis = f"""
这是来自 Python 9000 端口的 AI 深度解析模拟数据...

【接收到的八字】
{bazi_string}

【基础信息】
年柱：{bazi_string.split()[0] if len(bazi_string.split()) > 0 else '未知'}
月柱：{bazi_string.split()[1] if len(bazi_string.split()) > 1 else '未知'}
日柱：{bazi_string.split()[2] if len(bazi_string.split()) > 2 else '未知'}
时柱：{bazi_string.split()[3] if len(bazi_string.split()) > 3 else '未知'}

【AI 深度解析】
（此处将接入大模型生成详细分析报告）

- 五行分析
- 格局判断
- 运势走向
- 性格特点
- 事业财运
- 婚姻感情
- 健康建议

【提示】
当前为模拟数据，实际使用时将调用 AI 大模型生成专业的八字解析报告。
        """.strip()
        
        return BaziAnalyzeResponse(
            success=True,
            bazi_string=bazi_string,
            analysis=mock_analysis,
            message="分析完成（当前为模拟数据）"
        )
        
    except Exception as e:
        return BaziAnalyzeResponse(
            success=False,
            bazi_string=request.bazi_string,
            analysis="",
            message=f"分析失败：{str(e)}"
        )

