from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal

from app.models.wage import WageStatus
from app.schemas.repair_worker import RepairWorker

# Shared properties
class WageBase(BaseModel):
    period: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="工资周期 (YYYY-MM)")
    base_salary: Decimal = Field(..., ge=0, description="基本工资")
    work_days: int = Field(..., ge=0, description="工作天数")
    overtime_hours: Decimal = Field(..., ge=0, description="加班工时")
    overtime_pay: Decimal = Field(..., ge=0, description="加班费")
    commission: Decimal = Field(..., ge=0, description="提成")
    bonus: Decimal = Field(..., ge=0, description="奖金")
    deductions: Decimal = Field(..., ge=0, description="扣款")
    total_amount: Decimal = Field(..., ge=0, description="总支付金额")
    status: WageStatus = WageStatus.PENDING
    notes: Optional[str] = None

# Properties to receive on item creation
class WageCreate(WageBase):
    worker_id: int


# Properties to receive on item update
class WageUpdate(WageBase):
    pass


# Properties shared by models stored in DB
class WageInDBBase(WageBase):
    id: int
    worker_id: int
    pay_date: Optional[date] = None

    class Config:
        orm_mode = True


# Properties to return to client
class Wage(WageInDBBase):
    pass


class WageWithWorker(Wage):
    worker: RepairWorker


# Properties properties stored in DB
class WageInDB(WageInDBBase):
    pass 