from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_admin
from app.crud.material import material_crud
from app.models.admin import Admin
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialResponse
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=MaterialResponse, dependencies=[Depends(get_current_active_admin)])
def create_material(
    *,
    db: Session = Depends(get_db),
    material_in: MaterialCreate,
) -> Any:
    """
    创建材料 (管理员)
    """
    return material_crud.create(db=db, obj_in=material_in)


@router.get("/", response_model=PaginatedResponse[MaterialResponse], dependencies=[Depends(get_current_active_admin)])
def read_materials(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
) -> Any:
    """
    获取材料列表 (分页, 管理员)
    """
    materials = material_crud.get_multi(db, skip=pagination.get_offset(), limit=pagination.size)
    total = material_crud.count(db)
    return PaginatedResponse.create(items=materials, total=total, page=pagination.page, size=pagination.size)


@router.get("/{material_id}", response_model=MaterialResponse, dependencies=[Depends(get_current_active_admin)])
def read_material(
    *,
    db: Session = Depends(get_db),
    material_id: int,
) -> Any:
    """
    获取单个材料详情 (管理员)
    """
    material = material_crud.get(db=db, id=material_id)
    if not material:
        raise HTTPException(status_code=404, detail="材料未找到")
    return material


@router.put("/{material_id}", response_model=MaterialResponse, dependencies=[Depends(get_current_active_admin)])
def update_material(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    material_in: MaterialUpdate,
) -> Any:
    """
    更新材料 (管理员)
    """
    material = material_crud.get(db=db, id=material_id)
    if not material:
        raise HTTPException(status_code=404, detail="材料未找到")
    material = material_crud.update(db=db, db_obj=material, obj_in=material_in)
    return material


@router.delete("/{material_id}", response_model=MessageResponse, dependencies=[Depends(get_current_active_admin)])
def delete_material(
    *,
    db: Session = Depends(get_db),
    material_id: int,
) -> Any:
    """
    删除材料 (管理员)
    """
    material = material_crud.get(db=db, id=material_id)
    if not material:
        raise HTTPException(status_code=404, detail="材料未找到")
    material_crud.remove(db=db, id=material_id)
    return MessageResponse(message="材料删除成功") 