from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.wage import Wage
from app.schemas.wage import WageCreate, WageUpdate


class CRUDWage(CRUDBase[Wage, WageCreate, WageUpdate]):
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

    def get_by_worker_and_period(self, db: Session, *, worker_id: int, pay_period: str) -> Optional[Wage]:
        """
        根据工人和支付周期获取工资记录
        """
        return db.query(Wage).filter(
            and_(
                Wage.worker_id == worker_id,
                Wage.pay_period == pay_period
            )
        ).first()


wage_crud = CRUDWage(Wage) 