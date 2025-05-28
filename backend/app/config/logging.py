import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import sys

from app.config.settings import settings


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }

    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # 格式化消息
        formatted = super().format(record)
        return formatted


class RequestFilter(logging.Filter):
    """请求日志过滤器"""
    
    def filter(self, record):
        # 过滤掉健康检查等不重要的请求
        if hasattr(record, 'pathname'):
            if any(path in record.pathname for path in ['/health', '/metrics', '/favicon.ico']):
                return False
        return True


def setup_logging():
    """设置日志配置"""
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 日志配置字典
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "colored": {
                "()": ColoredFormatter,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "filters": {
            "request_filter": {
                "()": RequestFilter,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "colored",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": settings.LOG_FILE,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "default",
                "filename": "logs/access.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf8",
                "filters": ["request_filter"],
            },
            "security_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "WARNING",
                "formatter": "detailed",
                "filename": "logs/security.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf8",
            },
            "database_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/database.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            }
        },
        "loggers": {
            # 应用主日志器
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            # 访问日志器
            "app.access": {
                "level": "INFO",
                "handlers": ["access_file"],
                "propagate": False,
            },
            # 安全日志器
            "app.security": {
                "level": "WARNING",
                "handlers": ["security_file", "console"],
                "propagate": False,
            },
            # 数据库日志器
            "app.database": {
                "level": "INFO",
                "handlers": ["database_file"],
                "propagate": False,
            },
            # API日志器
            "app.api": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            # CRUD日志器
            "app.crud": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False,
            },
            # 第三方库日志器
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "access_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["access_file"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["database_file"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "INFO",
                "handlers": ["database_file"],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"],
        }
    }
    
    # 应用日志配置
    logging.config.dictConfig(logging_config)
    
    # 创建主应用日志器
    logger = logging.getLogger("app")
    logger.info(f"日志系统初始化完成 - 日志级别: {settings.LOG_LEVEL}")
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """获取日志器"""
    if name is None:
        return logging.getLogger("app")
    
    # 确保日志器名称以app开头
    if not name.startswith("app"):
        name = f"app.{name}"
    
    return logging.getLogger(name)


# 预定义的日志器
def get_api_logger() -> logging.Logger:
    """获取API日志器"""
    return logging.getLogger("app.api")


def get_security_logger() -> logging.Logger:
    """获取安全日志器"""
    return logging.getLogger("app.security")


def get_database_logger() -> logging.Logger:
    """获取数据库日志器"""
    return logging.getLogger("app.database")


def get_access_logger() -> logging.Logger:
    """获取访问日志器"""
    return logging.getLogger("app.access")


def get_crud_logger() -> logging.Logger:
    """获取CRUD日志器"""
    return logging.getLogger("app.crud")


# 日志装饰器
def log_function_call(logger: logging.Logger = None):
    """函数调用日志装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if logger is None:
                log = get_logger()
            else:
                log = logger
            
            log.debug(f"调用函数: {func.__name__} - 参数: args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                log.debug(f"函数 {func.__name__} 执行成功")
                return result
            except Exception as e:
                log.error(f"函数 {func.__name__} 执行失败: {str(e)}")
                raise
        return wrapper
    return decorator


def log_api_call(func):
    """API调用日志装饰器"""
    def wrapper(*args, **kwargs):
        api_logger = get_api_logger()
        api_logger.info(f"API调用: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            api_logger.info(f"API调用成功: {func.__name__}")
            return result
        except Exception as e:
            api_logger.error(f"API调用失败: {func.__name__} - 错误: {str(e)}")
            raise
    return wrapper


def log_security_event(event_type: str, details: str = None, user_id: int = None):
    """记录安全事件"""
    security_logger = get_security_logger()
    message = f"安全事件: {event_type}"
    if user_id:
        message += f" - 用户ID: {user_id}"
    if details:
        message += f" - 详情: {details}"
    security_logger.warning(message)


def log_database_operation(operation: str, table: str, record_id: int = None, details: str = None):
    """记录数据库操作"""
    db_logger = get_database_logger()
    message = f"数据库操作: {operation} - 表: {table}"
    if record_id:
        message += f" - 记录ID: {record_id}"
    if details:
        message += f" - 详情: {details}"
    db_logger.info(message) 