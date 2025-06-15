from sqlalchemy import Column, Integer, String, DECIMAL, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class WageStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"


class Wage(BaseModel):
    __tablename__ = "wages"

    worker_id = Column(Integer, ForeignKey("repair_workers.id"), nullable=False, comment="工人ID")
    period = Column(String(7), nullable=False, comment="工资周期(YYYY-MM)")
    base_salary = Column(DECIMAL(10, 2), nullable=False, default=0, comment="基本工资")
    work_days = Column(Integer, nullable=False, default=0, comment="工作天数")
    overtime_hours = Column(DECIMAL(8, 2), nullable=False, default=0, comment="加班工时")
    overtime_pay = Column(DECIMAL(10, 2), nullable=False, default=0, comment="加班费")
    commission = Column(DECIMAL(10, 2), nullable=False, default=0, comment="提成")
    bonus = Column(DECIMAL(10, 2), nullable=False, default=0, comment="奖金")
    deductions = Column(DECIMAL(10, 2), nullable=False, default=0, comment="扣款")
    total_amount = Column(DECIMAL(10, 2), nullable=False, default=0, comment="总支付金额")
    status = Column(Enum(WageStatus), default=WageStatus.PENDING, nullable=False, comment="状态")
    pay_date = Column(Date, nullable=True, comment="支付日期")
    notes = Column(String(255), nullable=True, comment="备注")

    # 关系
    worker = relationship("RepairWorker", back_populates="wages")

    def __repr__(self):
        return f"<Wage(id={self.id}, worker_id={self.worker_id}, period='{self.period}', total_amount={self.total_amount})>" 