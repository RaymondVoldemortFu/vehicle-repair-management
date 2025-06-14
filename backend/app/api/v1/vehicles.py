from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_user, get_current_active_admin
from app.crud.vehicle import vehicle_crud
from app.models.user import User
from app.models.admin import Admin
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleDetail
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=VehicleResponse)
def create_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_in: VehicleCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """创建车辆"""
    # 检查车牌号是否已存在
    if vehicle_crud.get_by_license_plate(db, license_plate=vehicle_in.license_plate):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="车牌号已存在"
        )
    
    # 设置车辆所有者为当前用户
    vehicle_data = vehicle_in.dict()
    vehicle_data["owner_id"] = current_user.id
    
    vehicle = vehicle_crud.create(db, obj_in=vehicle_data)
    return vehicle


@router.get("/my-vehicles", response_model=List[VehicleResponse])
def read_my_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取当前用户的车辆列表"""
    vehicles = vehicle_crud.get_by_owner(db, owner_id=current_user.id)
    return vehicles


@router.get("/{vehicle_id}", response_model=VehicleDetail)
def read_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取车辆详情"""
    vehicle = vehicle_crud.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 验证用户只能查看自己的车辆
    if vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此车辆"
        )
    
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新车辆信息"""
    vehicle = vehicle_crud.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 验证用户只能更新自己的车辆
    if vehicle.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此车辆"
        )
    
    # 如果更新车牌号，检查是否已存在
    if vehicle_in.license_plate and vehicle_in.license_plate != vehicle.license_plate:
        existing_vehicle = vehicle_crud.get_by_license_plate(db, license_plate=vehicle_in.license_plate)
        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="车牌号已存在"
            )
    
    vehicle = vehicle_crud.update(db, db_obj=vehicle, obj_in=vehicle_in)
    return vehicle


@router.delete("/{vehicle_id}", response_model=MessageResponse)
def delete_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """删除车辆"""
    vehicle = vehicle_crud.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 验证用户只能删除自己的车辆
    if vehicle.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此车辆"
        )
    
    vehicle_crud.remove(db, id=vehicle_id)
    return MessageResponse(message="车辆删除成功")


# 管理员专用接口
@router.get("/", response_model=PaginatedResponse[VehicleResponse])
def read_vehicles(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取车辆列表（管理员专用）"""
    vehicles = vehicle_crud.get_multi(db, skip=pagination.get_offset(), limit=pagination.size)
    total = vehicle_crud.count(db)
    
    return PaginatedResponse.create(
        items=vehicles,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/admin/{vehicle_id}", response_model=VehicleDetail)
def read_vehicle_admin(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取车辆详情（管理员专用）"""
    vehicle = vehicle_crud.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    return vehicle


@router.put("/admin/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle_admin(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新车辆信息（管理员专用）"""
    vehicle = vehicle_crud.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 如果更新车牌号，检查是否已存在
    if vehicle_in.license_plate and vehicle_in.license_plate != vehicle.license_plate:
        existing_vehicle = vehicle_crud.get_by_license_plate(db, license_plate=vehicle_in.license_plate)
        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="车牌号已存在"
            )
    
    vehicle = vehicle_crud.update(db, db_obj=vehicle, obj_in=vehicle_in)
    return vehicle


@router.delete("/admin/{vehicle_id}", response_model=MessageResponse)
def delete_vehicle_admin(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """删除车辆（管理员专用）"""
    vehicle = vehicle_crud.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    vehicle_crud.remove(db, id=vehicle_id)
    return MessageResponse(message="车辆删除成功")


@router.get("/search/license-plate/{license_plate}", response_model=VehicleResponse)
def search_vehicle_by_license_plate(
    *,
    db: Session = Depends(get_db),
    license_plate: str,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """根据车牌号搜索车辆（管理员专用）"""
    vehicle = vehicle_crud.get_by_license_plate(db, license_plate=license_plate)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该车牌号的车辆"
        )
    
    return vehicle


@router.get("/statistics/overview", response_model=dict)
def get_vehicle_statistics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取车辆统计信息（管理员专用）"""
    total_vehicles = vehicle_crud.count(db)
    
    # 按品牌统计
    brand_stats = vehicle_crud.get_brand_statistics(db)
    
    return {
        "total_vehicles": total_vehicles,
        "brand_statistics": brand_stats
    } 