# Frontend Documentation

Web 界面，用于与后端 API 交互进行工业异常检测。

## 目录结构

```
web/
├── index.html              # 仪表板主页
├── detection.html          # 检测任务创建表单页
├── assets/
│   ├── css/
│   │   ├── style.css              # 全局样式（导航栏、按钮、表单等）
│   │   ├── dashboard.css          # 仪表板特定样式
│   │   └── detection-form.css     # 检测表单特定样式
│   └── js/
│       ├── api-client.js          # API 通信模块
│       ├── dashboard.js           # 仪表板交互逻辑
│       └── detection-form.js      # 检测表单处理逻辑
└── README.md              
```

## 功能特性

### 1. 仪表板（Dashboard）- `index.html`

**主要功能：**
- 🔄 **系统状态监控**：实时显示后端 API 的健康状态
- 📊 **快速统计**：显示近期任务数、检测到的异常数、成功率
- 📋 **任务历史**：展示最近 10 个检测任务的列表
- ⚡ **快速操作**：快速创建新任务、查看历史、下载报告
- ℹ️ **API 信息**：显示 API 端点和文档链接

**交互元素：**
- 点击"View Details"展开任务详情
- 点击"Delete"移除任务记录
- 自动刷新系统状态（每 30 秒）

### 2. 检测表单（Detection Form）- `detection.html`

**主要功能：**
- 📝 **任务配置**：
  - Task ID（自动生成）
  - Asset ID（资产标识）
  - Data Source（数据源选择）
  - Time Range（开始/结束时间）
  
- 📊 **数据输入**：
  - 支持逗号分隔的数值：`10.5, 20.3, 15.8`
  - 支持 JSON 数组格式：`[10.5, 20.3, 15.8]`
  
- 🎚️ **阈值调整**：
  - 交互式滑块（0.0 - 1.0）
  - 彩色梯度指示（绿色 = 敏感，红色 = 不敏感）

- ✅ **结果显示**：
  - 状态指示（成功/失败）
  - 检测到的异常列表及分数
  - 任务总结和元数据
  - 下载结果为 JSON

## API 交互

### 后端 API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/` | 获取应用信息 |
| POST | `/v1/detect` | 运行异常检测 |

### DetectionTask 请求格式

```json
{
  "task_id": "task-1704067200000-abc123",
  "asset_id": "PUMP-001",
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T11:00:00Z",
  "data_source": "manual",
  "data": [10.5, 20.3, 15.8, 100.2, 12.1],
  "parameters": {
    "threshold": 0.5
  }
}
```

### DetectionResult 响应格式

```json
{
  "task_id": "task-1704067200000-abc123",
  "status": "success",
  "anomalies": [
    {
      "description": "Unusually high value",
      "score": 0.92,
      "details": "Value 100.2 is significantly higher than baseline"
    }
  ],
  "summary": "Found 1 anomaly in the input data",
  "metadata": {
    "processed_points": 5,
    "processing_time_ms": 125
  }
}
```

## 数据持久化

前端使用浏览器的 **LocalStorage** 自动保存最近 10 个检测任务：

```javascript
// 自动保存
localStorage.setItem('recentDetections', JSON.stringify(detections));

// 自动加载（页面刷新时）
const stored = localStorage.getItem('recentDetections');
```

这意味着即使刷新页面，最近的检测历史也会保留。

## 开发和调试

### 启动前端服务器

**使用 Python 简单 HTTP 服务器：**
```bash
cd frontend
python -m http.server 8080
```

然后访问 `http://localhost:8080`

**使用 Node.js http-server：**
```bash
npm install -g http-server
cd frontend
http-server -p 8080
```

**使用 VS Code Live Server 扩展：**
- 右键点击 `index.html` → "Open with Live Server"

### 浏览器开发者工具

**查看日志：**
- 按 `F12` 打开开发者工具
- 点击 "Console" 标签查看 JavaScript 日志和错误

**检查网络请求：**
- 点击 "Network" 标签
- 执行操作查看 API 请求和响应

**调试 JavaScript：**
- 在代码中设置断点
- 单步执行代码
- 检查变量值

### 修改 API 基础 URL

编辑 `assets/js/api-client.js`：

```javascript
// 修改这一行
const apiClient = new APIClient('http://localhost:8000');

// 改为
const apiClient = new APIClient('http://your-api-server:port');
```

## CSS 定制

### 颜色主题

编辑 `assets/css/style.css` 的 `:root` 变量：

```css
:root {
    --color-primary: #2563eb;      /* 主色（蓝色） */
    --color-secondary: #64748b;    /* 次要色（灰色） */
    --color-success: #16a34a;      /* 成功色（绿色） */
    --color-danger: #dc2626;       /* 危险色（红色） */
    --color-warning: #f59e0b;      /* 警告色（橙色） */
    ...
}
```

### 响应式断点

- **移动设备**：< 768px
- **平板/桌面**：>= 768px

所有组件都自动响应这些断点。

## 已知限制和改进空间

### 当前限制

- ❌ 实时数据流不支持（仅支持批量数据）
- ❌ 图表/可视化（仅显示列表）
- ❌ 用户认证（无登录机制）
- ❌ 数据导出（仅支持 JSON，不支持 CSV/PDF）
- ❌ 暗色模式

### 计划改进

- ✅ 添加图表库（Chart.js）用于异常分析可视化
- ✅ 实现暗色主题切换
- ✅ 添加更多导出格式（CSV、PDF）
- ✅ 改进错误处理和用户反馈
- ✅ 添加搜索和过滤功能
- ✅ 支持任务编排和自动化

## 浏览器兼容性

| 浏览器 | 最小版本 | 状态 |
|--------|---------|------|
| Chrome | 90+ | ✅ 完全支持 |
| Firefox | 88+ | ✅ 完全支持 |
| Safari | 14+ | ✅ 完全支持 |
| Edge | 90+ | ✅ 完全支持 |
| IE 11 | - | ❌ 不支持 |

## 性能优化

### 已应用

- ✅ 最小化 HTTP 请求数
- ✅ CSS 变量减少代码重复
- ✅ 防抖和节流处理频繁事件
- ✅ LocalStorage 缓存最近结果

### 可能的优化

- 图片优化和 WebP 格式
- 代码分割和懒加载
- 启用 HTTP/2 服务器推送
- Service Worker 离线支持

## 故障排除

### 问题：无法连接到 API

**症状：** 仪表板显示"🔴 Offline"或检测任务失败

**解决方案：**
1. 确保后端服务器运行：`python main.py`（或相应的启动命令）
2. 检查 API 地址是否正确（默认 `http://localhost:8000`）
3. 检查浏览器控制台是否有 CORS 错误
4. 如果需要 CORS，在后端配置 CORSMiddleware

### 问题：表单提交失败

**症状：** 点击"Run Detection"没有反应或显示错误

**解决方案：**
1. 检查浏览器控制台的错误信息
2. 验证数据格式是否正确（逗号分隔或 JSON）
3. 确保所有必填字段都已填写
4. 检查开始时间是否早于结束时间

### 问题：样式显示不正确

**症状：** 页面布局混乱或颜色错误

**解决方案：**
1. 清除浏览器缓存（Ctrl+Shift+Delete）
2. 硬刷新页面（Ctrl+Shift+R 或 Cmd+Shift+R）
3. 检查 CSS 文件是否正确加载（Network 标签）

## 许可证

MMDL-Agent Frontend © 2024. All rights reserved.

## 相关文档

- [后端 API 文档](../README.md)
- [项目架构](../README.md#architecture)
- [异常检测算法](../README.md#detection-algorithm)
