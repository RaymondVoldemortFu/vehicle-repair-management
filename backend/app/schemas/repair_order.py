from pydantic import Field, BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.schemas.base import BaseResponse, BaseSchema, PaginationParams
from app.models.repair_order import OrderStatus, OrderPriority
from pydantic import model_validator
from app.schemas.user import UserResponse as UserInfo
from app.schemas.vehicle import VehicleResponse
from app.schemas.repair_worker import RepairWorkerBasic
from app.schemas.material import MaterialSimpleResponse


class RepairOrderBase(BaseSchema):
    description: str = Field(..., min_length=1, description="故障描述")
    priority: OrderPriority = Field(OrderPriority.MEDIUM, description="优先级")


class RepairOrderCreate(RepairOrderBase):
    # user_id: int = Field(..., description="用户ID")
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


class RepairOrderStatusUpdate(BaseModel):
    status: OrderStatus
    internal_notes: Optional[str] = None


class WorkCompletionUpdate(BaseModel):
    work_hours: float = Field(..., gt=0, description="总工作小时数")
    overtime_hours: float = Field(0, ge=0, description="加班小时数")
    work_description: Optional[str] = Field(None, max_length=500, description="工作内容描述")

    @model_validator(mode='after')
    def check_hours(self):
        if self.overtime_hours > self.work_hours:
            raise ValueError('加班时长不能超过总时长')
        return self


class UsedMaterialCreate(BaseModel):
    material_id: int = Field(..., description="材料ID")
    quantity: int = Field(..., gt=0, description="使用数量")


class RepairOrderComplete(BaseModel):
    used_materials: List[UsedMaterialCreate] = Field([], description="使用的材料列表")
    work_hours: float = Field(..., gt=0, description="总工作小时数")
    work_description: Optional[str] = Field(None, max_length=500, description="工作内容描述")


class RepairOrderResponse(BaseResponse):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    vehicle_id: int
    admin_id: Optional[int]
    order_number: str
    description: str
    status: OrderStatus
    priority: OrderPriority
    create_time: datetime
    actual_completion_time: Optional[datetime]
    total_labor_cost: Decimal
    total_material_cost: Decimal
    total_cost: Decimal
    internal_notes: Optional[str]


# 添加嵌套的用户和车辆信息
class VehicleInfo(BaseSchema):
    """车辆基本信息"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    license_plate: str
    vin: str
    model: str
    manufacturer: str
    year: int
    color: Optional[str]
    mileage: Optional[int]


# 用于表示分配给订单的工人信息
class AssignedWorkerInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    worker: RepairWorkerBasic


# 订单详情，包含用户和车辆信息
class RepairOrderDetail(RepairOrderResponse):
    """包含详细信息的维修订单响应"""
    model_config = ConfigDict(from_attributes=True)
    user: Optional[UserInfo] = Field(None, description="用户信息")
    vehicle: Optional[VehicleInfo] = Field(None, description="车辆信息")
    assigned_workers: List[AssignedWorkerInfo] = []
    used_materials: List[MaterialSimpleResponse] = []


class RepairOrderWithDetails(RepairOrderResponse):
    user: Optional[UserInfo] = None
    vehicle: Optional[VehicleInfo] = None 