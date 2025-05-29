#!/usr/bin/env python3
"""
数据库迁移脚本
运行此脚本来更新数据库结构，添加username字段并移除手机号/邮箱认证功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.init_db import init_database
from app.config.logging import setup_logging, get_logger

def main():
    """主函数"""
    # 初始化日志
    setup_logging()
    logger = get_logger()
    
    logger.info("=" * 50)
    logger.info("开始执行数据库迁移")
    logger.info("=" * 50)
    
    try:
        # 执行数据库初始化/迁移
        init_database()
        
        logger.info("=" * 50)
        logger.info("数据库迁移完成！")
        logger.info("现在用户可以使用用户名和密码进行注册和登录")
        logger.info("手机号和邮箱字段已改为可选")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error("=" * 50)
        logger.error(f"数据库迁移失败: {str(e)}")
        logger.error("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main() 