# 车辆维修管理系统 🚗

[![Python](https://img.shields.io/badge/Python-3.10.8-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)](https://vuejs.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个功能完整的车辆维修管理系统，采用前后端分离架构，支持用户端、管理员端和维修工人端三个子系统。

## 📋 项目概述

车辆维修管理系统是为汽车维修店、4S店等维修服务机构设计的数字化管理平台。系统通过现代化的Web技术栈，实现了从车辆档案管理、维修订单处理到库存管理、财务统计的全流程数字化管理。

### 🎯 核心特性

- **多角色管理**：支持普通用户、管理员、维修工人三种角色
- **订单流转**：完整的维修订单生命周期管理
- **智能调度**：自动分配空闲维修工人
- **库存管理**：材料库存实时跟踪和成本核算
- **财务统计**：工资计算、收入分析、数据报表
- **权限控制**：基于JWT的细粒度权限管理
- **数据分析**：ECharts可视化业务数据

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI (Python 3.10.8)
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy
- **认证**: JWT Token
- **文档**: Swagger/OpenAPI

### 前端
- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **构建工具**: Vite
- **图表**: ECharts
- **状态管理**: Pinia
- **路由**: Vue Router

## 🚀 快速开始

### 环境要求

- Python 3.10.8
- Node.js 16+
- MySQL 8.0+

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/vehicle-repair-management.git
   cd vehicle-repair-management
   ```

2. **后端设置**
   ```bash
   cd backend
   
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或 venv\Scripts\activate  # Windows
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 配置数据库
   cp .env.example .env
   # 编辑 .env 文件，填入数据库连接信息
   
   # 运行数据库迁移
   python run_migration.py
   
   # 填充初始数据（可选）
   python initial_data.py
   
   # 启动后端服务
   uvicorn app.main:app --reload
   ```

3. **前端设置**
   ```bash
   cd frontend
   
   # 安装依赖
   npm install
   
   # 启动开发服务器
   npm run dev
   ```

4. **访问系统**
   - 前端: http://localhost:3000
   - 后端API: http://localhost:8000
   - API文档: http://localhost:8000/docs

## 👥 默认账号

运行初始化脚本后，系统将创建以下测试账号：

### 管理员账号
- **超级管理员**: `superadmin` / `SuperAdminPassword123`
- **经理**: `manager_wang` / `ManagerPassword123`

### 普通用户账号
- **用户**: `zhangsan` / `Password123`
- **用户**: `lisi` / `Password123`
- **用户**: `wangwu` / `Password123`

### 维修工人账号
- **高级技师**: `W001` / `WorkerPassword123`
- **中级技师**: `W002` / `WorkerPassword123`
- **初级学徒**: `W003` / `WorkerPassword123`

## 📱 系统功能

### 用户端功能
- 用户注册/登录
- 车辆档案管理
- 维修订单创建
- 订单状态跟踪
- 服务评价反馈

### 管理员端功能
- 订单管理和调度
- 维修工人管理
- 材料库存管理
- 财务统计分析
- 用户权限管理
- 系统配置管理

### 维修工人端功能
- 工作任务查看
- 维修过程记录
- 材料使用登记
- 工资查询统计

## 📊 数据库设计

系统包含13个核心数据表：

- **用户管理**: users, admins, repair_workers
- **车辆管理**: vehicles
- **订单管理**: repair_orders, repair_order_workers, repair_order_services
- **库存管理**: materials, repair_materials
- **服务管理**: services
- **财务管理**: wages
- **反馈管理**: feedback

详细的数据库ER图请参考 `backend/designs/current_ER_diagram.md`

## 🔧 开发指南

### 项目结构
```
vehicle-repair-management/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── crud/           # 数据库操作
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   └── core/           # 核心配置
│   ├── initial_data.py     # 初始化数据脚本
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── api/            # API调用
│   │   └── router/         # 路由配置
│   └── package.json        # Node.js依赖
└── README.md
```

### API文档

启动后端服务后，可通过以下地址查看完整的API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 部署说明

详细的生产环境部署指南请参考 [项目部署与使用指南.md](项目部署与使用指南.md)

### Docker部署（推荐）

```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

## 🐛 常见问题

### 后端启动失败
- 检查Python版本是否为3.10.8
- 确认MySQL服务已启动
- 验证数据库连接配置

### 前端启动失败
- 清除node_modules重新安装
- 检查Node.js版本是否符合要求

### 数据库连接问题
- 确认MySQL服务状态
- 检查.env文件中的数据库配置
- 验证数据库用户权限

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！