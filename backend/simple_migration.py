#!/usr/bin/env python3
"""
反馈表添加标题字段迁移脚本
修复前端标题字段无法存储到数据库的问题
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def add_title_column():
    """为feedback表添加title字段"""
    try:
        # 获取数据库连接参数
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            # 如果没有环境变量，使用默认值
            database_url = "mysql+pymysql://root:@localhost:3306/vehicle_repair_db"
        
        print(f"正在连接数据库: {database_url.split('@')[1] if '@' in database_url else database_url}")
        
        engine = create_engine(database_url, echo=False)
        
        print("开始检查feedback表的title字段...")
        
        # 检查title字段是否已存在
        with engine.connect() as connection:
            # 从DATABASE_URL中提取数据库名
            db_name = database_url.split('/')[-1]
            
            result = connection.execute(text(f"""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = '{db_name}' 
                AND TABLE_NAME = 'feedback' 
                AND COLUMN_NAME = 'title'
            """))
            row = result.fetchone()
            if row[0] > 0:
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
        print("提示：请确保数据库连接参数正确")
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
            return False
            
    except Exception as e:
        print(f"❌ 迁移过程中发生异常: {e}")
        return False
        
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        exit(1) 