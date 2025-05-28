from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class VehicleStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    SCRAPPED = "scrapped"


class Vehicle(BaseModel):
    __tablename__ = "vehicles"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="车主ID")
    license_plate = Column(String(20), unique=True, nullable=False, index=True, comment="车牌号")
    vin = Column(String(50), unique=True, nullable=False, index=True, comment="车架号")
    model = Column(String(100), nullable=False, comment="车型")
    manufacturer = Column(String(100), nullable=False, comment="制造商")
    year = Column(Integer, nullable=False, comment="生产年份")
    color = Column(String(50), nullable=True, comment="颜色")
    mileage = Column(Integer, nullable=True, comment="里程数")
    purchase_date = Column(Date, nullable=True, comment="购买日期")
    status = Column(Enum(VehicleStatus), default=VehicleStatus.ACTIVE, nullable=False, comment="车辆状态")

    # 关系
    owner = relationship("User", back_populates="vehicles")
    repair_orders = relationship("RepairOrder", back_populates="vehicle", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Vehicle(id={self.id}, license_plate='{self.license_plate}', model='{self.model}')>" 