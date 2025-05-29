# 车辆维修管理系统 - 前端

基于 Vue 3 + Element Plus 的现代化车辆维修管理系统前端应用。

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Vue Router 4** - 官方路由管理器
- **Pinia** - 现代状态管理库
- **Element Plus** - 基于Vue 3的组件库
- **Axios** - HTTP客户端
- **Vite** - 现代化构建工具
- **Sass** - CSS预处理器
- **ECharts** - 数据可视化图表库

## 功能特性

### 用户端功能
- ✅ 用户注册/登录
- ✅ 个人信息管理
- ✅ 车辆信息管理
- ✅ 维修订单创建与查看
- ✅ 订单状态跟踪
- ✅ 意见反馈

### 管理员端功能
- ✅ 数据概览仪表板
- ✅ 用户管理
- ✅ 车辆管理
- ✅ 维修订单管理
- ✅ 维修工人管理
- ✅ 服务项目管理
- ✅ 材料库存管理
- ✅ 工资管理
- ✅ 反馈审核
- ✅ 数据分析与报表
- ✅ 系统日志查看

### 维修工人端功能
- ✅ 工作台概览
- ✅ 分配的维修订单
- ✅ 工资查询
- ✅ 个人资料管理

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── components/         # 公共组件
│   ├── layouts/           # 布局组件
│   │   ├── UserLayout.vue     # 用户端布局
│   │   ├── AdminLayout.vue    # 管理员端布局
│   │   └── WorkerLayout.vue   # 维修工人端布局
│   ├── views/             # 页面组件
│   │   ├── user/              # 用户端页面
│   │   ├── admin/             # 管理员端页面
│   │   └── worker/            # 维修工人端页面
│   ├── stores/            # Pinia状态管理
│   ├── utils/             # 工具函数
│   ├── router/            # 路由配置
│   ├── styles/            # 全局样式
│   ├── App.vue           # 根组件
│   └── main.js           # 应用入口
├── package.json
├── vite.config.js
└── README.md
```

## 环境要求

- Node.js >= 16.0.0
- npm >= 7.0.0 或 yarn >= 1.22.0

## 安装与运行

### 1. 安装依赖

```bash
# 使用 npm
npm install

# 或使用 yarn
yarn install
```

### 2. 开发环境运行

```bash
# 使用 npm
npm run dev

# 或使用 yarn
yarn dev
```

应用将在 http://localhost:3000 启动

### 3. 生产环境构建

```bash
# 使用 npm
npm run build

# 或使用 yarn
yarn build
```

构建文件将生成在 `dist` 目录

### 4. 预览构建结果

```bash
# 使用 npm
npm run preview

# 或使用 yarn
yarn preview
```

## 环境配置

### macOS 系统

1. **安装 Node.js**
   ```bash
   # 使用 Homebrew
   brew install node
   
   # 或者从官网下载安装包
   # https://nodejs.org/
   ```

2. **验证安装**
   ```bash
   node --version
   npm --version
   ```

3. **运行项目**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Windows 系统

1. **安装 Node.js**
   - 访问 https://nodejs.org/
   - 下载 LTS 版本并安装
   - 安装过程中确保勾选 "Add to PATH"

2. **验证安装**
   ```cmd
   node --version
   npm --version
   ```

3. **运行项目**
   ```cmd
   cd frontend
   npm install
   npm run dev
   ```

## API 配置

项目默认通过代理连接后端API (localhost:8000)，配置在 `vite.config.js` 中：

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false
    }
  }
}
```

如需修改后端地址，请更新此配置。

## 业务流程使用指南

### 用户端流程

1. **注册登录**
   - 新用户访问 `/register` 进行注册
   - 已有用户访问 `/login` 选择"用户登录"

2. **车辆管理**
   - 登录后先在"我的车辆"页面添加车辆信息
   - 填写车牌号、车架号、车型等基本信息

3. **创建维修订单**
   - 在仪表板点击"新建订单"或访问"维修订单"页面
   - 选择要维修的车辆，描述故障情况
   - 设置优先级并提交订单

4. **订单跟踪**
   - 在"维修订单"页面查看所有订单状态
   - 订单状态：待处理 → 进行中 → 已完成

5. **意见反馈**
   - 在"意见反馈"页面提交建议或投诉
   - 查看历史反馈记录

### 管理员端流程

1. **登录系统**
   - 访问 `/login` 选择"管理员登录"
   - 使用管理员账号密码登录

2. **数据概览**
   - 仪表板显示系统整体运行状况
   - 查看用户、车辆、订单统计数据

3. **订单管理**
   - 查看所有维修订单
   - 分配维修工人
   - 更新订单状态
   - 管理订单优先级

4. **用户管理**
   - 查看所有注册用户
   - 管理用户状态（激活/禁用）
   - 查看用户详细信息

5. **资源管理**
   - 管理服务项目和价格
   - 维护材料库存
   - 监控库存预警

6. **工人管理**
   - 添加维修工人
   - 管理工人技能和等级
   - 查看工人工作量

7. **财务管理**
   - 工资发放管理
   - 收入统计分析
   - 财务报表生成

### 维修工人端流程

1. **登录系统**
   - 访问 `/login` 选择"维修工人登录"
   - 使用工号和密码登录

2. **查看工作台**
   - 查看分配给自己的维修任务
   - 查看工作进度统计

3. **处理订单**
   - 查看订单详情和要求
   - 更新工作进度
   - 记录维修过程

4. **工资查询**
   - 查看月度工资单
   - 查看工作时长统计
   - 下载工资明细

## 注意事项

1. **浏览器兼容性**
   - 推荐使用现代浏览器（Chrome、Firefox、Safari、Edge）
   - IE 不受支持

2. **移动端适配**
   - 项目已适配移动端，支持响应式布局
   - 在手机/平板上也能正常使用

3. **数据持久化**
   - 登录状态通过 localStorage 持久化
   - 刷新页面不会丢失登录状态

4. **权限控制**
   - 不同角色访问不同页面
   - 路由层面进行权限验证

## 开发指南

### 添加新页面

1. 在对应的 views 目录下创建 Vue 组件
2. 在 router/index.js 中添加路由配置
3. 在对应的 Layout 组件中添加菜单项

### 添加新的 API 调用

1. 在 utils/request.js 中查看请求拦截器配置
2. 直接使用 request 函数调用 API
3. 错误处理已统一在拦截器中处理

### 状态管理

项目使用 Pinia 进行状态管理，主要的 store：
- `authStore` - 用户认证状态
- 可根据需要添加其他业务状态

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :3000  # macOS/Linux
   netstat -ano | findstr :3000  # Windows
   
   # 修改端口
   # 在 vite.config.js 中修改 server.port
   ```

2. **依赖安装失败**
   ```bash
   # 清除缓存重新安装
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **构建失败**
   ```bash
   # 检查 Node.js 版本
   node --version
   
   # 确保版本 >= 16.0.0
   ```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 发起 Pull Request

## 许可证

MIT License 