import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from starlette.responses import Response as StarletteResponse
import json

from app.config.logging import get_access_logger, get_security_logger, log_security_event
from app.config.settings import settings


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
    
    def __init__(self, app, skip_paths: list = None, debug_mode: bool = None):
        super().__init__(app)
        self.access_logger = get_access_logger()
        self.security_logger = get_security_logger()
        self.skip_paths = skip_paths or ["/health", "/metrics", "/favicon.ico", "/docs", "/redoc", "/openapi.json"]
        # 使用传入的debug_mode参数，如果没有传入则使用配置文件中的设置
        self.debug_mode = debug_mode if debug_mode is not None else settings.DEBUG_MODE
    
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
        }
        
        # 在调试模式下记录所有请求头
        if self.debug_mode:
            request_info["headers"] = dict(request.headers)
            self.access_logger.debug(f"[DEBUG] 完整请求头: {json.dumps(dict(request.headers), ensure_ascii=False)}")
        else:
            # 非调试模式下只记录关键头信息
            key_headers = {}
            for key in ["authorization", "content-type", "accept", "user-agent", "referer"]:
                if key in request.headers:
                    key_headers[key] = request.headers[key]
            request_info["headers"] = key_headers
        
        # 记录请求体
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    try:
                        body_json = json.loads(body.decode())
                        
                        # 在调试模式下记录完整的请求体
                        if self.debug_mode:
                            # 创建一个副本用于日志记录，移除敏感字段
                            debug_body = body_json.copy()
                            sensitive_fields = ["password", "token", "secret", "key", "api_key", "access_token", "refresh_token"]
                            self._mask_sensitive_fields(debug_body, sensitive_fields)
                            request_info["body"] = debug_body
                            self.access_logger.debug(f"[DEBUG] 完整请求体: {json.dumps(debug_body, ensure_ascii=False)}")
                        else:
                            # 非调试模式下简化处理
                            masked_body = body_json.copy()
                            sensitive_fields = ["password", "token", "secret", "key", "api_key", "access_token", "refresh_token"]
                            self._mask_sensitive_fields(masked_body, sensitive_fields)
                            request_info["body"] = "数据已记录"
                            
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        if self.debug_mode:
                            request_info["body"] = "非JSON数据"
                            self.access_logger.debug(f"[DEBUG] 非JSON请求体: {body[:500]}...")  # 只记录前500字符
                        else:
                            request_info["body"] = "非JSON数据"
            except Exception as e:
                if self.debug_mode:
                    self.access_logger.debug(f"[DEBUG] 读取请求体失败: {str(e)}")
        
        # 记录请求开始日志
        if self.debug_mode:
            self.access_logger.debug(f"[DEBUG] 请求开始: {json.dumps(request_info, ensure_ascii=False)}")
        
        self.access_logger.info(f"请求开始: {json.dumps(request_info, ensure_ascii=False)}")
        
        # 检测可疑活动
        self.detect_suspicious_activity(request, client_ip, user_agent)
        
        # 处理请求
        response_body = None
        try:
            response = await call_next(request)
            
            # 在调试模式下记录响应体
            if self.debug_mode and response.status_code < 400:
                try:
                    # 获取响应体内容
                    response_body = b""
                    async for chunk in response.body_iterator:
                        response_body += chunk
                    
                    # 重新创建响应对象
                    from starlette.responses import Response as StarletteResponse
                    response = StarletteResponse(
                        content=response_body,
                        status_code=response.status_code,
                        headers=response.headers,
                        media_type=response.media_type
                    )
                    
                    # 记录响应体（如果是JSON格式）
                    if response_body and response.headers.get("content-type", "").startswith("application/json"):
                        try:
                            response_json = json.loads(response_body.decode())
                            self.access_logger.debug(f"[DEBUG] 响应体: {json.dumps(response_json, ensure_ascii=False)}")
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            self.access_logger.debug(f"[DEBUG] 非JSON响应: {response_body[:500]}...")
                            
                except Exception as e:
                    self.access_logger.debug(f"[DEBUG] 读取响应体失败: {str(e)}")
                    
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
            
            if self.debug_mode:
                self.access_logger.debug(f"[DEBUG] 异常详情: {repr(e)}")
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
        
        # 在调试模式下记录响应头
        if self.debug_mode:
            response_info["response_headers"] = dict(response.headers)
            self.access_logger.debug(f"[DEBUG] 响应头: {json.dumps(dict(response.headers), ensure_ascii=False)}")
        
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
        
        # 在调试模式下记录额外的性能信息
        if self.debug_mode:
            self.access_logger.debug(f"[DEBUG] 性能统计: 请求处理时间: {process_time:.4f}秒, 状态码: {response.status_code}")
        
        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        
        return response
    
    def _mask_sensitive_fields(self, data, sensitive_fields):
        """递归地屏蔽敏感字段"""
        if isinstance(data, dict):
            for key, value in data.items():
                if any(field in key.lower() for field in sensitive_fields):
                    data[key] = "***已屏蔽***"
                elif isinstance(value, (dict, list)):
                    self._mask_sensitive_fields(value, sensitive_fields)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._mask_sensitive_fields(item, sensitive_fields)
    
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
