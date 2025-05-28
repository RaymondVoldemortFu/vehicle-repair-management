from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.config.database import get_db
from app.core.deps import get_current_active_admin
from app.crud.user import user_crud
from app.crud.vehicle import vehicle_crud
from app.crud.repair_order import repair_order_crud
from app.crud.repair_worker import repair_worker_crud
from app.crud.admin import admin_crud
from app.models.admin import Admin

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取仪表板数据（管理员专用）"""
    # 基础统计
    total_users = user_crud.count(db)
    total_vehicles = vehicle_crud.count(db)
    total_orders = repair_order_crud.count(db)
    total_workers = repair_worker_crud.count(db)
    
    # 订单统计
    order_stats = repair_order_crud.get_statistics(db)
    
    # 可用工人数量
    available_workers = len(repair_worker_crud.get_available_workers(db))
    
    return {
        "basic_stats": {
            "total_users": total_users,
            "total_vehicles": total_vehicles,
            "total_orders": total_orders,
            "total_workers": total_workers,
            "available_workers": available_workers
        },
        "order_statistics": order_stats,
        "last_updated": datetime.now().isoformat()
    }


@router.get("/overview", response_model=Dict[str, Any])
def get_system_overview(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取系统概览（管理员专用）"""
    # 用户统计
    user_stats = {
        "total_users": user_crud.count(db),
        "active_users": len(user_crud.get_active_users(db))
    }
    
    # 车辆统计
    vehicle_stats = {
        "total_vehicles": vehicle_crud.count(db),
        "brand_statistics": vehicle_crud.get_brand_statistics(db)
    }
    
    # 订单统计
    order_stats = repair_order_crud.get_statistics(db)
    
    # 工人统计
    worker_stats = {
        "total_workers": repair_worker_crud.count(db),
        "available_workers": len(repair_worker_crud.get_available_workers(db))
    }
    
    # 管理员统计
    admin_stats = {
        "total_admins": admin_crud.count(db),
        "active_admins": len(admin_crud.get_active_admins(db))
    }
    
    return {
        "user_statistics": user_stats,
        "vehicle_statistics": vehicle_stats,
        "order_statistics": order_stats,
        "worker_statistics": worker_stats,
        "admin_statistics": admin_stats,
        "generated_at": datetime.now().isoformat()
    }


@router.get("/trends/orders", response_model=Dict[str, Any])
def get_order_trends(
    db: Session = Depends(get_db),
    days: int = 30,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取订单趋势数据（管理员专用）"""
    # 这里应该实现按日期统计订单数量的逻辑
    # 由于没有具体的日期查询方法，这里返回模拟数据结构
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 获取基础统计
    total_orders = repair_order_crud.count(db)
    order_stats = repair_order_crud.get_statistics(db)
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "summary": {
            "total_orders": total_orders,
            "order_statistics": order_stats
        },
        "message": "详细的趋势数据需要在CRUD层实现按日期查询的方法"
    }


@router.get("/performance/workers", response_model=Dict[str, Any])
def get_worker_performance(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取工人绩效数据（管理员专用）"""
    total_workers = repair_worker_crud.count(db)
    available_workers = len(repair_worker_crud.get_available_workers(db))
    
    # 按技能类型统计
    from app.models.repair_worker import SkillType
    skill_stats = {}
    for skill_type in SkillType:
        workers = repair_worker_crud.get_by_skill_type(db, skill_type=skill_type)
        skill_stats[skill_type.value] = len(workers)
    
    return {
        "worker_summary": {
            "total_workers": total_workers,
            "available_workers": available_workers,
            "utilization_rate": (total_workers - available_workers) / total_workers * 100 if total_workers > 0 else 0
        },
        "skill_distribution": skill_stats,
        "generated_at": datetime.now().isoformat()
    }


@router.get("/reports/monthly", response_model=Dict[str, Any])
def get_monthly_report(
    db: Session = Depends(get_db),
    year: int = None,
    month: int = None,
    current_admin: Admin = Depends(get_current_active_admin),
) -> Any:
    """获取月度报告（管理员专用）"""
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month
    
    # 获取各项统计数据
    user_count = user_crud.count(db)
    vehicle_count = vehicle_crud.count(db)
    order_count = repair_order_crud.count(db)
    worker_count = repair_worker_crud.count(db)
    
    order_stats = repair_order_crud.get_statistics(db)
    
    return {
        "report_period": {
            "year": year,
            "month": month
        },
        "summary": {
            "total_users": user_count,
            "total_vehicles": vehicle_count,
            "total_orders": order_count,
            "total_workers": worker_count
        },
        "order_analysis": order_stats,
        "generated_at": datetime.now().isoformat(),
        "note": "这是基于当前数据的报告，需要实现按月份筛选的功能"
    } 