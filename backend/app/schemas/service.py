from typing import Optional
from pydantic import BaseModel, Field
from app.models.service import ServiceStatus

class ServiceBase(BaseModel):
    service_code: str = Field(..., max_length=20, description="服务代码")
    name: str = Field(..., max_length=100, description="服务名称")
    description: Optional[str] = Field(None, description="服务描述")
    category: str = Field(..., max_length=50, description="服务分类")
    standard_price: float = Field(..., gt=0, description="标准价格")
    estimated_hours: int = Field(..., gt=0, description="预计耗时(小时)")
    status: ServiceStatus = ServiceStatus.ACTIVE

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    service_code: Optional[str] = Field(None, max_length=20, description="服务代码")
    name: Optional[str] = Field(None, max_length=100, description="服务名称")
    description: Optional[str] = Field(None, description="服务描述")
    category: Optional[str] = Field(None, max_length=50, description="服务分类")
    standard_price: Optional[float] = Field(None, gt=0, description="标准价格")
    estimated_hours: Optional[int] = Field(None, gt=0, description="预计耗时(小时)")
    status: Optional[ServiceStatus] = None

class ServiceResponse(ServiceBase):
    id: int

    class Config:
        orm_mode = True 