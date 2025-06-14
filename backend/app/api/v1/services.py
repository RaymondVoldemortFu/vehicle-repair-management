from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_admin
from app.crud.service import service_crud
from app.models.admin import Admin
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=ServiceResponse, dependencies=[Depends(get_current_active_admin)])
def create_service(
    *,
    db: Session = Depends(get_db),
    service_in: ServiceCreate,
) -> Any:
    """
    创建服务项目 (管理员)
    """
    return service_crud.create(db=db, obj_in=service_in)


@router.get("/", response_model=PaginatedResponse[ServiceResponse], dependencies=[Depends(get_current_active_admin)])
def read_services(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
) -> Any:
    """
    获取服务项目列表 (分页, 管理员)
    """
    services = service_crud.get_multi(db, skip=pagination.get_offset(), limit=pagination.size)
    total = service_crud.count(db)
    return PaginatedResponse.create(items=services, total=total, page=pagination.page, size=pagination.size)


@router.get("/{service_id}", response_model=ServiceResponse, dependencies=[Depends(get_current_active_admin)])
def read_service(
    *,
    db: Session = Depends(get_db),
    service_id: int,
) -> Any:
    """
    获取单个服务项目详情 (管理员)
    """
    service = service_crud.get(db=db, id=service_id)
    if not service:
        raise HTTPException(status_code=404, detail="服务项目未找到")
    return service


@router.put("/{service_id}", response_model=ServiceResponse, dependencies=[Depends(get_current_active_admin)])
def update_service(
    *,
    db: Session = Depends(get_db),
    service_id: int,
    service_in: ServiceUpdate,
) -> Any:
    """
    更新服务项目 (管理员)
    """
    service = service_crud.get(db=db, id=service_id)
    if not service:
        raise HTTPException(status_code=404, detail="服务项目未找到")
    service = service_crud.update(db=db, db_obj=service, obj_in=service_in)
    return service


@router.delete("/{service_id}", response_model=MessageResponse, dependencies=[Depends(get_current_active_admin)])
def delete_service(
    *,
    db: Session = Depends(get_db),
    service_id: int,
) -> Any:
    """
    删除服务项目 (管理员)
    """
    service = service_crud.get(db=db, id=service_id)
    if not service:
        raise HTTPException(status_code=404, detail="服务项目未找到")
    service_crud.remove(db=db, id=service_id)
    return MessageResponse(message="服务项目删除成功") 