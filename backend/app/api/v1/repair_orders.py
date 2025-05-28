from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_user, get_current_active_admin, get_current_active_worker
from app.crud.repair_order import repair_order_crud
from app.crud.user import user_crud
from app.crud.repair_worker import repair_worker_crud
from app.models.user import User
from app.models.admin import Admin
from app.models.repair_worker import RepairWorker
from app.models.repair_order import OrderStatus
from app.schemas.repair_order import (
    RepairOrderCreate, RepairOrderUpdate, RepairOrderResponse, 
    RepairOrderDetail, RepairOrderStatusUpdate
)
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=RepairOrderResponse)
def create_repair_order(
    *,
    db: Session = Depends(get_db),
    order_in: RepairOrderCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """创建维修订单"""
    # 验证用户只能为自己的车辆创建订单
    if order_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己的车辆创建维修订单"
        )
    
    order = repair_order_crud.create_with_order_number(db, obj_in=order_in)
    return order


@router.get("/my-orders", response_model=PaginatedResponse[RepairOrderResponse])
def read_my_repair_orders(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取当前用户的维修订单"""
    orders = repair_order_crud.get_by_user(
        db, user_id=current_user.id, skip=pagination.get_offset(), limit=pagination.size
    )
    
    # 计算总数
    total = len(repair_order_crud.get_by_user(db, user_id=current_user.id, skip=0, limit=10000))
    
    return PaginatedResponse.create(
        items=orders,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/worker-orders", response_model=PaginatedResponse[RepairOrderResponse])
def read_worker_orders(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """获取维修工人的订单（通过关联表）"""
    # 这里需要通过RepairOrderWorker表来查询
    # 暂时返回空列表，具体实现需要创建相应的CRUD方法
    return PaginatedResponse.create(
        items=[],
        total=0,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/{order_id}", response_model=RepairOrderDetail)
def read_repair_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取维修订单详情"""
    order = repair_order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修订单不存在"
        )
    
    # 验证用户只能查看自己的订单
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此维修订单"
        )
    
    return order


@router.put("/{order_id}/status", response_model=RepairOrderResponse)
def update_order_status(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    status_update: RepairOrderStatusUpdate,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新订单状态（管理员专用）"""
    order = repair_order_crud.update_status(
        db, 
        order_id=order_id, 
        status=status_update.status, 
        notes=status_update.internal_notes
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修订单不存在"
        )
    
    return order


# 管理员专用接口
@router.get("/", response_model=PaginatedResponse[RepairOrderResponse])
def read_repair_orders(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    status: OrderStatus = None,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取维修订单列表（管理员专用）"""
    if status:
        orders = repair_order_crud.get_by_status(
            db, status=status, skip=pagination.get_offset(), limit=pagination.size
        )
        total = len(repair_order_crud.get_by_status(db, status=status, skip=0, limit=10000))
    else:
        orders = repair_order_crud.get_multi(db, skip=pagination.get_offset(), limit=pagination.size)
        total = repair_order_crud.count(db)
    
    return PaginatedResponse.create(
        items=orders,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/admin/{order_id}", response_model=RepairOrderDetail)
def read_repair_order_admin(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取维修订单详情（管理员专用）"""
    order = repair_order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修订单不存在"
        )
    
    return order


@router.put("/admin/{order_id}", response_model=RepairOrderResponse)
def update_repair_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    order_in: RepairOrderUpdate,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新维修订单（管理员专用）"""
    order = repair_order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修订单不存在"
        )
    
    order = repair_order_crud.update(db, db_obj=order, obj_in=order_in)
    return order


@router.delete("/admin/{order_id}", response_model=MessageResponse)
def delete_repair_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """删除维修订单（管理员专用）"""
    order = repair_order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修订单不存在"
        )
    
    repair_order_crud.remove(db, id=order_id)
    return MessageResponse(message="维修订单删除成功")


@router.get("/statistics/overview", response_model=dict)
def get_order_statistics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取订单统计信息（管理员专用）"""
    stats = repair_order_crud.get_statistics(db)
    return stats 