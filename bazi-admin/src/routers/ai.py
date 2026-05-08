"""
AI 深度命理分析路由
调用 DeepSeek API，为八字排盘数据生成专属深度批注
"""
import os
import json
import logging
import datetime
from typing import List, Optional, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from openai import AsyncOpenAI, APIConnectionError, APIStatusError, APITimeoutError
from src.database import get_db
from src.models import Record
from src.api.deps import get_current_user
from src.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI 命理分析"])

# ── 干支纪年表（1924-2043）──────────────────────────────────────────────────────
_TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
_DIZHI   = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def _get_ganzhi(year: int) -> str:
    """将公历年份转换为干支纪年，如 2026 → 丙午"""
    tg = _TIANGAN[(year - 4) % 10]
    dz = _DIZHI[(year - 4) % 12]
    return f"{tg}{dz}"

# ── System Prompt ──────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """【角色设定】
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


# ── 请求 / 响应模型 ────────────────────────────────────────────────────────────

class PillarData(BaseModel):
    gan: str = ""
    zhi: str = ""
    nayin: str = ""
    canggan: List[str] = []
    shishen: str = ""
    changsheng: str = ""
    canggan_shishen: List[str] = []
    shensha: List[str] = []


class BaziAnalysisRequest(BaseModel):
    """前端传来的八字排盘数据"""
    name: str = Field(default="命主", description="命主姓名")
    gender: int = Field(description="性别：0=女，1=男")
    solar_date: str = Field(default="", description="公历日期")
    lunar_date: str = Field(default="", description="农历日期")
    shengxiao: str = Field(default="", description="生肖")
    bazi_string: str = Field(default="", description="八字字符串，如：壬午 丙午 庚午 丁亥")
    year_pillar: PillarData = Field(default_factory=PillarData)
    month_pillar: PillarData = Field(default_factory=PillarData)
    day_pillar: PillarData = Field(default_factory=PillarData)
    hour_pillar: PillarData = Field(default_factory=PillarData)
    day_master: str = Field(default="", description="日主天干")
    day_master_wuxing: str = Field(default="", description="日主五行")


class BaziAnalysisResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# ── 工具函数 ───────────────────────────────────────────────────────────────────

def _build_user_prompt(req: BaziAnalysisRequest) -> str:
    """将排盘数据序列化为结构化的 user prompt 文本，并注入当前年份"""
    gender_str = "女" if req.gender == 0 else "男"

    # 动态获取当前年份及未来两年的干支
    now = datetime.datetime.now()
    y0, y1, y2 = now.year, now.year + 1, now.year + 2
    gz0, gz1, gz2 = _get_ganzhi(y0), _get_ganzhi(y1), _get_ganzhi(y2)

    def fmt_pillar(label: str, p: PillarData) -> str:
        shensha_str = "、".join(p.shensha) if p.shensha else "无"
        canggan_pairs = [
            f"{cg}（{ss}）"
            for cg, ss in zip(p.canggan, p.canggan_shishen)
        ] if p.canggan else ["无"]
        return (
            f"【{label}】{p.gan}{p.zhi}（纳音：{p.nayin}）\n"
            f"  天干十神：{p.shishen}　十二长生：{p.changsheng}\n"
            f"  藏干及副星：{'、'.join(canggan_pairs)}\n"
            f"  神煞：{shensha_str}"
        )

    lines = [
        f"【重要时间基准】当前年份：{y0} 年（{gz0}年）",
        f"流年分析必须从 {y0} 年开始，重点分析 {y0}（{gz0}）、{y1}（{gz1}）、{y2}（{gz2}）这三年，绝对不分析过去的年份。",
        "",
        f"性别：{gender_str}",
        f"公历：{req.solar_date}　农历：{req.lunar_date}　生肖：{req.shengxiao}",
        f"八字：{req.bazi_string}",
        f"日主：{req.day_master}（{req.day_master_wuxing}）",
        "",
        fmt_pillar("年柱", req.year_pillar),
        fmt_pillar("月柱", req.month_pillar),
        fmt_pillar("日柱", req.day_pillar),
        fmt_pillar("时柱", req.hour_pillar),
    ]
    return "\n".join(lines)


def _get_deepseek_client() -> AsyncOpenAI:
    """构建 DeepSeek 异步客户端，缺少 API Key 时快速失败"""
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="DEEPSEEK_API_KEY 未配置，请在 .env 中设置后重启服务"
        )
    return AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
    )


# ── 路由 ───────────────────────────────────────────────────────────────────────

@router.post("/bazi-analysis", response_model=BaziAnalysisResponse)
async def bazi_analysis(request: BaziAnalysisRequest):
    """
    调用 DeepSeek AI 生成八字深度命理批注

    接收前端传来的完整排盘数据，返回包含以下字段的 JSON：
    - pattern:      命理总局
    - strength:     身强身弱
    - decades:      大运与流年
    - relationship: 姻缘与情感
    - advice:       禅意寄语（含七言绝句）
    """
    logger.info(f"[AI] 收到分析请求，命主：{request.name}，八字：{request.bazi_string}")

    client = _get_deepseek_client()
    user_prompt = _build_user_prompt(request)

    try:
        completion = await client.chat.completions.create(
            model="deepseek-chat",
            # 移除 response_format，因为现在返回 Markdown 而非 JSON
            temperature=0.85,       # 适度创意，保持文风稳定
            max_tokens=4000,        # 增加 token 限制以支持长文本
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
        )
    except APIConnectionError as e:
        logger.error(f"[AI] 连接 DeepSeek 失败：{e}")
        raise HTTPException(status_code=502, detail=f"无法连接 DeepSeek 服务：{e}")
    except APITimeoutError as e:
        logger.error(f"[AI] DeepSeek 请求超时：{e}")
        raise HTTPException(status_code=504, detail="DeepSeek 请求超时，请稍后重试")
    except APIStatusError as e:
        logger.error(f"[AI] DeepSeek 返回错误状态 {e.status_code}：{e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=f"DeepSeek API 错误：{e.message}"
        )

    # 获取 AI 返回的 Markdown 文本
    raw_content = completion.choices[0].message.content or ""
    logger.info(f"[AI] 原始返回（前200字）：{raw_content[:200]}")

    # 直接返回 Markdown 文本，不再解析 JSON
    logger.info(f"[AI] 分析完成，命主：{request.name}，返回字数：{len(raw_content)}")
    return BaziAnalysisResponse(
        success=True,
        message="AI 命理分析完成",
        data={"markdown": raw_content},  # 将 Markdown 文本包装在 data 中
    )


# ── SSE 流式接口 ───────────────────────────────────────────────────────────────

def _pillar_to_data(pillar_dict: dict) -> PillarData:
    """将数据库中的 pillar 字典转换为 PillarData"""
    return PillarData(
        gan=pillar_dict.get("gan", ""),
        zhi=pillar_dict.get("zhi", ""),
        nayin=pillar_dict.get("nayin", ""),
        canggan=pillar_dict.get("canggan", []),
        shishen=pillar_dict.get("shishen", ""),
        changsheng=pillar_dict.get("changsheng", ""),
        canggan_shishen=pillar_dict.get("canggan_shishen", []),
        shensha=pillar_dict.get("shensha", []),
    )


async def _stream_ai_content(
    record: Record,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
    """
    核心流式生成器：调用 DeepSeek 流式 API，逐 chunk 推送 SSE 数据，
    完成后将完整内容写回数据库。
    """
    fej = record.five_elements_json or {}

    # 从数据库记录重建 BaziAnalysisRequest
    ai_request = BaziAnalysisRequest(
        name=fej.get("name", "命主"),
        gender=fej.get("gender", 1),
        solar_date=fej.get("solar_date", ""),
        lunar_date=fej.get("lunar_date", ""),
        shengxiao=fej.get("shengxiao", ""),
        bazi_string=record.bazi_str or "",
        year_pillar=_pillar_to_data(fej.get("year_pillar", {})),
        month_pillar=_pillar_to_data(fej.get("month_pillar", {})),
        day_pillar=_pillar_to_data(fej.get("day_pillar", {})),
        hour_pillar=_pillar_to_data(fej.get("hour_pillar", {})),
        day_master=fej.get("day_master", ""),
        day_master_wuxing=fej.get("day_master_wuxing", ""),
    )

    client = _get_deepseek_client()
    user_prompt = _build_user_prompt(ai_request)

    full_content = ""

    try:
        # 使用流式模式
        stream = await client.chat.completions.create(
            model="deepseek-chat",
            temperature=0.85,
            max_tokens=4000,
            stream=True,  # 开启流式
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                text = delta.content
                full_content += text
                # SSE 格式：data: <内容>\n\n
                yield f"data: {json.dumps({'text': text}, ensure_ascii=False)}\n\n"

        # 流式完成，写回数据库
        logger.info(f"[AI Stream] 流式完成，总字数：{len(full_content)}，写回数据库")
        record.ai_report_markdown = full_content
        await db.commit()

        # 发送结束信号
        yield f"data: {json.dumps({'done': True, 'total': len(full_content)})}\n\n"

    except APIConnectionError as e:
        logger.error(f"[AI Stream] 连接失败：{e}")
        yield f"data: {json.dumps({'error': '连接AI服务失败，请稍后重试'})}\n\n"
    except APITimeoutError as e:
        logger.error(f"[AI Stream] 超时：{e}")
        yield f"data: {json.dumps({'error': 'AI响应超时，请稍后重试'})}\n\n"
    except APIStatusError as e:
        logger.error(f"[AI Stream] API错误 {e.status_code}：{e.message}")
        yield f"data: {json.dumps({'error': f'AI服务错误：{e.message}'})}\n\n"
    except Exception as e:
        logger.error(f"[AI Stream] 未知错误：{e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@router.get("/stream/{record_id}")
async def stream_ai_analysis(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    SSE 流式 AI 分析接口

    - 根据 record_id 从数据库读取排盘数据
    - 调用 DeepSeek 流式 API，逐字推送内容
    - 完成后将完整报告写回数据库
    - 前端通过 wx.request enableChunked 接收

    SSE 数据格式：
      data: {"text": "逐字内容"}\\n\\n
      data: {"done": true, "total": 1800}\\n\\n
      data: {"error": "错误信息"}\\n\\n
    """
    # 查询记录（数据隔离）
    stmt = select(Record).where(
        Record.record_id == record_id,
        Record.user_id == current_user.user_id,
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(status_code=404, detail="记录不存在或无权访问")

    # 如果已有 AI 报告，直接一次性返回（避免重复调用）
    if record.ai_report_markdown:
        logger.info(f"[AI Stream] 记录 {record_id} 已有报告，直接返回缓存")
        async def cached_stream():
            content = record.ai_report_markdown
            # 分块推送，模拟流式（每次 50 字）
            chunk_size = 50
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'done': True, 'total': len(content), 'cached': True})}\n\n"
        return StreamingResponse(
            cached_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
            }
        )

    logger.info(f"[AI Stream] 开始流式分析，record_id: {record_id}")
    return StreamingResponse(
        _stream_ai_content(record, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
