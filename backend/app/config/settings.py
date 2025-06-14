from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import dotenv
import os


class Settings(BaseSettings):
    def __init__(self):
        # 加载环境变量
        dotenv.load_dotenv()
        super().__init__()

    # 应用基础配置
    PROJECT_NAME: str = "车辆维修管理系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 安全配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # 数据库配置
    DATABASE_URL: str = os.environ.get("DATABASE_URL")
    DATABASE_TEST_URL: str = os.environ.get("DATABASE_TEST_URL")

    # Redis配置（缓存和会话）
    REDIS_URL: str = os.environ.get("REDIS_URL")

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # 默认超级管理员配置
    DEFAULT_SUPER_ADMIN_USERNAME: str = os.getenv("DEFAULT_SUPER_ADMIN_USERNAME", "super_admin")
    DEFAULT_SUPER_ADMIN_PASSWORD: str = os.getenv("DEFAULT_SUPER_ADMIN_PASSWORD", "admin123456")
    DEFAULT_SUPER_ADMIN_NAME: str = os.getenv("DEFAULT_SUPER_ADMIN_NAME", "系统超级管理员")
    DEFAULT_SUPER_ADMIN_EMAIL: str = os.getenv("DEFAULT_SUPER_ADMIN_EMAIL", "admin@vehicle-repair.com")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
