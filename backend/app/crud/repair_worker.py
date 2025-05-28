from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from passlib.context import CryptContext
from app.crud.base import CRUDBase
from app.models.repair_worker import RepairWorker, SkillType, WorkerStatus
from app.schemas.repair_worker import RepairWorkerCreate, RepairWorkerUpdate

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CRUDRepairWorker(CRUDBase[RepairWorker, RepairWorkerCreate, RepairWorkerUpdate]):
    def get_by_employee_id(self, db: Session, *, employee_id: str) -> Optional[RepairWorker]:
        """根据员工编号获取维修工人"""
        return db.query(RepairWorker).filter(
            and_(RepairWorker.employee_id == employee_id, RepairWorker.is_deleted == False)
        ).first()

    def get_by_skill_type(self, db: Session, *, skill_type: SkillType, skip: int = 0, limit: int = 100) -> List[RepairWorker]:
        """根据技能类型获取维修工人列表"""
        return db.query(RepairWorker).filter(
            and_(
                RepairWorker.skill_type == skill_type.value,
                RepairWorker.status == WorkerStatus.ACTIVE,
                RepairWorker.is_deleted == False
            )
        ).offset(skip).limit(limit).all()

    def get_available_workers(self, db: Session) -> List[RepairWorker]:
        """获取可用的维修工人"""
        return db.query(RepairWorker).filter(
            and_(
                RepairWorker.status == WorkerStatus.ACTIVE,
                RepairWorker.is_deleted == False
            )
        ).all()

    def is_active(self, worker: RepairWorker) -> bool:
        """检查维修工人是否活跃"""
        return worker.status == WorkerStatus.ACTIVE

    def create(self, db: Session, *, obj_in: RepairWorkerCreate) -> RepairWorker:
        """创建维修工人"""
        # 加密密码
        hashed_password = self.get_password_hash(obj_in.password)
        
        # 创建工人对象
        db_obj = RepairWorker(
            employee_id=obj_in.employee_id,
            name=obj_in.name,
            phone=obj_in.phone,
            email=obj_in.email,
            skill_type=obj_in.skill_type.value,
            skill_level=obj_in.skill_level,
            hourly_rate=obj_in.hourly_rate,
            hire_date=obj_in.hire_date,
            certifications=obj_in.certifications,
            hashed_password=hashed_password,
            status=WorkerStatus.ACTIVE
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)


repair_worker_crud = CRUDRepairWorker(RepairWorker)