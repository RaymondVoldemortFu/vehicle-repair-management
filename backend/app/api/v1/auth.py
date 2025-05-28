from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.settings import settings
from app.core.security import create_access_token
from app.crud.user import user_crud
from app.crud.admin import admin_crud
from app.crud.repair_worker import repair_worker_crud
from app.schemas.user import UserLogin
from app.schemas.base import MessageResponse

router = APIRouter()


@router.post("/login/user", response_model=dict)
def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """用户登录"""
    user = user_crud.authenticate(
        db, phone=user_credentials.phone, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误"
        )
    elif not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "email": user.email
        }
    }


@router.post("/login/admin", response_model=dict)
def login_admin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """管理员登录"""
    admin = admin_crud.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    elif not admin_crud.is_active(admin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理员账户已被禁用"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=admin.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin_info": {
            "id": admin.id,
            "username": admin.username,
            "name": admin.name,
            "role": admin.role,
            "email": admin.email
        }
    }


@router.post("/login/worker", response_model=dict)
def login_worker(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """维修工人登录（使用员工编号）"""
    worker = repair_worker_crud.get_by_employee_id(db, employee_id=form_data.username)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="员工编号不存在"
        )
    elif not repair_worker_crud.is_active(worker):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="维修工人账户已被禁用"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=worker.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "worker_info": {
            "id": worker.id,
            "employee_id": worker.employee_id,
            "name": worker.name,
            "skill_type": worker.skill_type,
            "skill_level": worker.skill_level
        }
    }


@router.post("/test-token", response_model=MessageResponse)
def test_token(
    current_user: Any = Depends()  # 这里可以根据需要使用不同的依赖
) -> Any:
    """测试令牌有效性"""
    return MessageResponse(message="令牌有效", success=True) 