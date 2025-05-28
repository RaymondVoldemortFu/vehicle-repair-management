from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.user import User
from app.models.admin import Admin
from app.models.repair_worker import RepairWorker

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def create_access_token(
            subject: Union[str, Any], expires_delta: timedelta = None
    ) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def authenticate_user(
            db: Session, phone: str, password: str, user_type: str = "user"
    ) -> Optional[Union[User, Admin, RepairWorker]]:
        """验证用户身份"""
        if user_type == "admin":
            user = db.query(Admin).filter(Admin.phone == phone).first()
        elif user_type == "worker":
            user = db.query(RepairWorker).filter(RepairWorker.phone == phone).first()
        else:
            user = db.query(User).filter(User.phone == phone).first()

        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def get_current_user_from_token(db: Session, token: str, user_type: str = "user"):
        """从token获取当前用户"""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
        except jwt.JWTError:
            return None

        if user_type == "admin":
            user = db.query(Admin).filter(Admin.id == user_id).first()
        elif user_type == "worker":
            user = db.query(RepairWorker).filter(RepairWorker.id == user_id).first()
        else:
            user = db.query(User).filter(User.id == user_id).first()

        return user