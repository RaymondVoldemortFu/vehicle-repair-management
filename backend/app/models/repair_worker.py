from sqlalchemy import Column, Integer, String, Enum, Date, DECIMAL, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class SkillLevel(str, enum.Enum):
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    EXPERT = "expert"


class SkillType(str, enum.Enum):
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    BODYWORK = "bodywork"
    ENGINE = "engine"
    TRANSMISSION = "transmission"
    BRAKE = "brake"
    SUSPENSION = "suspension"
    AIR_CONDITIONING = "air_conditioning"


class WorkerStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


class RepairWorker(BaseModel):
    __tablename__ = "repair_workers"

    employee_id = Column(String(20), unique=True, nullable=False, index=True, comment="员工编号")
    name = Column(String(100), nullable=False, comment="姓名")
    phone = Column(String(20), nullable=False, comment="手机号码")
    email = Column(String(100), nullable=True, comment="邮箱")
    skill_type = Column(String(50), nullable=False, comment="技能类型")
    skill_level = Column(Enum(SkillLevel), nullable=False, comment="技能等级")
    hourly_rate = Column(DECIMAL(10, 2), nullable=False, comment="时薪")
    status = Column(Enum(WorkerStatus), default=WorkerStatus.ACTIVE, nullable=False, comment="状态")
    hire_date = Column(Date, nullable=False, comment="入职日期")
    certifications = Column(Text, nullable=True, comment="资质证书")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")

    # 关系
    order_assignments = relationship("RepairOrderWorker", back_populates="worker")
    wages = relationship("Wage", back_populates="worker")

    def __repr__(self):
        return f"<RepairWorker(id={self.id}, employee_id='{self.employee_id}', name='{self.name}')>" 