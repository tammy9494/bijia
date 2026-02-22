# 汽车租赁比价网站 MVP

一个汽车租赁价格比价平台，支持从多个租车平台抓取价格并进行对比。

## 项目结构

```
bijia/
├── backend/                 # 后端服务
│   ├── main.py             # FastAPI 应用入口
│   ├── models.py           # 数据模型定义
│   ├── cache.py            # 内存缓存模块
│   ├── routers/            # API 路由
│   │   └── rental.py      # 租赁价格查询路由
│   └── scrapers/           # 爬虫模块
│       ├── base.py         # 爬虫基类
│       └── yihai.py        # 一嗨租车爬虫
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── services/       # API 服务
│   │   ├── App.jsx         # 主应用组件
│   │   └── main.jsx        # 入口文件
│   ├── package.json
│   └── vite.config.js
├── requirements.txt        # Python 依赖
└── README.md              # 项目说明
```

## 功能特性

- ✅ 支持一嗨租车价格抓取
- ✅ 15分钟内存缓存，减少重复请求
- ✅ 随机延迟和 User-Agent 轮换，防止被封
- ✅ 响应式前端界面，支持加载状态展示
- ✅ 模块化爬虫设计，方便扩展其他平台

## 安装步骤

### 1. 后端安装

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 前端安装

```bash
cd frontend

# 安装依赖
npm install
```

## 运行项目

### 启动后端服务

```bash
# 在项目根目录
uvicorn backend.main:app --reload --port 8000
```

后端服务将在 `http://localhost:8000` 启动。

### 启动前端服务

```bash
# 在 frontend 目录
cd frontend
npm run dev
```

前端服务将在 `http://localhost:3000` 启动。

## API 文档

启动后端服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API 端点

#### POST /api/rental/search

搜索租赁价格

**请求体：**
```json
{
  "car_model": "朗逸",
  "city": "北京",
  "pickup_time": "2026-02-14T10:00:00",
  "return_time": "2026-02-16T10:00:00"
}
```

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "platform": "一嗨租车",
      "car_model": "朗逸",
      "city": "北京",
      "daily_price": 150.00,
      "total_price": 300.00,
      "car_details": {
        "brand": "大众",
        "series": "朗逸",
        "seats": 5,
        "transmission": "自动",
        "fuel_type": "汽油"
      },
      "pickup_time": "2026-02-14T10:00:00",
      "return_time": "2026-02-16T10:00:00",
      "scraped_at": "2026-02-13T18:30:00"
    }
  ],
  "message": "成功获取 1 条价格信息"
}
```

## 反爬处理说明

爬虫模块实现了以下反爬措施：

1. **User-Agent 轮换**：每次请求随机选择不同的 User-Agent，模拟不同浏览器
2. **随机延迟**：在关键操作之间添加 1-3 秒的随机延迟，模拟人类行为
3. **无头浏览器**：使用 Playwright 的无头模式，避免被检测为自动化工具
4. **合理的等待策略**：使用 `networkidle` 等待页面完全加载

## 扩展其他平台

要添加新的租车平台，只需：

1. 在 `backend/scrapers/` 目录下创建新的爬虫文件（如 `hellobike.py`）
2. 继承 `BaseScraper` 类并实现 `scrape` 方法
3. 在 `backend/routers/rental.py` 中导入并调用新爬虫

示例：

```python
# backend/scrapers/hellobike.py
from backend.scrapers.base import BaseScraper
from backend.models import RentalPrice

class HelloBikeScraper(BaseScraper):
    def __init__(self):
        super().__init__("哈啰出行")
    
    async def scrape(self, car_model, city, pickup_time, return_time):
        # 实现爬虫逻辑
        pass
```

## 注意事项

1. **一嗨租车爬虫**：当前实现返回模拟数据，实际使用时需要根据一嗨租车网站的真实结构调整选择器和交互逻辑
2. **缓存策略**：当前使用内存缓存，重启服务后缓存会清空。生产环境建议使用 Redis
3. **错误处理**：爬虫失败不会中断整个查询流程，其他平台的数据仍会返回
4. **时间格式**：API 使用 ISO 8601 格式的日期时间字符串

## 开发计划

### Phase 1（当前）
- [x] 一嗨租车价格抓取
- [x] 基础前端界面
- [x] 内存缓存

### Phase 2（未来）
- [ ] 添加更多租车平台（神州租车、首汽租车等）
- [ ] Redis 缓存支持
- [ ] 用户认证和收藏功能
- [ ] 价格历史趋势图
- [ ] 邮件/短信价格提醒

## 技术栈

- **后端**：FastAPI, Playwright, Pydantic
- **前端**：React, Vite, Tailwind CSS, Axios
- **缓存**：内存缓存（可扩展为 Redis）

## 许可证

MIT
