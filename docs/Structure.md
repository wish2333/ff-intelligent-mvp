# 系统架构

## 整体结构

```
ff-intelligent-neo/
├── main.py                 # 后端入口，Bridge API 定义
├── core/                   # 核心业务逻辑
│   ├── models.py           # 数据模型（Task, TaskState, TranscodeConfig 等）
│   ├── task_runner.py      # 任务执行、暂停/恢复/终止/重置
│   ├── command_builder.py  # FFmpeg 命令构建
│   ├── ffmpeg_setup.py     # FFmpeg 下载/检测/版本管理
│   └── logging.py          # 日志系统
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── bridge.ts       # PyWebVue Bridge 通信层
│   │   ├── components/
│   │   │   ├── common/     # 通用组件
│   │   │   │   └── FileDropInput.vue  # 文件拖拽输入组件
│   │   │   ├── layout/     # 布局组件
│   │   │   │   └── AppNavbar.vue      # 导航栏（含主题切换、FFmpeg 状态）
│   │   │   ├── config/     # 配置相关组件
│   │   │   │   └── FilterForm.vue     # 滤镜配置表单
│   │   │   ├── settings/   # 设置相关组件
│   │   │   │   └── FFmpegSetup.vue    # FFmpeg 管理面板
│   │   │   └── task-queue/ # 任务队列组件
│   │   │       ├── TaskList.vue       # 任务列表
│   │   │       ├── TaskRow.vue        # 单行任务
│   │   │       └── TaskProgressBar.vue # 进度条
│   │   ├── composables/   # Vue Composables
│   │   │   ├── useTaskControl.ts      # 任务控制 API
│   │   │   ├── useSettings.ts         # 设置管理
│   │   │   └── useTheme.ts            # 主题切换管理
│   │   ├── pages/         # 页面组件
│   │   │   ├── TaskQueuePage.vue
│   │   │   ├── CommandConfigPage.vue
│   │   │   └── SettingsPage.vue
│   │   ├── types/         # TypeScript 类型定义
│   │   └── style.css      # 全局样式（DaisyUI 主题配置）
│   └── index.html
├── docs/                   # 设计文档
│   ├── StateMachine.md     # 状态机定义
│   ├── BusinessRules.md    # 业务规则
│   ├── Structure.md        # 本文件
│   ├── Procedure.md        # 业务流程
│   └── fields/             # 数据模型字段定义
└── references/             # 参考文档
```

## 通用组件

### FileDropInput.vue

<!-- v2.1.0-CHANGE: 新增 FileDropInput 组件文档 -->

文件拖拽输入组件，支持拖拽放置和点击选择两种输入方式。

**路径**: `frontend/src/components/common/FileDropInput.vue`

**Props**:

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `modelValue` | `string` | `""` | 当前文件路径（v-model 绑定） |
| `accept` | `string` | `undefined` | 接受的文件扩展名，逗号分隔（如 `.png,.jpg`） |
| `placeholder` | `string` | `"Drop file here or click to select"` | 空状态占位文本 |

**Events**:

| 事件 | 参数 | 说明 |
|------|------|------|
| `update:modelValue` | `value: string` | 文件路径变化时触发 |

**行为**:
- 拖拽进入时显示高亮边框（`border-primary`）
- 使用 `dragCounter` 计数器处理子元素 drag 事件冒泡
- drop 后等待 80ms 调用 `get_dropped_files`（兼容 pywebvue 文件处理延迟）
- 点击时调用 `select_file_filtered` 后端 API 打开文件对话框
- 有值时显示文件名，悬停显示完整路径（`title` 属性）
- 右上角 X 按钮清空文件

**使用场景**:
- `FilterForm.vue` 中水印路径输入（accept: `.png,.jpg,.jpeg,.bmp,.webp`）

## Composables

### useTheme.ts

<!-- v2.1.0-CHANGE: 新增 useTheme composable 文档 -->

主题管理 composable，处理 light/dark/auto 主题切换。

**路径**: `frontend/src/composables/useTheme.ts`

**类型定义**:
```typescript
type ThemeValue = "auto" | "light" | "dark"
```

**返回值**:

| 属性/方法 | 类型 | 说明 |
|----------|------|------|
| `currentTheme` | `Ref<ThemeValue>` | 当前主题偏好设置 |
| `setTheme` | `(theme: ThemeValue) => Promise<void>` | 设置主题并持久化到 settings.json |
| `toggleTheme` | `() => void` | 在 light/dark 之间快速切换 |
| `resolveTheme` | `(preference: ThemeValue) => string` | 解析实际应用的主题（auto -> light/dark） |

**行为**:
- 通过 `document.documentElement.setAttribute("data-theme", resolved)` 设置 DaisyUI 主题
- auto 模式下监听 `window.matchMedia("(prefers-color-scheme: light)")` 的 change 事件
- 主题变更通过 `save_settings` API 持久化到后端

### useTaskControl.ts

<!-- v2.1.0-CHANGE: 更新 useTaskControl 文档，新增 resetTask -->

任务控制 composable，提供单任务和批量操作 API。

**路径**: `frontend/src/composables/useTaskControl.ts`

**方法列表**:

| 方法 | 参数 | 后端 API | 说明 |
|------|------|---------|------|
| `startTask` | `taskId, config?` | `start_task` | 开始执行任务 |
| `stopTask` | `taskId` | `stop_task` | 终止任务 |
| `pauseTask` | `taskId` | `pause_task` | 暂停任务 |
| `resumeTask` | `taskId` | `resume_task` | 恢复任务 |
| `retryTask` | `taskId, config?` | `retry_task` | 重试失败任务 |
| `resetTask` | `taskId` | `reset_task` | 重置终态任务为 pending |
| `stopAll` | - | `stop_all` | 终止所有任务 |
| `pauseAll` | - | `pause_all` | 暂停所有任务 |
| `resumeAll` | - | `resume_all` | 恢复所有任务 |

## Bridge API

### 事件系统

<!-- v2.1.0-CHANGE: 新增事件系统文档 -->

后端通过 `self._emit(event_name, data)` 向前端发送事件，前端通过 `onEvent(event_name, callback)` 监听。

#### ffmpeg_version_changed

<!-- v2.1.0-CHANGE: 新增版本切换事件 -->

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | `string` | FFmpeg 版本号 |
| `path` | `string` | FFmpeg 二进制路径 |
| `status` | `string` | 状态（`"ready"` 或 `"not_found"`） |

**触发时机**: `main.py` 中 `switch_ffmpeg` 方法调用成功后
**监听组件**: `AppNavbar.vue` — 更新导航栏 FFmpeg 状态徽标
