from typing import Optional
from pydantic import BaseModel, Field
from app.models.material import MaterialStatus
import datetime

class MaterialBase(BaseModel):
    material_code: str = Field(..., max_length=20, description="材料编码")
    name: str = Field(..., max_length=100, description="材料名称")
    description: Optional[str] = Field(None, description="材料描述")
    category: str = Field(..., max_length=50, description="材料分类")
    unit_price: float = Field(..., gt=0, description="单价")
    unit: str = Field(..., max_length=20, description="单位")
    stock_quantity: int = Field(0, ge=0, description="库存数量")
    min_stock_level: int = Field(0, ge=0, description="最低库存警戒线")
    status: MaterialStatus = MaterialStatus.ACTIVE
    last_purchase_date: Optional[datetime.date] = Field(None, description="最后采购日期")

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    material_code: Optional[str] = Field(None, max_length=20, description="材料编码")
    name: Optional[str] = Field(None, max_length=100, description="材料名称")
    description: Optional[str] = Field(None, description="材料描述")
    category: Optional[str] = Field(None, max_length=50, description="材料分类")
    unit_price: Optional[float] = Field(None, gt=0, description="单价")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    stock_quantity: Optional[int] = Field(None, ge=0, description="库存数量")
    min_stock_level: Optional[int] = Field(None, ge=0, description="最低库存警戒线")
    status: Optional[MaterialStatus] = None
    last_purchase_date: Optional[datetime.date] = Field(None, description="最后采购日期")

class MaterialResponse(MaterialBase):
    id: int

    class Config:
        orm_mode = True 