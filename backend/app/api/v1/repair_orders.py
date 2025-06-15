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
    RepairOrderDetail, RepairOrderStatusUpdate, RepairOrderComplete
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
    user_id = current_user.id
    
    order = repair_order_crud.create_with_order_number(db, obj_in=order_in, user_id=user_id)
    return order


@router.get("/my-orders", response_model=PaginatedResponse[RepairOrderDetail])
def read_my_repair_orders(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取当前用户的维修订单"""
    orders = repair_order_crud.get_by_user_with_details(
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


@router.get("/worker-orders", response_model=PaginatedResponse[RepairOrderDetail])
def read_worker_orders(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """获取维修工人的订单（通过关联表）"""
    orders, total = repair_order_crud.get_by_worker_with_details(
        db, worker_id=current_worker.id, skip=pagination.get_offset(), limit=pagination.size
    )
    
    return PaginatedResponse.create(
        items=orders,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/available", response_model=PaginatedResponse[RepairOrderDetail])
def read_available_orders(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """获取可接取的订单列表（状态为待处理）"""
    orders = repair_order_crud.get_by_status_with_details(
        db, status=OrderStatus.PENDING, skip=pagination.get_offset(), limit=pagination.size
    )
    total = repair_order_crud.count_by_status(db, status=OrderStatus.PENDING)

    return PaginatedResponse.create(
        items=orders,
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get("/statistics/overview", response_model=dict)
def get_order_statistics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取订单统计信息（管理员专用）"""
    stats = repair_order_crud.get_statistics(db)
    return stats


@router.put("/worker-orders/{order_id}/status", response_model=RepairOrderResponse)
def update_order_status_worker(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    status_update: RepairOrderStatusUpdate,
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """更新订单状态（维修工专用）"""
    # 验证订单是否分配给当前工人
    order = repair_order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    is_assigned = any(worker.id == current_worker.id for worker in order.assigned_workers)
    if not is_assigned:
        raise HTTPException(status_code=403, detail="无权操作此订单")

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


@router.post("/worker-orders/{order_id}/complete", response_model=RepairOrderResponse)
def complete_order_with_materials(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    completion_data: RepairOrderComplete,
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """
    工人完成订单，提交工时和使用的材料。
    """
    order = repair_order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    try:
        order = repair_order_crud.complete_order(
            db=db, order=order, completion_data=completion_data, worker_id=current_worker.id
        )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{order_id}/accept", response_model=RepairOrderResponse)
def accept_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """维修工接受订单"""
    try:
        order = repair_order_crud.accept_order(db, order_id=order_id, worker_id=current_worker.id)
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{order_id}", response_model=RepairOrderDetail)
def read_repair_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取维修订单详情"""
    order = repair_order_crud.get_with_details(db, id=order_id)
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


@router.put("/{order_id}/reject", response_model=RepairOrderResponse)
def reject_repair_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """
    工人拒绝维修订单
    """
    try:
        order = repair_order_crud.reject_order(db=db, order_id=order_id, worker_id=current_worker.id)
        if not order:
            raise HTTPException(status_code=404, detail="未找到订单或无法拒绝")
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 管理员专用接口
@router.get("/", response_model=PaginatedResponse[RepairOrderDetail])
def read_repair_orders(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    status: OrderStatus = None,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取维修订单列表（管理员专用）"""
    if status:
        orders = repair_order_crud.get_by_status_with_details(
            db, status=status, skip=pagination.get_offset(), limit=pagination.size
        )
        total = len(repair_order_crud.get_by_status(db, status=status, skip=0, limit=10000))
    else:
        orders = repair_order_crud.get_multi_with_details(db, skip=pagination.get_offset(), limit=pagination.size)
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
    order = repair_order_crud.get_with_details(db, id=order_id)
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
    
    order = repair_order_crud.remove(db, id=order_id)
    return MessageResponse(message="维修订单删除成功") 