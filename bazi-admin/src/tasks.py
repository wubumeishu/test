"""
RQ 异步任务模块

由 RQ Worker 独立进程执行，不在 FastAPI 进程内运行。
任务流程：
  1. 从参数接收 task_id 和 bazi_data（八字排盘数据字典）
  2. 调用 DeepSeek 流式 API，逐 chunk 追加写入 Redis
  3. 任务完成后将状态写为 "done"，失败写为 "error"

Redis Key 约定：
  task_status:{task_id}    → "pending" | "running" | "done" | "error"
  task_content:{task_id}   → 已生成的完整文本（追加写入）
  task_error:{task_id}     → 错误信息（仅 error 状态时存在）

所有 Key 的 TTL 为 2 小时，避免 Redis 内存泄漏。
"""
import os
import json
import datetime
import certifi
import httpx
from dotenv import load_dotenv

# RQ Worker 是独立进程，必须手动加载 .env
load_dotenv()

# ── 常量 ──────────────────────────────────────────────────────────────────────
REDIS_URL        = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE    = "https://api.deepseek.com/v1/chat/completions"

# Redis Key TTL：2 小时
TASK_TTL = 7200

# ── 干支纪年（流年 Prompt 用）────────────────────────────────────────────────
_TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
_DIZHI   = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _get_ganzhi(year: int) -> str:
    return f"{_TIANGAN[(year - 4) % 10]}{_DIZHI[(year - 4) % 12]}"


# ── System Prompt 基础版 ─────────────────────────────────────────────────────
_SYSTEM_PROMPT_BASE = """【角色设定】
你是《云水禅心》的首席命理与心理学大师。你拥有20年四柱八字实战经验，并精通荣格心理学。你的文风：通透、深邃、极具文学美感与悲悯之心。

【深度强制指令】（必须严格执行）
1. 拒绝套话，直击灵魂：不要说"你是一个善良的人"这种废话。你必须结合排盘中的具体参数（如"丁火生于酉月"、"八字劫财过重"等）来解释他为什么会这样。
2. 字数与格式压迫：你必须输出至少 5 个章节，每个章节不少于 3 个自然段，总字数必须超过 1500 字！
3. 格式排版：严格使用 ### 章节名 作为标题，重点核心命理词汇使用 **重点** 标注。
4. 禁止在文中出现命主的真实姓名，统一用"你"或"命主"代称。

【解析结构严格遵循】

### 第一篇：本我灵图·灵魂的底色（展开 3 段以上）
指出日主天干（如甲木、癸水等）代表的自然意象。深度剖析内心深处不为人知的伤痛、渴望，以及在人群中扮演的角色。指出八字中最强旺的五行或十神是如何塑造这种性格的。

### 第二篇：尘世修行·世俗的道场（展开 3 段以上）
分析事业与财富。不要只说吉凶，要告诉"靠什么赚钱"。是因为"食神生财"适合做内容/创意，还是"七杀化印"适合做管理？指出职业生涯中容易掉入的陷阱（如过度内耗、不善拒绝等）。

### 第三篇：情执与镜子·亲密关系（展开 3 段以上）
结合夫妻宫（日支）分析。探讨为什么会吸引特定类型的人？在亲密关系中，是在寻找保护者，还是在寻找崇拜者？给出打破目前情感困局的心理学建议。

### 第四篇：岁月流转·近三年的宇宙周期（展开 3 段以上）
【流年分析规则】：
- 必须严格以 user prompt 中标注的【当前年份】为起点，分析该年及未来两年，绝对不分析过去的年份。
- 结合命主当前所处的大运，深度剖析这三年的流年天干地支如何引动全局。
- 使用深邃的禅意意象描述周期阶段，禁止使用农业比喻（播种/除草/收获）。
  - 逆境年份示例："淬火与沉淀的闭关期"、"褪去浮华的内观之年"、"暗夜潜行的蛰伏期"
  - 顺境年份示例："乘风而起的显化之年"、"拨云见日的破局期"、"木火通明的绽放时刻"
- 明确指出这三年的核心能量主题、最大挑战，以及宇宙正在试图教会命主什么课题。
- 给出极具实操性的心理学破局建议。

### 第五篇：云水寄语（1 段）
用极其优美、充满哲理的禅意散文句，为命运进行升华和祝福。

【输出格式】
直接输出 Markdown 格式的文本，不要包含 JSON 结构。使用 ### 作为章节标题，使用 **文字** 标注重点。"""

# ── 首测专属破冰指令（追加在 System Prompt 末尾）────────────────────────────
_FIRST_READING_ADDON = """

【首测专属指令·破冰仪式感】（本次为该用户的第一份命理报告，必须严格执行）
1. 这是一位新用户的第一份分析报告。请在保持专业准确的基础上，文字风格要更加具有启发性、温暖且充满哲理，让他感受到被看见、被理解的温度。
2. 在第一篇章节正文开始之前，必须先输出一段独立的"破冰欢迎词"，格式如下：
   - 使用 > 引用块格式
   - 内容：以禅意散文的笔触，欢迎他开启探索自我之旅。可以用"星盘初开""命盘初启""第一次与自己的灵魂相遇"等意象，字数 60-100 字，充满温暖与哲理。
3. 整体基调：比常规报告多一份温柔，少一份锋芒。在指出命主的挑战与困境时，要多给予心理支持与前行的勇气，而非单纯的命理判断。"""


def _build_system_prompt(is_first_reading: bool = False) -> str:
    """
    动态构建 System Prompt。

    Args:
        is_first_reading: 是否为首测（用户的第一份命理报告）

    Returns:
        完整的 System Prompt 字符串
    """
    if is_first_reading:
        return _SYSTEM_PROMPT_BASE + _FIRST_READING_ADDON
    return _SYSTEM_PROMPT_BASE


# 向后兼容：保留 _SYSTEM_PROMPT 常量供其他模块直接引用
_SYSTEM_PROMPT = _SYSTEM_PROMPT_BASE


def _build_user_prompt(bazi_data: dict) -> str:
    """将前端传来的排盘数据字典构建为 DeepSeek user prompt"""
    gender_str = "女" if bazi_data.get("gender", 1) == 0 else "男"

    now = datetime.datetime.now()
    y0, y1, y2 = now.year, now.year + 1, now.year + 2
    gz0, gz1, gz2 = _get_ganzhi(y0), _get_ganzhi(y1), _get_ganzhi(y2)

    def fmt_pillar(label: str, p: dict) -> str:
        shensha = "、".join(p.get("shensha", [])) or "无"
        canggan = p.get("canggan", [])
        canggan_ss = p.get("canggan_shishen", [])
        pairs = [f"{cg}（{ss}）" for cg, ss in zip(canggan, canggan_ss)] or ["无"]
        return (
            f"【{label}】{p.get('gan', '')}{p.get('zhi', '')}（纳音：{p.get('nayin', '')}）\n"
            f"  天干十神：{p.get('shishen', '')}　十二长生：{p.get('changsheng', '')}\n"
            f"  藏干及副星：{'、'.join(pairs)}\n"
            f"  神煞：{shensha}"
        )

    lines = [
        f"【重要时间基准】当前年份：{y0} 年（{gz0}年）",
        f"流年分析必须从 {y0} 年开始，重点分析 {y0}（{gz0}）、{y1}（{gz1}）、{y2}（{gz2}）这三年，绝对不分析过去的年份。",
        "",
        f"性别：{gender_str}",
        f"公历：{bazi_data.get('solar_date', '')}　农历：{bazi_data.get('lunar_date', '')}　生肖：{bazi_data.get('shengxiao', '')}",
        f"八字：{bazi_data.get('bazi_string', '')}",
        f"日主：{bazi_data.get('day_master', '')}（{bazi_data.get('day_master_wuxing', '')}）",
        "",
        fmt_pillar("年柱", bazi_data.get("year_pillar", {})),
        fmt_pillar("月柱", bazi_data.get("month_pillar", {})),
        fmt_pillar("日柱", bazi_data.get("day_pillar", {})),
        fmt_pillar("时柱", bazi_data.get("hour_pillar", {})),
    ]
    return "\n".join(lines)


def _get_sync_redis():
    """
    获取同步 Redis 客户端（RQ Worker 是同步环境）
    使用 redis-py 的同步客户端，不使用 aioredis。
    """
    import redis as sync_redis
    return sync_redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


def ai_analysis_task(task_id: str, bazi_data: dict, is_first_reading: bool = False) -> None:
    """
    RQ 异步任务：调用 DeepSeek 生成八字深度分析报告

    此函数在 RQ Worker 进程中以同步方式执行。
    使用 httpx 同步客户端 + 流式请求，逐 chunk 写入 Redis。

    Args:
        task_id:          任务唯一标识（UUID），用于构造 Redis Key
        bazi_data:        八字排盘数据字典（前端传来的完整排盘结果）
        is_first_reading: 是否为首测，True 时注入破冰欢迎词指令
    """
    r = _get_sync_redis()

    # 标记任务开始
    r.setex(f"task_status:{task_id}", TASK_TTL, "running")
    r.setex(f"task_content:{task_id}", TASK_TTL, "")

    if not DEEPSEEK_API_KEY:
        r.setex(f"task_status:{task_id}", TASK_TTL, "error")
        r.setex(f"task_error:{task_id}", TASK_TTL, "DEEPSEEK_API_KEY 未配置")
        print(f"❌ [tasks] task_id={task_id} DEEPSEEK_API_KEY 未配置")
        return

    # 动态构建 System Prompt（首测注入破冰指令）
    system_prompt = _build_system_prompt(is_first_reading=is_first_reading)
    if is_first_reading:
        print(f"🌟 [tasks] 首测任务，已注入破冰指令，task_id={task_id}")

    user_prompt = _build_user_prompt(bazi_data)
    payload = {
        "model": "deepseek-chat",
        "temperature": 0.9 if is_first_reading else 0.85,  # 首测略提高创意度
        "max_tokens": 4000,
        "stream": True,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    full_content = ""

    try:
        print(f"🔄 [tasks] 开始 AI 分析，task_id={task_id}")

        # verify=certifi.where() 防止服务器 SSL 证书验证失败
        with httpx.Client(verify=certifi.where(), timeout=120.0) as client:
            with client.stream(
                "POST",
                DEEPSEEK_BASE,
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue

                    raw = line[len("data:"):].strip()
                    if raw == "[DONE]":
                        break

                    try:
                        chunk_data = json.loads(raw)
                        delta = chunk_data["choices"][0]["delta"]
                        text = delta.get("content", "")
                        if text:
                            full_content += text
                            # 追加写入 Redis，同时刷新 TTL
                            r.setex(f"task_content:{task_id}", TASK_TTL, full_content)
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

        # 任务成功
        r.setex(f"task_status:{task_id}", TASK_TTL, "done")
        r.setex(f"task_content:{task_id}", TASK_TTL, full_content)
        print(f"✅ [tasks] AI 分析完成，task_id={task_id}，字数={len(full_content)}")

    except httpx.HTTPStatusError as e:
        err = f"DeepSeek API 返回错误：{e.response.status_code}"
        r.setex(f"task_status:{task_id}", TASK_TTL, "error")
        r.setex(f"task_error:{task_id}", TASK_TTL, err)
        print(f"❌ [tasks] {err}，task_id={task_id}")

    except httpx.TimeoutException:
        err = "DeepSeek 请求超时（120s）"
        r.setex(f"task_status:{task_id}", TASK_TTL, "error")
        r.setex(f"task_error:{task_id}", TASK_TTL, err)
        print(f"❌ [tasks] {err}，task_id={task_id}")

    except Exception as e:
        err = str(e)
        r.setex(f"task_status:{task_id}", TASK_TTL, "error")
        r.setex(f"task_error:{task_id}", TASK_TTL, err)
        print(f"❌ [tasks] 未知错误：{err}，task_id={task_id}")
