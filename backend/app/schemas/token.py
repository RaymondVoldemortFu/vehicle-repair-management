from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.schemas.base import BaseSchema


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