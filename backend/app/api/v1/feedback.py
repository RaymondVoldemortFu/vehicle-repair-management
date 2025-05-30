from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import get_current_active_admin, get_current_active_user
from app.crud.feedback import feedback_crud
from app.models.admin import Admin
from app.models.user import User
from app.models.feedback import FeedbackStatus, FeedbackType
from app.schemas.feedback import (
    FeedbackCreate, FeedbackUpdate, FeedbackResponse, FeedbackDetail,
    FeedbackPublic, FeedbackAdminUpdate, FeedbackStatistics
)
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=FeedbackResponse)
def create_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_in: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """创建反馈"""
    feedback = feedback_crud.create_feedback(db, obj_in=feedback_in, user_id=current_user.id)
    return feedback


@router.get("/my-feedback", response_model=List[FeedbackResponse])
def read_my_feedback(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取当前用户的反馈列表"""
    feedback_list = feedback_crud.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return feedback_list


@router.get("/published", response_model=List[FeedbackPublic])
def read_published_feedback(
    db: Session = Depends(get_db),
    feedback_type: Optional[FeedbackType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """获取已发布的反馈（公开接口）"""
    feedback_list = feedback_crud.get_published(
        db, feedback_type=feedback_type, skip=skip, limit=limit
    )
    return feedback_list


@router.get("/{feedback_id}", response_model=FeedbackDetail)
def read_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取反馈详情"""
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    # 验证用户只能查看自己的反馈
    if feedback.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此反馈"
        )
    
    return feedback


@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    feedback_in: FeedbackUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新反馈"""
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    try:
        feedback = feedback_crud.update_by_user(
            db, db_obj=feedback, obj_in=feedback_in, user_id=current_user.id
        )
        return feedback
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{feedback_id}", response_model=MessageResponse)
def delete_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """删除反馈"""
    success = feedback_crud.delete_by_user(db, id=feedback_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在或无权删除"
        )
    
    return MessageResponse(message="反馈删除成功")


# 管理员专用接口
@router.get("/admin/all", response_model=PaginatedResponse[FeedbackResponse])
def read_all_feedback_admin(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    status_filter: Optional[FeedbackStatus] = Query(None),
    feedback_type: Optional[FeedbackType] = Query(None),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取所有反馈（管理员专用）"""
    if status_filter:
        feedback_list = feedback_crud.get_by_status(
            db, status=status_filter, skip=pagination.get_offset(), limit=pagination.size
        )
        total = len(feedback_crud.get_by_status(db, status=status_filter, skip=0, limit=10000))
    elif feedback_type:
        feedback_list = feedback_crud.get_by_type(
            db, feedback_type=feedback_type, skip=pagination.get_offset(), limit=pagination.size
        )
        total = len(feedback_crud.get_by_type(db, feedback_type=feedback_type, skip=0, limit=10000))
    else:
        feedback_list = feedback_crud.get_multi(
            db, skip=pagination.get_offset(), limit=pagination.size
        )
        total = feedback_crud.count(db)
    
    return PaginatedResponse.create(
        items=feedback_list,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/admin/pending", response_model=List[FeedbackResponse])
def read_pending_feedback(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取待审核的反馈（管理员专用）"""
    feedback_list = feedback_crud.get_by_status(
        db, status=FeedbackStatus.PENDING, skip=skip, limit=limit
    )
    return feedback_list


@router.get("/admin/{feedback_id}", response_model=FeedbackDetail)
def read_feedback_admin(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取反馈详情（管理员专用）"""
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    return feedback


@router.put("/admin/{feedback_id}", response_model=FeedbackResponse)
def update_feedback_admin(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    feedback_in: FeedbackAdminUpdate,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新反馈（管理员专用）"""
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    feedback = feedback_crud.update_by_admin(
        db, db_obj=feedback, obj_in=feedback_in, admin_id=current_admin.id
    )
    return feedback


@router.put("/admin/{feedback_id}/approve", response_model=FeedbackResponse)
def approve_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """批准反馈（管理员专用）"""
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    feedback_update = FeedbackAdminUpdate(status=FeedbackStatus.PUBLISHED)
    feedback = feedback_crud.update_by_admin(
        db, db_obj=feedback, obj_in=feedback_update, admin_id=current_admin.id
    )
    return feedback


@router.put("/admin/{feedback_id}/reject", response_model=FeedbackResponse)
def reject_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    reason: Optional[str] = None,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """拒绝反馈（管理员专用）"""
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    feedback_update = FeedbackAdminUpdate(
        status=FeedbackStatus.REJECTED,
        response=reason or "反馈被拒绝"
    )
    feedback = feedback_crud.update_by_admin(
        db, db_obj=feedback, obj_in=feedback_update, admin_id=current_admin.id
    )
    return feedback


@router.delete("/admin/{feedback_id}", response_model=MessageResponse)
def delete_feedback_admin(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """删除反馈（管理员专用）"""
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    feedback_crud.remove(db, id=feedback_id)
    return MessageResponse(message="反馈删除成功")


@router.get("/admin/statistics/overview", response_model=FeedbackStatistics)
def get_feedback_statistics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取反馈统计信息（管理员专用）"""
    statistics = feedback_crud.get_statistics(db)
    return statistics 