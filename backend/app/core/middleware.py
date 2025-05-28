import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from starlette.responses import Response as StarletteResponse
import json

from app.config.logging import get_access_logger, get_security_logger, log_security_event


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """
    处理时间中间件
    用于测量请求处理的时间，并将处理时间添加到响应头中
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 记录请求开始时间
        start_time = time.time()

        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time

        # 将处理时间添加到响应头中（毫秒为单位）
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # 可以在这里添加日志记录
        # 路径、方法、处理时间
        path = request.url.path
        method = request.method
        print(f"{method} {path} - 处理时间: {process_time:.4f}秒")

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志记录中间件"""
    
    def __init__(self, app, skip_paths: list = None):
        super().__init__(app)
        self.access_logger = get_access_logger()
        self.security_logger = get_security_logger()
        self.skip_paths = skip_paths or ["/health", "/metrics", "/favicon.ico", "/docs", "/redoc", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取客户端信息
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # 跳过不需要记录的路径
        if any(skip_path in str(request.url.path) for skip_path in self.skip_paths):
            response = await call_next(request)
            return response
        
        # 记录请求信息
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "headers": dict(request.headers),
        }
        
        # 记录请求体（仅对POST/PUT/PATCH请求，且排除敏感信息）
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # 尝试解析JSON
                    try:
                        body_json = json.loads(body.decode())
                        # 移除敏感字段
                        sensitive_fields = ["password", "token", "secret", "key"]
                        for field in sensitive_fields:
                            if field in body_json:
                                body_json[field] = "***"
                        request_info["body"] = body_json
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_info["body"] = "非JSON数据"
            except Exception:
                pass
        
        self.access_logger.info(f"请求开始: {json.dumps(request_info, ensure_ascii=False)}")
        
        # 检测可疑活动
        self.detect_suspicious_activity(request, client_ip, user_agent)
        
        # 处理请求
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            error_info = {
                "request_id": request_id,
                "error": str(e),
                "process_time": round(process_time, 4),
                "status": "error"
            }
            self.access_logger.error(f"请求异常: {json.dumps(error_info, ensure_ascii=False)}")
            raise
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        response_info = {
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "response_size": response.headers.get("content-length", "unknown")
        }
        
        # 根据状态码选择日志级别
        if response.status_code >= 500:
            self.access_logger.error(f"请求完成(服务器错误): {json.dumps(response_info, ensure_ascii=False)}")
        elif response.status_code >= 400:
            self.access_logger.warning(f"请求完成(客户端错误): {json.dumps(response_info, ensure_ascii=False)}")
        else:
            self.access_logger.info(f"请求完成: {json.dumps(response_info, ensure_ascii=False)}")
        
        # 记录慢请求
        if process_time > 2.0:  # 超过2秒的请求
            self.access_logger.warning(f"慢请求警告: {request.method} {request.url.path} - 耗时: {process_time:.4f}秒")
        
        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def detect_suspicious_activity(self, request: Request, client_ip: str, user_agent: str):
        """检测可疑活动"""
        
        # 检测SQL注入尝试
        sql_injection_patterns = ["'", "union", "select", "drop", "insert", "delete", "update", "--", "/*"]
        query_string = str(request.url.query).lower()
        path = request.url.path.lower()
        
        for pattern in sql_injection_patterns:
            if pattern in query_string or pattern in path:
                log_security_event(
                    "SQL注入尝试",
                    f"IP: {client_ip}, Path: {request.url.path}, Query: {request.url.query}",
                    None
                )
                break
        
        # 检测XSS尝试
        xss_patterns = ["<script", "javascript:", "onerror=", "onload=", "alert("]
        for pattern in xss_patterns:
            if pattern in query_string or pattern in path:
                log_security_event(
                    "XSS尝试",
                    f"IP: {client_ip}, Path: {request.url.path}",
                    None
                )
                break
        
        # 检测路径遍历尝试
        if "../" in path or "..%2f" in path or "..%5c" in path:
            log_security_event(
                "路径遍历尝试",
                f"IP: {client_ip}, Path: {request.url.path}",
                None
            )
        
        # 检测可疑User-Agent
        suspicious_agents = ["sqlmap", "nikto", "nmap", "masscan", "nessus"]
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            log_security_event(
                "可疑User-Agent",
                f"IP: {client_ip}, User-Agent: {user_agent}",
                None
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的速率限制中间件"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # 在生产环境中应该使用Redis
        self.security_logger = get_security_logger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self.get_client_ip(request)
        current_time = time.time()
        
        # 清理过期记录
        self.cleanup_expired_records(current_time)
        
        # 检查速率限制
        if client_ip in self.requests:
            request_times = self.requests[client_ip]
            # 计算窗口内的请求数
            recent_requests = [t for t in request_times if current_time - t < self.window_seconds]
            
            if len(recent_requests) >= self.max_requests:
                # 记录速率限制事件
                log_security_event(
                    "速率限制触发",
                    f"IP: {client_ip}, 请求数: {len(recent_requests)}, 限制: {self.max_requests}/{self.window_seconds}秒",
                    None
                )
                
                # 返回429状态码
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={"detail": "请求过于频繁，请稍后再试"}
                )
            
            # 更新请求记录
            recent_requests.append(current_time)
            self.requests[client_ip] = recent_requests
        else:
            self.requests[client_ip] = [current_time]
        
        return await call_next(request)
    
    def get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def cleanup_expired_records(self, current_time: float):
        """清理过期的请求记录"""
        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                t for t in self.requests[ip] 
                if current_time - t < self.window_seconds
            ]
            if not self.requests[ip]:
                del self.requests[ip]
