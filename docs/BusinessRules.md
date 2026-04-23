# 业务规则

## 日志生命周期规则

<!-- v2.1.0-CHANGE: 行5-行30 新增日志生命周期规则 -->

| 场景 | 行为 |
|------|------|
| FFmpeg 运行中（running） | 日志实时写入 `task.log_lines`，前端 Log 按钮可查看 |
| FFmpeg 报错退出（failed） | 日志保留不清除，Log 按钮持续可查看 |
| FFmpeg 正常完成（completed） | 日志保留，Log 按钮隐藏（前端不显示） |
| 用户取消（cancelled） | 日志保留，Log 按钮隐藏（前端不显示） |
| 用户 Reset（completed/cancelled） | 清空 log_lines、error、output_path、progress、时间戳 |
| 用户 Retry（failed） | 日志保留，不清除 |
| 手动删除任务 | 同步从内存队列中移除 |
| 重启恢复 | 任务从 APPDATA 恢复，日志截断为最近 100 行 |

### 日志容量

- 每个任务最多保留 100 行日志（`log_lines` 数组上限）
- 日志仅在内存中维护，不持久化到磁盘文件

## Download FFmpeg 二次确认规则

<!-- v2.1.0-CHANGE: 行35-行50 新增下载确认规则 -->

| 规则 | 说明 |
|------|------|
| 按钮可见性 | Download FFmpeg 按钮始终可见，不受 FFmpeg 当前状态影响 |
| 二次确认 | 点击后弹出 DaisyUI modal 对话框："This will download FFmpeg and overwrite the current version. Continue?" |
| 取消操作 | 点击 Cancel 或点击背景遮罩关闭对话框，不触发下载 |
| 确认操作 | 点击 Confirm 触发 `download` 事件给父组件处理 |
| 加载状态 | 下载中按钮显示 loading spinner，禁用点击，5 秒后自动恢复 |
| 检测中禁用 | FFmpeg 正在检测时（status=detecting），下载按钮禁用 |

## FFmpeg 版本切换事件规则

<!-- v2.1.0-CHANGE: 行55-行68 新增版本切换事件规则 -->

| 规则 | 说明 |
|------|------|
| 事件名称 | `ffmpeg_version_changed` |
| 触发时机 | `switch_ffmpeg` 后端方法调用成功时 |
| 事件数据 | `{ version: string, path: string, status: 'ready' }` |
| 前端监听 | `AppNavbar.vue` 通过 `onEvent` 监听此事件 |
| 更新内容 | 导航栏 FFmpeg 状态徽标实时更新版本号和状态 |

## Reset 行为规则

<!-- v2.1.0-CHANGE: 行73-行88 新增 Reset 业务规则 -->

| 规则 | 说明 |
|------|------|
| 适用状态 | 仅 `completed` 和 `cancelled` 状态可执行 Reset |
| 目标状态 | Reset 后任务变为 `pending` |
| 自动执行 | Reset 不自动开始任务，需用户手动点击 Start |
| 数据清理 | 清空：error, log_lines, output_path, progress, started_at, completed_at |
| 数据保留 | 保留：id, file_path, file_name, file_size_bytes, duration_seconds, config |
| 前端触发 | `useTaskControl.ts` 的 `resetTask(id)` 调用后端 `reset_task(id)` |

## 主题切换规则

<!-- v2.1.0-CHANGE: 行93-行108 新增主题规则 -->

| 规则 | 说明 |
|------|------|
| 支持主题 | `auto`（跟随系统）、`light`、`dark` |
| 实现方式 | 通过 `document.documentElement.setAttribute("data-theme", resolved)` 切换 |
| 持久化 | 保存到 `settings.json` 的 `theme` 字段 |
| 自动检测 | auto 模式下通过 `window.matchMedia("(prefers-color-scheme: light)")` 检测 |
| 实时监听 | auto 模式下监听 `matchMedia` change 事件，系统主题变化时自动更新 |
| UI 入口 | 导航栏右侧太阳/月亮图标按钮，`toggleTheme()` 在 light/dark 间切换 |

## 文件拖拽输入规则

<!-- v2.1.0-CHANGE: 行113-行130 新增 FileDropInput 规则 -->

| 规则 | 说明 |
|------|------|
| 组件 | `FileDropInput.vue`（`frontend/src/components/common/`） |
| 输入方式 | 拖拽文件到区域 或 点击打开文件选择器 |
| 文件类型验证 | 前端通过 `accept` prop（如 `.png,.jpg`）验证扩展名 |
| 拖拽延迟 | drop 后等待 80ms 再调用 `get_dropped_files`（兼容 pywebvue 事件冒泡） |
| 显示内容 | 有值时显示文件名（非完整路径），鼠标悬停显示完整路径 |
| 清除操作 | 右侧 X 按钮清空已选文件 |
| 错误提示 | 类型不匹配时在区域内显示红色错误文本 |
| 使用场景 | 水印路径（FilterForm.vue）、横竖屏背景图片（预留） |
