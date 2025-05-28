from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.config.database import get_db
from app.core.deps import get_current_active_admin, get_current_active_user
from app.models.admin import Admin
from app.models.user import User
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()

# 模拟反馈数据结构
MOCK_FEEDBACK = [
    {
        "id": 1,
        "user_id": 1,
        "order_id": 1,
        "rating": 5,
        "comment": "服务很好，维修质量高，工人很专业",
        "feedback_type": "service_rating",
        "status": "published",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
    },
    {
        "id": 2,
        "user_id": 2,
        "order_id": 2,
        "rating": 4,
        "comment": "整体满意，但等待时间稍长",
        "feedback_type": "service_rating",
        "status": "published",
        "created_at": "2024-01-16T14:20:00",
        "updated_at": "2024-01-16T14:20:00"
    },
    {
        "id": 3,
        "user_id": 3,
        "order_id": None,
        "rating": None,
        "comment": "希望能增加在线预约功能",
        "feedback_type": "suggestion",
        "status": "pending",
        "created_at": "2024-01-17T09:15:00",
        "updated_at": "2024-01-17T09:15:00"
    }
]


@router.post("/", response_model=dict)
def create_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_data: dict,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """创建反馈"""
    # 生成新ID
    new_id = max([f["id"] for f in MOCK_FEEDBACK]) + 1 if MOCK_FEEDBACK else 1
    
    new_feedback = {
        "id": new_id,
        "user_id": current_user.id,
        "order_id": feedback_data.get("order_id"),
        "rating": feedback_data.get("rating"),
        "comment": feedback_data.get("comment"),
        "feedback_type": feedback_data.get("feedback_type", "service_rating"),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    MOCK_FEEDBACK.append(new_feedback)
    return new_feedback


@router.get("/my-feedback", response_model=List[dict])
def read_my_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取当前用户的反馈列表"""
    user_feedback = [f for f in MOCK_FEEDBACK if f["user_id"] == current_user.id]
    return user_feedback


@router.get("/published", response_model=List[dict])
def read_published_feedback(
    db: Session = Depends(get_db),
    feedback_type: str = None,
    limit: int = 20,
) -> Any:
    """获取已发布的反馈（公开接口）"""
    published_feedback = [f for f in MOCK_FEEDBACK if f["status"] == "published"]
    
    if feedback_type:
        published_feedback = [f for f in published_feedback if f["feedback_type"] == feedback_type]
    
    # 限制返回数量
    published_feedback = published_feedback[:limit]
    
    # 移除敏感信息
    public_feedback = []
    for feedback in published_feedback:
        public_feedback.append({
            "id": feedback["id"],
            "rating": feedback["rating"],
            "comment": feedback["comment"],
            "feedback_type": feedback["feedback_type"],
            "created_at": feedback["created_at"]
        })
    
    return public_feedback


@router.put("/{feedback_id}", response_model=dict)
def update_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    feedback_data: dict,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新反馈"""
    feedback_index = next((i for i, f in enumerate(MOCK_FEEDBACK) if f["id"] == feedback_id), None)
    if feedback_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    feedback = MOCK_FEEDBACK[feedback_index]
    
    # 验证用户只能更新自己的反馈
    if feedback["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此反馈"
        )
    
    # 只有待审核的反馈才能修改
    if feedback["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能修改待审核的反馈"
        )
    
    # 更新反馈信息
    allowed_fields = {"rating", "comment", "feedback_type"}
    for key, value in feedback_data.items():
        if key in allowed_fields:
            MOCK_FEEDBACK[feedback_index][key] = value
    
    MOCK_FEEDBACK[feedback_index]["updated_at"] = datetime.now().isoformat()
    
    return MOCK_FEEDBACK[feedback_index]


@router.delete("/{feedback_id}", response_model=MessageResponse)
def delete_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """删除反馈"""
    feedback_index = next((i for i, f in enumerate(MOCK_FEEDBACK) if f["id"] == feedback_id), None)
    if feedback_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    feedback = MOCK_FEEDBACK[feedback_index]
    
    # 验证用户只能删除自己的反馈
    if feedback["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此反馈"
        )
    
    # 只有待审核的反馈才能删除
    if feedback["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能删除待审核的反馈"
        )
    
    MOCK_FEEDBACK.pop(feedback_index)
    return MessageResponse(message="反馈删除成功")


# 管理员专用接口
@router.get("/admin/all", response_model=List[dict])
def read_all_feedback_admin(
    db: Session = Depends(get_db),
    status_filter: str = None,
    feedback_type: str = None,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取所有反馈（管理员专用）"""
    feedback_list = MOCK_FEEDBACK.copy()
    
    if status_filter:
        feedback_list = [f for f in feedback_list if f["status"] == status_filter]
    
    if feedback_type:
        feedback_list = [f for f in feedback_list if f["feedback_type"] == feedback_type]
    
    return feedback_list


@router.get("/admin/pending", response_model=List[dict])
def read_pending_feedback(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取待审核的反馈（管理员专用）"""
    pending_feedback = [f for f in MOCK_FEEDBACK if f["status"] == "pending"]
    return pending_feedback


@router.put("/admin/{feedback_id}/approve", response_model=dict)
def approve_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """批准反馈（管理员专用）"""
    feedback_index = next((i for i, f in enumerate(MOCK_FEEDBACK) if f["id"] == feedback_id), None)
    if feedback_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    MOCK_FEEDBACK[feedback_index]["status"] = "published"
    MOCK_FEEDBACK[feedback_index]["updated_at"] = datetime.now().isoformat()
    
    return MOCK_FEEDBACK[feedback_index]


@router.put("/admin/{feedback_id}/reject", response_model=dict)
def reject_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    reason: str = None,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """拒绝反馈（管理员专用）"""
    feedback_index = next((i for i, f in enumerate(MOCK_FEEDBACK) if f["id"] == feedback_id), None)
    if feedback_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    MOCK_FEEDBACK[feedback_index]["status"] = "rejected"
    MOCK_FEEDBACK[feedback_index]["updated_at"] = datetime.now().isoformat()
    if reason:
        MOCK_FEEDBACK[feedback_index]["rejection_reason"] = reason
    
    return MOCK_FEEDBACK[feedback_index]


@router.delete("/admin/{feedback_id}", response_model=MessageResponse)
def delete_feedback_admin(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """删除反馈（管理员专用）"""
    feedback_index = next((i for i, f in enumerate(MOCK_FEEDBACK) if f["id"] == feedback_id), None)
    if feedback_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    MOCK_FEEDBACK.pop(feedback_index)
    return MessageResponse(message="反馈删除成功")


@router.get("/admin/statistics/overview", response_model=dict)
def get_feedback_statistics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取反馈统计信息（管理员专用）"""
    total_feedback = len(MOCK_FEEDBACK)
    pending_count = len([f for f in MOCK_FEEDBACK if f["status"] == "pending"])
    published_count = len([f for f in MOCK_FEEDBACK if f["status"] == "published"])
    rejected_count = len([f for f in MOCK_FEEDBACK if f["status"] == "rejected"])
    
    # 评分统计
    ratings = [f["rating"] for f in MOCK_FEEDBACK if f["rating"] is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # 按类型统计
    type_stats = {}
    for feedback in MOCK_FEEDBACK:
        feedback_type = feedback["feedback_type"]
        if feedback_type not in type_stats:
            type_stats[feedback_type] = 0
        type_stats[feedback_type] += 1
    
    return {
        "total_feedback": total_feedback,
        "pending_count": pending_count,
        "published_count": published_count,
        "rejected_count": rejected_count,
        "average_rating": round(avg_rating, 2),
        "total_ratings": len(ratings),
        "type_distribution": type_stats
    } 