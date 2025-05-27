from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates

from app.api.v1.api import api_router
from app.core.middleware import ProcessTimeMiddleware
from app.core.exceptions import setup_exception_handlers
from app.config.settings import settings


app = FastAPI(
    title="车辆维修管理系统",
    description="Vehicle Repair Management System API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ProcessTimeMiddleware)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板
# templates = Jinja2Templates(directory="templates")
# 前后端分离架构不使用模版

# 异常处理
setup_exception_handlers(app)

# API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content="<h1>车辆维修管理系统</h1><p>项目开发中</p>")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Vehicle Repair Management System is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
