#!/usr/bin/env python3
"""
测试数据库初始化功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.init_db import init_database_on_startup, check_table_exists, check_column_exists
from app.config.logging import setup_logging, get_logger

def test_database_initialization():
    """测试数据库初始化功能"""
    # 初始化日志
    setup_logging()
    logger = get_logger()
    
    logger.info("=" * 50)
    logger.info("开始测试数据库初始化功能")
    logger.info("=" * 50)
    
    try:
        # 测试数据库初始化
        success = init_database_on_startup()
        
        if success:
            logger.info("✅ 数据库初始化成功")
            
            # 检查关键表是否存在
            tables_to_check = ["users", "admins", "vehicles", "repair_orders"]
            
            for table in tables_to_check:
                if check_table_exists(table):
                    logger.info(f"✅ 表 '{table}' 存在")
                else:
                    logger.warning(f"⚠️  表 '{table}' 不存在")
            
            # 检查users表的username字段
            if check_column_exists("users", "username"):
                logger.info("✅ users表的username字段存在")
            else:
                logger.warning("⚠️  users表的username字段不存在")
            
            logger.info("=" * 50)
            logger.info("✅ 数据库初始化测试完成")
            logger.info("=" * 50)
            
        else:
            logger.error("❌ 数据库初始化失败")
            
    except Exception as e:
        logger.error(f"❌ 测试过程中出现异常: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_database_initialization() 