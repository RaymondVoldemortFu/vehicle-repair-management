from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseResponse, BaseSchema
from app.models.user import UserStatus


class UserBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100, description="用户姓名")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    phone: Optional[str] = Field(None, min_length=11, max_length=20, description="手机号码")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    address: Optional[str] = Field(None, max_length=500, description="联系地址")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="用户姓名")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    phone: Optional[str] = Field(None, min_length=11, max_length=20, description="手机号码")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    address: Optional[str] = Field(None, max_length=500, description="联系地址")
    status: Optional[UserStatus] = Field(None, description="用户状态")


class UserResponse(BaseResponse):
    name: str
    username: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    status: UserStatus


class UserLogin(BaseSchema):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserProfile(UserResponse):
    """用户个人资料，包含关联信息"""
    pass


class User(UserResponse):
    """用户完整信息，用于认证和授权"""
    pass


class PasswordChange(BaseSchema):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码") 