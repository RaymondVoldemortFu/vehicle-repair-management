from fastapi import APIRouter

from app.api.v1 import (
    auth, users, vehicles, repair_orders, workers,
    services, materials, feedback, wages, analytics, admin, logs
)

api_router = APIRouter()

# 认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 用户相关路由
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["车辆管理"])

# 维修相关路由
api_router.include_router(repair_orders.router, prefix="/repair-orders", tags=["维修订单"])
api_router.include_router(workers.router, prefix="/workers", tags=["维修工人"])
api_router.include_router(services.router, prefix="/services", tags=["服务项目"])
api_router.include_router(materials.router, prefix="/materials", tags=["材料管理"])

# 反馈和工资路由
api_router.include_router(feedback.router, prefix="/feedback", tags=["用户反馈"])
api_router.include_router(wages.router, prefix="/wages", tags=["工资管理"])

# 数据分析路由
api_router.include_router(analytics.router, prefix="/analytics", tags=["数据分析"])

# 管理员路由
api_router.include_router(admin.router, prefix="/admin", tags=["系统管理"])

# 日志管理路由
api_router.include_router(logs.router, prefix="/logs", tags=["日志管理"])
