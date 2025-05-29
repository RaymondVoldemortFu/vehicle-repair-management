from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.config import settings
from app.crud import user as user_crud
from app.crud import admin as admin_crud
from app.crud import repair_worker as repair_worker_crud
from app.schemas.token import Token
from app.schemas.user import User
from app.schemas.admin import Admin
from app.schemas.repair_worker import RepairWorker
from app.config.logging import get_api_logger, log_api_call, log_security_event

router = APIRouter()
logger = get_api_logger()

@router.post("/login/user", response_model=Token)
@log_api_call
def login_user(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    用户登录
    """
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    logger.info(f"用户登录尝试 - 用户名: {form_data.username}, IP: {client_ip}")
    
    # 验证用户凭据
    user = user_crud.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        logger.warning(f"用户登录失败 - 无效凭据, 用户名: {form_data.username}, IP: {client_ip}")
        log_security_event(
            "登录失败", 
            f"无效凭据 - 用户名: {form_data.username}, IP: {client_ip}, User-Agent: {user_agent}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    # 检查用户状态
    if not user_crud.is_active(user):
        logger.warning(f"用户登录失败 - 账户未激活, 用户ID: {user.id}, IP: {client_ip}")
        log_security_event(
            "登录失败", 
            f"账户未激活 - 用户ID: {user.id}, IP: {client_ip}", 
            user.id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户未激活",
        )
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    logger.info(f"用户登录成功 - 用户ID: {user.id}, 姓名: {user.name}, IP: {client_ip}")
    log_security_event(
        "登录成功", 
        f"用户登录 - 用户ID: {user.id}, IP: {client_ip}, User-Agent: {user_agent}", 
        user.id
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "phone": user.phone,
            "email": user.email,
            "status": user.status
        }
    }

@router.post("/login/admin", response_model=Token)
@log_api_call
def login_admin(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    管理员登录
    """
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    logger.info(f"管理员登录尝试 - 用户名: {form_data.username}, IP: {client_ip}")
    
    # 验证管理员凭据
    admin = admin_crud.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not admin:
        logger.warning(f"管理员登录失败 - 无效凭据, 用户名: {form_data.username}, IP: {client_ip}")
        log_security_event(
            "管理员登录失败", 
            f"无效凭据 - 用户名: {form_data.username}, IP: {client_ip}, User-Agent: {user_agent}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    # 检查管理员状态
    if not admin_crud.is_active(admin):
        logger.warning(f"管理员登录失败 - 账户未激活, 管理员ID: {admin.id}, IP: {client_ip}")
        log_security_event(
            "管理员登录失败", 
            f"账户未激活 - 管理员ID: {admin.id}, IP: {client_ip}", 
            admin.id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户未激活",
        )
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        admin.id, expires_delta=access_token_expires, user_type="admin"
    )
    
    logger.info(f"管理员登录成功 - 管理员ID: {admin.id}, 用户名: {admin.username}, IP: {client_ip}")
    log_security_event(
        "管理员登录成功", 
        f"管理员登录 - 管理员ID: {admin.id}, IP: {client_ip}, User-Agent: {user_agent}", 
        admin.id
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin_info": {
            "id": admin.id,
            "username": admin.username,
            "name": admin.name,
            "role": admin.role,
            "status": admin.status
        }
    }

@router.post("/login/worker", response_model=Token)
@log_api_call
def login_worker(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    维修工人登录
    """
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    logger.info(f"维修工人登录尝试 - 工号: {form_data.username}, IP: {client_ip}")
    
    # 验证工人凭据
    worker = repair_worker_crud.authenticate(
        db, employee_id=form_data.username, password=form_data.password
    )
    if not worker:
        logger.warning(f"维修工人登录失败 - 无效凭据, 工号: {form_data.username}, IP: {client_ip}")
        log_security_event(
            "维修工人登录失败", 
            f"无效凭据 - 工号: {form_data.username}, IP: {client_ip}, User-Agent: {user_agent}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="工号或密码错误",
        )
    
    # 检查工人状态
    if not repair_worker_crud.is_active(worker):
        logger.warning(f"维修工人登录失败 - 账户未激活, 工人ID: {worker.id}, IP: {client_ip}")
        log_security_event(
            "维修工人登录失败", 
            f"账户未激活 - 工人ID: {worker.id}, IP: {client_ip}", 
            worker.id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户未激活",
        )
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        worker.id, expires_delta=access_token_expires, user_type="worker"
    )
    
    logger.info(f"维修工人登录成功 - 工人ID: {worker.id}, 姓名: {worker.name}, IP: {client_ip}")
    log_security_event(
        "维修工人登录成功", 
        f"维修工人登录 - 工人ID: {worker.id}, IP: {client_ip}, User-Agent: {user_agent}", 
        worker.id
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "worker_info": {
            "id": worker.id,
            "employee_id": worker.employee_id,
            "name": worker.name,
            "skill_type": worker.skill_type,
            "status": worker.status
        }
    }

@router.post("/test-token")
@log_api_call
def test_token(
    request: Request,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    测试访问令牌
    """
    client_ip = request.client.host
    logger.info(f"令牌验证成功 - 用户ID: {current_user.id}, IP: {client_ip}")
    
    return {"message": "令牌有效", "user_id": current_user.id} 