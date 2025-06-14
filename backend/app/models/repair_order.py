from sqlalchemy import Column, Integer, String, Text, Enum, DECIMAL, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum
from app.config.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RepairOrder(BaseModel):
    __tablename__ = "repair_orders"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, comment="车辆ID")
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True, comment="管理员ID")
    order_number = Column(String(50), unique=True, nullable=False, index=True, comment="订单编号")
    description = Column(Text, nullable=False, comment="故障描述")
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, comment="订单状态")
    priority = Column(Enum(OrderPriority), default=OrderPriority.MEDIUM, nullable=False, comment="优先级")
    create_time = Column(DateTime, nullable=False, comment="创建时间")
    estimated_completion_time = Column(DateTime, nullable=True, comment="预计完成时间")
    actual_completion_time = Column(DateTime, nullable=True, comment="实际完成时间")
    total_labor_cost = Column(DECIMAL(10, 2), nullable=False, default=0, comment="总人工费")
    total_material_cost = Column(DECIMAL(10, 2), nullable=False, default=0, comment="总材料费")
    total_service_cost = Column(DECIMAL(10, 2), nullable=False, default=0, comment="总服务费")
    total_cost = Column(DECIMAL(10, 2), nullable=False, default=0, comment="总费用")
    internal_notes = Column(Text, nullable=True, comment="内部备注")
    comment = Column(String(500))
    status_history = Column(String(1000))
    is_deleted = Column(Boolean, default=False)

    # 关系
    user = relationship("User", back_populates="repair_orders")
    vehicle = relationship("Vehicle", back_populates="repair_orders")
    admin = relationship("Admin", back_populates="managed_orders")
    order_workers = relationship("RepairOrderWorker", back_populates="order", cascade="all, delete-orphan")
    order_services = relationship("RepairOrderService", back_populates="order", cascade="all, delete-orphan")
    repair_materials = relationship("RepairMaterial", back_populates="order", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="order", uselist=False, cascade="all, delete-orphan")
    assigned_workers = relationship(
        "RepairWorker",
        secondary="repair_order_workers",
        back_populates="assigned_orders"
    )

    def __repr__(self):
        return f"<RepairOrder(id={self.id}, order_number='{self.order_number}', status='{self.status}')>"

# 维修订单与维修工人的多对多关联表
repair_order_workers = Table(
    'repair_order_workers', Base.metadata,
    Column('repair_order_id', Integer, ForeignKey('repair_orders.id')),
    Column('repair_worker_id', Integer, ForeignKey('repair_workers.id'))
) 