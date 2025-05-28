from sqlalchemy import Column, Integer, DECIMAL, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class RepairMaterial(BaseModel):
    __tablename__ = "repair_materials"

    order_id = Column(Integer, ForeignKey("repair_orders.id"), nullable=False, comment="订单ID")
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, comment="材料ID")
    quantity_used = Column(Integer, nullable=False, comment="使用数量")
    unit_price = Column(DECIMAL(10, 2), nullable=False, comment="单价快照")
    total_cost = Column(DECIMAL(10, 2), nullable=False, comment="总费用")
    notes = Column(Text, nullable=True, comment="使用备注")
    used_at = Column(DateTime, nullable=False, comment="使用时间")

    # 关系
    order = relationship("RepairOrder", back_populates="repair_materials")
    material = relationship("Material", back_populates="repair_materials")

    def __repr__(self):
        return f"<RepairMaterial(order_id={self.order_id}, material_id={self.material_id}, quantity={self.quantity_used})>" 