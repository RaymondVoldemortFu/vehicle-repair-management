from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.crud.base import CRUDBase
from app.models.admin import Admin, AdminStatus, AdminRole
from app.schemas.admin import AdminCreate, AdminUpdate
from app.core.security import get_password_hash, verify_password


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
        db_obj = Admin(
            username=obj_in.username,
            name=obj_in.name,
            email=obj_in.email,
            phone=obj_in.phone,
            role=obj_in.role,
            password_hash=get_password_hash(obj_in.password),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[Admin]:
        """管理员认证"""
        admin = self.get_by_username(db, username=username)
        if not admin:
            return None
        if not verify_password(password, admin.password_hash):
            return None
        return admin

    def is_active(self, admin: Admin) -> bool:
        """检查管理员是否活跃"""
        return admin.status == AdminStatus.ACTIVE

    def update_password(self, db: Session, *, admin: Admin, new_password: str) -> Admin:
        """更新管理员密码"""
        admin.password_hash = get_password_hash(new_password)
        db.add(admin)
        db.commit()
        db.refresh(admin)
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


admin_crud = CRUDAdmin(Admin) 