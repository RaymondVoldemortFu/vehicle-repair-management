from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
import datetime

class MaterialBase(BaseModel):
    material_code: str = Field(..., max_length=20, description="材料编码")
    name: str = Field(..., max_length=100, description="材料名称")
    description: Optional[str] = Field(None, description="材料描述")
    category: str = Field(..., max_length=50, description="材料分类")
    unit_price: Decimal = Field(..., gt=0, description="单价")
    unit: str = Field(..., max_length=20, description="单位")
    stock_quantity: int = Field(0, ge=0, description="库存数量")

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    material_code: Optional[str] = Field(None, max_length=20, description="材料编码")
    name: Optional[str] = Field(None, max_length=100, description="材料名称")
    description: Optional[str] = Field(None, description="材料描述")
    category: Optional[str] = Field(None, max_length=50, description="材料分类")
    unit_price: Optional[Decimal] = Field(None, gt=0, description="单价")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    stock_quantity: Optional[int] = Field(None, ge=0, description="库存数量")

class MaterialResponse(MaterialBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class MaterialSimpleResponse(BaseModel):
    """用于在订单详情中显示的简化材料信息"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    unit_price: Decimal
    unit: str
    quantity: int # This field will be populated from the association table 