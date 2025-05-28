from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.crud.base import CRUDBase
from app.models.repair_worker import RepairWorker
from app.schemas.base import BaseSchema


class RepairWorkerCreate(BaseSchema):
    employee_id: str
    name: str
    phone: str
    email: Optional[str] = None
    skill_type: str
    skill_level: str
    hourly_rate: float
    hire_date: str
    certifications: Optional[str] = None


class RepairWorkerUpdate(BaseSchema):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    skill_type: Optional[str] = None
    skill_level: Optional[str] = None
    hourly_rate: Optional[float] = None
    status: Optional[str] = None
    certifications: Optional[str] = None


class CRUDRepairWorker(CRUDBase[RepairWorker, RepairWorkerCreate, RepairWorkerUpdate]):
    def get_by_employee_id(self, db: Session, *, employee_id: str) -> Optional[RepairWorker]:
        """根据员工编号获取维修工人"""
        return db.query(RepairWorker).filter(
            and_(RepairWorker.employee_id == employee_id, RepairWorker.is_deleted == False)
        ).first()

    def get_by_skill_type(self, db: Session, *, skill_type: str) -> List[RepairWorker]:
        """根据技能类型获取维修工人列表"""
        return db.query(RepairWorker).filter(
            and_(
                RepairWorker.skill_type == skill_type,
                RepairWorker.status == "active",
                RepairWorker.is_deleted == False
            )
        ).all()

    def get_available_workers(self, db: Session) -> List[RepairWorker]:
        """获取可用的维修工人"""
        return db.query(RepairWorker).filter(
            and_(
                RepairWorker.status == "active",
                RepairWorker.is_deleted == False
            )
        ).all()

    def is_active(self, worker: RepairWorker) -> bool:
        """检查维修工人是否活跃"""
        return worker.status == "active"


repair_worker_crud = CRUDRepairWorker(RepairWorker)