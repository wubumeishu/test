# 八字排盘 API 文档

## 概述

八字排盘 API 提供完整的八字计算和测算记录管理功能,基于 `bazi_engine.py` 核心算法实现。

## 基础信息

- **Base URL**: `http://127.0.0.1:9000`
- **API 前缀**: `/api/fortune`
- **认证方式**: 暂时使用模拟用户ID (后续接入 JWT)

## 接口列表

### 1. 八字排盘 (通过档案ID)

**接口**: `POST /api/fortune/calculate`

**功能**: 根据档案ID查询档案信息,调用八字引擎计算,并将结果存入数据库

**请求参数**:

```json
{
  "archive_id": "d3b458fd-7413-4506-8f7f-0889d7e756c5",
  "is_deep_analysis": false
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| archive_id | string | ✅ | 档案ID (UUID) |
| is_deep_analysis | boolean | ❌ | 是否为深度分析 (默认 false) |

**响应示例**:

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

**错误响应**:

```json
{
  "detail": "档案不存在"
}
```

**状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `404`: 档案不存在
- `500`: 服务器错误

---

### 2. 八字排盘 (通过原始数据)

**接口**: `POST /api/fortune/calculate-by-data`

**功能**: 直接接收生辰数据进行八字计算,不创建档案

**请求参数**:

```json
{
  "name": "李四",
  "gender": 0,
  "birth_year": 1992,
  "birth_month": 8,
  "birth_day": 20,
  "birth_hour": 10,
  "birth_minute": 0,
  "is_deep_analysis": false
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 姓名 (1-50字符) |
| gender | integer | ✅ | 性别 (1=男, 0=女) |
| birth_year | integer | ✅ | 出生年份 (1000-2100) |
| birth_month | integer | ✅ | 出生月份 (1-12) |
| birth_day | integer | ✅ | 出生日期 (1-31) |
| birth_hour | integer | ✅ | 出生小时 (0-23) |
| birth_minute | integer | ❌ | 出生分钟 (0-59, 默认0) |
| is_deep_analysis | boolean | ❌ | 是否为深度分析 (默认 false) |

**响应示例**: 同上

**注意**: 此接口不会创建档案,仅用于临时计算

---

### 3. 获取测算记录列表

**接口**: `GET /api/fortune/records`

**功能**: 获取用户的测算记录列表,支持分页和筛选

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| archive_id | string | ❌ | 档案ID (用于筛选) |
| limit | integer | ❌ | 每页数量 (默认20) |
| offset | integer | ❌ | 偏移量 (默认0) |

**请求示例**:

```
GET /api/fortune/records?archive_id=d3b458fd-7413-4506-8f7f-0889d7e756c5&limit=10&offset=0
```

**响应示例**:

```json
{
  "success": true,
  "message": "获取记录成功",
  "total": 5,
  "records": [
    {
      "record_id": "50257132-249a-4e9f-b79d-5e921714d4d9",
      "user_id": "00000000-0000-0000-0000-000000000001",
      "archive_id": "d3b458fd-7413-4506-8f7f-0889d7e756c5",
      "bazi_str": "庚午 辛巳 庚辰 癸未",
      "five_elements_json": { ... },
      "ai_report_markdown": "AI 分析报告...",
      "is_deep_analysis": false,
      "created_at": "2026-04-27T15:24:50.097000",
      "updated_at": "2026-04-27T15:24:50.097000"
    }
  ]
}
```

---

### 4. 获取单个测算记录

**接口**: `GET /api/fortune/records/{record_id}`

**功能**: 获取指定测算记录的详细信息

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| record_id | string | ✅ | 记录ID (UUID) |

**请求示例**:

```
GET /api/fortune/records/50257132-249a-4e9f-b79d-5e921714d4d9
```

**响应示例**:

```json
{
  "record_id": "50257132-249a-4e9f-b79d-5e921714d4d9",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "archive_id": "d3b458fd-7413-4506-8f7f-0889d7e756c5",
  "bazi_str": "庚午 辛巳 庚辰 癸未",
  "five_elements_json": {
    "solar_date": "1990-05-15 14:30",
    "lunar_date": "一九九〇年四月廿一",
    "shengxiao": "马",
    "year_pillar": { ... },
    "month_pillar": { ... },
    "day_pillar": { ... },
    "hour_pillar": { ... },
    "day_master": "庚",
    "day_master_wuxing": "金",
    "wuxing_strength": { ... },
    "wuxing_summary": { ... }
  },
  "ai_report_markdown": "AI 分析报告...",
  "is_deep_analysis": false,
  "created_at": "2026-04-27T15:24:50.097000",
  "updated_at": "2026-04-27T15:24:50.097000"
}
```

**错误响应**:

```json
{
  "detail": "记录不存在"
}
```

---

### 5. 删除测算记录

**接口**: `DELETE /api/fortune/records/{record_id}`

**功能**: 删除指定的测算记录

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| record_id | string | ✅ | 记录ID (UUID) |

**请求示例**:

```
DELETE /api/fortune/records/50257132-249a-4e9f-b79d-5e921714d4d9
```

**响应示例**:

```json
{
  "success": true,
  "message": "记录删除成功",
  "record_id": "50257132-249a-4e9f-b79d-5e921714d4d9"
}
```

---

## 数据结构说明

### PillarResponse (四柱)

```typescript
{
  gan: string;        // 天干
  zhi: string;        // 地支
  nayin: string;      // 纳音
  canggan: string[];  // 藏干
}
```

### WuxingStrengthResponse (五行强度)

```typescript
{
  jin: number;   // 金 (%)
  mu: number;    // 木 (%)
  shui: number;  // 水 (%)
  huo: number;   // 火 (%)
  tu: number;    // 土 (%)
}
```

### WuxingSummary (五行统计)

```typescript
{
  "金": number;  // 金的个数
  "木": number;  // 木的个数
  "水": number;  // 水的个数
  "火": number;  // 火的个数
  "土": number;  // 土的个数
}
```

## 业务流程

### 排盘流程

```
1. 前端发送请求 (档案ID 或 原始数据)
   ↓
2. 后端查询档案信息 (如果是档案ID)
   ↓
3. 调用 bazi_engine.py 计算八字
   ↓
4. 将完整结果存入 records 表 (JSONB 格式)
   ↓
5. 返回精简数据给前端展示
```

### 数据存储

**records 表结构**:

| 字段 | 类型 | 说明 |
|------|------|------|
| record_id | UUID | 记录ID (主键) |
| user_id | UUID | 用户ID (外键) |
| archive_id | UUID | 档案ID (外键) |
| bazi_str | VARCHAR | 八字字符串 |
| five_elements_json | JSONB | 完整的八字数据 (JSON) |
| ai_report_markdown | TEXT | AI 分析报告 (Markdown) |
| is_deep_analysis | BOOLEAN | 是否为深度分析 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**five_elements_json 结构**:

```json
{
  "solar_date": "1990-05-15 14:30",
  "lunar_date": "一九九〇年四月廿一",
  "shengxiao": "马",
  "year_pillar": { "gan": "庚", "zhi": "午", "nayin": "路旁土", "canggan": [...] },
  "month_pillar": { ... },
  "day_pillar": { ... },
  "hour_pillar": { ... },
  "day_master": "庚",
  "day_master_wuxing": "金",
  "wuxing_strength": { "jin": 38.89, "mu": 2.78, ... },
  "wuxing_summary": { "金": 3, "木": 0, ... }
}
```

## 使用示例

### Python (requests)

```python
import requests

# 1. 通过档案ID排盘
response = requests.post(
    "http://127.0.0.1:9000/api/fortune/calculate",
    json={
        "archive_id": "d3b458fd-7413-4506-8f7f-0889d7e756c5",
        "is_deep_analysis": False
    }
)
result = response.json()
print(f"八字: {result['bazi_string']}")
print(f"生肖: {result['shengxiao']}")

# 2. 通过原始数据排盘
response = requests.post(
    "http://127.0.0.1:9000/api/fortune/calculate-by-data",
    json={
        "name": "李四",
        "gender": 0,
        "birth_year": 1992,
        "birth_month": 8,
        "birth_day": 20,
        "birth_hour": 10,
        "birth_minute": 0
    }
)
result = response.json()

# 3. 获取记录列表
response = requests.get(
    "http://127.0.0.1:9000/api/fortune/records",
    params={"limit": 10, "offset": 0}
)
records = response.json()
```

### JavaScript (fetch)

```javascript
// 1. 通过档案ID排盘
const response = await fetch('http://127.0.0.1:9000/api/fortune/calculate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    archive_id: 'd3b458fd-7413-4506-8f7f-0889d7e756c5',
    is_deep_analysis: false
  })
});
const result = await response.json();
console.log('八字:', result.bazi_string);

// 2. 获取记录列表
const response = await fetch('http://127.0.0.1:9000/api/fortune/records?limit=10');
const records = await response.json();
```

### uni-app (前端集成)

```typescript
// 在 request.ts 中添加
export const calculateBazi = (archiveId: string, isDeepAnalysis = false) => {
  return request<BaziCalculateResponse>({
    url: '/api/fortune/calculate',
    method: 'POST',
    data: { archive_id: archiveId, is_deep_analysis: isDeepAnalysis }
  });
};

// 使用
const result = await calculateBazi('d3b458fd-7413-4506-8f7f-0889d7e756c5');
console.log('八字:', result.bazi_string);
```

## 错误处理

### 常见错误

| 错误码 | 错误信息 | 原因 | 解决方案 |
|--------|----------|------|----------|
| 400 | 无效的日期 | 日期参数不合法 | 检查日期范围和格式 |
| 400 | 暂不支持农历 | 档案使用农历 | 使用公历日期 |
| 404 | 档案不存在 | 档案ID不存在 | 检查档案ID是否正确 |
| 404 | 记录不存在 | 记录ID不存在 | 检查记录ID是否正确 |
| 500 | 八字排盘失败 | 服务器内部错误 | 查看后端日志 |

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

## 性能优化

### 1. 数据库索引

- `user_id`: 已建立索引
- `archive_id`: 已建立索引
- `created_at`: 建议添加索引 (用于排序)

### 2. 缓存策略

- 相同档案的重复计算可以从数据库读取历史记录
- 建议在前端缓存最近的计算结果

### 3. 批量操作

- 如需批量计算,建议使用异步任务队列
- 避免在单个请求中计算大量八字

## 后续扩展

### 待实现功能

- [ ] AI 深度分析报告生成
- [ ] 大运计算
- [ ] 流年分析
- [ ] 神煞推算
- [ ] 格局判断
- [ ] 批量计算接口
- [ ] WebSocket 实时推送

### 优化建议

- [ ] 添加 Redis 缓存
- [ ] 实现异步任务队列
- [ ] 添加请求限流
- [ ] 完善错误日志
- [ ] 添加性能监控

## 测试

### 运行测试脚本

```bash
cd bazi-admin
python ../kiro/scripts/test_fortune_api.py
```

### Swagger UI

访问 `http://127.0.0.1:9000/docs` 可以在线测试所有接口

---

最后更新: 2026-04-27
