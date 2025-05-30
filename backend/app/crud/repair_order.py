from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.crud.base import CRUDBase
from app.models.repair_order import RepairOrder, OrderStatus
from app.schemas.repair_order import RepairOrderCreate, RepairOrderUpdate


class CRUDRepairOrder(CRUDBase[RepairOrder, RepairOrderCreate, RepairOrderUpdate]):
    def get_by_order_number(self, db: Session, *, order_number: str) -> Optional[RepairOrder]:
        """根据订单编号获取维修订单"""
        return db.query(RepairOrder).filter(
            and_(RepairOrder.order_number == order_number, RepairOrder.is_deleted == False)
        ).first()

    def get_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[RepairOrder]:
        """获取用户的维修订单"""
        return db.query(RepairOrder).filter(
            and_(RepairOrder.user_id == user_id, RepairOrder.is_deleted == False)
        ).offset(skip).limit(limit).all()

    def get_by_vehicle(self, db: Session, *, vehicle_id: int) -> List[RepairOrder]:
        """获取车辆的维修订单"""
        return db.query(RepairOrder).filter(
            and_(RepairOrder.vehicle_id == vehicle_id, RepairOrder.is_deleted == False)
        ).all()

    def get_by_status(self, db: Session, *, status: OrderStatus, skip: int = 0, limit: int = 100) -> List[RepairOrder]:
        """根据状态获取维修订单"""
        return db.query(RepairOrder).filter(
            and_(RepairOrder.status == status, RepairOrder.is_deleted == False)
        ).offset(skip).limit(limit).all()

    def get_by_status_with_details(self, db: Session, *, status: OrderStatus, skip: int = 0, limit: int = 100) -> List[RepairOrder]:
        """根据状态获取维修订单（包含详细信息）"""
        return db.query(RepairOrder).options(
            joinedload(RepairOrder.vehicle),
            joinedload(RepairOrder.user)
        ).filter(
            and_(RepairOrder.status == status, RepairOrder.is_deleted == False)
        ).offset(skip).limit(limit).all()

    def get_pending_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[RepairOrder]:
        """获取待处理的维修订单"""
        return self.get_by_status(db, status=OrderStatus.PENDING, skip=skip, limit=limit)

    def get_in_progress_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[RepairOrder]:
        """获取进行中的维修订单"""
        return self.get_by_status(db, status=OrderStatus.IN_PROGRESS, skip=skip, limit=limit)

    def create_with_order_number(self, db: Session, *, obj_in: RepairOrderCreate, user_id: int) -> RepairOrder:
        """创建维修订单并生成订单编号"""
        # 生成订单编号
        order_number = self._generate_order_number(db)
        
        db_obj = RepairOrder(
            user_id=user_id,
            vehicle_id=obj_in.vehicle_id,
            order_number=order_number,
            description=obj_in.description,
            priority=obj_in.priority,
            create_time=datetime.utcnow(),
            estimated_completion_time=obj_in.estimated_completion_time,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_status(self, db: Session, *, order_id: int, status: OrderStatus, notes: str = None) -> Optional[RepairOrder]:
        """更新订单状态"""
        order = self.get(db, id=order_id)
        if not order:
            return None
        
        order.status = status
        if notes:
            order.internal_notes = notes
        
        # 如果状态为完成，设置实际完成时间
        if status == OrderStatus.COMPLETED:
            order.actual_completion_time = datetime.utcnow()
        
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def calculate_total_cost(self, db: Session, *, order_id: int) -> Optional[RepairOrder]:
        """计算订单总费用"""
        order = self.get(db, id=order_id)
        if not order:
            return None
        
        # 计算总费用（人工费 + 材料费 + 服务费）
        order.total_cost = order.total_labor_cost + order.total_material_cost + order.total_service_cost
        
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def _generate_order_number(self, db: Session) -> str:
        """生成订单编号"""
        today = datetime.now().strftime("%Y%m%d")
        
        # 查询今天的订单数量
        count = db.query(func.count(RepairOrder.id)).filter(
            and_(
                func.date(RepairOrder.create_time) == datetime.now().date(),
                RepairOrder.is_deleted == False
            )
        ).scalar()
        
        # 生成订单编号：RO + 日期 + 4位序号
        order_number = f"RO{today}{count + 1:04d}"
        return order_number

    def get_statistics(self, db: Session) -> dict:
        """获取订单统计信息"""
        total = self.count(db)
        pending = db.query(func.count(RepairOrder.id)).filter(
            and_(RepairOrder.status == OrderStatus.PENDING, RepairOrder.is_deleted == False)
        ).scalar()
        in_progress = db.query(func.count(RepairOrder.id)).filter(
            and_(RepairOrder.status == OrderStatus.IN_PROGRESS, RepairOrder.is_deleted == False)
        ).scalar()
        completed = db.query(func.count(RepairOrder.id)).filter(
            and_(RepairOrder.status == OrderStatus.COMPLETED, RepairOrder.is_deleted == False)
        ).scalar()
        cancelled = db.query(func.count(RepairOrder.id)).filter(
            and_(RepairOrder.status == OrderStatus.CANCELLED, RepairOrder.is_deleted == False)
        ).scalar()
        
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled
        }

    def get_with_details(self, db: Session, id: int) -> Optional[RepairOrder]:
        """获取包含详细信息的维修订单"""
        return db.query(RepairOrder).options(
            joinedload(RepairOrder.vehicle),
            joinedload(RepairOrder.user)
        ).filter(
            and_(RepairOrder.id == id, RepairOrder.is_deleted == False)
        ).first()

    def get_by_user_with_details(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[RepairOrder]:
        """获取用户的维修订单（包含车辆详情）"""
        return db.query(RepairOrder).options(
            joinedload(RepairOrder.vehicle),
            joinedload(RepairOrder.user)
        ).filter(
            and_(RepairOrder.user_id == user_id, RepairOrder.is_deleted == False)
        ).offset(skip).limit(limit).all()

    def get_multi_with_details(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[RepairOrder]:
        """获取多个维修订单（包含详细信息）"""
        return db.query(RepairOrder).options(
            joinedload(RepairOrder.vehicle),
            joinedload(RepairOrder.user)
        ).filter(RepairOrder.is_deleted == False).offset(skip).limit(limit).all()


repair_order_crud = CRUDRepairOrder(RepairOrder) 