from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.core.security import verify_token
from app.models import User, Admin, RepairWorker
from app.models.admin import AdminStatus, AdminRole
from app.crud.user import user_crud
from app.crud.admin import admin_crud
from app.crud.repair_worker import repair_worker_crud

# HTTP Bearer 认证
security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_crud.get(db, id=int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    return user


def get_current_admin(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Admin:
    """获取当前管理员"""
    token = credentials.credentials
    admin_id = verify_token(token)
    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    admin = admin_crud.get(db, id=int(admin_id))
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    if admin.status != AdminStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员账户已被禁用"
        )
    
    return admin


def get_current_worker(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> RepairWorker:
    """获取当前维修工人"""
    token = credentials.credentials
    worker_id = verify_token(token)
    if worker_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    worker = repair_worker_crud.get(db, id=int(worker_id))
    if worker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修工人不存在"
        )
    
    if worker.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="维修工人账户已被禁用"
        )
    
    return worker


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    return current_user


def get_current_active_admin(
    current_admin: Admin = Depends(get_current_admin),
) -> Admin:
    """获取当前活跃管理员"""
    return current_admin


def get_current_active_worker(
    current_worker: RepairWorker = Depends(get_current_worker),
) -> RepairWorker:
    """获取当前活跃维修工人"""
    return current_worker


def get_current_super_admin(
    current_admin: Admin = Depends(get_current_admin),
) -> Admin:
    """获取当前超级管理员"""
    if current_admin.role != AdminRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )
    return current_admin


def check_admin_permission(permission: str):
    """检查管理员权限的依赖工厂函数"""
    def permission_checker(
        current_admin: Admin = Depends(get_current_active_admin),
    ) -> Admin:
        # 超级管理员拥有所有权限
        if current_admin.role == AdminRole.SUPER_ADMIN:
            return current_admin
        
        # 检查特定权限
        if not admin_crud.has_permission(current_admin, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少必要权限: {permission}"
            )
        
        return current_admin
    
    return permission_checker


def get_admin_with_user_management_permission(
    current_admin: Admin = Depends(check_admin_permission("user_management")),
) -> Admin:
    """获取具有用户管理权限的管理员"""
    return current_admin


def get_admin_with_order_management_permission(
    current_admin: Admin = Depends(check_admin_permission("order_management")),
) -> Admin:
    """获取具有订单管理权限的管理员"""
    return current_admin


def get_admin_with_worker_management_permission(
    current_admin: Admin = Depends(check_admin_permission("worker_management")),
) -> Admin:
    """获取具有工人管理权限的管理员"""
    return current_admin


def get_admin_with_material_management_permission(
    current_admin: Admin = Depends(check_admin_permission("material_management")),
) -> Admin:
    """获取具有材料管理权限的管理员"""
    return current_admin


def get_admin_with_service_management_permission(
    current_admin: Admin = Depends(check_admin_permission("service_management")),
) -> Admin:
    """获取具有服务管理权限的管理员"""
    return current_admin


def get_admin_with_analytics_permission(
    current_admin: Admin = Depends(check_admin_permission("analytics")),
) -> Admin:
    """获取具有分析权限的管理员"""
    return current_admin


def get_admin_with_feedback_management_permission(
    current_admin: Admin = Depends(check_admin_permission("feedback_management")),
) -> Admin:
    """获取具有反馈管理权限的管理员"""
    return current_admin


def get_admin_with_wage_management_permission(
    current_admin: Admin = Depends(check_admin_permission("wage_management")),
) -> Admin:
    """获取具有工资管理权限的管理员"""
    return current_admin 