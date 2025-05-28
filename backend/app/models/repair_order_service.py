from sqlalchemy import Column, Integer, DECIMAL, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class ServiceStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class RepairOrderService(BaseModel):
    __tablename__ = "repair_order_services"

    order_id = Column(Integer, ForeignKey("repair_orders.id"), nullable=False, comment="订单ID")
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, comment="服务ID")
    price = Column(DECIMAL(10, 2), nullable=False, comment="服务价格")
    quantity = Column(Integer, nullable=False, default=1, comment="数量")
    total_cost = Column(DECIMAL(10, 2), nullable=False, comment="总费用")
    status = Column(Enum(ServiceStatus), default=ServiceStatus.PENDING, nullable=False, comment="状态")
    notes = Column(Text, nullable=True, comment="备注")

    # 关系
    order = relationship("RepairOrder", back_populates="order_services")
    service = relationship("Service", back_populates="order_services")

    def __repr__(self):
        return f"<RepairOrderService(order_id={self.order_id}, service_id={self.service_id}, status='{self.status}')>" 