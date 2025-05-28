from sqlalchemy import Column, Integer, String, Enum, DateTime, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    CLERK = "clerk"


class AdminStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


class Admin(BaseModel):
    __tablename__ = "admins"

    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    name = Column(String(100), nullable=False, comment="姓名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号码")
    role = Column(Enum(AdminRole), nullable=False, comment="管理员角色")
    permissions = Column(JSON, nullable=True, comment="权限配置")
    status = Column(Enum(AdminStatus), default=AdminStatus.ACTIVE, nullable=False, comment="状态")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")

    # 关系
    managed_orders = relationship("RepairOrder", back_populates="admin")
    feedback_responses = relationship("Feedback", back_populates="response_admin")

    def __repr__(self):
        return f"<Admin(id={self.id}, username='{self.username}', role='{self.role}')>" 