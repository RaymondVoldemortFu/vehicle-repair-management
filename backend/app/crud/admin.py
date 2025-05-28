from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.crud.base import CRUDBase
from app.models.admin import Admin
from app.schemas.base import BaseSchema
from app.core.security import get_password_hash, verify_password


class AdminCreate(BaseSchema):
    username: str
    name: str
    password: str
    email: str
    phone: Optional[str] = None
    role: str


class AdminUpdate(BaseSchema):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


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
        return admin.status == "active"

    def update_password(self, db: Session, *, admin: Admin, new_password: str) -> Admin:
        """更新管理员密码"""
        admin.password_hash = get_password_hash(new_password)
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin


admin_crud = CRUDAdmin(Admin) 