from typing import Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import os
import json
from pathlib import Path

from app.api import deps
from app.schemas.user import User
from app.schemas.admin import Admin
from app.config.logging import get_api_logger
from app.config import settings

router = APIRouter()
logger = get_api_logger()

def get_log_files() -> List[str]:
    """获取所有日志文件列表"""
    log_dir = Path("logs")
    if not log_dir.exists():
        return []
    
    log_files = []
    for file in log_dir.glob("*.log"):
        log_files.append(file.name)
    
    return sorted(log_files, reverse=True)

def read_log_file(filename: str, lines: int = 100, search: Optional[str] = None) -> List[str]:
    """读取日志文件内容"""
    log_file = Path("logs") / filename
    if not log_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志文件不存在"
        )
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        # 如果有搜索关键词，过滤行
        if search:
            filtered_lines = [line for line in all_lines if search.lower() in line.lower()]
            return filtered_lines[-lines:] if len(filtered_lines) > lines else filtered_lines
        
        # 返回最后N行
        return all_lines[-lines:] if len(all_lines) > lines else all_lines
    
    except Exception as e:
        logger.error(f"读取日志文件失败: {filename}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="读取日志文件失败"
        )

@router.get("/files")
def get_log_file_list(
    current_admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    获取日志文件列表（仅管理员）
    """
    logger.info(f"管理员查看日志文件列表 - 管理员ID: {current_admin.id}")
    
    try:
        files = get_log_files()
        return {
            "files": files,
            "total": len(files)
        }
    except Exception as e:
        logger.error(f"获取日志文件列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志文件列表失败"
        )

@router.get("/content/{filename}")
def get_log_content(
    filename: str,
    lines: int = Query(100, ge=1, le=1000, description="读取行数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    获取日志文件内容（仅管理员）
    """
    logger.info(f"管理员查看日志内容 - 管理员ID: {current_admin.id}, 文件: {filename}")
    
    try:
        content = read_log_file(filename, lines, search)
        return {
            "filename": filename,
            "lines": len(content),
            "content": content,
            "search": search
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取日志内容失败: {filename}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志内容失败"
        )

@router.get("/security")
def get_security_logs(
    lines: int = Query(100, ge=1, le=1000, description="读取行数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    获取安全日志（仅管理员）
    """
    logger.info(f"管理员查看安全日志 - 管理员ID: {current_admin.id}")
    
    try:
        content = read_log_file("security.log", lines, search)
        return {
            "filename": "security.log",
            "lines": len(content),
            "content": content,
            "search": search
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取安全日志失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取安全日志失败"
        )

@router.get("/access")
def get_access_logs(
    lines: int = Query(100, ge=1, le=1000, description="读取行数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    获取访问日志（仅管理员）
    """
    logger.info(f"管理员查看访问日志 - 管理员ID: {current_admin.id}")
    
    try:
        content = read_log_file("access.log", lines, search)
        return {
            "filename": "access.log",
            "lines": len(content),
            "content": content,
            "search": search
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取访问日志失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取访问日志失败"
        )

@router.get("/errors")
def get_error_logs(
    lines: int = Query(100, ge=1, le=1000, description="读取行数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    获取错误日志（仅管理员）
    """
    logger.info(f"管理员查看错误日志 - 管理员ID: {current_admin.id}")
    
    try:
        content = read_log_file("error.log", lines, search)
        return {
            "filename": "error.log",
            "lines": len(content),
            "content": content,
            "search": search
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取错误日志失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取错误日志失败"
        )

@router.get("/database")
def get_database_logs(
    lines: int = Query(100, ge=1, le=1000, description="读取行数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    获取数据库日志（仅管理员）
    """
    logger.info(f"管理员查看数据库日志 - 管理员ID: {current_admin.id}")
    
    try:
        content = read_log_file("database.log", lines, search)
        return {
            "filename": "database.log",
            "lines": len(content),
            "content": content,
            "search": search
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取数据库日志失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取数据库日志失败"
        )

@router.get("/stats")
def get_log_statistics(
    current_admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    获取日志统计信息（仅管理员）
    """
    logger.info(f"管理员查看日志统计 - 管理员ID: {current_admin.id}")
    
    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            return {
                "total_files": 0,
                "total_size": 0,
                "files": []
            }
        
        files_info = []
        total_size = 0
        
        for file in log_dir.glob("*.log"):
            file_stat = file.stat()
            file_size = file_stat.st_size
            total_size += file_size
            
            files_info.append({
                "name": file.name,
                "size": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat()
            })
        
        return {
            "total_files": len(files_info),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files": sorted(files_info, key=lambda x: x["modified"], reverse=True)
        }
    
    except Exception as e:
        logger.error(f"获取日志统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志统计失败"
        )

@router.delete("/clean")
def clean_old_logs(
    days: int = Query(30, ge=1, le=365, description="保留天数"),
    current_admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    清理旧日志文件（仅管理员）
    """
    logger.info(f"管理员清理旧日志 - 管理员ID: {current_admin.id}, 保留天数: {days}")
    
    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            return {
                "message": "日志目录不存在",
                "deleted_files": 0
            }
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_files = []
        
        for file in log_dir.glob("*.log"):
            file_stat = file.stat()
            file_modified = datetime.fromtimestamp(file_stat.st_mtime)
            
            if file_modified < cutoff_date:
                try:
                    file.unlink()
                    deleted_files.append(file.name)
                    logger.info(f"删除旧日志文件: {file.name}")
                except Exception as e:
                    logger.error(f"删除日志文件失败: {file.name}, 错误: {str(e)}")
        
        return {
            "message": f"成功清理 {len(deleted_files)} 个旧日志文件",
            "deleted_files": deleted_files,
            "cutoff_date": cutoff_date.isoformat()
        }
    
    except Exception as e:
        logger.error(f"清理旧日志失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清理旧日志失败"
        )

@router.get("/download/{filename}")
def download_log_file(
    filename: str,
    current_admin: Admin = Depends(deps.get_current_admin)
) -> Any:
    """
    下载日志文件（仅管理员）
    """
    logger.info(f"管理员下载日志文件 - 管理员ID: {current_admin.id}, 文件: {filename}")
    
    log_file = Path("logs") / filename
    if not log_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志文件不存在"
        )
    
    from fastapi.responses import FileResponse
    
    return FileResponse(
        path=str(log_file),
        filename=filename,
        media_type='text/plain'
    ) 