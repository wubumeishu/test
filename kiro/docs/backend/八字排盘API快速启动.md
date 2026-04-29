# 八字排盘 API 快速启动指南

## 1. 启动后端服务

```bash
cd bazi-admin
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

**验证服务**:
- 访问: http://127.0.0.1:9000/docs
- 应该能看到 Swagger UI 文档
- 确认 `/api/fortune/calculate` 接口存在

---

## 2. 测试 API

### 方式一: 使用 Swagger UI (推荐)

1. 访问 http://127.0.0.1:9000/docs
2. 找到 `POST /api/fortune/calculate` 接口
3. 点击 "Try it out"
4. 输入测试数据:
   ```json
   {
     "archive_id": "需要先创建档案",
     "is_deep_analysis": false
   }
   ```
5. 点击 "Execute"

### 方式二: 使用测试脚本

```bash
cd bazi-admin
python ../kiro/scripts/test_fortune_api.py
```

**预期输出**:
```
============================================================
测试八字排盘 API
============================================================

1️⃣ 创建测试档案...
✅ 档案创建成功

2️⃣ 调用八字计算引擎...
✅ 八字计算成功
   八字: 庚午 辛巳 庚辰 癸未
   生肖: 马
   日主: 庚 (金)

...

============================================================
✅ 所有测试通过!
============================================================
```

### 方式三: 使用 curl

```bash
# 1. 先创建一个档案
curl -X POST "http://127.0.0.1:9000/api/archives/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "archives": [{
      "archive_id": "test-001",
      "name": "张三",
      "gender": 1,
      "calendar_type": "solar",
      "birth_year": 1990,
      "birth_month": 5,
      "birth_day": 15,
      "birth_hour": 14,
      "birth_minute": 30,
      "tags": "测试",
      "is_default": true,
      "local_created_at": 1714233600000
    }]
  }'

# 2. 使用档案ID进行排盘
curl -X POST "http://127.0.0.1:9000/api/fortune/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "archive_id": "test-001",
    "is_deep_analysis": false
  }'

# 3. 或者直接使用原始数据排盘
curl -X POST "http://127.0.0.1:9000/api/fortune/calculate-by-data" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "李四",
    "gender": 0,
    "birth_year": 1992,
    "birth_month": 8,
    "birth_day": 20,
    "birth_hour": 10,
    "birth_minute": 0
  }'
```

---

## 3. 查看结果

### 成功响应示例

```json
{
  "success": true,
  "message": "八字排盘成功",
  "record_id": "50257132-249a-4e9f-b79d-5e921714d4d9",
  "name": "张三",
  "gender": 1,
  "solar_date": "1990-05-15 14:30",
  "lunar_date": "一九九〇年四月廿一",
  "shengxiao": "马",
  "bazi_string": "庚午 辛巳 庚辰 癸未",
  "year_pillar": {
    "gan": "庚",
    "zhi": "午",
    "nayin": "路旁土",
    "canggan": ["丁", "己"]
  },
  "month_pillar": {
    "gan": "辛",
    "zhi": "巳",
    "nayin": "白蜡金",
    "canggan": ["丙", "戊", "庚"]
  },
  "day_pillar": {
    "gan": "庚",
    "zhi": "辰",
    "nayin": "白蜡金",
    "canggan": ["戊", "乙", "癸"]
  },
  "hour_pillar": {
    "gan": "癸",
    "zhi": "未",
    "nayin": "杨柳木",
    "canggan": ["己", "丁", "乙"]
  },
  "day_master": "庚",
  "day_master_wuxing": "金",
  "wuxing_strength": {
    "jin": 38.89,
    "mu": 2.78,
    "shui": 13.89,
    "huo": 21.53,
    "tu": 22.92
  },
  "wuxing_summary": {
    "金": 3,
    "木": 0,
    "水": 1,
    "火": 2,
    "土": 2
  },
  "ai_report": null
}
```

---

## 4. 常见问题

### Q1: 档案不存在

**错误**: `{"detail": "档案不存在"}`

**解决**: 先使用 `/api/archives/sync` 接口创建档案

### Q2: 日期无效

**错误**: `{"detail": "无效的日期: 2020-2-30 0:0"}`

**解决**: 检查日期是否合法 (如 2月没有30日)

### Q3: 暂不支持农历

**错误**: `{"detail": "暂不支持农历，请使用公历日期"}`

**解决**: 将档案的 `calendar_type` 改为 `"solar"`

### Q4: 服务器错误

**错误**: `{"detail": "八字排盘失败: ..."}`

**解决**: 查看后端控制台日志,检查数据库连接

---

## 5. 完整测试流程

```bash
# 1. 启动后端
cd bazi-admin
uvicorn main:app --host 127.0.0.1 --port 9000 --reload

# 2. 新开一个终端,运行测试
cd bazi-admin
python ../kiro/scripts/test_fortune_api.py

# 3. 或者访问 Swagger UI
# 浏览器打开: http://127.0.0.1:9000/docs
```

---

## 6. 下一步

- ✅ API 已可用
- ✅ 数据库已集成
- ✅ 测试已通过

**后续工作**:
1. 前端集成 (在 uni-app 中调用 API)
2. AI 深度分析 (接入大模型)
3. 高级功能 (大运、流年等)

---

最后更新: 2026-04-27
