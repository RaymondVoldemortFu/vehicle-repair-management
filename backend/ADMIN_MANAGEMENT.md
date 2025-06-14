# 管理员管理指南

本文档描述如何管理车辆维修管理系统的管理员账号，包括超级管理员的创建、管理和系统初始化。

## 目录

- [概述](#概述)
- [系统启动时自动初始化](#系统启动时自动初始化)
- [管理员工具](#管理员工具)
- [API接口](#api接口)
- [权限说明](#权限说明)
- [安全建议](#安全建议)

## 概述

系统支持多级管理员体系：
- **超级管理员 (SUPER_ADMIN)**: 拥有所有权限
- **经理 (MANAGER)**: 高级管理权限
- **主管 (SUPERVISOR)**: 中级管理权限
- **职员 (CLERK)**: 基础操作权限

## 系统启动时自动初始化

### 默认超级管理员

系统在启动时会自动检查并创建默认超级管理员（如果不存在）：

**默认凭据：**
- 用户名: `super_admin`
- 密码: `admin123456`
- 邮箱: `admin@vehicle-repair.com`
- 姓名: `系统超级管理员`

### 环境变量配置

可以通过环境变量自定义默认超级管理员：

```bash
# .env 文件
DEFAULT_SUPER_ADMIN_USERNAME=your_admin
DEFAULT_SUPER_ADMIN_PASSWORD=your_password
DEFAULT_SUPER_ADMIN_NAME=管理员姓名
DEFAULT_SUPER_ADMIN_EMAIL=admin@yourcompany.com
```

## 管理员工具

### 1. 管理员管理工具 (admin_manager.py)

强大的命令行管理工具，提供完整的管理员管理功能。

#### 安装依赖

```bash
cd backend
conda activate backenddev3108  # 切换到指定环境
```

#### 使用方法

```bash
# 查看所有命令
python admin_manager.py --help

# 列出所有管理员
python admin_manager.py list

# 创建超级管理员（交互式）
python admin_manager.py create

# 创建超级管理员（命令行参数）
python admin_manager.py create --username admin --name "管理员" --email admin@example.com --password password123

# 强制创建（即使已存在其他超级管理员）
python admin_manager.py create --force

# 重置密码
python admin_manager.py reset admin_username
python admin_manager.py reset admin_username --password newpassword

# 激活管理员
python admin_manager.py activate admin_username

# 停用管理员
python admin_manager.py deactivate admin_username

# 检查系统状态
python admin_manager.py status
```

### 2. 超级管理员创建工具 (create_super_admin.py)

专门用于创建超级管理员的简化工具。

```bash
# 交互式创建
python create_super_admin.py

# 命令行参数创建
python create_super_admin.py --username admin --name "管理员" --email admin@example.com --password password123 --force
```

## API接口

### 管理员登录

```http
POST /api/v1/auth/login/admin
Content-Type: application/json

{
    "username": "super_admin",
    "password": "admin123456"
}
```

### 超级管理员专用接口

以下接口需要超级管理员权限：

#### 1. 创建管理员

```http
POST /api/v1/admin/
Authorization: Bearer <token>
Content-Type: application/json

{
    "username": "new_admin",
    "name": "新管理员",
    "email": "new_admin@example.com",
    "role": "manager",
    "password": "password123"
}
```

#### 2. 管理员列表

```http
GET /api/v1/admin/?page=1&size=20
Authorization: Bearer <token>
```

#### 3. 重置密码

```http
PUT /api/v1/admin/{admin_id}/reset-password?new_password=newpassword
Authorization: Bearer <token>
```

#### 4. 更新权限

```http
PUT /api/v1/admin/{admin_id}/permissions
Authorization: Bearer <token>
Content-Type: application/json

{
    "user_management": true,
    "order_management": true,
    "analytics": false
}
```

#### 5. 更新角色

```http
PUT /api/v1/admin/{admin_id}/role
Authorization: Bearer <token>
Content-Type: application/json

{
    "new_role": "manager"
}
```

#### 6. 系统健康检查

```http
POST /api/v1/admin/system/check
Authorization: Bearer <token>
```

#### 7. 管理员活动记录

```http
GET /api/v1/admin/activity/recent?limit=10
Authorization: Bearer <token>
```

#### 8. 统计信息

```http
GET /api/v1/admin/statistics/overview
Authorization: Bearer <token>
```

## 权限说明

### 权限类型

| 权限名称 | 说明 |
|---------|------|
| `system_admin` | 系统管理权限（仅超级管理员） |
| `user_management` | 用户管理 |
| `order_management` | 订单管理 |
| `worker_management` | 工人管理 |
| `material_management` | 材料管理 |
| `service_management` | 服务管理 |
| `analytics` | 数据分析 |
| `feedback_management` | 反馈管理 |
| `wage_management` | 工资管理 |

### 角色默认权限

#### 超级管理员 (SUPER_ADMIN)
- 拥有所有权限
- 可以管理其他管理员
- 可以创建和删除管理员账号

#### 经理 (MANAGER)
- 大部分管理权限
- 不能管理其他管理员

#### 主管 (SUPERVISOR)
- 部分管理权限
- 主要负责日常运营

#### 职员 (CLERK)
- 基础操作权限
- 只能处理订单和客户服务

## 安全建议

### 1. 密码安全

- **立即更改默认密码**: 首次部署后立即更改默认超级管理员密码
- **使用强密码**: 密码应包含大小写字母、数字和特殊字符
- **定期更换密码**: 建议每3-6个月更换一次密码

### 2. 账号管理

- **最小权限原则**: 只给管理员必要的权限
- **定期审查**: 定期检查管理员账号和权限
- **及时停用**: 员工离职时立即停用对应账号

### 3. 环境配置

```bash
# 生产环境应设置强密码
DEFAULT_SUPER_ADMIN_PASSWORD=your_very_strong_password_here

# 使用公司邮箱
DEFAULT_SUPER_ADMIN_EMAIL=admin@yourcompany.com
```

### 4. 监控和日志

- 系统会记录所有管理员操作日志
- 定期检查安全日志：`logs/security.log`
- 异常登录会被记录并告警

### 5. 备份管理员

- 建议至少有2个超级管理员账号
- 超级管理员账号信息应妥善保管
- 建立管理员账号的应急恢复流程

## 故障排除

### 1. 忘记超级管理员密码

```bash
# 使用管理工具重置密码
python admin_manager.py reset super_admin

# 或者创建新的超级管理员
python admin_manager.py create --force
```

### 2. 没有超级管理员

```bash
# 检查系统状态
python admin_manager.py status

# 创建超级管理员
python admin_manager.py create
```

### 3. 数据库初始化失败

```bash
# 手动运行数据库初始化
cd backend
python -c "from app.db.init_db import init_database; init_database()"
```

### 4. 权限问题

如果管理员无法访问某些功能：

1. 检查管理员角色和权限
2. 使用超级管理员更新权限
3. 检查API token是否有效

## 开发环境设置

```bash
# 确保在正确的conda环境
conda activate backenddev3108

# 设置环境变量（开发环境）
export DATABASE_URL="mysql+pymysql://user:password@localhost/vehicle_repair"

# 运行数据库初始化
python -m app.db.init_db

# 启动应用
python -m app.main
```

## 联系支持

如果遇到问题或需要帮助，请：

1. 检查日志文件：`backend/logs/`
2. 运行系统状态检查：`python admin_manager.py status`
3. 查看本文档的故障排除部分
4. 联系系统管理员或开发团队 