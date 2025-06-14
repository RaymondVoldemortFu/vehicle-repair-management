from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.crud.base import CRUDBase
from app.models.admin import Admin, AdminStatus, AdminRole
from app.schemas.admin import AdminCreate, AdminUpdate
from app.core.security import get_password_hash, verify_password
from app.config.logging import get_crud_logger

logger = get_crud_logger()


class CRUDAdmin(CRUDBase[Admin, AdminCreate, AdminUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[Admin]:
        """根据用户名获取管理员"""
        return db.query(Admin).filter(
            and_(Admin.username == username, Admin.is_deleted == False)
        ).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Admin]:
        """根据邮箱获取管理员"""
        return db.query(Admin).filter(
            and_(Admin.email == email, Admin.is_deleted == False)
        ).first()

    def create(self, db: Session, *, obj_in: AdminCreate) -> Admin:
        """创建管理员"""
        logger.info(f"开始创建管理员: {obj_in.username}, 角色: {obj_in.role}")
        
        # 默认权限配置
        default_permissions = {
            "user_management": False,
            "order_management": True,
            "worker_management": False,
            "material_management": False,
            "service_management": False,
            "analytics": False,
            "feedback_management": False,
            "wage_management": False
        }
        
        # 如果是超级管理员，给予所有权限
        if obj_in.role == AdminRole.SUPER_ADMIN:
            default_permissions = {
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
            logger.info(f"创建超级管理员，给予所有权限: {obj_in.username}")
        
        # 创建管理员对象
        db_obj = Admin(
            username=obj_in.username,
            name=obj_in.name,
            email=obj_in.email,
            phone=obj_in.phone,
            role=obj_in.role,
            password_hash=get_password_hash(obj_in.password),
            permissions=default_permissions,
            status=AdminStatus.ACTIVE
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        logger.info(f"管理员创建成功: ID={db_obj.id}, 用户名={obj_in.username}")
        return db_obj

    def create_super_admin(self, db: Session, *, obj_in: AdminCreate) -> Admin:
        """创建超级管理员（强制设置权限和角色）"""
        logger.info(f"开始创建超级管理员: {obj_in.username}")
        
        # 超级管理员权限配置
        super_admin_permissions = {
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
        
        db_obj = Admin(
            username=obj_in.username,
            name=obj_in.name,
            email=obj_in.email,
            phone=obj_in.phone,
            role=AdminRole.SUPER_ADMIN,  # 强制设置为超级管理员
            password_hash=get_password_hash(obj_in.password),
            permissions=super_admin_permissions,
            status=AdminStatus.ACTIVE
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        logger.info(f"超级管理员创建成功: ID={db_obj.id}, 用户名={obj_in.username}")
        return db_obj

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[Admin]:
        """管理员认证"""
        logger.debug(f"管理员认证尝试: {username}")
        
        admin = self.get_by_username(db, username=username)
        if not admin:
            logger.warning(f"管理员认证失败 - 用户名不存在: {username}")
            return None
        
        if not verify_password(password, admin.password_hash):
            logger.warning(f"管理员认证失败 - 密码错误: {username}")
            return None
        
        if admin.status != AdminStatus.ACTIVE:
            logger.warning(f"管理员认证失败 - 账号未激活: {username}, 状态: {admin.status}")
            return None
        
        logger.info(f"管理员认证成功: {username}")
        return admin

    def is_active(self, admin: Admin) -> bool:
        """检查管理员是否活跃"""
        return admin.status == AdminStatus.ACTIVE

    def is_super_admin(self, admin: Admin) -> bool:
        """检查是否为超级管理员"""
        return admin.role == AdminRole.SUPER_ADMIN

    def update_last_login(self, db: Session, *, admin: Admin) -> Admin:
        """更新最后登录时间"""
        from datetime import datetime
        admin.last_login = datetime.now()
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        logger.info(f"更新管理员最后登录时间: {admin.username}")
        return admin

    def update_password(self, db: Session, *, admin: Admin, new_password: str) -> Admin:
        """更新管理员密码"""
        admin.password_hash = get_password_hash(new_password)
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        logger.info(f"管理员密码更新成功: {admin.username}")
        return admin

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return verify_password(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return get_password_hash(password)

    def get_active_admins(self, db: Session) -> List[Admin]:
        """获取活跃管理员列表"""
        return db.query(Admin).filter(
            and_(Admin.status == AdminStatus.ACTIVE, Admin.is_deleted == False)
        ).all()

    def get_super_admins(self, db: Session) -> List[Admin]:
        """获取超级管理员列表"""
        return db.query(Admin).filter(
            and_(Admin.role == AdminRole.SUPER_ADMIN, Admin.is_deleted == False)
        ).all()

    def get_by_role(self, db: Session, *, role: AdminRole) -> List[Admin]:
        """根据角色获取管理员列表"""
        return db.query(Admin).filter(
            and_(Admin.role == role, Admin.is_deleted == False)
        ).all()

    def count_by_role(self, db: Session, *, role: AdminRole) -> int:
        """统计指定角色的管理员数量"""
        return db.query(Admin).filter(
            and_(Admin.role == role, Admin.is_deleted == False)
        ).count()

    def count_by_status(self, db: Session, *, status: AdminStatus) -> int:
        """统计指定状态的管理员数量"""
        return db.query(Admin).filter(
            and_(Admin.status == status, Admin.is_deleted == False)
        ).count()

    def has_permission(self, admin: Admin, permission: str) -> bool:
        """检查管理员是否有指定权限"""
        if admin.role == AdminRole.SUPER_ADMIN:
            return True  # 超级管理员拥有所有权限
        
        if not admin.permissions:
            return False
        
        return admin.permissions.get(permission, False)

    def grant_permission(self, db: Session, *, admin: Admin, permission: str) -> Admin:
        """授予管理员权限"""
        if not admin.permissions:
            admin.permissions = {}
        
        admin.permissions[permission] = True
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        logger.info(f"授予管理员权限: {admin.username} - {permission}")
        return admin

    def revoke_permission(self, db: Session, *, admin: Admin, permission: str) -> Admin:
        """撤销管理员权限"""
        if admin.role == AdminRole.SUPER_ADMIN:
            logger.warning(f"不能撤销超级管理员的权限: {admin.username}")
            return admin
        
        if admin.permissions:
            admin.permissions[permission] = False
            db.add(admin)
            db.commit()
            db.refresh(admin)
            
            logger.info(f"撤销管理员权限: {admin.username} - {permission}")
        
        return admin


admin_crud = CRUDAdmin(Admin) 