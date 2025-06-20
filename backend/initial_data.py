import sys
import os

# 将项目根目录添加到Python路径，以确保模块可以被正确导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.crud.user import user_crud
from app.crud.admin import admin_crud
from app.crud.repair_worker import repair_worker_crud as worker_crud
from app.crud.material import material_crud
from app.schemas.user import UserCreate
from app.schemas.admin import AdminCreate
from app.schemas.repair_worker import RepairWorkerCreate
from app.schemas.material import MaterialCreate
from app.models.user import User
from app.models.admin import Admin
from app.models.repair_worker import RepairWorker
from app.models.material import Material
from app.core.security import get_password_hash

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始数据
INITIAL_ADMINS = [
    {
        "username": "superadmin", "name": "超级管理员", "password": "SuperAdminPassword123", "role": "super_admin",
        "email": "superadmin@example.com", "phone": "10000000000"
    },
    {
        "username": "manager_wang", "name": "王经理", "password": "ManagerPassword123", "role": "manager",
        "email": "manager.wang@example.com", "phone": "10000000001"
    },
]

INITIAL_USERS = [
    {
        "username": "zhangsan", "name": "张三", "password": "Password123", "email": "zhangsan@example.com",
        "phone": "13800138000", "address": "北京市朝阳区"
    },
    {
        "username": "lisi", "name": "李四", "password": "Password123", "email": "lisi@example.com",
        "phone": "13800138001", "address": "上海市浦东新区"
    },
    {
        "username": "wangwu", "name": "王五", "password": "Password123", "email": "wangwu@example.com",
        "phone": "13800138002", "address": "广州市天河区"
    },
]

INITIAL_WORKERS = [
    {
        "employee_id": "W001", "name": "维修师傅赵", "password": "WorkerPassword123", "phone": "13900139000",
        "email": "worker.zhao@example.com", "skill_type": "engine", "skill_level": "senior", "hourly_rate": 150.00,
        "hire_date": "2022-01-15"
    },
    {
        "employee_id": "W002", "name": "维修师傅钱", "password": "WorkerPassword123", "phone": "13900139001",
        "email": "worker.qian@example.com", "skill_type": "electrical", "skill_level": "intermediate",
        "hourly_rate": 120.50, "hire_date": "2023-03-20"
    },
    {
        "employee_id": "W003", "name": "维修学徒孙", "password": "WorkerPassword123", "phone": "13900139002",
        "email": "worker.sun@example.com", "skill_type": "bodywork", "skill_level": "junior", "hourly_rate": 80.00,
        "hire_date": "2024-05-10"
    },
]

INITIAL_MATERIALS = [
    {"material_code": "OIL-5W30", "name": "5W-30 全合成机油", "category": "润滑油", "unit_price": 88.00, "unit": "升", "stock_quantity": 100},
    {"material_code": "FILTER-OIL", "name": "机油滤清器", "category": "滤清器", "unit_price": 35.50, "unit": "个", "stock_quantity": 200},
    {"material_code": "FILTER-AIR", "name": "空气滤清器", "category": "滤清器", "unit_price": 50.00, "unit": "个", "stock_quantity": 150},
    {"material_code": "BRAKE-PAD-F", "name": "前刹车片", "category": "刹车系统", "unit_price": 280.00, "unit": "套", "stock_quantity": 50},
    {"material_code": "BRAKE-PAD-R", "name": "后刹车片", "category": "刹车系统", "unit_price": 240.00, "unit": "套", "stock_quantity": 50},
    {"material_code": "SPARK-PLUG", "name": "火花塞 (铱金)", "category": "点火系统", "unit_price": 75.00, "unit": "支", "stock_quantity": 300},
    {"material_code": "BATTERY-60AH", "name": "60Ah 汽车电瓶", "category": "电气系统", "unit_price": 450.00, "unit": "个", "stock_quantity": 30},
    {"material_code": "TYRE-205-55-R16", "name": "轮胎 205/55 R16", "category": "轮胎", "unit_price": 380.00, "unit": "条", "stock_quantity": 40},
]


def init_db(db: Session) -> None:
    # 创建管理员
    for admin_data in INITIAL_ADMINS:
        admin = admin_crud.get_by_username(db, username=admin_data["username"])
        if not admin:
            admin_in = AdminCreate(**admin_data)
            admin_crud.create(db, obj_in=admin_in)
            logger.info(f"Admin '{admin_data['username']}' created.")
        else:
            logger.info(f"Admin '{admin_data['username']}' already exists.")

    # 创建用户
    for user_data in INITIAL_USERS:
        user = user_crud.get_by_username(db, username=user_data["username"])
        if not user:
            user_in = UserCreate(**user_data)
            user_crud.create(db, obj_in=user_in)
            logger.info(f"User '{user_data['username']}' created.")
        else:
            logger.info(f"User '{user_data['username']}' already exists.")

    # 创建工人
    for worker_data in INITIAL_WORKERS:
        worker = worker_crud.get_by_employee_id(db, employee_id=worker_data["employee_id"])
        if not worker:
            worker_in = RepairWorkerCreate(**worker_data)
            worker_crud.create(db, obj_in=worker_in)
            logger.info(f"Worker '{worker_data['name']}' ({worker_data['employee_id']}) created.")
        else:
            logger.info(f"Worker '{worker_data['name']}' ({worker_data['employee_id']}) already exists.")

    # 创建材料
    for material_data in INITIAL_MATERIALS:
        material = material_crud.get_by_code(db, code=material_data["material_code"])
        if not material:
            material_in = MaterialCreate(**material_data)
            material_crud.create(db, obj_in=material_in)
            logger.info(f"Material '{material_data['name']}' ({material_data['material_code']}) created.")
        else:
            logger.info(f"Material '{material_data['name']}' ({material_data['material_code']}) already exists.")


def main() -> None:
    logger.info("Starting database initialization...")
    db = SessionLocal()
    try:
        init_db(db)
        logger.info("Database initialization finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main() 