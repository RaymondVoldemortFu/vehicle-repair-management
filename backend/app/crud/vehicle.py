from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.crud.base import CRUDBase
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class CRUDVehicle(CRUDBase[Vehicle, VehicleCreate, VehicleUpdate]):
    def get_by_license_plate(self, db: Session, *, license_plate: str) -> Optional[Vehicle]:
        """根据车牌号获取车辆"""
        return db.query(Vehicle).filter(
            and_(Vehicle.license_plate == license_plate, Vehicle.is_deleted == False)
        ).first()

    def get_by_owner(self, db: Session, *, owner_id: int) -> List[Vehicle]:
        """根据车主ID获取车辆列表"""
        return db.query(Vehicle).filter(
            and_(Vehicle.user_id == owner_id, Vehicle.is_deleted == False)
        ).all()

    def get_by_vin(self, db: Session, *, vin: str) -> Optional[Vehicle]:
        """根据车架号获取车辆"""
        return db.query(Vehicle).filter(
            and_(Vehicle.vin == vin, Vehicle.is_deleted == False)
        ).first()

    def get_brand_statistics(self, db: Session) -> List[Dict[str, Any]]:
        """获取品牌统计信息"""
        result = db.query(
            Vehicle.manufacturer,
            func.count(Vehicle.id).label('count')
        ).filter(
            Vehicle.is_deleted == False
        ).group_by(Vehicle.manufacturer).all()

        return [{"manufacturer": row.manufacturer, "count": row.count} for row in result]

    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> Vehicle:
        """创建车辆"""
        # 处理 owner_id 到 user_id 的映射
        if "owner_id" in obj_in:
            obj_in["user_id"] = obj_in.pop("owner_id")

        db_obj = Vehicle(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


vehicle_crud = CRUDVehicle(Vehicle)