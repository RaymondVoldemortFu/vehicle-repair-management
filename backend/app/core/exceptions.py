from typing import Union
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose import JWTError
import logging

from app.config.logging import get_logger, log_security_event

logger = get_logger()


class CustomHTTPException(HTTPException):
    """自定义HTTP异常"""
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class DatabaseException(Exception):
    """数据库异常"""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class AuthenticationException(Exception):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        self.message = message
        super().__init__(self.message)


class AuthorizationException(Exception):
    """授权异常"""
    def __init__(self, message: str = "权限不足"):
        self.message = message
        super().__init__(self.message)


class BusinessLogicException(Exception):
    """业务逻辑异常"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def setup_exception_handlers(app: FastAPI):
    """设置全局异常处理器"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP异常处理器"""
        client_ip = request.client.host
        logger.warning(
            f"HTTP异常 - 状态码: {exc.status_code}, 详情: {exc.detail}, "
            f"路径: {request.url.path}, IP: {client_ip}"
        )
        
        # 记录安全相关的异常
        if exc.status_code in [401, 403]:
            log_security_event(
                "HTTP异常",
                f"状态码: {exc.status_code}, 路径: {request.url.path}, IP: {client_ip}"
            )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求验证异常处理器"""
        client_ip = request.client.host
        logger.warning(
            f"请求验证失败 - 路径: {request.url.path}, IP: {client_ip}, "
            f"错误: {exc.errors()}"
        )
        
        # 格式化验证错误信息
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"{field}: {message}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "message": "请求参数验证失败",
                "details": errors,
                "status_code": 422,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """SQLAlchemy异常处理器"""
        client_ip = request.client.host
        logger.error(
            f"数据库异常 - 路径: {request.url.path}, IP: {client_ip}, "
            f"错误: {str(exc)}"
        )
        
        # 不向客户端暴露具体的数据库错误信息
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "数据库操作失败，请稍后重试",
                "status_code": 500,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """数据完整性异常处理器"""
        client_ip = request.client.host
        logger.error(
            f"数据完整性异常 - 路径: {request.url.path}, IP: {client_ip}, "
            f"错误: {str(exc)}"
        )
        
        # 根据具体的完整性错误提供友好的错误信息
        error_message = "数据操作失败"
        if "UNIQUE constraint failed" in str(exc) or "Duplicate entry" in str(exc):
            error_message = "数据已存在，请检查输入信息"
        elif "FOREIGN KEY constraint failed" in str(exc):
            error_message = "关联数据不存在或已被删除"
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": True,
                "message": error_message,
                "status_code": 400,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(JWTError)
    async def jwt_exception_handler(request: Request, exc: JWTError):
        """JWT异常处理器"""
        client_ip = request.client.host
        logger.warning(
            f"JWT异常 - 路径: {request.url.path}, IP: {client_ip}, "
            f"错误: {str(exc)}"
        )
        
        log_security_event(
            "JWT异常",
            f"路径: {request.url.path}, IP: {client_ip}, 错误: {str(exc)}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": True,
                "message": "令牌无效或已过期",
                "status_code": 401,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(AuthenticationException)
    async def authentication_exception_handler(request: Request, exc: AuthenticationException):
        """认证异常处理器"""
        client_ip = request.client.host
        logger.warning(
            f"认证异常 - 路径: {request.url.path}, IP: {client_ip}, "
            f"消息: {exc.message}"
        )
        
        log_security_event(
            "认证失败",
            f"路径: {request.url.path}, IP: {client_ip}, 消息: {exc.message}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": True,
                "message": exc.message,
                "status_code": 401,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(AuthorizationException)
    async def authorization_exception_handler(request: Request, exc: AuthorizationException):
        """授权异常处理器"""
        client_ip = request.client.host
        logger.warning(
            f"授权异常 - 路径: {request.url.path}, IP: {client_ip}, "
            f"消息: {exc.message}"
        )
        
        log_security_event(
            "授权失败",
            f"路径: {request.url.path}, IP: {client_ip}, 消息: {exc.message}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": True,
                "message": exc.message,
                "status_code": 403,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException):
        """数据库异常处理器"""
        client_ip = request.client.host
        logger.error(
            f"数据库异常 - 路径: {request.url.path}, IP: {client_ip}, "
            f"消息: {exc.message}, 原始错误: {exc.original_error}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": exc.message,
                "status_code": 500,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(BusinessLogicException)
    async def business_logic_exception_handler(request: Request, exc: BusinessLogicException):
        """业务逻辑异常处理器"""
        client_ip = request.client.host
        logger.warning(
            f"业务逻辑异常 - 路径: {request.url.path}, IP: {client_ip}, "
            f"消息: {exc.message}, 错误代码: {exc.error_code}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": True,
                "message": exc.message,
                "error_code": exc.error_code,
                "status_code": 400,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器"""
        client_ip = request.client.host
        logger.error(
            f"未处理的异常 - 路径: {request.url.path}, IP: {client_ip}, "
            f"异常类型: {type(exc).__name__}, 错误: {str(exc)}",
            exc_info=True
        )
        
        # 记录安全事件
        log_security_event(
            "系统异常",
            f"路径: {request.url.path}, IP: {client_ip}, 异常: {type(exc).__name__}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "服务器内部错误，请稍后重试",
                "status_code": 500,
                "path": str(request.url.path)
            }
        )
    
    logger.info("全局异常处理器设置完成")