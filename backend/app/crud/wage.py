from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from decimal import Decimal

from app.crud.base import CRUDBase
from app.models.wage import Wage, WageStatus
from app.models.repair_worker import RepairWorker
from app.schemas.wage import WageCreate, WageUpdate


class CRUDWage(CRUDBase[Wage, WageCreate, WageUpdate]):
    def get_multi_with_filter(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        keyword: Optional[str] = None,
        status: Optional[WageStatus] = None,
        month: Optional[str] = None,
        min_amount: Optional[Decimal] = None,
    ) -> Dict[str, Any]:
        """
        获取带筛选和分页的工资列表
        """
        query = db.query(self.model).options(joinedload(self.model.worker))

        filters = []
        if keyword:
            filters.append(
                or_(
                    RepairWorker.name.ilike(f"%{keyword}%"),
                    RepairWorker.worker_id.ilike(f"%{keyword}%")
                )
            )
        if status:
            filters.append(self.model.status == status)
        if month:
            filters.append(self.model.period == month)
        if min_amount is not None:
            filters.append(self.model.total_amount >= min_amount)

        if filters:
            query = query.join(RepairWorker).filter(and_(*filters))

        total = query.count()
        wages = query.order_by(self.model.period.desc(), self.model.id.desc()).offset(skip).limit(limit).all()
        
        return {"total": total, "wages": wages}

    def get_by_worker(
        self, db: Session, *, worker_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[Wage]:
        """
        根据工人ID和可选的日期范围获取工资记录
        """
        query = db.query(Wage).filter(Wage.worker_id == worker_id)
        
        if start_date:
            query = query.filter(Wage.pay_period >= start_date)
            
        if end_date:
            query = query.filter(Wage.pay_period <= end_date)
            
        return query.order_by(Wage.pay_period.desc()).all()

    def get_by_worker_and_period(self, db: Session, *, worker_id: int, period: str) -> Optional[Wage]:
        """
        根据工人和支付周期获取工资记录
        """
        return db.query(Wage).filter(
            and_(
                Wage.worker_id == worker_id,
                Wage.period == period
            )
        ).first()


wage_crud = CRUDWage(Wage) 