from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_admin, get_current_active_worker
from app.crud.repair_worker import repair_worker_crud
from app.crud.wage import wage_crud
from app.models.admin import Admin
from app.models.repair_worker import RepairWorker, SkillType
from app.schemas.repair_worker import (
    RepairWorkerCreate, RepairWorkerUpdate, RepairWorkerResponse, 
    RepairWorkerDetail, RepairWorkerPasswordUpdate, RepairWorker as RepairWorkerSchema
)
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse
from app.schemas.wage import Wage
from app import schemas

router = APIRouter()


@router.post("/", response_model=RepairWorkerResponse)
def create_repair_worker(
    *,
    db: Session = Depends(get_db),
    worker_in: RepairWorkerCreate,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """创建维修工人（管理员专用）"""
    # 检查工号是否已存在
    if repair_worker_crud.get_by_employee_id(db, employee_id=worker_in.employee_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="工号已存在"
        )
    
    worker = repair_worker_crud.create(db, obj_in=worker_in)
    return worker


@router.get("/", response_model=PaginatedResponse[RepairWorkerResponse])
def read_repair_workers(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    skill_type: SkillType = None,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取维修工人列表（管理员专用）"""
    if skill_type:
        workers = repair_worker_crud.get_by_skill_type(
            db, skill_type=skill_type, skip=pagination.get_offset(), limit=pagination.size
        )
        total = len(repair_worker_crud.get_by_skill_type(db, skill_type=skill_type, skip=0, limit=10000))
    else:
        workers = repair_worker_crud.get_multi(db, skip=pagination.get_offset(), limit=pagination.size)
        total = repair_worker_crud.count(db)
    
    return PaginatedResponse.create(
        items=workers,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/available", response_model=List[RepairWorkerResponse])
def read_available_workers(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取可用的维修工人列表（管理员专用）"""
    workers = repair_worker_crud.get_available_workers(db)
    return workers


@router.get("/me", response_model=RepairWorkerDetail)
def read_current_worker_info(
    db: Session = Depends(get_db),
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """获取当前维修工人信息"""
    return RepairWorkerSchema.from_orm(current_worker)


@router.put("/me", response_model=RepairWorkerResponse)
def update_current_worker_info(
    *,
    db: Session = Depends(get_db),
    worker_in: RepairWorkerUpdate,
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """更新当前维修工人信息"""
    # 工人只能更新部分信息（不包括工号、技能等级等敏感信息）
    allowed_fields = {"name", "phone", "email"}
    update_data = {k: v for k, v in worker_in.dict(exclude_unset=True).items() if k in allowed_fields}
    
    worker = repair_worker_crud.update(db, db_obj=current_worker, obj_in=update_data)
    return RepairWorkerSchema.from_orm(worker)


@router.put("/me/password", response_model=MessageResponse)
def change_worker_password(
    *,
    db: Session = Depends(get_db),
    password_update: RepairWorkerPasswordUpdate,
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """修改当前维修工人密码"""
    # 验证旧密码
    if not repair_worker_crud.verify_password(password_update.old_password, current_worker.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    hashed_password = repair_worker_crud.get_password_hash(password_update.new_password)
    repair_worker_crud.update(db, db_obj=current_worker, obj_in={"hashed_password": hashed_password})
    
    return MessageResponse(message="密码修改成功")


@router.get("/my-wages", response_model=List[Wage])
def read_my_wages(
    *,
    db: Session = Depends(get_db),
    current_worker: RepairWorker = Depends(get_current_active_worker),
    start_date: Optional[str] = Query(None, description="开始月份 (YYYY-MM)", regex=r"^\d{4}-\d{2}$"),
    end_date: Optional[str] = Query(None, description="结束月份 (YYYY-MM)", regex=r"^\d{4}-\d{2}$"),
) -> Any:
    """
    获取当前登录工人的工资记录
    """
    wages = wage_crud.get_by_worker(
        db,
        worker_id=current_worker.id,
        start_date=start_date,
        end_date=end_date
    )
    return wages


@router.get("/search/employee-id/{employee_id}", response_model=RepairWorkerResponse)
def search_worker_by_employee_id(
    *,
    db: Session = Depends(get_db),
    employee_id: str,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """根据工号搜索维修工人（管理员专用）"""
    worker = repair_worker_crud.get_by_employee_id(db, employee_id=employee_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该工号的维修工人"
        )
    
    return RepairWorkerSchema.from_orm(worker)


@router.get("/statistics/overview", response_model=dict)
def get_worker_statistics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取维修工人统计信息（管理员专用）"""
    total_workers = repair_worker_crud.count(db)
    available_workers = len(repair_worker_crud.get_available_workers(db))
    
    # 按技能类型统计
    skill_stats = {}
    for skill_type in SkillType:
        workers = repair_worker_crud.get_by_skill_type(db, skill_type=skill_type)
        skill_stats[skill_type.value] = len(workers)
    
    return {
        "total_workers": total_workers,
        "available_workers": available_workers,
        "skill_statistics": skill_stats
    }


@router.get("/{worker_id}", response_model=RepairWorkerDetail)
def read_repair_worker(
    *,
    db: Session = Depends(get_db),
    worker_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取维修工人详情（管理员专用）"""
    worker = repair_worker_crud.get(db, id=worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修工人不存在"
        )
    
    return RepairWorkerSchema.from_orm(worker)


@router.put("/{worker_id}", response_model=RepairWorkerResponse)
def update_repair_worker(
    *,
    db: Session = Depends(get_db),
    worker_id: int,
    worker_in: RepairWorkerUpdate,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新维修工人信息（管理员专用）"""
    worker = repair_worker_crud.get(db, id=worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修工人不存在"
        )
    
    # 如果更新工号，检查是否已存在
    if worker_in.employee_id and worker_in.employee_id != worker.employee_id:
        existing_worker = repair_worker_crud.get_by_employee_id(db, employee_id=worker_in.employee_id)
        if existing_worker:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="工号已存在"
            )
    
    worker = repair_worker_crud.update(db, db_obj=worker, obj_in=worker_in)
    return RepairWorkerSchema.from_orm(worker)


@router.delete("/{worker_id}", response_model=MessageResponse)
def delete_repair_worker(
    *,
    db: Session = Depends(get_db),
    worker_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """删除维修工人（管理员专用）"""
    worker = repair_worker_crud.get(db, id=worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维修工人不存在"
        )
    
    repair_worker_crud.remove(db, id=worker_id)
    return MessageResponse(message="维修工人删除成功") 