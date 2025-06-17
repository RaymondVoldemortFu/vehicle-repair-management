# 日志系统使用说明

## 概述

本项目实现了完整的日志系统，包括请求日志、安全日志、数据库操作日志、错误日志等多种类型的日志记录。

## 日志类型

### 1. 应用日志 (app.log)
- 记录应用程序的一般运行信息
- 包括启动、关闭、配置加载等事件

### 2. 访问日志 (access.log)
- 记录所有HTTP请求和响应
- 包括请求方法、URL、状态码、响应时间、用户信息等

### 3. 安全日志 (security.log)
- 记录安全相关事件
- 包括登录成功/失败、权限检查、可疑活动等

### 4. 错误日志 (error.log)
- 记录应用程序错误和异常
- 包括堆栈跟踪和错误详情

### 5. 数据库日志 (database.log)
- 记录数据库操作
- 包括CRUD操作、事务处理等

## 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

## 日志格式

### 控制台输出格式
```
[2024-01-01 12:00:00] [INFO] [app.api.auth] 用户登录成功 - 用户ID: 1, IP: 127.0.0.1
```

### 文件输出格式
```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "INFO",
  "logger": "app.api.auth",
  "message": "用户登录成功 - 用户ID: 1, IP: 127.0.0.1",
  "request_id": "req_123456",
  "user_id": 1,
  "ip": "127.0.0.1"
}
```

## 配置说明

### 环境变量
```bash
# 日志级别
LOG_LEVEL=INFO

# 日志文件路径
LOG_FILE=logs/app.log

# 日志轮转配置
LOG_ROTATION_SIZE=10MB
LOG_BACKUP_COUNT=5
LOG_RETENTION_DAYS=30
```

### 日志目录结构
```
logs/
├── app.log          # 主应用日志
├── access.log       # 访问日志
├── security.log     # 安全日志
├── error.log        # 错误日志
├── database.log     # 数据库日志
└── archived/        # 归档日志
```

## 使用方法

### 1. 在代码中使用日志

```python
from app.config.logging import get_api_logger, log_security_event, log_database_operation

# 获取日志器
logger = get_api_logger()

# 记录一般信息
logger.info("用户操作成功")

# 记录安全事件
log_security_event("登录成功", "用户登录", user_id=1)

# 记录数据库操作
log_database_operation("CREATE", "users", 1, "创建用户")
```

### 2. 使用装饰器

```python
from app.config.logging import log_api_call, log_function_call

@log_api_call
def api_endpoint():
    """API端点自动记录请求和响应"""
    pass

@log_function_call
def business_function():
    """业务函数自动记录调用"""
    pass
```

### 3. 中间件自动记录

系统已配置中间件自动记录：
- HTTP请求和响应
- 请求处理时间
- 用户信息
- 安全事件

## API接口

### 日志查看接口（仅管理员）

#### 获取日志文件列表
```http
GET /api/v1/logs/files
```

#### 获取日志内容
```http
GET /api/v1/logs/content/{filename}?lines=100&search=keyword
```

#### 获取特定类型日志
```http
GET /api/v1/logs/security?lines=100
GET /api/v1/logs/access?lines=100
GET /api/v1/logs/errors?lines=100
GET /api/v1/logs/database?lines=100
```

#### 获取日志统计
```http
GET /api/v1/logs/stats
```

#### 清理旧日志
```http
DELETE /api/v1/logs/clean?days=30
```

#### 下载日志文件
```http
GET /api/v1/logs/download/{filename}
```

## 日志轮转

系统自动进行日志轮转：
- 当日志文件达到指定大小时自动轮转
- 保留指定数量的备份文件
- 自动删除过期的日志文件

## 监控和告警

### 日志监控
- 监控错误日志数量
- 监控安全事件
- 监控系统性能指标

### 告警规则
- 错误率超过阈值时告警
- 安全事件异常时告警
- 系统资源不足时告警

## 性能优化

### 异步日志
- 使用异步写入提高性能
- 避免阻塞主线程

### 日志压缩
- 自动压缩归档日志
- 节省存储空间

### 缓冲机制
- 使用缓冲区减少磁盘I/O
- 定期刷新缓冲区

## 安全考虑

### 敏感信息过滤
- 自动过滤密码、令牌等敏感信息
- 对用户数据进行脱敏处理

### 访问控制
- 日志文件访问权限控制
- API接口权限验证

### 数据保护
- 日志文件加密存储
- 传输过程中的数据保护

## 故障排查

### 常见问题

1. **日志文件无法创建**
   - 检查目录权限
   - 检查磁盘空间

2. **日志级别不生效**
   - 检查环境变量配置
   - 重启应用程序

3. **日志文件过大**
   - 调整轮转配置
   - 清理旧日志文件

### 调试技巧

1. **临时调整日志级别**
```python
import logging
logging.getLogger('app').setLevel(logging.DEBUG)
```

2. **查看特定模块日志**
```bash
grep "app.api.auth" logs/app.log
```

3. **实时监控日志**
```bash
tail -f logs/app.log
```

## 最佳实践

1. **合理设置日志级别**
   - 生产环境使用INFO级别
   - 开发环境使用DEBUG级别

2. **避免过度日志记录**
   - 不要在循环中记录大量日志
   - 避免记录敏感信息

3. **定期清理日志**
   - 设置合理的保留期限
   - 定期归档重要日志

4. **监控日志质量**
   - 定期检查日志格式
   - 确保日志信息完整
