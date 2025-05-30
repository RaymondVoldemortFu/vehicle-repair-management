from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from app.crud.base import CRUDBase
from app.models.feedback import Feedback, FeedbackStatus, FeedbackType
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackAdminUpdate


class CRUDFeedback(CRUDBase[Feedback, FeedbackCreate, FeedbackUpdate]):
    
    def create_feedback(self, db: Session, *, obj_in: FeedbackCreate, user_id: int) -> Feedback:
        """创建反馈"""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Feedback]:
        """获取用户的反馈列表"""
        return db.query(self.model).filter(
            and_(
                self.model.user_id == user_id,
                self.model.is_deleted == False
            )
        ).order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
    
    def get_by_status(
        self, 
        db: Session, 
        *, 
        status: FeedbackStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Feedback]:
        """根据状态获取反馈"""
        return db.query(self.model).filter(
            and_(
                self.model.status == status,
                self.model.is_deleted == False
            )
        ).order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
    
    def get_by_type(
        self, 
        db: Session, 
        *, 
        feedback_type: FeedbackType, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Feedback]:
        """根据类型获取反馈"""
        return db.query(self.model).filter(
            and_(
                self.model.feedback_type == feedback_type,
                self.model.is_deleted == False
            )
        ).order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
    
    def get_published(
        self, 
        db: Session, 
        *, 
        feedback_type: Optional[FeedbackType] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Feedback]:
        """获取已发布的反馈"""
        query = db.query(self.model).filter(
            and_(
                self.model.status == FeedbackStatus.PUBLISHED,
                self.model.is_deleted == False
            )
        )
        
        if feedback_type:
            query = query.filter(self.model.feedback_type == feedback_type)
        
        return query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
    
    def update_by_user(
        self, 
        db: Session, 
        *, 
        db_obj: Feedback, 
        obj_in: FeedbackUpdate, 
        user_id: int
    ) -> Feedback:
        """用户更新反馈"""
        # 只能更新待审核的反馈
        if db_obj.status != FeedbackStatus.PENDING:
            raise ValueError("只能修改待审核的反馈")
        
        # 只能更新自己的反馈
        if db_obj.user_id != user_id:
            raise ValueError("无权修改此反馈")
        
        return self.update(db, db_obj=db_obj, obj_in=obj_in)
    
    def update_by_admin(
        self, 
        db: Session, 
        *, 
        db_obj: Feedback, 
        obj_in: FeedbackAdminUpdate, 
        admin_id: int
    ) -> Feedback:
        """管理员更新反馈"""
        obj_data = obj_in.dict(exclude_unset=True)
        
        # 如果有回复内容，设置回复时间和管理员ID
        if "response" in obj_data and obj_data["response"]:
            obj_data["response_time"] = datetime.now()
            obj_data["response_admin_id"] = admin_id
        
        return self.update(db, db_obj=db_obj, obj_in=obj_data)
    
    def get_statistics(self, db: Session) -> dict:
        """获取反馈统计"""
        total_feedback = db.query(func.count(self.model.id)).filter(
            self.model.is_deleted == False
        ).scalar()
        
        pending_count = db.query(func.count(self.model.id)).filter(
            and_(
                self.model.status == FeedbackStatus.PENDING,
                self.model.is_deleted == False
            )
        ).scalar()
        
        published_count = db.query(func.count(self.model.id)).filter(
            and_(
                self.model.status == FeedbackStatus.PUBLISHED,
                self.model.is_deleted == False
            )
        ).scalar()
        
        rejected_count = db.query(func.count(self.model.id)).filter(
            and_(
                self.model.status == FeedbackStatus.REJECTED,
                self.model.is_deleted == False
            )
        ).scalar()
        
        # 评分统计
        rating_stats = db.query(
            func.avg(self.model.rating).label('avg_rating'),
            func.count(self.model.rating).label('rating_count')
        ).filter(
            and_(
                self.model.rating.isnot(None),
                self.model.is_deleted == False
            )
        ).first()
        
        avg_rating = float(rating_stats.avg_rating) if rating_stats.avg_rating else 0
        rating_count = rating_stats.rating_count or 0
        
        # 按类型统计
        type_stats = db.query(
            self.model.feedback_type,
            func.count(self.model.id).label('count')
        ).filter(
            self.model.is_deleted == False
        ).group_by(self.model.feedback_type).all()
        
        type_distribution = {stat.feedback_type.value: stat.count for stat in type_stats}
        
        return {
            "total_feedback": total_feedback,
            "pending_count": pending_count,
            "published_count": published_count,
            "rejected_count": rejected_count,
            "average_rating": round(avg_rating, 2),
            "total_ratings": rating_count,
            "type_distribution": type_distribution
        }
    
    def delete_by_user(self, db: Session, *, id: int, user_id: int) -> bool:
        """用户删除反馈"""
        db_obj = self.get(db, id=id)
        if not db_obj:
            return False
        
        # 只能删除自己的待审核反馈
        if db_obj.user_id != user_id or db_obj.status != FeedbackStatus.PENDING:
            return False
        
        return self.remove(db, id=id)


feedback_crud = CRUDFeedback(Feedback) 