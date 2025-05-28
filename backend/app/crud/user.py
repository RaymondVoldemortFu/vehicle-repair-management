from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_phone(self, db: Session, *, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return db.query(User).filter(
            and_(User.phone == phone, User.is_deleted == False)
        ).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(
            and_(User.email == email, User.is_deleted == False)
        ).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """创建用户"""
        db_obj = User(
            name=obj_in.name,
            phone=obj_in.phone,
            email=obj_in.email,
            address=obj_in.address,
            password_hash=get_password_hash(obj_in.password),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, phone: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.get_by_phone(db, phone=phone)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """检查用户是否活跃"""
        return user.status == "active"

    def update_password(self, db: Session, *, user: User, new_password: str) -> User:
        """更新用户密码"""
        user.password_hash = get_password_hash(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_crud = CRUDUser(User) 