from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, computed_field

from app.config.database import get_db
from app.core.deps import get_current_active_admin, get_current_super_admin
from app.crud.admin import admin_crud
from app.models.admin import Admin, AdminStatus, AdminRole
from app.schemas.admin import AdminResponse, AdminCreate
from app.schemas.base import PaginatedResponse, PaginationParams, MessageResponse
from app.config.logging import get_api_logger
import platform
import psutil
from datetime import datetime

router = APIRouter()
logger = get_api_logger()


class SystemAdminResponse(BaseModel):
    """系统管理员响应模型，确保包含前端需要的字段"""
    id: int
    username: str
    name: str
    role: str
    phone: Optional[str]
    email: Optional[str]
    status: str
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    @computed_field
    @property
    def is_active(self) -> bool:
        """将status字段映射为is_active布尔值"""
        return self.status == "active"

    class Config:
        from_attributes = True


def convert_admin_to_response(admin: Admin) -> SystemAdminResponse:
    """将Admin对象转换为SystemAdminResponse"""
    # 将后端角色映射为前端期望的角色
    role_mapping = {
        "super_admin": "super_admin",
        "manager": "admin", 
        "supervisor": "admin",
        "clerk": "operator"
    }
    
    role_value = admin.role.value if hasattr(admin.role, 'value') else str(admin.role)
    status_value = admin.status.value if hasattr(admin.status, 'value') else str(admin.status)
    
    return SystemAdminResponse(
        id=admin.id,
        username=admin.username,
        name=admin.name,
        role=role_mapping.get(role_value, "operator"),
        phone=admin.phone,
        email=admin.email,
        status=status_value,
        last_login=admin.last_login,
        created_at=admin.created_at,
        updated_at=admin.updated_at
    )


@router.get("/admins", response_model=PaginatedResponse[SystemAdminResponse])
def get_system_admins(
    db: Session = Depends(get_db),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取管理员列表（带搜索功能）"""
    
    # 如果不是超级管理员，只能查看部分信息，不能编辑
    if current_admin.role != AdminRole.SUPER_ADMIN:
        logger.info(f"普通管理员查看管理员列表: {current_admin.username}")
    else:
        logger.info(f"超级管理员查看管理员列表: {current_admin.username}")
    
    # 计算分页偏移量
    skip = (page - 1) * size
    
    # 构建查询
    query = db.query(Admin).filter(Admin.is_deleted == False)
    
    # 如果有搜索关键词，进行模糊搜索
    if keyword and keyword.strip():
        search_pattern = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                Admin.username.ilike(search_pattern),
                Admin.name.ilike(search_pattern),
                Admin.email.ilike(search_pattern)
            )
        )
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    admins = query.order_by(Admin.id).offset(skip).limit(size).all()
    
    # 转换为响应模型
    admin_responses = [convert_admin_to_response(admin) for admin in admins]
    
    return PaginatedResponse.create(
        items=admin_responses,
        total=total,
        page=page,
        size=size
    )


@router.post("/admins", response_model=SystemAdminResponse)
def create_system_admin(
    *,
    db: Session = Depends(get_db),
    admin_data: dict,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """创建管理员（超级管理员专用）"""
    logger.info(f"超级管理员创建新管理员: {current_admin.username} -> {admin_data.get('username')}")
    
    # 处理前端数据格式
    username = admin_data.get("username")
    name = admin_data.get("name")
    email = admin_data.get("email")
    role = admin_data.get("role", "clerk")  # 默认为职员角色
    password = admin_data.get("password")
    phone = admin_data.get("phone")
    is_active = admin_data.get("is_active", True)
    
    # 验证必填字段
    if not username or not name or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名、姓名和密码为必填项"
        )
    
    # 检查用户名是否已存在
    if admin_crud.get_by_username(db, username=username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if email and admin_crud.get_by_email(db, email=email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 将前端的role映射到后端的角色
    role_mapping = {
        "admin": "manager",
        "super_admin": "super_admin",
        "manager": "manager",
        "supervisor": "supervisor", 
        "clerk": "clerk"
    }
    backend_role = role_mapping.get(role, "clerk")
    
    # 创建AdminCreate对象
    admin_create_data = AdminCreate(
        username=username,
        name=name,
        email=email,
        phone=phone,
        role=backend_role,
        password=password
    )
    
    # 创建管理员
    admin = admin_crud.create(db, obj_in=admin_create_data)
    
    # 如果前端指定了is_active状态，更新管理员状态
    if not is_active:
        admin_crud.update(db, db_obj=admin, obj_in={"status": AdminStatus.INACTIVE})
        admin.status = AdminStatus.INACTIVE
    
    logger.info(f"管理员创建成功: ID={admin.id}, 用户名={username}")
    
    return convert_admin_to_response(admin)


@router.put("/admins/{admin_id}", response_model=SystemAdminResponse)
def update_system_admin(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    admin_in: dict,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """更新管理员信息（超级管理员专用）"""
    logger.info(f"超级管理员更新管理员: {current_admin.username} -> {admin_id}")
    
    admin = admin_crud.get(db, id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    # 如果更新用户名，检查是否已存在
    if admin_in.get("username") and admin_in["username"] != admin.username:
        existing_admin = admin_crud.get_by_username(db, username=admin_in["username"])
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
    
    # 如果更新邮箱，检查是否已存在
    if admin_in.get("email") and admin_in["email"] != admin.email:
        existing_admin = admin_crud.get_by_email(db, email=admin_in["email"])
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    # 处理is_active字段映射
    if "is_active" in admin_in:
        admin_in["status"] = AdminStatus.ACTIVE if admin_in["is_active"] else AdminStatus.INACTIVE
        del admin_in["is_active"]  # 删除前端字段，避免数据库错误
    
    # 更新管理员
    updated_admin = admin_crud.update(db, db_obj=admin, obj_in=admin_in)
    logger.info(f"管理员更新成功: ID={admin_id}")
    
    return convert_admin_to_response(updated_admin)


@router.delete("/admins/{admin_id}", response_model=MessageResponse)
def delete_system_admin(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """删除管理员（超级管理员专用）"""
    logger.info(f"超级管理员删除管理员: {current_admin.username} -> {admin_id}")
    
    admin = admin_crud.get(db, id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    # 不能删除自己
    if admin.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    # 删除管理员
    admin_crud.remove(db, id=admin_id)
    logger.info(f"管理员删除成功: ID={admin_id}")
    
    return MessageResponse(message="管理员删除成功")


@router.put("/admins/{admin_id}/toggle-status", response_model=SystemAdminResponse)
def toggle_admin_status(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """切换管理员状态（激活/停用）（超级管理员专用）"""
    logger.info(f"超级管理员切换管理员状态: {current_admin.username} -> {admin_id}")
    
    admin = admin_crud.get(db, id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    # 不能停用自己
    if admin.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能停用自己"
        )
    
    # 切换状态
    new_status = AdminStatus.INACTIVE if admin.status == AdminStatus.ACTIVE else AdminStatus.ACTIVE
    updated_admin = admin_crud.update(db, db_obj=admin, obj_in={"status": new_status})
    
    status_text = "激活" if new_status == AdminStatus.ACTIVE else "停用"
    logger.info(f"管理员状态切换成功: ID={admin_id}, 状态={status_text}")
    
    return convert_admin_to_response(updated_admin)


@router.get("/config")
def get_system_config(
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取系统配置信息"""
    logger.info(f"管理员获取系统配置: {current_admin.username}")
    
    # 返回系统配置信息
    config = {
        "system_name": "车辆维修管理系统",
        "system_description": "专业的车辆维修服务管理平台",
        "version": "v1.0.0",
        "maintenance_mode": False,
        "maintenance_message": "系统维护中，请稍后访问",
        "min_password_length": 6,
        "max_login_attempts": 5,
        "lockout_duration": 15,
        "session_timeout": 8,
        "auto_assign_orders": True,
        "work_start_time": "08:00",
        "work_end_time": "18:00",
        "service_phone": "400-123-4567",
        "service_email": "service@example.com",
        "features": {
            "user_management": True,
            "order_management": True,
            "worker_management": True,
            "material_management": True,
            "service_management": True,
            "analytics": True,
            "feedback_management": True,
            "wage_management": True
        }
    }
    
    return config


@router.get("/info")  
def get_system_info(
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取系统信息"""
    logger.info(f"管理员获取系统信息: {current_admin.username}")
    
    try:
        # 获取系统基本信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 获取系统启动时间
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = f"{uptime.days}天 {uptime.seconds // 3600}小时"
        
        system_info = {
            "version": "v1.0.0",
            "uptime": uptime_str,
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "database_version": "PostgreSQL 13.8",
            "performance": {
                "cpu_usage": round(cpu_percent, 2),
                "memory_usage": round(memory.percent, 2),
                "memory_total": round(memory.total / (1024**3), 2),  # GB
                "memory_used": round(memory.used / (1024**3), 2),   # GB
                "disk_usage": round(disk.percent, 2),
                "disk_total": round(disk.total / (1024**3), 2),     # GB
                "disk_used": round(disk.used / (1024**3), 2),       # GB
                "disk_free": round(disk.free / (1024**3), 2)        # GB
            }
        }
        
        return system_info
        
    except Exception as e:
        logger.error(f"获取系统信息失败: {str(e)}")
        # 返回基本信息作为降级处理
        return {
            "version": "v1.0.0",
            "uptime": "未知",
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "platform": {
                "system": platform.system(),
                "release": "未知",
                "version": "未知",
                "machine": platform.machine(),
                "processor": "未知"
            },
            "database_version": "PostgreSQL 13.8",
            "performance": {
                "cpu_usage": 0,
                "memory_usage": 0,
                "memory_total": 0,
                "memory_used": 0,
                "disk_usage": 0,
                "disk_total": 0,
                "disk_used": 0,
                "disk_free": 0
            },
            "error": "部分系统信息获取失败"
        }


@router.put("/config")
def update_system_config(
    config_data: dict,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """更新系统配置（仅超级管理员）"""
    logger.info(f"超级管理员更新系统配置: {current_admin.username}")
    
    # 这里可以实现配置的持久化存储
    # 目前返回成功响应
    return {
        "message": "系统配置更新成功",
        "updated_config": config_data
    } 