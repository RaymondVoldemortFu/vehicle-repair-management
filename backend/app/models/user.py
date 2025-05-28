from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(100), nullable=False, comment="用户姓名")
    phone = Column(String(20), unique=True, nullable=False, index=True, comment="手机号码")
    email = Column(String(100), unique=True, nullable=True, index=True, comment="邮箱地址")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    address = Column(String(500), nullable=True, comment="联系地址")
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False, comment="用户状态")

    # 关系
    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")
    repair_orders = relationship("RepairOrder", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', phone='{self.phone}')>" 