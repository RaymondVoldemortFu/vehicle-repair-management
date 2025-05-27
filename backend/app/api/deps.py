from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.settings import settings
from app.models.user import User
from app.models.admin import Admin
from app.models.worker import RepairWorker
from app.services.auth_service import AuthService

security = HTTPBearer()

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前普通用户"""
    user = AuthService.get_current_user_from_token(
        db, credentials.credentials, "user"
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_admin(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Admin:
    """获取当前管理员"""
    admin = AuthService.get_current_user_from_token(
        db, credentials.credentials, "admin"
    )
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin

def get_current_worker(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> RepairWorker:
    """获取当前维修工人"""
    worker = AuthService.get_current_user_from_token(
        db, credentials.credentials, "worker"
    )
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Worker authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return worker

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if current_user.status != "active":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# 权限检查装饰器
def require_roles(*roles):
    """角色权限检查装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 这里可以实现角色权限检查逻辑
            return func(*args, **kwargs)
        return wrapper
    return decorator