from sqlalchemy import Column, Integer, Text, Enum, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class FeedbackType(str, enum.Enum):
    SERVICE_RATING = "service_rating"
    SERVICE_QUALITY = "service_quality" 
    SYSTEM_ISSUE = "system_issue"
    FEATURE_REQUEST = "feature_request"
    SUGGESTION = "suggestion"
    COMPLAINT = "complaint"
    OTHER = "other"


class FeedbackStatus(str, enum.Enum):
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"


class Feedback(BaseModel):
    __tablename__ = "feedback"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    order_id = Column(Integer, ForeignKey("repair_orders.id"), nullable=True, comment="相关订单ID（可选）")
    title = Column(String(100), nullable=False, comment="反馈标题")
    rating = Column(Integer, nullable=True, comment="评分(1-5)")
    comment = Column(Text, nullable=False, comment="反馈内容")
    feedback_type = Column(Enum(FeedbackType), default=FeedbackType.SERVICE_RATING, nullable=False, comment="反馈类型")
    contact_info = Column(String(200), nullable=True, comment="联系方式")
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.PENDING, nullable=False, comment="状态")
    response = Column(Text, nullable=True, comment="管理员回复")
    response_admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True, comment="回复管理员ID")
    response_time = Column(DateTime, nullable=True, comment="回复时间")

    # 关系
    user = relationship("User", back_populates="feedback")
    order = relationship("RepairOrder", back_populates="feedback")
    response_admin = relationship("Admin", back_populates="feedback_responses")

    def __repr__(self):
        return f"<Feedback(id={self.id}, user_id={self.user_id}, feedback_type='{self.feedback_type}', status='{self.status}')>" 