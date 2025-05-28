from sqlalchemy import Column, Integer, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class FeedbackStatus(str, enum.Enum):
    PENDING = "pending"
    RESPONDED = "responded"
    RESOLVED = "resolved"


class Feedback(BaseModel):
    __tablename__ = "feedback"

    order_id = Column(Integer, ForeignKey("repair_orders.id"), nullable=False, unique=True, comment="订单ID")
    rating = Column(Integer, nullable=False, comment="评分(1-5)")
    comment = Column(Text, nullable=True, comment="评价内容")
    response = Column(Text, nullable=True, comment="回复内容")
    response_admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True, comment="回复管理员ID")
    submit_time = Column(DateTime, nullable=False, comment="提交时间")
    response_time = Column(DateTime, nullable=True, comment="回复时间")
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.PENDING, nullable=False, comment="状态")

    # 关系
    order = relationship("RepairOrder", back_populates="feedback")
    response_admin = relationship("Admin", back_populates="feedback_responses")

    def __repr__(self):
        return f"<Feedback(id={self.id}, order_id={self.order_id}, rating={self.rating}, status='{self.status}')>" 