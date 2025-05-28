from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseResponse, BaseSchema


class AdminBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    name: str = Field(..., min_length=1, max_length=100, description="管理员姓名")
    role: str = Field(..., description="角色")
    phone: Optional[str] = Field(None, min_length=11, max_length=20, description="手机号码")
    email: Optional[str] = Field(None, description="邮箱地址")


class AdminCreate(AdminBase):
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class AdminUpdate(BaseSchema):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="管理员姓名")
    role: Optional[str] = Field(None, description="角色")
    phone: Optional[str] = Field(None, min_length=11, max_length=20, description="手机号码")
    email: Optional[str] = Field(None, description="邮箱地址")
    status: Optional[str] = Field(None, description="状态")


class AdminResponse(BaseResponse):
    username: str
    name: str
    role: str
    phone: Optional[str]
    email: Optional[str]
    status: str


class AdminDetail(AdminResponse):
    """管理员详细信息"""
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    permissions: Optional[dict] = Field(None, description="权限配置")


class AdminPasswordUpdate(BaseSchema):
    """管理员密码更新"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class AdminLogin(BaseSchema):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class Admin(AdminResponse):
    """管理员完整信息"""
    pass


class PasswordChange(BaseSchema):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码") 