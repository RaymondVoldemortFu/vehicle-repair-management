from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from app.models import vehicle, repair_order, feedback, repair_order_worker, repair_worker
from decimal import Decimal

class CRUDAnalytics:
    def get_vehicle_repair_stats(self, db: Session):
        return db.query(
            vehicle.Vehicle.model,
            func.count(repair_order.RepairOrder.id).label("repair_count"),
            func.avg(repair_order.RepairOrder.total_cost).label("average_cost")
        ).join(vehicle.Vehicle, repair_order.RepairOrder.vehicle_id == vehicle.Vehicle.id)\
         .filter(repair_order.RepairOrder.status == 'completed')\
         .group_by(vehicle.Vehicle.model).all()

    def get_cost_trends(self, db: Session, period: str = 'month'):
        # period can be 'month' or 'quarter'
        # Replaced PostgreSQL-specific date_trunc with MySQL-compatible functions
        if period == 'quarter':
            date_trunc_field = func.concat(
                func.year(repair_order.RepairOrder.actual_completion_time),
                '-Q',
                func.quarter(repair_order.RepairOrder.actual_completion_time)
            )
        else:  # default to 'month'
            date_trunc_field = func.date_format(repair_order.RepairOrder.actual_completion_time, '%Y-%m')

        return db.query(
            date_trunc_field.label("period"),
            func.sum(repair_order.RepairOrder.total_labor_cost).label("labor_cost"),
            func.sum(repair_order.RepairOrder.total_material_cost).label("material_cost"),
            func.sum(repair_order.RepairOrder.total_service_cost).label("service_cost"),
            func.sum(repair_order.RepairOrder.total_cost).label("total_cost")
        ).filter(repair_order.RepairOrder.status == 'completed')\
         .group_by("period").order_by("period").all()

    def get_negative_feedback_cases(self, db: Session, rating_threshold: int = 2):
        return db.query(
            feedback.Feedback.id.label("feedback_id"),
            feedback.Feedback.rating,
            feedback.Feedback.comment.label("feedback_comment"),
            repair_order.RepairOrder.id.label("order_id"),
            repair_order.RepairOrder.order_number,
            repair_worker.RepairWorker.id.label("worker_id"),
            repair_worker.RepairWorker.name.label("worker_name")
        ).join(repair_order.RepairOrder, feedback.Feedback.order_id == repair_order.RepairOrder.id)\
         .join(repair_order_worker.RepairOrderWorker, repair_order.RepairOrder.id == repair_order_worker.RepairOrderWorker.order_id)\
         .join(repair_worker.RepairWorker, repair_order_worker.RepairOrderWorker.worker_id == repair_worker.RepairWorker.id)\
         .filter(feedback.Feedback.rating <= rating_threshold).all()

    def get_worker_task_distribution(self, db: Session):
        total_tasks = db.query(func.count(repair_order_worker.RepairOrderWorker.id)).scalar() or 1
        
        return db.query(
            repair_worker.RepairWorker.skill_type,
            func.count(repair_order_worker.RepairOrderWorker.id).label("task_count"),
            (func.count(repair_order_worker.RepairOrderWorker.id) * 100.0 / total_tasks).label("percentage")
        ).join(repair_worker.RepairWorker, repair_order_worker.RepairOrderWorker.worker_id == repair_worker.RepairWorker.id)\
         .group_by(repair_worker.RepairWorker.skill_type).all()

    def get_unfinished_order_stats(self, db: Session):
        return db.query(
            repair_order.RepairOrder.status,
            func.count(repair_order.RepairOrder.id).label("count")
        ).filter(repair_order.RepairOrder.status.in_(['pending', 'in_progress']))\
         .group_by(repair_order.RepairOrder.status).all()

analytics_crud = CRUDAnalytics() 