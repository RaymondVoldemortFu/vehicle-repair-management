from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal

from app.config.database import get_db
from app.core.deps import get_current_active_admin, get_current_active_worker
from app.models.admin import Admin
from app.models.repair_worker import RepairWorker
from app.schemas.base import MessageResponse, PaginationParams, PaginatedResponse

router = APIRouter()

# 模拟工资数据结构
MOCK_WAGES = [
    {
        "id": 1,
        "worker_id": 1,
        "worker_name": "张师傅",
        "year": 2024,
        "month": 1,
        "base_salary": 5000.00,
        "overtime_hours": 20,
        "overtime_rate": 50.00,
        "overtime_pay": 1000.00,
        "bonus": 500.00,
        "deductions": 200.00,
        "total_salary": 6300.00,
        "status": "paid",
        "pay_date": "2024-02-05",
        "created_at": "2024-02-01T10:00:00",
        "updated_at": "2024-02-05T15:30:00"
    },
    {
        "id": 2,
        "worker_id": 2,
        "worker_name": "李师傅",
        "year": 2024,
        "month": 1,
        "base_salary": 4800.00,
        "overtime_hours": 15,
        "overtime_rate": 45.00,
        "overtime_pay": 675.00,
        "bonus": 300.00,
        "deductions": 150.00,
        "total_salary": 5625.00,
        "status": "paid",
        "pay_date": "2024-02-05",
        "created_at": "2024-02-01T10:00:00",
        "updated_at": "2024-02-05T15:30:00"
    },
    {
        "id": 3,
        "worker_id": 1,
        "worker_name": "张师傅",
        "year": 2024,
        "month": 2,
        "base_salary": 5000.00,
        "overtime_hours": 25,
        "overtime_rate": 50.00,
        "overtime_pay": 1250.00,
        "bonus": 800.00,
        "deductions": 100.00,
        "total_salary": 6950.00,
        "status": "pending",
        "pay_date": None,
        "created_at": "2024-03-01T10:00:00",
        "updated_at": "2024-03-01T10:00:00"
    }
]


@router.get("/my-wages", response_model=List[dict])
def read_my_wages(
    db: Session = Depends(get_db),
    year: int = None,
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """获取当前工人的工资记录"""
    worker_wages = [w for w in MOCK_WAGES if w["worker_id"] == current_worker.id]
    
    if year:
        worker_wages = [w for w in worker_wages if w["year"] == year]
    
    return worker_wages


@router.get("/my-wages/{wage_id}", response_model=dict)
def read_my_wage_detail(
    *,
    db: Session = Depends(get_db),
    wage_id: int,
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """获取工资详情"""
    wage = next((w for w in MOCK_WAGES if w["id"] == wage_id), None)
    if not wage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工资记录不存在"
        )
    
    # 验证工人只能查看自己的工资
    if wage["worker_id"] != current_worker.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此工资记录"
        )
    
    return wage


@router.get("/my-wages/summary/{year}", response_model=dict)
def get_my_wage_summary(
    *,
    db: Session = Depends(get_db),
    year: int,
    current_worker: RepairWorker = Depends(get_current_active_worker),
) -> Any:
    """获取年度工资汇总"""
    worker_wages = [w for w in MOCK_WAGES if w["worker_id"] == current_worker.id and w["year"] == year]
    
    if not worker_wages:
        return {
            "year": year,
            "total_months": 0,
            "total_salary": 0.00,
            "total_overtime_hours": 0,
            "total_overtime_pay": 0.00,
            "total_bonus": 0.00,
            "total_deductions": 0.00,
            "average_monthly_salary": 0.00
        }
    
    total_salary = sum(w["total_salary"] for w in worker_wages)
    total_overtime_hours = sum(w["overtime_hours"] for w in worker_wages)
    total_overtime_pay = sum(w["overtime_pay"] for w in worker_wages)
    total_bonus = sum(w["bonus"] for w in worker_wages)
    total_deductions = sum(w["deductions"] for w in worker_wages)
    
    return {
        "year": year,
        "total_months": len(worker_wages),
        "total_salary": total_salary,
        "total_overtime_hours": total_overtime_hours,
        "total_overtime_pay": total_overtime_pay,
        "total_bonus": total_bonus,
        "total_deductions": total_deductions,
        "average_monthly_salary": total_salary / len(worker_wages)
    }


# 管理员专用接口
@router.get("/admin/all", response_model=List[dict])
def read_all_wages_admin(
    db: Session = Depends(get_db),
    year: int = None,
    month: int = None,
    status: str = None,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取所有工资记录（管理员专用）"""
    wages = MOCK_WAGES.copy()
    
    if year:
        wages = [w for w in wages if w["year"] == year]
    
    if month:
        wages = [w for w in wages if w["month"] == month]
    
    if status:
        wages = [w for w in wages if w["status"] == status]
    
    return wages


@router.get("/admin/pending", response_model=List[dict])
def read_pending_wages(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取待支付的工资（管理员专用）"""
    pending_wages = [w for w in MOCK_WAGES if w["status"] == "pending"]
    return pending_wages


@router.post("/admin/", response_model=dict)
def create_wage_record(
    *,
    db: Session = Depends(get_db),
    wage_data: dict,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """创建工资记录（管理员专用）"""
    # 检查是否已存在该工人该月的工资记录
    existing_wage = next((
        w for w in MOCK_WAGES 
        if w["worker_id"] == wage_data["worker_id"] 
        and w["year"] == wage_data["year"] 
        and w["month"] == wage_data["month"]
    ), None)
    
    if existing_wage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该工人该月的工资记录已存在"
        )
    
    # 生成新ID
    new_id = max([w["id"] for w in MOCK_WAGES]) + 1 if MOCK_WAGES else 1
    
    # 计算总工资
    base_salary = wage_data.get("base_salary", 0)
    overtime_pay = wage_data.get("overtime_pay", 0)
    bonus = wage_data.get("bonus", 0)
    deductions = wage_data.get("deductions", 0)
    total_salary = base_salary + overtime_pay + bonus - deductions
    
    new_wage = {
        "id": new_id,
        "worker_id": wage_data["worker_id"],
        "worker_name": wage_data["worker_name"],
        "year": wage_data["year"],
        "month": wage_data["month"],
        "base_salary": base_salary,
        "overtime_hours": wage_data.get("overtime_hours", 0),
        "overtime_rate": wage_data.get("overtime_rate", 0),
        "overtime_pay": overtime_pay,
        "bonus": bonus,
        "deductions": deductions,
        "total_salary": total_salary,
        "status": "pending",
        "pay_date": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    MOCK_WAGES.append(new_wage)
    return new_wage


@router.put("/admin/{wage_id}", response_model=dict)
def update_wage_record(
    *,
    db: Session = Depends(get_db),
    wage_id: int,
    wage_data: dict,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """更新工资记录（管理员专用）"""
    wage_index = next((i for i, w in enumerate(MOCK_WAGES) if w["id"] == wage_id), None)
    if wage_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工资记录不存在"
        )
    
    # 只有待支付的工资才能修改
    if MOCK_WAGES[wage_index]["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能修改待支付的工资记录"
        )
    
    # 更新工资信息
    allowed_fields = {
        "base_salary", "overtime_hours", "overtime_rate", 
        "overtime_pay", "bonus", "deductions"
    }
    
    for key, value in wage_data.items():
        if key in allowed_fields:
            MOCK_WAGES[wage_index][key] = value
    
    # 重新计算总工资
    wage = MOCK_WAGES[wage_index]
    total_salary = (wage["base_salary"] + wage["overtime_pay"] + 
                   wage["bonus"] - wage["deductions"])
    MOCK_WAGES[wage_index]["total_salary"] = total_salary
    MOCK_WAGES[wage_index]["updated_at"] = datetime.now().isoformat()
    
    return MOCK_WAGES[wage_index]


@router.put("/admin/{wage_id}/pay", response_model=dict)
def mark_wage_as_paid(
    *,
    db: Session = Depends(get_db),
    wage_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """标记工资为已支付（管理员专用）"""
    wage_index = next((i for i, w in enumerate(MOCK_WAGES) if w["id"] == wage_id), None)
    if wage_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工资记录不存在"
        )
    
    if MOCK_WAGES[wage_index]["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能支付待支付的工资"
        )
    
    MOCK_WAGES[wage_index]["status"] = "paid"
    MOCK_WAGES[wage_index]["pay_date"] = date.today().isoformat()
    MOCK_WAGES[wage_index]["updated_at"] = datetime.now().isoformat()
    
    return MOCK_WAGES[wage_index]


@router.delete("/admin/{wage_id}", response_model=MessageResponse)
def delete_wage_record(
    *,
    db: Session = Depends(get_db),
    wage_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """删除工资记录（管理员专用）"""
    wage_index = next((i for i, w in enumerate(MOCK_WAGES) if w["id"] == wage_id), None)
    if wage_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工资记录不存在"
        )
    
    # 只有待支付的工资才能删除
    if MOCK_WAGES[wage_index]["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能删除待支付的工资记录"
        )
    
    MOCK_WAGES.pop(wage_index)
    return MessageResponse(message="工资记录删除成功")


@router.get("/admin/statistics/overview", response_model=dict)
def get_wage_statistics(
    db: Session = Depends(get_db),
    year: int = None,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取工资统计信息（管理员专用）"""
    wages = MOCK_WAGES.copy()
    
    if year:
        wages = [w for w in wages if w["year"] == year]
    
    total_wages = len(wages)
    pending_wages = len([w for w in wages if w["status"] == "pending"])
    paid_wages = len([w for w in wages if w["status"] == "paid"])
    
    # 金额统计
    total_amount = sum(w["total_salary"] for w in wages)
    pending_amount = sum(w["total_salary"] for w in wages if w["status"] == "pending")
    paid_amount = sum(w["total_salary"] for w in wages if w["status"] == "paid")
    
    # 平均工资
    avg_salary = total_amount / total_wages if total_wages > 0 else 0
    
    return {
        "period": f"{year}年" if year else "全部",
        "total_records": total_wages,
        "pending_records": pending_wages,
        "paid_records": paid_wages,
        "total_amount": round(total_amount, 2),
        "pending_amount": round(pending_amount, 2),
        "paid_amount": round(paid_amount, 2),
        "average_salary": round(avg_salary, 2)
    } 