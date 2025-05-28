from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseResponse(BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseSchema):
    page: int = 1
    size: int = 20
    
    def get_offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseSchema, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int):
        pages = (total + size - 1) // size
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


class MessageResponse(BaseSchema):
    message: str
    success: bool = True


class ErrorResponse(BaseSchema):
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None 