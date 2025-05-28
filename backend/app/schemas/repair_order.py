from pydantic import Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.schemas.base import BaseResponse, BaseSchema
from app.models.repair_order import OrderStatus, OrderPriority


class RepairOrderBase(BaseSchema):
    description: str = Field(..., min_length=1, description="故障描述")
    priority: OrderPriority = Field(OrderPriority.MEDIUM, description="优先级")


class RepairOrderCreate(RepairOrderBase):
    user_id: int = Field(..., description="用户ID")
    vehicle_id: int = Field(..., description="车辆ID")
    estimated_completion_time: Optional[datetime] = Field(None, description="预计完成时间")


class RepairOrderUpdate(BaseSchema):
    description: Optional[str] = Field(None, min_length=1, description="故障描述")
    status: Optional[OrderStatus] = Field(None, description="订单状态")
    priority: Optional[OrderPriority] = Field(None, description="优先级")
    admin_id: Optional[int] = Field(None, description="管理员ID")
    estimated_completion_time: Optional[datetime] = Field(None, description="预计完成时间")
    actual_completion_time: Optional[datetime] = Field(None, description="实际完成时间")
    internal_notes: Optional[str] = Field(None, description="内部备注")


class RepairOrderResponse(BaseResponse):
    user_id: int
    vehicle_id: int
    admin_id: Optional[int]
    order_number: str
    description: str
    status: OrderStatus
    priority: OrderPriority
    create_time: datetime
    estimated_completion_time: Optional[datetime]
    actual_completion_time: Optional[datetime]
    total_labor_cost: Decimal
    total_material_cost: Decimal
    total_service_cost: Decimal
    total_cost: Decimal
    internal_notes: Optional[str]


class RepairOrderDetail(RepairOrderResponse):
    """包含详细信息的维修订单响应"""
    # 这里可以添加关联的工人、服务、材料等信息
    pass


class RepairOrderStatusUpdate(BaseSchema):
    status: OrderStatus = Field(..., description="订单状态")
    internal_notes: Optional[str] = Field(None, description="内部备注") 