from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_admin, get_current_super_admin
from app.crud.admin import admin_crud
from app.models.admin import Admin, AdminStatus, AdminRole
from app.schemas.admin import (
    AdminCreate, AdminUpdate, AdminResponse, 
    AdminDetail, AdminPasswordUpdate
)
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse
from app.core.security import get_password_hash
from app.config.logging import get_api_logger

router = APIRouter()
logger = get_api_logger()


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


@router.put("/{admin_id}/reset-password", response_model=MessageResponse)
def reset_admin_password(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    new_password: str = Query(..., description="新密码"),
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """重置管理员密码（超级管理员专用）"""
    admin = admin_crud.get(db, id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    # 重置密码
    hashed_password = get_password_hash(new_password)
    admin_crud.update(db, db_obj=admin, obj_in={"password_hash": hashed_password})
    
    logger.info(f"超级管理员 {current_admin.username} 重置了管理员 {admin.username} 的密码")
    
    return MessageResponse(message="密码重置成功")


@router.put("/{admin_id}/permissions", response_model=AdminResponse)
def update_admin_permissions(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    permissions: dict,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """更新管理员权限（超级管理员专用）"""
    admin = admin_crud.get(db, id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    # 不能修改超级管理员的权限（除非是自己）
    if admin.role == AdminRole.SUPER_ADMIN and admin.id != current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能修改其他超级管理员的权限"
        )
    
    admin = admin_crud.update(db, db_obj=admin, obj_in={"permissions": permissions})
    
    logger.info(f"超级管理员 {current_admin.username} 更新了管理员 {admin.username} 的权限")
    
    return admin


@router.put("/{admin_id}/role", response_model=AdminResponse)
def update_admin_role(
    *,
    db: Session = Depends(get_db),
    admin_id: int,
    new_role: AdminRole,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """更新管理员角色（超级管理员专用）"""
    admin = admin_crud.get(db, id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    # 不能修改自己的角色
    if admin.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的角色"
        )
    
    # 如果要设置为超级管理员角色，需要额外检查
    if new_role == AdminRole.SUPER_ADMIN:
        # 可以在这里添加额外的安全检查
        logger.warning(f"超级管理员 {current_admin.username} 将管理员 {admin.username} 提升为超级管理员")
    
    admin = admin_crud.update(db, db_obj=admin, obj_in={"role": new_role})
    
    logger.info(f"超级管理员 {current_admin.username} 更新管理员 {admin.username} 的角色为 {new_role}")
    
    return admin


@router.get("/statistics/overview", response_model=dict)
def get_admin_statistics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """获取管理员统计信息（超级管理员专用）"""
    # 统计各角色管理员数量
    total_admins = admin_crud.count(db)
    super_admins = len(admin_crud.get_super_admins(db))
    active_admins = len(admin_crud.get_active_admins(db))
    
    # 统计各状态管理员数量
    from sqlalchemy import func
    status_stats = db.query(
        Admin.status,
        func.count(Admin.id).label('count')
    ).filter(Admin.is_deleted == False).group_by(Admin.status).all()
    
    status_distribution = {stat.status.value: stat.count for stat in status_stats}
    
    # 统计各角色管理员数量
    role_stats = db.query(
        Admin.role,
        func.count(Admin.id).label('count')
    ).filter(Admin.is_deleted == False).group_by(Admin.role).all()
    
    role_distribution = {stat.role.value: stat.count for stat in role_stats}
    
    return {
        "total_admins": total_admins,
        "super_admins": super_admins,
        "active_admins": active_admins,
        "status_distribution": status_distribution,
        "role_distribution": role_distribution
    }


@router.get("/activity/recent", response_model=List[dict])
def get_recent_admin_activity(
    db: Session = Depends(get_db),
    limit: int = Query(10, description="返回记录数量"),
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """获取最近管理员活动（超级管理员专用）"""
    # 获取最近登录的管理员
    recent_admins = db.query(Admin).filter(
        Admin.is_deleted == False,
        Admin.last_login.isnot(None)
    ).order_by(Admin.last_login.desc()).limit(limit).all()
    
    activity_list = []
    for admin in recent_admins:
        activity_list.append({
            "admin_id": admin.id,
            "username": admin.username,
            "name": admin.name,
            "role": admin.role.value,
            "last_login": admin.last_login,
            "status": admin.status.value
        })
    
    return activity_list


@router.post("/system/check", response_model=dict)
def system_health_check(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """系统健康检查（超级管理员专用）"""
    health_status = {
        "database": "healthy",
        "admin_system": "healthy",
        "super_admin_exists": False,
        "issues": []
    }
    
    try:
        # 检查数据库连接
        db.execute("SELECT 1")
        
        # 检查是否存在超级管理员
        super_admins = admin_crud.get_super_admins(db)
        if super_admins:
            health_status["super_admin_exists"] = True
        else:
            health_status["issues"].append("没有超级管理员账号")
            health_status["admin_system"] = "warning"
        
        # 检查是否有活跃的管理员
        active_admins = admin_crud.get_active_admins(db)
        if not active_admins:
            health_status["issues"].append("没有活跃的管理员账号")
            health_status["admin_system"] = "error"
        
    except Exception as e:
        health_status["database"] = "error"
        health_status["issues"].append(f"数据库连接失败: {str(e)}")
    
    # 设置总体状态
    if health_status["issues"]:
        health_status["overall"] = "warning" if health_status["database"] == "healthy" else "error"
    else:
        health_status["overall"] = "healthy"
    
    return health_status


@router.post("/system/create-super-admin", response_model=AdminResponse)
def create_emergency_super_admin(
    *,
    db: Session = Depends(get_db),
    admin_in: AdminCreate,
    current_admin: Admin = Depends(get_current_super_admin),
) -> Any:
    """创建紧急超级管理员（超级管理员专用）"""
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
    
    # 强制设置为超级管理员角色
    admin_data = admin_in.dict()
    admin_data["role"] = AdminRole.SUPER_ADMIN
    
    from app.schemas.admin import AdminCreate
    super_admin_create = AdminCreate(**admin_data)
    
    admin = admin_crud.create(db, obj_in=super_admin_create)
    
    logger.warning(f"超级管理员 {current_admin.username} 创建了紧急超级管理员账号: {admin.username}")
    
    return admin 