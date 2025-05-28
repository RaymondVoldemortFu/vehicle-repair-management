from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.config.logging import get_crud_logger, log_database_operation, log_security_event


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self, model):
        super().__init__(model)
        self.logger = get_crud_logger()

    def get_by_phone(self, db: Session, *, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        self.logger.debug(f"查询用户 - 手机号: {phone}")
        user = db.query(User).filter(
            and_(User.phone == phone, User.is_deleted == False)
        ).first()
        
        if user:
            self.logger.info(f"用户查询成功 - 用户ID: {user.id}, 手机号: {phone}")
        else:
            self.logger.warning(f"用户查询失败 - 手机号不存在: {phone}")
        
        return user

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        self.logger.debug(f"查询用户 - 邮箱: {email}")
        user = db.query(User).filter(
            and_(User.email == email, User.is_deleted == False)
        ).first()
        
        if user:
            self.logger.info(f"用户查询成功 - 用户ID: {user.id}, 邮箱: {email}")
        else:
            self.logger.warning(f"用户查询失败 - 邮箱不存在: {email}")
        
        return user

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """创建用户"""
        self.logger.info(f"开始创建用户 - 手机号: {obj_in.phone}, 邮箱: {obj_in.email}")
        
        try:
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
            
            # 记录数据库操作
            log_database_operation("CREATE", "users", db_obj.id, f"创建用户: {obj_in.name}")
            self.logger.info(f"用户创建成功 - 用户ID: {db_obj.id}, 姓名: {obj_in.name}")
            
            return db_obj
        except Exception as e:
            self.logger.error(f"用户创建失败 - 手机号: {obj_in.phone}, 错误: {str(e)}")
            db.rollback()
            raise

    def authenticate(self, db: Session, *, phone: str, password: str) -> Optional[User]:
        """用户认证"""
        self.logger.info(f"用户认证尝试 - 手机号: {phone}")
        
        user = self.get_by_phone(db, phone=phone)
        if not user:
            self.logger.warning(f"认证失败 - 用户不存在: {phone}")
            log_security_event("登录失败", f"用户不存在 - 手机号: {phone}")
            return None
        
        if not verify_password(password, user.password_hash):
            self.logger.warning(f"认证失败 - 密码错误: {phone}")
            log_security_event("登录失败", f"密码错误 - 用户ID: {user.id}, 手机号: {phone}", user.id)
            return None
        
        self.logger.info(f"用户认证成功 - 用户ID: {user.id}, 手机号: {phone}")
        log_security_event("登录成功", f"用户登录 - 用户ID: {user.id}", user.id)
        return user

    def is_active(self, user: User) -> bool:
        """检查用户是否活跃"""
        is_active = user.status == "active"
        if not is_active:
            self.logger.warning(f"用户状态检查 - 用户ID: {user.id}, 状态: {user.status}")
        return is_active

    def update_password(self, db: Session, *, user: User, new_password: str) -> User:
        """更新用户密码"""
        self.logger.info(f"开始更新用户密码 - 用户ID: {user.id}")
        
        try:
            user.password_hash = get_password_hash(new_password)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # 记录安全事件
            log_security_event("密码修改", f"用户修改密码 - 用户ID: {user.id}", user.id)
            log_database_operation("UPDATE", "users", user.id, "更新密码")
            self.logger.info(f"用户密码更新成功 - 用户ID: {user.id}")
            
            return user
        except Exception as e:
            self.logger.error(f"用户密码更新失败 - 用户ID: {user.id}, 错误: {str(e)}")
            db.rollback()
            raise

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        """更新用户信息"""
        self.logger.info(f"开始更新用户信息 - 用户ID: {db_obj.id}")
        
        try:
            # 记录更新前的信息
            old_data = {
                "name": db_obj.name,
                "phone": db_obj.phone,
                "email": db_obj.email,
                "address": db_obj.address,
                "status": db_obj.status
            }
            
            # 执行更新
            updated_user = super().update(db, db_obj=db_obj, obj_in=obj_in)
            
            # 记录更新后的信息
            new_data = {
                "name": updated_user.name,
                "phone": updated_user.phone,
                "email": updated_user.email,
                "address": updated_user.address,
                "status": updated_user.status
            }
            
            # 找出变更的字段
            changes = []
            for key in old_data:
                if old_data[key] != new_data[key]:
                    changes.append(f"{key}: {old_data[key]} -> {new_data[key]}")
            
            if changes:
                change_details = ", ".join(changes)
                log_database_operation("UPDATE", "users", db_obj.id, f"更新用户信息: {change_details}")
                self.logger.info(f"用户信息更新成功 - 用户ID: {db_obj.id}, 变更: {change_details}")
            else:
                self.logger.info(f"用户信息无变更 - 用户ID: {db_obj.id}")
            
            return updated_user
        except Exception as e:
            self.logger.error(f"用户信息更新失败 - 用户ID: {db_obj.id}, 错误: {str(e)}")
            raise

    def remove(self, db: Session, *, id: int) -> User:
        """删除用户（软删除）"""
        self.logger.info(f"开始删除用户 - 用户ID: {id}")
        
        try:
            user = super().remove(db, id=id)
            log_database_operation("DELETE", "users", id, "软删除用户")
            self.logger.info(f"用户删除成功 - 用户ID: {id}")
            return user
        except Exception as e:
            self.logger.error(f"用户删除失败 - 用户ID: {id}, 错误: {str(e)}")
            raise

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100):
        """获取用户列表"""
        self.logger.debug(f"查询用户列表 - skip: {skip}, limit: {limit}")
        users = super().get_multi(db, skip=skip, limit=limit)
        self.logger.info(f"用户列表查询成功 - 返回 {len(users)} 条记录")
        return users

    def get(self, db: Session, id: int) -> Optional[User]:
        """根据ID获取用户"""
        self.logger.debug(f"查询用户 - 用户ID: {id}")
        user = super().get(db, id=id)
        
        if user:
            self.logger.debug(f"用户查询成功 - 用户ID: {id}")
        else:
            self.logger.warning(f"用户查询失败 - 用户ID不存在: {id}")
        
        return user


user_crud = CRUDUser(User) 