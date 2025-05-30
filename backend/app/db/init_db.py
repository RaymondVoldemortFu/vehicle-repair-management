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
from app.config.settings import settings
from app.config.logging import get_database_logger

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
        
        # 检查 feedback 表是否存在
        if not check_table_exists("feedback"):
            logger.info("检测到 feedback 表不存在，将创建缺失的表...")
            # 创建所有表（SQLAlchemy 会自动跳过已存在的表）
            Base.metadata.create_all(bind=engine)
            logger.info("数据库表创建/更新完成")
        else:
            logger.info("所有必要的表都已存在")
        
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


def init_database():
    """初始化数据库"""
    logger.info("开始初始化数据库...")
    
    try:
        # 创建数据库（如果不存在）
        create_database_if_not_exists()
        
        # 创建表
        create_tables()
        
        # 添加username字段
        add_username_column()
        
        # 更新phone字段
        update_phone_column()
        
        logger.info("数据库初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


def init_database_on_startup():
    """应用启动时的数据库初始化（静默模式）"""
    try:
        logger.info("正在检查数据库状态...")
        
        # 创建数据库（如果不存在）
        create_database_if_not_exists()
        
        # 创建表
        create_tables()
        
        # 添加username字段
        add_username_column()
        
        # 更新phone字段
        update_phone_column()
        
        logger.info("数据库检查完成")
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise e
        return False


if __name__ == "__main__":
    init_database() 