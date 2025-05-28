from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_admin, get_current_active_user
from app.models.admin import Admin
from app.models.user import User
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()

# 模拟服务数据结构
MOCK_SERVICES = [
    {
        "id": 1,
        "name": "发动机维修",
        "description": "发动机故障诊断和维修",
        "price": 500.00,
        "duration_hours": 4,
        "category": "engine",
        "is_active": True
    },
    {
        "id": 2,
        "name": "刹车系统检修",
        "description": "刹车片更换和系统检查",
        "price": 200.00,
        "duration_hours": 2,
        "category": "brake",
        "is_active": True
    },
    {
        "id": 3,
        "name": "轮胎更换",
        "description": "轮胎更换和平衡调整",
        "price": 300.00,
        "duration_hours": 1,
        "category": "tire",
        "is_active": True
    },
    {
        "id": 4,
        "name": "空调维修",
        "description": "空调系统检修和制冷剂添加",
        "price": 150.00,
        "duration_hours": 2,
        "category": "ac",
        "is_active": True
    },
    {
        "id": 5,
        "name": "电路系统检修",
        "description": "车辆电路故障诊断和维修",
        "price": 250.00,
        "duration_hours": 3,
        "category": "electrical",
        "is_active": True
    }
]


@router.get("/", response_model=List[dict])
def read_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取服务列表（用户可查看）"""
    # 返回活跃的服务
    active_services = [service for service in MOCK_SERVICES if service["is_active"]]
    return active_services


@router.get("/{service_id}", response_model=dict)
def read_service(
    *,
    db: Session = Depends(get_db),
    service_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取服务详情"""
    service = next((s for s in MOCK_SERVICES if s["id"] == service_id), None)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    if not service["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务已停用"
        )
    
    return service


@router.get("/category/{category}", response_model=List[dict])
def read_services_by_category(
    *,
    db: Session = Depends(get_db),
    category: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """根据类别获取服务列表"""
    services = [
        service for service in MOCK_SERVICES 
        if service["category"] == category and service["is_active"]
    ]
    return services


# 管理员专用接口
@router.get("/admin/all", response_model=List[dict])
def read_all_services_admin(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取所有服务列表（管理员专用）"""
    return MOCK_SERVICES


@router.post("/admin/", response_model=dict)
def create_service(
    *,
    db: Session = Depends(get_db),
    service_data: dict,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """创建服务（管理员专用）"""
    # 生成新ID
    new_id = max([s["id"] for s in MOCK_SERVICES]) + 1 if MOCK_SERVICES else 1
    
    new_service = {
        "id": new_id,
        "name": service_data.get("name"),
        "description": service_data.get("description"),
        "price": service_data.get("price"),
        "duration_hours": service_data.get("duration_hours"),
        "category": service_data.get("category"),
        "is_active": service_data.get("is_active", True)
    }
    
    MOCK_SERVICES.append(new_service)
    return new_service


@router.put("/admin/{service_id}", response_model=dict)
def update_service(
    *,
    db: Session = Depends(get_db),
    service_id: int,
    service_data: dict,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新服务（管理员专用）"""
    service_index = next((i for i, s in enumerate(MOCK_SERVICES) if s["id"] == service_id), None)
    if service_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    # 更新服务信息
    for key, value in service_data.items():
        if key in MOCK_SERVICES[service_index]:
            MOCK_SERVICES[service_index][key] = value
    
    return MOCK_SERVICES[service_index]


@router.delete("/admin/{service_id}", response_model=MessageResponse)
def delete_service(
    *,
    db: Session = Depends(get_db),
    service_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """删除服务（管理员专用）"""
    service_index = next((i for i, s in enumerate(MOCK_SERVICES) if s["id"] == service_id), None)
    if service_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    MOCK_SERVICES.pop(service_index)
    return MessageResponse(message="服务删除成功")


@router.get("/admin/statistics/overview", response_model=dict)
def get_service_statistics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取服务统计信息（管理员专用）"""
    total_services = len(MOCK_SERVICES)
    active_services = len([s for s in MOCK_SERVICES if s["is_active"]])
    
    # 按类别统计
    categories = {}
    for service in MOCK_SERVICES:
        category = service["category"]
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    # 价格统计
    prices = [s["price"] for s in MOCK_SERVICES if s["is_active"]]
    avg_price = sum(prices) / len(prices) if prices else 0
    
    return {
        "total_services": total_services,
        "active_services": active_services,
        "inactive_services": total_services - active_services,
        "category_distribution": categories,
        "average_price": round(avg_price, 2),
        "price_range": {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0
        }
    } 