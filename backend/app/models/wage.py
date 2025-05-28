from sqlalchemy import Column, Integer, String, DECIMAL, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class WageStatus(str, enum.Enum):
    CALCULATED = "calculated"
    PAID = "paid"
    DISPUTED = "disputed"


class Wage(BaseModel):
    __tablename__ = "wages"

    worker_id = Column(Integer, ForeignKey("repair_workers.id"), nullable=False, comment="工人ID")
    pay_period = Column(String(7), nullable=False, comment="工资周期(YYYY-MM)")
    total_hours = Column(DECIMAL(8, 2), nullable=False, default=0, comment="总工作小时")
    regular_hours = Column(DECIMAL(8, 2), nullable=False, default=0, comment="正常工时")
    overtime_hours = Column(DECIMAL(8, 2), nullable=False, default=0, comment="加班工时")
    base_salary = Column(DECIMAL(10, 2), nullable=False, default=0, comment="基本工资")
    overtime_pay = Column(DECIMAL(10, 2), nullable=False, default=0, comment="加班费")
    bonus = Column(DECIMAL(10, 2), nullable=False, default=0, comment="奖金")
    total_payment = Column(DECIMAL(10, 2), nullable=False, default=0, comment="总支付金额")
    status = Column(Enum(WageStatus), default=WageStatus.CALCULATED, nullable=False, comment="状态")
    pay_date = Column(Date, nullable=True, comment="支付日期")

    # 关系
    worker = relationship("RepairWorker", back_populates="wages")

    def __repr__(self):
        return f"<Wage(id={self.id}, worker_id={self.worker_id}, pay_period='{self.pay_period}', total_payment={self.total_payment})>" 