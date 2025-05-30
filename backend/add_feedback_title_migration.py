#!/usr/bin/env python3
"""
反馈表添加标题字段迁移脚本
修复前端标题字段无法存储到数据库的问题
使用SQLAlchemy进行数据库操作
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings


def check_column_exists(engine, table_name, column_name):
    """检查表中是否存在指定字段"""
    with engine.connect() as connection:
        result = connection.execute(text(f"""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = '{settings.DB_NAME}' 
            AND TABLE_NAME = '{table_name}' 
            AND COLUMN_NAME = '{column_name}'
        """))
        row = result.fetchone()
        return row[0] > 0


def add_title_column():
    """为feedback表添加title字段"""
    try:
        # 创建数据库引擎
        engine = create_engine(
            f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
            echo=False
        )
        
        print("开始检查feedback表的title字段...")
        
        # 检查title字段是否已存在
        if check_column_exists(engine, 'feedback', 'title'):
            print("✅ title字段已存在，跳过添加")
            return True
        
        print("正在添加title字段...")
        
        with engine.connect() as connection:
            # 开始事务
            trans = connection.begin()
            try:
                # 添加title字段
                connection.execute(text("""
                    ALTER TABLE feedback 
                    ADD COLUMN title VARCHAR(100) NOT NULL DEFAULT '' COMMENT '反馈标题'
                    AFTER order_id
                """))
                
                print("正在为现有记录生成标题...")
                
                # 为现有记录生成标题（从comment字段的前50个字符）
                connection.execute(text("""
                    UPDATE feedback 
                    SET title = CASE 
                        WHEN LENGTH(comment) > 50 THEN CONCAT(LEFT(comment, 50), '...')
                        ELSE comment
                    END
                    WHERE title = '' OR title IS NULL
                """))
                
                # 提交事务
                trans.commit()
                print("✅ title字段添加成功")
                print("✅ 现有记录标题生成完成")
                
                return True
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                raise e
        
    except SQLAlchemyError as e:
        print(f"❌ 数据库操作失败: {e}")
        return False
        
    except Exception as e:
        print(f"❌ 发生异常: {e}")
        return False


def main():
    """主函数"""
    print("=================================================================")
    print("🔧 反馈系统标题字段迁移工具")
    print("修复前端标题字段无法存储到数据库的问题")
    print("=================================================================")
    
    try:
        success = add_title_column()
        
        if success:
            print("=================================================================")
            print("✅ 迁移完成!")
            print("现在可以正常使用反馈系统的标题功能了")
            print("=================================================================")
        else:
            print("=================================================================")
            print("❌ 迁移失败!")
            print("请检查错误信息并重试")
            print("=================================================================")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 迁移过程中发生异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 