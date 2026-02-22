"""
FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import rental

app = FastAPI(title="汽车租赁比价 API", version="1.0.0")

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React 开发服务器端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(rental.router, prefix="/api", tags=["rental"])


@app.get("/")
async def root():
    return {"message": "汽车租赁比价 API"}


@app.get("/health")
async def health():
    return {"status": "ok"}
