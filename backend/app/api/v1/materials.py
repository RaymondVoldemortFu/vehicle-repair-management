from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_admin, get_current_active_user
from app.models.admin import Admin
from app.models.user import User
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()

# 模拟材料数据结构
MOCK_MATERIALS = [
    {
        "id": 1,
        "name": "机油",
        "description": "5W-30全合成机油",
        "unit_price": 50.00,
        "stock_quantity": 100,
        "unit": "升",
        "category": "lubricant",
        "supplier": "壳牌",
        "is_active": True
    },
    {
        "id": 2,
        "name": "刹车片",
        "description": "前轮刹车片套装",
        "unit_price": 120.00,
        "stock_quantity": 50,
        "unit": "套",
        "category": "brake_parts",
        "supplier": "博世",
        "is_active": True
    },
    {
        "id": 3,
        "name": "轮胎",
        "description": "205/55R16轮胎",
        "unit_price": 400.00,
        "stock_quantity": 20,
        "unit": "条",
        "category": "tire",
        "supplier": "米其林",
        "is_active": True
    },
    {
        "id": 4,
        "name": "空气滤芯",
        "description": "发动机空气滤芯",
        "unit_price": 30.00,
        "stock_quantity": 80,
        "unit": "个",
        "category": "filter",
        "supplier": "曼牌",
        "is_active": True
    },
    {
        "id": 5,
        "name": "火花塞",
        "description": "铱金火花塞",
        "unit_price": 25.00,
        "stock_quantity": 60,
        "unit": "个",
        "category": "ignition",
        "supplier": "NGK",
        "is_active": True
    }
]


@router.get("/", response_model=List[dict])
def read_materials(
    db: Session = Depends(get_db),
    category: str = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取材料列表（用户可查看）"""
    materials = [material for material in MOCK_MATERIALS if material["is_active"]]
    
    if category:
        materials = [m for m in materials if m["category"] == category]
    
    # 用户只能看到基本信息，不包括库存数量
    user_materials = []
    for material in materials:
        user_material = {
            "id": material["id"],
            "name": material["name"],
            "description": material["description"],
            "unit_price": material["unit_price"],
            "unit": material["unit"],
            "category": material["category"],
            "supplier": material["supplier"]
        }
        user_materials.append(user_material)
    
    return user_materials


@router.get("/{material_id}", response_model=dict)
def read_material(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取材料详情"""
    material = next((m for m in MOCK_MATERIALS if m["id"] == material_id), None)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="材料不存在"
        )
    
    if not material["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="材料已停用"
        )
    
    # 用户只能看到基本信息
    return {
        "id": material["id"],
        "name": material["name"],
        "description": material["description"],
        "unit_price": material["unit_price"],
        "unit": material["unit"],
        "category": material["category"],
        "supplier": material["supplier"]
    }


@router.get("/category/{category}", response_model=List[dict])
def read_materials_by_category(
    *,
    db: Session = Depends(get_db),
    category: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """根据类别获取材料列表"""
    materials = [
        material for material in MOCK_MATERIALS 
        if material["category"] == category and material["is_active"]
    ]
    
    # 用户只能看到基本信息
    user_materials = []
    for material in materials:
        user_material = {
            "id": material["id"],
            "name": material["name"],
            "description": material["description"],
            "unit_price": material["unit_price"],
            "unit": material["unit"],
            "category": material["category"],
            "supplier": material["supplier"]
        }
        user_materials.append(user_material)
    
    return user_materials


# 管理员专用接口
@router.get("/admin/all", response_model=List[dict])
def read_all_materials_admin(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取所有材料列表（管理员专用）"""
    return MOCK_MATERIALS


@router.get("/admin/low-stock", response_model=List[dict])
def read_low_stock_materials(
    db: Session = Depends(get_db),
    threshold: int = 20,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取库存不足的材料（管理员专用）"""
    low_stock_materials = [
        material for material in MOCK_MATERIALS 
        if material["stock_quantity"] <= threshold and material["is_active"]
    ]
    return low_stock_materials


@router.post("/admin/", response_model=dict)
def create_material(
    *,
    db: Session = Depends(get_db),
    material_data: dict,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """创建材料（管理员专用）"""
    # 生成新ID
    new_id = max([m["id"] for m in MOCK_MATERIALS]) + 1 if MOCK_MATERIALS else 1
    
    new_material = {
        "id": new_id,
        "name": material_data.get("name"),
        "description": material_data.get("description"),
        "unit_price": material_data.get("unit_price"),
        "stock_quantity": material_data.get("stock_quantity", 0),
        "unit": material_data.get("unit"),
        "category": material_data.get("category"),
        "supplier": material_data.get("supplier"),
        "is_active": material_data.get("is_active", True)
    }
    
    MOCK_MATERIALS.append(new_material)
    return new_material


@router.put("/admin/{material_id}", response_model=dict)
def update_material(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    material_data: dict,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新材料（管理员专用）"""
    material_index = next((i for i, m in enumerate(MOCK_MATERIALS) if m["id"] == material_id), None)
    if material_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="材料不存在"
        )
    
    # 更新材料信息
    for key, value in material_data.items():
        if key in MOCK_MATERIALS[material_index]:
            MOCK_MATERIALS[material_index][key] = value
    
    return MOCK_MATERIALS[material_index]


@router.put("/admin/{material_id}/stock", response_model=dict)
def update_material_stock(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    quantity_change: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新材料库存（管理员专用）"""
    material_index = next((i for i, m in enumerate(MOCK_MATERIALS) if m["id"] == material_id), None)
    if material_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="材料不存在"
        )
    
    # 更新库存
    new_quantity = MOCK_MATERIALS[material_index]["stock_quantity"] + quantity_change
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="库存不足"
        )
    
    MOCK_MATERIALS[material_index]["stock_quantity"] = new_quantity
    return MOCK_MATERIALS[material_index]


@router.delete("/admin/{material_id}", response_model=MessageResponse)
def delete_material(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """删除材料（管理员专用）"""
    material_index = next((i for i, m in enumerate(MOCK_MATERIALS) if m["id"] == material_id), None)
    if material_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="材料不存在"
        )
    
    MOCK_MATERIALS.pop(material_index)
    return MessageResponse(message="材料删除成功")


@router.get("/admin/statistics/overview", response_model=dict)
def get_material_statistics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取材料统计信息（管理员专用）"""
    total_materials = len(MOCK_MATERIALS)
    active_materials = len([m for m in MOCK_MATERIALS if m["is_active"]])
    
    # 库存统计
    total_stock_value = sum(m["unit_price"] * m["stock_quantity"] for m in MOCK_MATERIALS if m["is_active"])
    low_stock_count = len([m for m in MOCK_MATERIALS if m["stock_quantity"] <= 20 and m["is_active"]])
    
    # 按类别统计
    categories = {}
    for material in MOCK_MATERIALS:
        if material["is_active"]:
            category = material["category"]
            if category not in categories:
                categories[category] = {"count": 0, "value": 0}
            categories[category]["count"] += 1
            categories[category]["value"] += material["unit_price"] * material["stock_quantity"]
    
    return {
        "total_materials": total_materials,
        "active_materials": active_materials,
        "inactive_materials": total_materials - active_materials,
        "total_stock_value": round(total_stock_value, 2),
        "low_stock_count": low_stock_count,
        "category_distribution": categories
    } 