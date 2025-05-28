from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates

from app.api.v1.api import api_router
from app.core.middleware import ProcessTimeMiddleware, LoggingMiddleware, SecurityHeadersMiddleware, RateLimitMiddleware
from app.core.exceptions import setup_exception_handlers
from app.config.settings import settings
from app.config.logging import setup_logging, get_logger

# 初始化日志系统
setup_logging()
logger = get_logger()

app = FastAPI(
    title="车辆维修管理系统",
    description="Vehicle Repair Management System API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 记录应用启动
logger.info("正在启动车辆维修管理系统...")

# 中间件配置（注意顺序很重要）
# 1. 安全头中间件
app.add_middleware(SecurityHeadersMiddleware)

# 2. 速率限制中间件
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# 3. 日志中间件
app.add_middleware(LoggingMiddleware)

# 4. CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. 处理时间中间件
app.add_middleware(ProcessTimeMiddleware)

# 静态文件
app.mount("/static", StaticFiles(directory="../static"), name="static")

# 模板
# templates = Jinja2Templates(directory="templates")
# 前后端分离架构不使用模版

# 异常处理
setup_exception_handlers(app)

# API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", response_class=HTMLResponse)
async def root():
    logger.info("访问根路径")
    return HTMLResponse(content="<h1>车辆维修管理系统</h1><p>项目开发中</p>")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Vehicle Repair Management System is running"}

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("车辆维修管理系统启动完成")
    logger.info(f"API文档地址: http://localhost:8000{settings.API_V1_STR}/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("车辆维修管理系统正在关闭...")

if __name__ == "__main__":
    import uvicorn
    logger.info("使用uvicorn启动应用")
    uvicorn.run(
        app, 
        host="127.0.0.1",
        port=8001,
        log_config=None,  # 禁用uvicorn默认日志配置，使用我们的配置
        access_log=False  # 禁用uvicorn访问日志，使用我们的中间件
    )
