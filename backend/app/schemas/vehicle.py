from pydantic import Field
from typing import Optional
from datetime import date
from app.schemas.base import BaseResponse, BaseSchema
from app.models.vehicle import VehicleStatus


class VehicleBase(BaseSchema):
    license_plate: str = Field(..., min_length=1, max_length=20, description="车牌号")
    vin: str = Field(..., min_length=1, max_length=50, description="车架号")
    model: str = Field(..., min_length=1, max_length=100, description="车型")
    manufacturer: str = Field(..., min_length=1, max_length=100, description="制造商")
    year: int = Field(..., ge=1900, le=2030, description="生产年份")
    color: Optional[str] = Field(None, max_length=50, description="颜色")
    mileage: Optional[int] = Field(None, ge=0, description="里程数")
    purchase_date: Optional[date] = Field(None, description="购买日期")


class VehicleCreate(VehicleBase):
    user_id: int = Field(..., description="车主ID")


class VehicleUpdate(BaseSchema):
    license_plate: Optional[str] = Field(None, min_length=1, max_length=20, description="车牌号")
    vin: Optional[str] = Field(None, min_length=1, max_length=50, description="车架号")
    model: Optional[str] = Field(None, min_length=1, max_length=100, description="车型")
    manufacturer: Optional[str] = Field(None, min_length=1, max_length=100, description="制造商")
    year: Optional[int] = Field(None, ge=1900, le=2030, description="生产年份")
    color: Optional[str] = Field(None, max_length=50, description="颜色")
    mileage: Optional[int] = Field(None, ge=0, description="里程数")
    purchase_date: Optional[date] = Field(None, description="购买日期")
    status: Optional[VehicleStatus] = Field(None, description="车辆状态")


class VehicleResponse(BaseResponse):
    user_id: int
    license_plate: str
    vin: str
    model: str
    manufacturer: str
    year: int
    color: Optional[str]
    mileage: Optional[int]
    purchase_date: Optional[date]
    status: VehicleStatus


class OwnerInfo(BaseSchema):
    """车主基本信息"""
    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]


class VehicleDetail(VehicleResponse):
    """车辆详细信息，包含车主信息"""
    owner: OwnerInfo = Field(..., description="车主信息") 