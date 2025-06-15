"""
数据库初始化脚本
"""
from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
import pymysql
from app.config.database import engine, SessionLocal
from app.models.base import Base
# 导入所有模型以确保它们被注册到 SQLAlchemy 元数据中
from app.models import (
    User, Vehicle, Admin, RepairWorker, Service, Material,
    RepairOrder, RepairOrderWorker, RepairOrderService, 
    RepairMaterial, Feedback, Wage
)
from app.models.admin import AdminRole, AdminStatus
from app.config.settings import settings
from app.config.logging import get_database_logger
from app.core.security import get_password_hash
from app.db.init_data import init_materials

logger = get_database_logger()


def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    try:
        # 解析数据库URL获取数据库名
        db_url = settings.DATABASE_URL
        if "mysql" not in db_url:
            logger.info("非MySQL数据库，跳过数据库创建检查")
            return
        
        # 提取数据库连接信息
        import re
        pattern = r'mysql\+pymysql://([^:@]+)(?::([^@]+))?@([^:/]+)(?::(\d+))?/(.+)'
        match = re.match(pattern, db_url)
        
        if not match:
            logger.warning("无法解析数据库URL，跳过数据库创建")
            return
            
        username, password, host, port, database_name = match.groups()
        
        # 创建不包含数据库名的连接URL
        if password:
            base_url = f"mysql+pymysql://{username}:{password}@{host}:{port}"
        else:
            base_url = f"mysql+pymysql://{username}@{host}:{port}"
        
        # 连接到MySQL服务器（不指定数据库）
        temp_engine = create_engine(base_url)
        
        with temp_engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text(f"SHOW DATABASES LIKE '{database_name}'"))
            if result.fetchone():
                logger.info(f"数据库 '{database_name}' 已存在")
            else:
                # 创建数据库
                logger.info(f"正在创建数据库 '{database_name}'...")
                conn.execute(text(f"CREATE DATABASE `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
                logger.info(f"数据库 '{database_name}' 创建成功")
        
        temp_engine.dispose()
        
    except Exception as e:
        logger.error(f"创建数据库失败: {str(e)}")
        raise


def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_name = :table_name 
            AND table_schema = DATABASE()
        """), {"table_name": table_name})
        
        count = result.fetchone()[0]
        return count > 0
        
    except Exception as e:
        logger.error(f"检查表 {table_name} 是否存在时出错: {str(e)}")
        return False
    finally:
        db.close()


def create_tables():
    """创建所有表"""
    try:
        logger.info("开始检查并创建数据库表...")
        # SQLAlchemy 的 create_all 会自动跳过已存在的表，所以可以直接调用
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建/更新完成")
    except Exception as e:
        logger.error(f"创建数据库表失败: {str(e)}")
        raise


def check_column_exists(table_name: str, column_name: str) -> bool:
    """检查字段是否存在"""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT COUNT(*) as count 
            FROM information_schema.columns 
            WHERE table_name = :table_name 
            AND column_name = :column_name 
            AND table_schema = DATABASE()
        """), {"table_name": table_name, "column_name": column_name})
        
        count = result.fetchone()[0]
        return count > 0
        
    except Exception as e:
        logger.error(f"检查字段 {table_name}.{column_name} 是否存在时出错: {str(e)}")
        return False
    finally:
        db.close()


def add_username_column():
    """为用户表添加username字段（如果不存在）"""
    if not check_table_exists("users"):
        logger.info("users表不存在，跳过username字段添加")
        return
        
    if check_column_exists("users", "username"):
        logger.info("username字段已存在，跳过添加")
        return
    
    db = SessionLocal()
    try:
        logger.info("正在为users表添加username字段...")
        
        # 添加username字段
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN username VARCHAR(50) UNIQUE AFTER name
        """))
        
        # 为现有用户生成默认用户名（基于手机号或ID）
        db.execute(text("""
            UPDATE users 
            SET username = CASE 
                WHEN phone IS NOT NULL THEN CONCAT('user_', SUBSTRING(phone, -6))
                ELSE CONCAT('user_', id)
            END
            WHERE username IS NULL
        """))
        
        # 设置username为非空
        db.execute(text("""
            ALTER TABLE users 
            MODIFY COLUMN username VARCHAR(50) NOT NULL
        """))
        
        # 添加索引
        db.execute(text("""
            CREATE INDEX idx_users_username ON users(username)
        """))
        
        db.commit()
        logger.info("username字段添加完成")
        
    except Exception as e:
        logger.error(f"添加username字段失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def update_phone_column():
    """将phone字段改为可选"""
    if not check_table_exists("users"):
        logger.info("users表不存在，跳过phone字段更新")
        return
    
    db = SessionLocal()
    try:
        logger.info("正在更新phone字段为可选...")
        
        # 修改phone字段为可空
        db.execute(text("""
            ALTER TABLE users 
            MODIFY COLUMN phone VARCHAR(20) NULL
        """))
        
        db.commit()
        logger.info("phone字段更新完成")
        
    except Exception as e:
        logger.error(f"更新phone字段失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def add_missing_repair_order_columns():
    """为 repair_orders 表添加缺失的字段"""
    if not check_table_exists("repair_orders"):
        logger.info("repair_orders 表不存在，跳过字段添加")
        return

    db = SessionLocal()
    try:
        if not check_column_exists("repair_orders", "comment"):
            logger.info("正在为 repair_orders 表添加 comment 字段...")
            db.execute(text("ALTER TABLE repair_orders ADD COLUMN comment VARCHAR(500) AFTER internal_notes"))
            db.commit()
            logger.info("comment 字段添加成功")

        if not check_column_exists("repair_orders", "status_history"):
            logger.info("正在为 repair_orders 表添加 status_history 字段...")
            db.execute(text("ALTER TABLE repair_orders ADD COLUMN status_history VARCHAR(1000) AFTER comment"))
            db.commit()
            logger.info("status_history 字段添加成功")
            
    except Exception as e:
        logger.error(f"为 repair_orders 添加字段失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


def create_default_super_admin():
    """创建默认超级管理员账号"""
    db = SessionLocal()
    try:
        # 检查是否已存在超级管理员
        existing_super_admin = db.query(Admin).filter(
            Admin.role == AdminRole.SUPER_ADMIN,
            Admin.is_deleted == False
        ).first()
        
        if existing_super_admin:
            logger.info(f"超级管理员已存在: {existing_super_admin.username}")
            return
        
        # 检查默认用户名是否已被占用
        existing_admin = db.query(Admin).filter(
            Admin.username == settings.DEFAULT_SUPER_ADMIN_USERNAME,
            Admin.is_deleted == False
        ).first()
        
        if existing_admin:
            # 如果已存在同名用户但不是超级管理员，更新其角色
            if existing_admin.role != AdminRole.SUPER_ADMIN:
                logger.info(f"更新现有管理员 {existing_admin.username} 为超级管理员")
                existing_admin.role = AdminRole.SUPER_ADMIN
                existing_admin.status = AdminStatus.ACTIVE
                db.commit()
                db.refresh(existing_admin)
                logger.info(f"超级管理员更新成功: {existing_admin.username}")
            return
        
        # 创建新的超级管理员
        logger.info("创建默认超级管理员账号...")
        
        super_admin = Admin(
            username=settings.DEFAULT_SUPER_ADMIN_USERNAME,
            name=settings.DEFAULT_SUPER_ADMIN_NAME,
            email=settings.DEFAULT_SUPER_ADMIN_EMAIL,
            password_hash=get_password_hash(settings.DEFAULT_SUPER_ADMIN_PASSWORD),
            role=AdminRole.SUPER_ADMIN,
            status=AdminStatus.ACTIVE,
            permissions={
                "system_admin": True,
                "user_management": True,
                "order_management": True,
                "worker_management": True,
                "material_management": True,
                "service_management": True,
                "analytics": True,
                "feedback_management": True,
                "wage_management": True
            }
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        logger.info(f"默认超级管理员创建成功!")
        logger.info(f"用户名: {settings.DEFAULT_SUPER_ADMIN_USERNAME}")
        logger.info(f"密码: {settings.DEFAULT_SUPER_ADMIN_PASSWORD}")
        logger.info("请在生产环境中立即更改默认密码!")
        
    except Exception as e:
        logger.error(f"创建默认超级管理员失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_database():
    """初始化数据库、表和默认数据"""
    try:
        # 1. 创建数据库（如果需要）
        create_database_if_not_exists()
        
        # 2. 创建所有表
        create_tables()
        
        # 3. 数据迁移/结构更新（如果需要）
        add_username_column()
        update_phone_column()
        add_missing_repair_order_columns()

        # 4. 初始化基础数据
        db = SessionLocal()
        try:
            create_default_super_admin()
            # 在这里添加其他数据初始化函数
            init_materials(db)
            db.commit()
            logger.info("默认数据初始化完成")
        except Exception as e:
            logger.error(f"初始化默认数据时发生错误: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
            
        logger.info("数据库初始化流程完成")
        return True

    except Exception as e:
        logger.error(f"数据库初始化流程失败: {str(e)}")
        return False


def init_database_on_startup():
    """应用启动时的数据库初始化（静默模式）"""
    try:
        logger.info("正在检查数据库状态...")
        
        # 创建数据库（如果不存在）
        create_database_if_not_exists()
        
        # 创建表
        create_tables()
        
        # 添加/更新字段
        add_username_column()
        update_phone_column()
        add_missing_repair_order_columns()
        
        # 创建默认超级管理员
        create_default_super_admin()
        
        logger.info("数据库检查完成")
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise e
        return False


if __name__ == "__main__":
    init_database() 