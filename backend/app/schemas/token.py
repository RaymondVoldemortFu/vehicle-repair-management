from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from app.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
    """登录请求基础模型"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.strip():
            raise ValueError('用户名不能为空')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        return v


class UserLoginRequest(LoginRequest):
    """用户登录请求"""
    pass


class AdminLoginRequest(LoginRequest):
    """管理员登录请求"""
    pass


class WorkerLoginRequest(BaseSchema):
    """维修工人登录请求"""
    username: str = Field(..., min_length=1, max_length=20, description="工号", alias="employee_id")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    
    @validator('username')
    def validate_employee_id(cls, v):
        if not v.strip():
            raise ValueError('工号不能为空')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        return v


class Token(BaseSchema):
    """访问令牌响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user_info: Optional[Dict[str, Any]] = Field(None, description="用户信息")
    admin_info: Optional[Dict[str, Any]] = Field(None, description="管理员信息")
    worker_info: Optional[Dict[str, Any]] = Field(None, description="工人信息")


class TokenData(BaseSchema):
    """令牌数据"""
    user_id: Optional[int] = Field(None, description="用户ID")
    user_type: Optional[str] = Field(default="user", description="用户类型")


class TokenPayload(BaseSchema):
    """JWT 载荷"""
    sub: Optional[int] = Field(None, description="主题（用户ID）")
    exp: Optional[int] = Field(None, description="过期时间")
    user_type: Optional[str] = Field(default="user", description="用户类型")