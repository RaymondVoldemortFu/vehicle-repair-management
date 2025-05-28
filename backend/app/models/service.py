from sqlalchemy import Column, Integer, String, Text, Enum, DECIMAL
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class ServiceStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class Service(BaseModel):
    __tablename__ = "services"

    service_code = Column(String(20), unique=True, nullable=False, index=True, comment="服务代码")
    name = Column(String(100), nullable=False, comment="服务名称")
    description = Column(Text, nullable=True, comment="服务描述")
    category = Column(String(50), nullable=False, comment="服务分类")
    standard_price = Column(DECIMAL(10, 2), nullable=False, comment="标准价格")
    estimated_hours = Column(Integer, nullable=False, comment="预计耗时(小时)")
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE, nullable=False, comment="状态")

    # 关系
    order_services = relationship("RepairOrderService", back_populates="service")

    def __repr__(self):
        return f"<Service(id={self.id}, service_code='{self.service_code}', name='{self.name}')>" 