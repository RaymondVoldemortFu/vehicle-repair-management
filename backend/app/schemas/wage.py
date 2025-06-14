from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal

from app.models.wage import WageStatus

# Shared properties
class WageBase(BaseModel):
    pay_period: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="支付周期 (YYYY-MM)")
    total_hours: Optional[Decimal] = Field(None, ge=0, description="总工时")
    base_salary: Optional[Decimal] = Field(None, ge=0, description="基本工资")
    overtime_pay: Optional[Decimal] = Field(None, ge=0, description="加班费")
    bonus: Optional[Decimal] = Field(None, ge=0, description="奖金")
    total_payment: Optional[Decimal] = Field(None, ge=0, description="总支付")
    status: Optional[WageStatus] = WageStatus.CALCULATED

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


# Properties properties stored in DB
class WageInDB(WageInDBBase):
    pass 