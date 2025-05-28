from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_admin, get_current_super_admin
from app.crud.admin import admin_crud
from app.models.admin import Admin, AdminStatus
from app.schemas.admin import (
    AdminCreate, AdminUpdate, AdminResponse, 
    AdminDetail, AdminPasswordUpdate
)
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=AdminResponse)
def create_admin(
    *,
    db: Session = Depends(get_db),
    admin_in: AdminCreate,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """创建管理员（超级管理员专用）"""
    # 检查用户名是否已存在
    if admin_crud.get_by_username(db, username=admin_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if admin_in.email and admin_crud.get_by_email(db, email=admin_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    admin = admin_crud.create(db, obj_in=admin_in)
    return admin


@router.get("/", response_model=PaginatedResponse[AdminResponse])
def read_admins(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """获取管理员列表（超级管理员专用）"""
    admins = admin_crud.get_multi(db, skip=pagination.get_offset(), limit=pagination.size)
    total = admin_crud.count(db)
    
    return PaginatedResponse.create(
        items=admins,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/me", response_model=AdminDetail)
def read_current_admin_info(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取当前管理员信息"""
    return current_admin


@router.put("/me", response_model=AdminResponse)
def update_current_admin_info(
    *,
    db: Session = Depends(get_db),
    admin_in: AdminUpdate,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新当前管理员信息"""
    # 管理员只能更新部分信息（不包括用户名、权限等敏感信息）
    allowed_fields = {"name", "phone", "email"}
    update_data = {k: v for k, v in admin_in.dict(exclude_unset=True).items() if k in allowed_fields}
    
    # 如果更新邮箱，检查是否已存在
    if "email" in update_data and update_data["email"] != current_admin.email:
        existing_admin = admin_crud.get_by_email(db, email=update_data["email"])
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    admin = admin_crud.update(db, db_obj=current_admin, obj_in=update_data)
    return admin


@router.put("/me/password", response_model=MessageResponse)
def change_admin_password(
    *,
    db: Session = Depends(get_db),
    password_update: AdminPasswordUpdate,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """修改当前管理员密码"""
    # 验证旧密码
    if not admin_crud.verify_password(password_update.old_password, current_admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    hashed_password = admin_crud.get_password_hash(password_update.new_password)
    admin_crud.update(db, db_obj=current_admin, obj_in={"password_hash": hashed_password})
    
    return MessageResponse(message="密码修改成功")


@router.get("/{admin_id}", response_model=AdminDetail)
def read_admin(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """获取管理员详情（超级管理员专用）"""
    admin = admin_crud.get(db, id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    return admin


@router.put("/{admin_id}", response_model=AdminResponse)
def update_admin(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    admin_in: AdminUpdate,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """更新管理员信息（超级管理员专用）"""
    admin = admin_crud.get(db, id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    # 如果更新用户名，检查是否已存在
    if admin_in.username and admin_in.username != admin.username:
        existing_admin = admin_crud.get_by_username(db, username=admin_in.username)
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
    
    # 如果更新邮箱，检查是否已存在
    if admin_in.email and admin_in.email != admin.email:
        existing_admin = admin_crud.get_by_email(db, email=admin_in.email)
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    admin = admin_crud.update(db, db_obj=admin, obj_in=admin_in)
    return admin


@router.delete("/{admin_id}", response_model=MessageResponse)
def delete_admin(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """删除管理员（超级管理员专用）"""
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
    
    admin_crud.remove(db, id=admin_id)
    return MessageResponse(message="管理员删除成功")


@router.put("/{admin_id}/activate", response_model=AdminResponse)
def activate_admin(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """激活管理员（超级管理员专用）"""
    admin = admin_crud.get(db, id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    admin = admin_crud.update(db, db_obj=admin, obj_in={"status": AdminStatus.ACTIVE})
    return admin


@router.put("/{admin_id}/deactivate", response_model=AdminResponse)
def deactivate_admin(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """停用管理员（超级管理员专用）"""
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
    
    admin = admin_crud.update(db, db_obj=admin, obj_in={"status": AdminStatus.INACTIVE})
    return admin


@router.get("/search/username/{username}", response_model=AdminResponse)
def search_admin_by_username(
    *,
    db: Session = Depends(get_db),
    username: str,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """根据用户名搜索管理员（超级管理员专用）"""
    admin = admin_crud.get_by_username(db, username=username)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该用户名的管理员"
        )
    
    return admin


@router.get("/statistics/overview", response_model=dict)
def get_admin_statistics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """获取管理员统计信息（超级管理员专用）"""
    total_admins = admin_crud.count(db)
    active_admins = len(admin_crud.get_active_admins(db))
    super_admins = len(admin_crud.get_super_admins(db))
    
    return {
        "total_admins": total_admins,
        "active_admins": active_admins,
        "super_admins": super_admins,
        "inactive_admins": total_admins - active_admins
    } 