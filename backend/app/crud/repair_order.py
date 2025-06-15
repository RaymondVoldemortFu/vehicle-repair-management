from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, func
from app.crud.base import CRUDBase
from app.models.repair_order import RepairOrder, OrderStatus
from app.models.repair_worker import RepairWorker, WorkerStatus
from app.models.repair_order_worker import RepairOrderWorker
from app.models.wage import Wage
from app.schemas.repair_order import RepairOrderCreate, RepairOrderUpdate, WorkCompletionUpdate
import random

# 加班费率
OVERTIME_RATE_MULTIPLIER = Decimal("1.5")


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
        """创建维修订单并生成订单编号, 并尝试自动分配给一个随机的空闲工人"""
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
            status=OrderStatus.PENDING  # 默认状态
        )
        db.add(db_obj)
        db.flush() # 先 flush 以获取订单的 ID

        # 尝试自动分配
        active_workers = db.query(RepairWorker).filter(RepairWorker.status == WorkerStatus.ACTIVE).all()
        if active_workers:
            assigned_worker = random.choice(active_workers)
            
            # 创建关联记录
            assignment = RepairOrderWorker(
                order_id=db_obj.id,
                worker_id=assigned_worker.id,
                hourly_rate=assigned_worker.hourly_rate
            )
            db.add(assignment)
            
            # 更新订单状态
            db_obj.status = OrderStatus.IN_PROGRESS

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
            joinedload(RepairOrder.user),
            selectinload(RepairOrder.assigned_workers).selectinload(RepairOrderWorker.worker)
        ).filter(
            and_(RepairOrder.id == id, RepairOrder.is_deleted == False)
        ).first()

    def get_by_user_with_details(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[RepairOrder]:
        """获取用户的维修订单（包含车辆和工人详情）"""
        return db.query(RepairOrder).options(
            joinedload(RepairOrder.vehicle),
            joinedload(RepairOrder.user),
            selectinload(RepairOrder.assigned_workers).selectinload(RepairOrderWorker.worker)
        ).filter(
            and_(RepairOrder.user_id == user_id, RepairOrder.is_deleted == False)
        ).order_by(RepairOrder.create_time.desc()).offset(skip).limit(limit).all()

    def get_by_worker_with_details(self, db: Session, *, worker_id: int, skip: int = 0, limit: int = 100) -> (List[RepairOrder], int):
        """获取分配给维修工人的维修订单（包含详细信息）"""
        query = db.query(RepairOrder).join(
            RepairOrder.assigned_workers
        ).filter(
            RepairOrderWorker.worker_id == worker_id,
            RepairOrder.is_deleted == False
        )
        total = query.count()
        orders = query.options(
            joinedload(RepairOrder.vehicle),
            joinedload(RepairOrder.user)
        ).order_by(RepairOrder.create_time.desc()).offset(skip).limit(limit).all()
        return orders, total

    def count_by_status(self, db: Session, *, status: OrderStatus) -> int:
        """根据状态计算订单数量"""
        return db.query(RepairOrder).filter(
            and_(
                RepairOrder.status == status,
                RepairOrder.is_deleted == False
            )
        ).count()

    def get_multi_with_details(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[RepairOrder]:
        """获取多个维修订单（包含详细信息）"""
        return db.query(RepairOrder).options(
            joinedload(RepairOrder.vehicle),
            joinedload(RepairOrder.user)
        ).filter(RepairOrder.is_deleted == False).offset(skip).limit(limit).all()

    def accept_order(self, db: Session, *, order_id: int, worker_id: int) -> Optional[RepairOrder]:
        """维修工接受订单"""
        order = self.get(db, id=order_id)
        if not order:
            raise ValueError("订单不存在")

        if order.status != OrderStatus.PENDING:
            raise ValueError("订单无法被接受，可能已被处理")

        worker = db.query(RepairWorker).filter(RepairWorker.id == worker_id).first()
        if not worker:
            raise ValueError("维修工不存在")

        # 创建关联对象，并填入额外数据
        assignment = RepairOrderWorker(
            order_id=order.id,
            worker_id=worker.id,
            hourly_rate=worker.hourly_rate  # 记录当前的小时费率
        )
        db.add(assignment)

        order.status = OrderStatus.IN_PROGRESS

        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def reject_order(self, db: Session, *, order_id: int, worker_id: int) -> Optional[RepairOrder]:
        """维修工拒绝/退回订单"""
        # 查找特定的分配记录
        assignment = db.query(RepairOrderWorker).filter(
            RepairOrderWorker.order_id == order_id,
            RepairOrderWorker.worker_id == worker_id
        ).first()

        if not assignment:
            raise ValueError("该维修工未被分配此订单")

        # 获取订单
        order = self.get(db, id=order_id)
        if not order:
            # 如果存在分配记录，这不应该发生
            raise ValueError("订单不存在")

        # 删除分配记录
        db.delete(assignment)
        db.flush()  # 先执行删除，以便后续查询能看到变化

        # 检查是否还有其他工人被分配
        remaining_assignments = db.query(RepairOrderWorker).filter(
            RepairOrderWorker.order_id == order_id
        ).count()

        # 如果没有工人了，将状态设置回 PENDING
        if remaining_assignments == 0:
            order.status = OrderStatus.PENDING
            db.add(order)

        db.commit()
        db.refresh(order)
        return order

    def complete_order_and_log_work(
        self, db: Session, *, order_id: int, worker_id: int, work_log: WorkCompletionUpdate
    ) -> Optional[RepairOrder]:
        """
        完成订单，记录工时，并计算更新工资
        """
        # 1. 验证订单和分配记录
        assignment = db.query(RepairOrderWorker).filter(
            RepairOrderWorker.order_id == order_id,
            RepairOrderWorker.worker_id == worker_id
        ).first()

        if not assignment:
            raise ValueError("该维修工未被分配此订单")

        order = self.get(db, id=order_id)
        if not order:
            raise ValueError("订单不存在")
        if order.status != OrderStatus.IN_PROGRESS:
            raise ValueError("订单当前状态无法完成")

        worker = db.query(RepairWorker).filter(RepairWorker.id == worker_id).first()
        if not worker:
            raise ValueError("维修工不存在")

        # 2. 计算本次工作收入
        regular_hours = Decimal(str(work_log.work_hours)) - Decimal(str(work_log.overtime_hours))
        
        regular_pay = regular_hours * worker.hourly_rate
        overtime_pay = Decimal(str(work_log.overtime_hours)) * worker.hourly_rate * OVERTIME_RATE_MULTIPLIER
        total_payment_for_assignment = regular_pay + overtime_pay

        # 3. 更新分配记录(repair_order_workers)
        assignment.work_hours = Decimal(str(work_log.work_hours))
        assignment.total_payment = total_payment_for_assignment
        assignment.work_description = work_log.work_description
        assignment.status = 'completed'
        assignment.end_time = datetime.utcnow()
        db.add(assignment)

        # 4. 更新主订单状态
        order.status = OrderStatus.COMPLETED
        order.actual_completion_time = datetime.utcnow()
        db.add(order)
        
        # 5. 更新或创建当月工资单(wages)
        pay_period = datetime.now().strftime('%Y-%m')
        wage = db.query(Wage).filter(
            Wage.worker_id == worker.id,
            Wage.period == pay_period
        ).first()
        
        if not wage:
            wage = Wage(
                worker_id=worker.id,
                period=pay_period,
            )
            db.add(wage)
            db.flush() # flush to get wage object initialized

        # 将本次工作产生的收入记为提成，并累加加班时长
        wage.commission = (wage.commission or 0) + total_payment_for_assignment
        wage.overtime_hours = (wage.overtime_hours or 0) + Decimal(str(work_log.overtime_hours))
        
        # 重新计算总金额
        wage.total_amount = (
            (wage.base_salary or 0) +
            (wage.overtime_pay or 0) +
            (wage.commission or 0) +
            (wage.bonus or 0) -
            (wage.deductions or 0)
        )
        
        db.add(wage)
        db.commit()
        db.refresh(order)
        return order

    def get_revenue_by_month(self, db: Session, year: int, month: int) -> Decimal:
        """根据年月计算总收入"""
        total_revenue = db.query(func.sum(RepairOrder.total_cost)).filter(
            and_(
                func.extract('year', RepairOrder.actual_completion_time) == year,
                func.extract('month', RepairOrder.actual_completion_time) == month,
                RepairOrder.status == OrderStatus.COMPLETED
            )
        ).scalar()
        return total_revenue or Decimal(0)


repair_order_crud = CRUDRepairOrder(RepairOrder) 