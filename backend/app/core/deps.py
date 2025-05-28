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