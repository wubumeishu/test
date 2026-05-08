from sqladmin import ModelView
from src.models.user import User
from src.models.archive import Archive
from src.models.record import Record
from src.core.security import get_password_hash
from src.core import redis as redis_module


class UserAdmin(ModelView, model=User):
    # --- 基础与菜单配置 ---
    name = "用户"
    name_plural = "用户管理"
    icon = "fa-solid fa-users"
    category = "用户生态"
    
    # --- 模板配置 ---
    list_template = "custom_list.html"
    create_template = "custom_create.html"
    edit_template = "custom_edit.html"
    
    # --- 权限与功能 ---
    can_export = True
    can_delete = False  # 安全起见，禁止直接删除用户
    page_size = 50
    
    # --- 字段汉化映射 ---
    column_labels = {
        User.user_id: "用户标识(ID)",
        User.phone: "手机号码",
        User.nickname: "用户昵称",
        User.avatar_url: "头像链接",
        User.hashed_password: "登录密码",
        User.wechat_unionid: "微信UnionID",
        User.created_at: "注册时间",
        User.updated_at: "更新时间",
        User.last_login: "最近登录"
    }
    
    # --- 视图控制 ---
    column_list = [User.phone, User.nickname, User.created_at, User.last_login]
    column_details_list = [User.user_id, User.phone, User.nickname, User.wechat_unionid, User.created_at, User.last_login]
    form_columns = [User.phone, User.nickname, User.avatar_url, User.hashed_password]
    column_searchable_list = [User.phone, User.nickname]
    column_sortable_list = [User.created_at, User.last_login]
    column_default_sort = [(User.created_at, True)]
    
    async def on_model_change(self, data: dict, model: User, is_created: bool, request) -> None:
        """
        在模型保存前自动处理密码加密
        
        安全策略：
        1. 已加密的密码（以 $2 开头）不会重复加密
        2. 空密码不会覆盖原有密码
        3. 密码长度限制由 get_password_hash 内部处理
        """
        if "hashed_password" in data:
            pwd = data["hashed_password"]
            
            # 判断密码是否有效，且没有被 bcrypt 加密过（bcrypt 密文通常以 $2 开头）
            if pwd and not pwd.startswith("$2"):
                # 执行加密存入（get_password_hash 内部会自动处理 72 字节限制）
                data["hashed_password"] = get_password_hash(pwd)
            elif not pwd:
                # 如果管理员清空了密码框，不要覆盖原密码
                data.pop("hashed_password", None)
        
        return await super().on_model_change(data, model, is_created, request)


class ArchiveAdmin(ModelView, model=Archive):
    name = "命理档案"
    name_plural = "档案管理"
    icon = "fa-solid fa-folder-open"
    category = "用户生态"
    
    # --- 模板配置 ---
    list_template = "custom_list.html"
    create_template = "custom_create.html"
    edit_template = "custom_edit.html"
    
    can_export = True
    
    column_labels = {
        Archive.archive_id: "档案ID",
        Archive.user_id: "所属用户",
        Archive.name: "姓名",
        Archive.gender: "性别",
        Archive.birth_year: "出生年",
        Archive.birth_month: "出生月",
        Archive.birth_day: "出生日",
        Archive.birth_hour: "出生时辰",
        Archive.is_default: "默认档案",
        Archive.created_at: "创建时间"
    }
    
    column_list = [Archive.name, Archive.gender, Archive.birth_year, Archive.birth_month, Archive.birth_day, Archive.is_default, Archive.created_at]
    form_columns = [Archive.name, Archive.gender, Archive.birth_year, Archive.birth_month, Archive.birth_day, Archive.birth_hour, Archive.is_default]
    column_searchable_list = [Archive.name]


class RecordAdmin(ModelView, model=Record):
    name = "测算记录"
    name_plural = "测算历史"
    icon = "fa-solid fa-history"
    category = "业务数据"
    
    # --- 模板配置 ---
    list_template = "custom_list.html"
    create_template = "custom_create.html"
    edit_template = "custom_edit.html"
    
    can_create = False  # 历史记录由用户生成，管理员不可伪造
    can_edit = False    # 历史记录不可篡改
    can_delete = False  # 历史记录不可删除
    can_export = True
    

    column_labels = {
        Record.record_id: "记录ID",
        Record.user_id: "测算用户",
        Record.archive_id: "使用档案",
        Record.bazi_str: "八字",
        Record.five_elements_json: "五行分析",
        Record.ai_report_markdown: "AI分析报告",
        Record.is_deep_analysis: "是否精批",
        Record.created_at: "测算时间"
    }
    
    column_list = [Record.record_id, Record.bazi_str, Record.is_deep_analysis, Record.created_at]
    column_details_list = [Record.record_id, Record.user_id, Record.archive_id, Record.bazi_str, Record.five_elements_json, Record.ai_report_markdown, Record.is_deep_analysis, Record.created_at]
    column_sortable_list = [Record.created_at]
    column_default_sort = [(Record.created_at, True)]
    column_searchable_list = [Record.bazi_str]
    
    # 直观展示精批状态
    column_formatters = {
        Record.is_deep_analysis: lambda m, a: "👑 精批" if getattr(m, 'is_deep_analysis', False) else "基础"
    }


# ==================== 开发工具视图 ====================

from sqladmin import BaseView, expose
from starlette.requests import Request
from src.core.redis import redis_client



#虚拟短信接码台
# --- SMSMonitorView 增强版 ---
class SMSMonitorView(BaseView):
    name = "临时接码台"
    icon = "fa-solid fa-mobile-screen"
    category = "开发工具"
    
    @expose("/sms-monitor", methods=["GET"])
    async def monitor_page(self, request: Request):
        codes = []
        
        # 🚀 核心破局点：每次请求都动态获取最新的 redis 客户端！
        client = getattr(redis_module, 'redis_client', None)
        
        if client:
            try:
                search_pattern = "login_code:*"
                keys = await client.keys(search_pattern)
                
                # 加上 flush=True，强迫 Python 立即把这句话写进 app.log，不准缓存！
                print(f"🔎 [接码台] 动态获取 Redis 成功！搜到 {len(keys)} 个 Key", flush=True)
                
                for key in keys:
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                    phone = key_str.split(":")[-1]
                    
                    val = await client.get(key_str)
                    code_val = val.decode('utf-8') if isinstance(val, bytes) else str(val)
                    ttl = await client.ttl(key_str)
                    
                    codes.append({
                        "phone": phone,
                        "code": code_val,
                        "ttl": max(0, ttl)
                    })
            except Exception as e:
                print(f"❌ [接码台] Redis 读取失败: {e}", flush=True)
        else:
            print("⚠️ [接码台] 警告：client 依然是 None，请检查 src/core/redis.py 的变量名", flush=True)
        
        return await self.templates.TemplateResponse(
            request,
            "sms_monitor.html",
            context={"request": request, "codes": codes}
        )