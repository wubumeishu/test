"""
每日禅语路由

GET /api/zen/daily   根据「日期 + UserID」返回当日固定禅语（日课）

算法：
  seed = djb2_hash(f"{user_id}-{today}")
  index = seed % len(ZEN_LIBRARY)

缓存：
  Redis Key: zen_daily:{user_id}:{today}
  TTL: 到当天 23:59:59（精确到秒），确保次日自动刷新
"""
import hashlib
from datetime import datetime, date, time
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
import redis.asyncio as aioredis

from src.api.deps import get_current_user
from src.core.redis import get_redis
from src.models.user import User

router = APIRouter(prefix="/api/zen", tags=["每日禅语"])


# ── 禅语库（60 条，内存存储，无需数据库）────────────────────────────────────
ZEN_LIBRARY = [
    # 佛偈 / 禅宗
    {"id": 1,  "content": "菩提本无树，明镜亦非台。本来无一物，何处惹尘埃。",        "author": "六祖慧能"},
    {"id": 2,  "content": "身是菩提树，心如明镜台。时时勤拂拭，勿使惹尘埃。",        "author": "神秀"},
    {"id": 3,  "content": "不是风动，不是幡动，仁者心动。",                          "author": "六祖慧能"},
    {"id": 4,  "content": "千江有水千江月，万里无云万里天。",                        "author": "禅语"},
    {"id": 5,  "content": "春有百花秋有月，夏有凉风冬有雪。若无闲事挂心头，便是人间好时节。", "author": "无门慧开"},
    {"id": 6,  "content": "放下屠刀，立地成佛。",                                    "author": "禅语"},
    {"id": 7,  "content": "佛在心中莫浪求，灵山只在汝心头。",                        "author": "禅语"},
    {"id": 8,  "content": "一花一世界，一叶一如来。",                                "author": "华严经"},
    {"id": 9,  "content": "色即是空，空即是色。",                                    "author": "心经"},
    {"id": 10, "content": "凡所有相，皆是虚妄。若见诸相非相，即见如来。",            "author": "金刚经"},
    {"id": 11, "content": "应无所住，而生其心。",                                    "author": "金刚经"},
    {"id": 12, "content": "过去心不可得，现在心不可得，未来心不可得。",              "author": "金刚经"},
    {"id": 13, "content": "一切有为法，如梦幻泡影，如露亦如电，应作如是观。",        "author": "金刚经"},
    {"id": 14, "content": "心生则种种法生，心灭则种种法灭。",                        "author": "大乘起信论"},
    {"id": 15, "content": "随缘自适，烦恼即菩提。",                                  "author": "禅语"},

    # 道德经 / 老子
    {"id": 16, "content": "上善若水，水善利万物而不争。",                            "author": "老子"},
    {"id": 17, "content": "知足者富，强行者有志。",                                  "author": "老子"},
    {"id": 18, "content": "致虚极，守静笃。万物并作，吾以观复。",                    "author": "老子"},
    {"id": 19, "content": "曲则全，枉则直，洼则盈，弊则新。",                        "author": "老子"},
    {"id": 20, "content": "为学日益，为道日损。损之又损，以至于无为。",              "author": "老子"},
    {"id": 21, "content": "知人者智，自知者明。胜人者有力，自胜者强。",              "author": "老子"},
    {"id": 22, "content": "信言不美，美言不信。善者不辩，辩者不善。",                "author": "老子"},
    {"id": 23, "content": "天下莫柔弱于水，而攻坚强者莫之能胜。",                    "author": "老子"},
    {"id": 24, "content": "损之又损，以至于无为。无为而无不为。",                    "author": "老子"},
    {"id": 25, "content": "为而不争，天下莫能与之争。",                              "author": "老子"},

    # 庄子
    {"id": 26, "content": "至人无己，神人无功，圣人无名。",                          "author": "庄子"},
    {"id": 27, "content": "吾生也有涯，而知也无涯。以有涯随无涯，殆已。",            "author": "庄子"},
    {"id": 28, "content": "天地与我并生，而万物与我为一。",                          "author": "庄子"},
    {"id": 29, "content": "相濡以沫，不如相忘于江湖。",                              "author": "庄子"},
    {"id": 30, "content": "独与天地精神往来，而不傲倪于万物。",                      "author": "庄子"},

    # 古诗词禅意
    {"id": 31, "content": "行到水穷处，坐看云起时。",                                "author": "王维"},
    {"id": 32, "content": "云无心以出岫，鸟倦飞而知还。",                            "author": "陶渊明"},
    {"id": 33, "content": "此心安处是吾乡。",                                        "author": "苏轼"},
    {"id": 34, "content": "竹密不妨流水过，山高岂碍白云飞。",                        "author": "禅语"},
    {"id": 35, "content": "花开不并百花丛，独立疏篱趣未穷。",                        "author": "郑思肖"},
    {"id": 36, "content": "采菊东篱下，悠然见南山。",                                "author": "陶渊明"},
    {"id": 37, "content": "明月松间照，清泉石上流。",                                "author": "王维"},
    {"id": 38, "content": "空山新雨后，天气晚来秋。",                                "author": "王维"},
    {"id": 39, "content": "人闲桂花落，夜静春山空。",                                "author": "王维"},
    {"id": 40, "content": "独坐幽篁里，弹琴复长啸。深林人不知，明月来相照。",        "author": "王维"},

    # 现代禅意语录
    {"id": 41, "content": "不执着于过去，不忧虑于未来，只是活在当下这一刻。",        "author": "禅语"},
    {"id": 42, "content": "心若简单，世界便简单；心若复杂，世界便复杂。",            "author": "禅语"},
    {"id": 43, "content": "放下，不是放弃，而是以更轻盈的姿态前行。",                "author": "禅语"},
    {"id": 44, "content": "每一次呼吸，都是一次新的开始。",                          "author": "禅语"},
    {"id": 45, "content": "静水流深，大音希声。真正的力量，往往藏于宁静之中。",      "author": "禅语"},
    {"id": 46, "content": "万物皆有裂缝，那是光照进来的地方。",                      "author": "禅语"},
    {"id": 47, "content": "不与过去纠缠，不为未来焦虑，此刻的你，已经足够完整。",    "author": "禅语"},
    {"id": 48, "content": "山不争高，自成其峻；海不争深，自成其渊。",                "author": "禅语"},
    {"id": 49, "content": "凡事顺其自然，遇事处之泰然，得意之时淡然，失意之时坦然。", "author": "禅语"},
    {"id": 50, "content": "心宽，天地就宽；心静，岁月就静。",                        "author": "禅语"},

    # 补充 10 条
    {"id": 51, "content": "不以物喜，不以己悲。",                                    "author": "范仲淹"},
    {"id": 52, "content": "宠辱不惊，闲看庭前花开花落；去留无意，漫随天外云卷云舒。", "author": "洪应明"},
    {"id": 53, "content": "知止而后有定，定而后能静，静而后能安，安而后能虑，虑而后能得。", "author": "大学"},
    {"id": 54, "content": "吾日三省吾身：为人谋而不忠乎？与朋友交而不信乎？传不习乎？", "author": "曾子"},
    {"id": 55, "content": "君子坦荡荡，小人长戚戚。",                                "author": "孔子"},
    {"id": 56, "content": "岁寒，然后知松柏之后凋也。",                              "author": "孔子"},
    {"id": 57, "content": "逝者如斯夫，不舍昼夜。",                                  "author": "孔子"},
    {"id": 58, "content": "天行健，君子以自强不息；地势坤，君子以厚德载物。",        "author": "易经"},
    {"id": 59, "content": "穷则独善其身，达则兼善天下。",                            "author": "孟子"},
    {"id": 60, "content": "生于忧患，死于安乐。",                                    "author": "孟子"},
]

ZEN_COUNT = len(ZEN_LIBRARY)


# ── 响应模型 ──────────────────────────────────────────────────────────────────

class DailyZenResponse(BaseModel):
    id: int
    content: str
    author: Optional[str] = None
    date: str


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def _djb2_hash(s: str) -> int:
    """
    djb2 哈希算法：将字符串映射为非负整数。
    同一输入永远返回同一结果，适合做确定性种子。
    """
    h = 5381
    for c in s:
        h = ((h << 5) + h) + ord(c)
        h &= 0xFFFFFFFF  # 保持 32 位
    return h


def _today_str() -> str:
    """返回今日日期字符串，格式 YYYY-MM-DD"""
    return date.today().isoformat()


def _seconds_until_midnight() -> int:
    """返回距今天 23:59:59 的剩余秒数，用于 Redis TTL"""
    now = datetime.now()
    midnight = datetime.combine(now.date(), time(23, 59, 59))
    delta = midnight - now
    return max(int(delta.total_seconds()), 1)


def _pick_zen(user_id: str, today: str) -> dict:
    """
    根据 user_id + 日期确定性地选取一条禅语。
    同一用户同一天永远返回同一条。
    """
    seed_str = f"{user_id}-{today}"
    idx = _djb2_hash(seed_str) % ZEN_COUNT
    return ZEN_LIBRARY[idx]


# ── 路由 ──────────────────────────────────────────────────────────────────────

@router.get("/daily", response_model=DailyZenResponse, summary="获取今日禅语（日课）")
async def get_daily_zen(
    current_user: User = Depends(get_current_user),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    """
    根据「当前日期 + UserID」返回当日固定禅语。

    同一用户同一天调用多次，结果完全一致（日课特性）。
    结果缓存至当天 23:59:59，次日自动刷新。

    返回示例：
    ```json
    {
      "id": 12,
      "content": "过去心不可得，现在心不可得，未来心不可得。",
      "author": "金刚经",
      "date": "2026-05-10"
    }
    ```
    """
    today = _today_str()
    cache_key = f"zen_daily:{current_user.user_id}:{today}"

    # ── 读缓存 ────────────────────────────────────────────────────────────────
    cached = await redis_client.get(cache_key)
    if cached:
        import json
        data = json.loads(cached)
        return DailyZenResponse(**data)

    # ── 计算今日禅语 ──────────────────────────────────────────────────────────
    zen = _pick_zen(current_user.user_id, today)
    result = DailyZenResponse(
        id=zen["id"],
        content=zen["content"],
        author=zen.get("author"),
        date=today,
    )

    # ── 写缓存（精确到当天 23:59:59）─────────────────────────────────────────
    import json
    ttl = _seconds_until_midnight()
    await redis_client.setex(
        cache_key,
        ttl,
        json.dumps(result.model_dump(), ensure_ascii=False),
    )

    return result
