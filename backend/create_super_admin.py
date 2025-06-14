#!/usr/bin/env python3
"""
手动创建超级管理员脚本
使用方法: python create_super_admin.py
"""

import sys
import os
import getpass
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.config.database import SessionLocal
from app.crud.admin import admin_crud
from app.models.admin import AdminRole, AdminStatus
from app.schemas.admin import AdminCreate
from app.config.logging import get_logger

logger = get_logger()


def validate_username(username: str) -> bool:
    """验证用户名格式"""
    if not username:
        return False
    if len(username) < 3 or len(username) > 50:
        return False
    if not username.replace('_', '').replace('-', '').isalnum():
        return False
    return True


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """验证密码强度"""
    if len(password) < 6:
        return False
    return True


def create_super_admin_interactive():
    """交互式创建超级管理员"""
    print("=" * 60)
    print("车辆维修管理系统 - 超级管理员创建工具")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # 检查是否已存在超级管理员
        existing_super_admins = admin_crud.get_super_admins(db)
        if existing_super_admins:
            print("⚠️  警告: 系统中已存在以下超级管理员:")
            for admin in existing_super_admins:
                print(f"   - {admin.username} ({admin.name}) - {admin.email}")
            print()
            
            confirm = input("是否继续创建新的超级管理员? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("操作已取消。")
                return
            print()
        
        # 收集管理员信息
        print("请输入超级管理员信息:")
        print("-" * 30)
        
        # 用户名
        while True:
            username = input("用户名 (3-50个字符，仅含字母数字下划线): ").strip()
            if not validate_username(username):
                print("❌ 用户名格式不正确，请重新输入。")
                continue
            
            # 检查用户名是否已存在
            existing_admin = admin_crud.get_by_username(db, username=username)
            if existing_admin:
                print("❌ 用户名已存在，请选择其他用户名。")
                continue
            
            break
        
        # 姓名
        while True:
            name = input("姓名: ").strip()
            if name and len(name) <= 100:
                break
            print("❌ 姓名不能为空且不能超过100个字符。")
        
        # 邮箱
        while True:
            email = input("邮箱地址: ").strip()
            if not validate_email(email):
                print("❌ 邮箱格式不正确，请重新输入。")
                continue
            
            # 检查邮箱是否已存在
            existing_admin = admin_crud.get_by_email(db, email=email)
            if existing_admin:
                print("❌ 邮箱已存在，请选择其他邮箱。")
                continue
            
            break
        
        # 手机号（可选）
        phone = input("手机号码 (可选): ").strip()
        if phone and (len(phone) < 11 or len(phone) > 20):
            print("⚠️  手机号码长度不正确，将忽略此字段。")
            phone = None
        
        # 密码
        while True:
            password = getpass.getpass("密码 (至少6位): ")
            if not validate_password(password):
                print("❌ 密码长度至少6位，请重新输入。")
                continue
            
            confirm_password = getpass.getpass("确认密码: ")
            if password != confirm_password:
                print("❌ 两次输入的密码不一致，请重新输入。")
                continue
            
            break
        
        print()
        print("超级管理员信息确认:")
        print("-" * 30)
        print(f"用户名: {username}")
        print(f"姓名: {name}")
        print(f"邮箱: {email}")
        if phone:
            print(f"手机: {phone}")
        print(f"角色: 超级管理员")
        print()
        
        confirm = input("确认创建超级管理员? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("操作已取消。")
            return
        
        # 创建超级管理员
        admin_create = AdminCreate(
            username=username,
            name=name,
            email=email,
            phone=phone,
            role=AdminRole.SUPER_ADMIN,
            password=password
        )
        
        super_admin = admin_crud.create_super_admin(db, obj_in=admin_create)
        
        print()
        print("✅ 超级管理员创建成功！")
        print("-" * 30)
        print(f"ID: {super_admin.id}")
        print(f"用户名: {super_admin.username}")
        print(f"姓名: {super_admin.name}")
        print(f"邮箱: {super_admin.email}")
        print(f"角色: {super_admin.role.value}")
        print(f"状态: {super_admin.status.value}")
        print()
        print("🔐 请妥善保管登录凭据，建议在首次登录后立即修改密码。")
        
    except Exception as e:
        logger.error(f"创建超级管理员失败: {str(e)}")
        print(f"❌ 创建失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


def create_super_admin_from_args():
    """从命令行参数创建超级管理员"""
    import argparse
    
    parser = argparse.ArgumentParser(description='创建超级管理员')
    parser.add_argument('--username', required=True, help='用户名')
    parser.add_argument('--name', required=True, help='姓名')
    parser.add_argument('--email', required=True, help='邮箱')
    parser.add_argument('--phone', help='手机号码')
    parser.add_argument('--password', required=True, help='密码')
    parser.add_argument('--force', action='store_true', help='强制创建（即使已存在超级管理员）')
    
    args = parser.parse_args()
    
    # 验证输入
    if not validate_username(args.username):
        print("❌ 用户名格式不正确")
        return False
    
    if not validate_email(args.email):
        print("❌ 邮箱格式不正确")
        return False
    
    if not validate_password(args.password):
        print("❌ 密码长度至少6位")
        return False
    
    db = SessionLocal()
    try:
        # 检查是否已存在
        if not args.force:
            existing_super_admins = admin_crud.get_super_admins(db)
            if existing_super_admins:
                print("❌ 系统中已存在超级管理员，使用 --force 参数强制创建")
                return False
        
        # 检查用户名和邮箱是否已被占用
        if admin_crud.get_by_username(db, username=args.username):
            print("❌ 用户名已存在")
            return False
        
        if admin_crud.get_by_email(db, email=args.email):
            print("❌ 邮箱已存在")
            return False
        
        # 创建超级管理员
        admin_create = AdminCreate(
            username=args.username,
            name=args.name,
            email=args.email,
            phone=args.phone,
            role=AdminRole.SUPER_ADMIN,
            password=args.password
        )
        
        super_admin = admin_crud.create_super_admin(db, obj_in=admin_create)
        
        print("✅ 超级管理员创建成功！")
        print(f"ID: {super_admin.id}")
        print(f"用户名: {super_admin.username}")
        
        return True
        
    except Exception as e:
        logger.error(f"创建超级管理员失败: {str(e)}")
        print(f"❌ 创建失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        create_super_admin_from_args()
    else:
        create_super_admin_interactive() 