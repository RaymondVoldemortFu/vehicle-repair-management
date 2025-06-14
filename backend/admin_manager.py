#!/usr/bin/env python3
"""
管理员管理工具
提供超级管理员创建、重置、查看等功能
使用方法: python admin_manager.py [command] [options]
"""

import sys
import os
import getpass
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.config.database import SessionLocal
from app.crud.admin import admin_crud
from app.models.admin import AdminRole, AdminStatus
from app.schemas.admin import AdminCreate
from app.config.settings import settings
from app.config.logging import get_logger

logger = get_logger()


def list_admins():
    """列出所有管理员"""
    print("=" * 80)
    print("管理员列表")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        admins = db.query(admin_crud.model).filter(
            admin_crud.model.is_deleted == False
        ).order_by(admin_crud.model.id).all()
        
        if not admins:
            print("❌ 系统中没有管理员")
            return
        
        print(f"{'ID':<5} {'用户名':<20} {'姓名':<15} {'角色':<15} {'状态':<10} {'邮箱':<30} {'最后登录':<20}")
        print("-" * 115)
        
        for admin in admins:
            last_login = admin.last_login.strftime("%Y-%m-%d %H:%M") if admin.last_login else "从未登录"
            role_display = {
                AdminRole.SUPER_ADMIN: "超级管理员",
                AdminRole.MANAGER: "经理",
                AdminRole.SUPERVISOR: "主管",
                AdminRole.CLERK: "职员"
            }.get(admin.role, admin.role.value)
            
            status_display = {
                AdminStatus.ACTIVE: "正常",
                AdminStatus.INACTIVE: "禁用",
                AdminStatus.LOCKED: "锁定"
            }.get(admin.status, admin.status.value)
            
            print(f"{admin.id:<5} {admin.username:<20} {admin.name:<15} {role_display:<15} {status_display:<10} {admin.email:<30} {last_login:<20}")
        
        print(f"\n共 {len(admins)} 名管理员")
        
        # 统计信息
        super_admin_count = len([a for a in admins if a.role == AdminRole.SUPER_ADMIN])
        active_count = len([a for a in admins if a.status == AdminStatus.ACTIVE])
        
        print(f"超级管理员: {super_admin_count} 名")
        print(f"活跃管理员: {active_count} 名")
        
    except Exception as e:
        logger.error(f"列出管理员失败: {str(e)}")
        print(f"❌ 列出管理员失败: {str(e)}")
    finally:
        db.close()


def create_super_admin(username=None, name=None, email=None, phone=None, password=None, force=False):
    """创建超级管理员"""
    print("=" * 60)
    print("创建超级管理员")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 检查是否已存在超级管理员
        if not force:
            existing_super_admins = admin_crud.get_super_admins(db)
            if existing_super_admins:
                print("⚠️  系统中已存在超级管理员:")
                for admin in existing_super_admins:
                    print(f"   - {admin.username} ({admin.name})")
                return False
        
        # 如果参数不完整，交互式输入
        if not all([username, name, email, password]):
            print("请输入超级管理员信息:")
            if not username:
                username = input("用户名: ").strip()
            if not name:
                name = input("姓名: ").strip()
            if not email:
                email = input("邮箱: ").strip()
            if not phone:
                phone = input("手机号 (可选): ").strip() or None
            if not password:
                password = getpass.getpass("密码: ")
        
        # 验证输入
        if admin_crud.get_by_username(db, username=username):
            print("❌ 用户名已存在")
            return False
        
        if admin_crud.get_by_email(db, email=email):
            print("❌ 邮箱已存在")
            return False
        
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
        
        print("✅ 超级管理员创建成功！")
        print(f"ID: {super_admin.id}")
        print(f"用户名: {super_admin.username}")
        print(f"姓名: {super_admin.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"创建超级管理员失败: {str(e)}")
        print(f"❌ 创建失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def reset_admin_password(username=None, new_password=None):
    """重置管理员密码"""
    print("=" * 60)
    print("重置管理员密码")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        if not username:
            username = input("请输入要重置密码的管理员用户名: ").strip()
        
        admin = admin_crud.get_by_username(db, username=username)
        if not admin:
            print("❌ 管理员不存在")
            return False
        
        if not new_password:
            new_password = getpass.getpass("请输入新密码: ")
        
        admin_crud.update_password(db, admin=admin, new_password=new_password)
        
        print("✅ 密码重置成功！")
        print(f"管理员: {admin.username} ({admin.name})")
        
        return True
        
    except Exception as e:
        logger.error(f"重置密码失败: {str(e)}")
        print(f"❌ 重置密码失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def activate_admin(username):
    """激活管理员"""
    db = SessionLocal()
    try:
        admin = admin_crud.get_by_username(db, username=username)
        if not admin:
            print("❌ 管理员不存在")
            return False
        
        admin_crud.update(db, db_obj=admin, obj_in={"status": AdminStatus.ACTIVE})
        
        print(f"✅ 管理员 {username} 已激活")
        return True
        
    except Exception as e:
        logger.error(f"激活管理员失败: {str(e)}")
        print(f"❌ 激活失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def deactivate_admin(username):
    """停用管理员"""
    db = SessionLocal()
    try:
        admin = admin_crud.get_by_username(db, username=username)
        if not admin:
            print("❌ 管理员不存在")
            return False
        
        if admin.role == AdminRole.SUPER_ADMIN:
            # 检查是否还有其他超级管理员
            super_admins = admin_crud.get_super_admins(db)
            if len(super_admins) <= 1:
                print("❌ 不能停用最后一个超级管理员")
                return False
        
        admin_crud.update(db, db_obj=admin, obj_in={"status": AdminStatus.INACTIVE})
        
        print(f"✅ 管理员 {username} 已停用")
        return True
        
    except Exception as e:
        logger.error(f"停用管理员失败: {str(e)}")
        print(f"❌ 停用失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def system_status():
    """检查系统状态"""
    print("=" * 60)
    print("系统状态检查")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 检查数据库连接
        try:
            db.execute("SELECT 1")
            print("✅ 数据库连接正常")
        except Exception as e:
            print(f"❌ 数据库连接失败: {str(e)}")
            return
        
        # 检查管理员状态
        total_admins = admin_crud.count(db)
        super_admins = admin_crud.get_super_admins(db)
        active_admins = admin_crud.get_active_admins(db)
        
        print(f"📊 管理员统计:")
        print(f"   总数: {total_admins}")
        print(f"   超级管理员: {len(super_admins)}")
        print(f"   活跃管理员: {len(active_admins)}")
        
        # 安全检查
        issues = []
        if len(super_admins) == 0:
            issues.append("没有超级管理员")
        if len(active_admins) == 0:
            issues.append("没有活跃的管理员")
        
        if issues:
            print("\n⚠️  安全问题:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("\n✅ 系统状态正常")
        
        # 显示默认超级管理员配置
        print(f"\n🔧 默认超级管理员配置:")
        print(f"   用户名: {settings.DEFAULT_SUPER_ADMIN_USERNAME}")
        print(f"   密码: {settings.DEFAULT_SUPER_ADMIN_PASSWORD}")
        print(f"   邮箱: {settings.DEFAULT_SUPER_ADMIN_EMAIL}")
        
    except Exception as e:
        logger.error(f"系统状态检查失败: {str(e)}")
        print(f"❌ 系统状态检查失败: {str(e)}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description='管理员管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list 命令
    subparsers.add_parser('list', help='列出所有管理员')
    
    # create 命令
    create_parser = subparsers.add_parser('create', help='创建超级管理员')
    create_parser.add_argument('--username', help='用户名')
    create_parser.add_argument('--name', help='姓名')
    create_parser.add_argument('--email', help='邮箱')
    create_parser.add_argument('--phone', help='手机号')
    create_parser.add_argument('--password', help='密码')
    create_parser.add_argument('--force', action='store_true', help='强制创建')
    
    # reset 命令
    reset_parser = subparsers.add_parser('reset', help='重置管理员密码')
    reset_parser.add_argument('username', help='要重置密码的管理员用户名')
    reset_parser.add_argument('--password', help='新密码')
    
    # activate 命令
    activate_parser = subparsers.add_parser('activate', help='激活管理员')
    activate_parser.add_argument('username', help='要激活的管理员用户名')
    
    # deactivate 命令
    deactivate_parser = subparsers.add_parser('deactivate', help='停用管理员')
    deactivate_parser.add_argument('username', help='要停用的管理员用户名')
    
    # status 命令
    subparsers.add_parser('status', help='检查系统状态')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'list':
        list_admins()
    elif args.command == 'create':
        create_super_admin(
            username=args.username,
            name=args.name,
            email=args.email,
            phone=args.phone,
            password=args.password,
            force=args.force
        )
    elif args.command == 'reset':
        reset_admin_password(args.username, args.password)
    elif args.command == 'activate':
        activate_admin(args.username)
    elif args.command == 'deactivate':
        deactivate_admin(args.username)
    elif args.command == 'status':
        system_status()


if __name__ == "__main__":
    main() 