from sqlalchemy import Column, Integer, DECIMAL, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class WorkerAssignmentStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    WORKING = "working"
    COMPLETED = "completed"


class RepairOrderWorker(BaseModel):
    __tablename__ = "repair_order_workers"

    order_id = Column(Integer, ForeignKey("repair_orders.id"), nullable=False, comment="订单ID")
    worker_id = Column(Integer, ForeignKey("repair_workers.id"), nullable=False, comment="工人ID")
    work_hours = Column(DECIMAL(5, 2), nullable=False, default=0, comment="工作小时数")
    hourly_rate = Column(DECIMAL(10, 2), nullable=False, comment="时薪快照")
    total_payment = Column(DECIMAL(10, 2), nullable=False, default=0, comment="总支付金额")
    status = Column(Enum(WorkerAssignmentStatus), default=WorkerAssignmentStatus.ASSIGNED, nullable=False, comment="状态")
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    work_description = Column(Text, nullable=True, comment="工作描述")

    # 关系
    order = relationship("RepairOrder", back_populates="order_workers")
    worker = relationship("RepairWorker", back_populates="order_assignments")

    def __repr__(self):
        return f"<RepairOrderWorker(order_id={self.order_id}, worker_id={self.worker_id}, status='{self.status}')>" 