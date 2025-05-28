from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from app.schemas.base import BaseResponse, BaseSchema
from app.models.repair_worker import SkillLevel, SkillType, WorkerStatus


class RepairWorkerBase(BaseSchema):
    employee_id: str = Field(..., min_length=3, max_length=20, description="工号")
    name: str = Field(..., min_length=1, max_length=100, description="工人姓名")
    skill_type: SkillType = Field(..., description="技能类型")
    skill_level: SkillLevel = Field(..., description="技能等级")
    phone: Optional[str] = Field(None, min_length=11, max_length=20, description="手机号码")
    email: Optional[str] = Field(None, description="邮箱地址")
    hourly_rate: Decimal = Field(..., description="时薪")
    hire_date: date = Field(..., description="入职日期")
    certifications: Optional[str] = Field(None, description="资质证书")


class RepairWorkerCreate(RepairWorkerBase):
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class RepairWorkerUpdate(BaseSchema):
    employee_id: Optional[str] = Field(None, min_length=3, max_length=20, description="工号")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="工人姓名")
    skill_type: Optional[SkillType] = Field(None, description="技能类型")
    skill_level: Optional[SkillLevel] = Field(None, description="技能等级")
    phone: Optional[str] = Field(None, min_length=11, max_length=20, description="手机号码")
    email: Optional[str] = Field(None, description="邮箱地址")
    hourly_rate: Optional[Decimal] = Field(None, description="时薪")
    status: Optional[WorkerStatus] = Field(None, description="状态")
    hire_date: Optional[date] = Field(None, description="入职日期")
    certifications: Optional[str] = Field(None, description="资质证书")


class RepairWorkerResponse(BaseResponse):
    employee_id: str
    name: str
    skill_type: SkillType
    skill_level: SkillLevel
    phone: Optional[str]
    email: Optional[str]
    hourly_rate: Decimal
    status: WorkerStatus
    hire_date: date
    certifications: Optional[str]


class RepairWorkerDetail(RepairWorkerResponse):
    """维修工人详细信息"""
    pass


class RepairWorkerLogin(BaseSchema):
    employee_id: str = Field(..., description="工号")
    password: str = Field(..., description="密码")


class RepairWorker(RepairWorkerResponse):
    """维修工人完整信息"""
    pass


class RepairWorkerPasswordUpdate(BaseSchema):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class PasswordChange(BaseSchema):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class WorkerSkillUpdate(BaseSchema):
    skill_type: SkillType = Field(..., description="技能类型")
    skill_level: Optional[SkillLevel] = Field(None, description="技能等级")
    certification: Optional[str] = Field(None, description="认证信息") 