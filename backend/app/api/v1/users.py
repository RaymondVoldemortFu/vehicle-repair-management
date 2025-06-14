from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_user, get_current_active_admin
from app.crud.user import user_crud
from app.crud.repair_order import repair_order_crud
from app.crud.vehicle import vehicle_crud
from app.models.user import User
from app.models.admin import Admin
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserProfile, PasswordChange
)
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """用户注册"""
    # 检查用户名是否已存在
    user = user_crud.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被注册"
        )
    
    user = user_crud.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新当前用户信息"""
    # 检查用户名是否被其他用户使用
    if user_in.username and user_in.username != current_user.username:
        existing_user = user_crud.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被其他用户使用"
            )
    
    user = user_crud.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    *,
    db: Session = Depends(get_db),
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """修改密码"""
    # 验证旧密码
    if not user_crud.authenticate(db, username=current_user.username, password=password_data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    user_crud.update_password(db, user=current_user, new_password=password_data.new_password)
    return MessageResponse(message="密码修改成功")


@router.get("/me/stats", response_model=dict)
def read_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取当前用户统计信息"""
    # 获取用户的订单统计
    user_orders = repair_order_crud.get_by_user(db, user_id=current_user.id, skip=0, limit=1000)
    completed_orders = len([order for order in user_orders if order.status == 'completed'])
    user_vehicles = vehicle_crud.get_by_owner(db, owner_id=current_user.id)
    
    return {
        "total_orders": len(user_orders),
        "completed_orders": completed_orders,
        "total_vehicles": len(user_vehicles)
    }


# 管理员专用接口
@router.get("/", response_model=PaginatedResponse[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取用户列表（管理员专用）"""
    users = user_crud.get_multi(
        db, skip=pagination.get_offset(), limit=pagination.size
    )
    total = user_crud.count(db)
    
    return PaginatedResponse.create(
        items=users,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """根据ID获取用户（管理员专用）"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新用户信息（管理员专用）"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查用户名是否被其他用户使用
    if user_in.username and user_in.username != user.username:
        existing_user = user_crud.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被其他用户使用"
            )
    
    user = user_crud.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """删除用户（管理员专用）"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user_crud.remove(db, id=user_id)
    return MessageResponse(message="用户删除成功")
 