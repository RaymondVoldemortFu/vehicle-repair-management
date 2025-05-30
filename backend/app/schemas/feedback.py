from pydantic import Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseResponse, BaseSchema
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


class FeedbackBase(BaseSchema):
    order_id: Optional[int] = Field(None, description="相关订单ID（可选）")
    title: str = Field(..., min_length=1, max_length=100, description="反馈标题")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分(1-5)")
    comment: str = Field(..., min_length=1, max_length=1000, description="反馈内容")
    feedback_type: FeedbackType = Field(FeedbackType.SERVICE_RATING, description="反馈类型")
    contact_info: Optional[str] = Field(None, max_length=200, description="联系方式")


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="反馈标题")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分(1-5)")
    comment: Optional[str] = Field(None, min_length=1, max_length=1000, description="反馈内容")
    feedback_type: Optional[FeedbackType] = Field(None, description="反馈类型")
    contact_info: Optional[str] = Field(None, max_length=200, description="联系方式")


class FeedbackResponse(BaseResponse):
    user_id: int
    order_id: Optional[int]
    title: str
    rating: Optional[int]
    comment: str
    feedback_type: FeedbackType
    contact_info: Optional[str]
    status: FeedbackStatus
    response: Optional[str] = Field(None, description="管理员回复")
    response_admin_id: Optional[int] = Field(None, description="回复管理员ID")
    response_time: Optional[datetime] = Field(None, description="回复时间")


class FeedbackDetail(FeedbackResponse):
    """反馈详情，包含关联信息"""
    pass


class FeedbackPublic(BaseSchema):
    """公开展示的反馈信息"""
    id: int
    title: str
    rating: Optional[int]
    comment: str
    feedback_type: FeedbackType
    created_at: datetime


class FeedbackAdminUpdate(BaseSchema):
    """管理员更新反馈"""
    status: Optional[FeedbackStatus] = Field(None, description="状态")
    response: Optional[str] = Field(None, max_length=1000, description="回复内容")


class FeedbackStatistics(BaseSchema):
    """反馈统计信息"""
    total_feedback: int
    pending_count: int
    published_count: int
    rejected_count: int
    average_rating: float
    total_ratings: int
    type_distribution: dict 