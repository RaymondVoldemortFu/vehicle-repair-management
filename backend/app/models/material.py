from sqlalchemy import Column, Integer, String, Text, Enum, DECIMAL, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class MaterialStatus(str, enum.Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"


class Material(BaseModel):
    __tablename__ = "materials"

    material_code = Column(String(20), unique=True, nullable=False, index=True, comment="材料编码")
    name = Column(String(100), nullable=False, comment="材料名称")
    description = Column(Text, nullable=True, comment="材料描述")
    category = Column(String(50), nullable=False, comment="材料分类")
    unit_price = Column(DECIMAL(10, 2), nullable=False, comment="单价")
    unit = Column(String(20), nullable=False, comment="单位")
    stock_quantity = Column(Integer, nullable=False, default=0, comment="库存数量")
    min_stock_level = Column(Integer, nullable=False, default=0, comment="最低库存警戒线")
    status = Column(Enum(MaterialStatus), default=MaterialStatus.ACTIVE, nullable=False, comment="状态")
    last_purchase_date = Column(Date, nullable=True, comment="最后采购日期")

    # 关系
    repair_materials = relationship("RepairMaterial", back_populates="material")

    def __repr__(self):
        return f"<Material(id={self.id}, material_code='{self.material_code}', name='{self.name}')>" 