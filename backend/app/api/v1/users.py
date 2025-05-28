from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_user, get_current_active_admin
from app.crud.user import user_crud
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
    # 检查手机号是否已存在
    user = user_crud.get_by_phone(db, phone=user_in.phone)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已被注册"
        )
    
    # 检查邮箱是否已存在
    if user_in.email:
        user = user_crud.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )
    
    user = user_crud.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=UserProfile)
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
    # 检查手机号是否被其他用户使用
    if user_in.phone and user_in.phone != current_user.phone:
        existing_user = user_crud.get_by_phone(db, phone=user_in.phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被其他用户使用"
            )
    
    # 检查邮箱是否被其他用户使用
    if user_in.email and user_in.email != current_user.email:
        existing_user = user_crud.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被其他用户使用"
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
    if not user_crud.authenticate(db, phone=current_user.phone, password=password_data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    user_crud.update_password(db, user=current_user, new_password=password_data.new_password)
    return MessageResponse(message="密码修改成功")


# 管理员专用接口
@router.get("/", response_model=PaginatedResponse[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取用户列表（管理员专用）"""
    users = user_crud.get_multi(db, skip=pagination.get_offset(), limit=pagination.size)
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
    """获取指定用户信息（管理员专用）"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_crud.remove(db, id=user_id)
 