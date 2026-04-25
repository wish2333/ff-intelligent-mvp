# ff-intelligent-neo 2.1.1 - 产品需求文档

> 版本: 2.1.1
> 日期: 2026-04-25
> 状态: Draft
> 基于: PRD-2.1.0.md + Code Review Reports 2026-04-25

---

## 开发流程规范（重要）

> **本节为强制性规范，所有开发者必须遵守。**（继承自 PRD-2.1.0）

### 文档先行原则

2.1.1 版本的每个需求在进入开发阶段之前，**必须先更新 `docs/` 目录下的对应文档**。具体要求：

1. **定位关联文档**：每个需求明确关联需要修改的 `docs/` 文件
2. **标记变更行数**：在 `docs/` 文件中使用注释标记行号范围，格式为 `<!-- v2.1.1-CHANGE: 行N-行M -->`
3. **同步到 PRD**：将修改后的 `docs/` 内容段复制到本 PRD 的"文档变更追踪"附录中，以便开发时快速参照
4. **变更完成后开发**：文档变更经确认后，方可开始代码实现

### 文档与代码映射

| 需求类别 | 需关联的 docs 文件 | 说明 |
|---------|-------------------|------|
| 状态机/任务行为变更 | `docs/StateMachine.md` | 状态转移、按钮映射、终态处理 |
| 业务规则变更 | `docs/BusinessRules.md` | 验证规则、约束条件、异常处理 |
| 流程变更 | `docs/Procedure.md` | 操作流程、时序图 |
| 数据模型变更 | `docs/fields/*.csv` | 字段新增/修改/删除 |
| 架构变更 | `docs/Structure.md` | 模块关系、API 变更 |

---

## 0. 版本概述

### 0.1 版本背景

2.1.0 版本完成了大规模功能开发（多平台兼容性、命令构建器全功能、国际化、主题切换、队列布局优化等），但在开发过程中积累了多项性能瓶颈和用户体验缺陷。

2026-04-25 的全面代码审查发现：
- **前端**：39 个问题（12 HIGH / 18 MEDIUM / 12 LOW），涵盖命令预览延迟、静默错误吞没、类型安全等
- **后端**：8 个问题（2 HIGH / 3 MEDIUM / 3 LOW），涵盖 Bridge IPC 冗余调用、主线程阻塞、验证返回结构不完整等

### 0.2 版本目标

| 类别 | 目标 |
|------|------|
| 命令预览性能 | 消除竞态条件、合并 IPC 调用、优化 debounce 策略，将预览延迟从 ~350ms 降至 <150ms |
| UX 可靠性 | 消除静默错误吞没、为所有破坏性操作添加确认对话框、提供操作反馈 |
| 后端响应性 | 异步化阻塞操作、结构化验证返回、预览模式跳过文件系统检查 |
| 代码质量 | 消除 floating promises、强化类型安全、清理生产环境 console.log |

### 0.3 不兼容说明

2.1.1 向下兼容 2.1.0。不引入破坏性 API 变更。新增的 `preview_command` API 与现有 `build_command` + `validate_config` API 并存。

### 0.4 变更范围

> **不包含新功能**。本版本为纯优化和质量改进版本，不引入新的用户可见功能。

---

## 1. 命令预览性能优化

> 关联文档：`docs/Structure.md`（useCommandPreview composable）、`docs/Procedure.md`（命令预览流程）
> 参考文档：`references/Python Code Review Report-20260425.md` 第一、二节、`references/Frontend-Code-Review-Report-20260425.md` Part 1

### 1.1 合并 Bridge IPC 调用

**来源**: Python Review [HIGH] + Frontend Review [HIGH-3]

**现状问题**：
- 每次参数变化发两次独立 Bridge IPC 请求：`validate_config` + `build_command`
- 每次 IPC 包含完整的 JSON 序列化/反序列化 + `TaskConfig.from_dict()` 重建
- 两次调用产生 2 次进程间往返，增加 20-100ms 延迟

**需求**：

新增合并 API `preview_command`，一次 IPC 往返返回全部结果：

```python
# main.py 新增
@api.expose
def preview_command(config: dict) -> dict:
    """合并命令预览和参数校验，单次 IPC 返回全部结果。"""
    task_config = TaskConfig.from_dict(config)
    errors, warnings = validate_task_config(task_config)
    command = build_command_preview(task_config)
    return {"command": command, "errors": errors, "warnings": warnings}
```

**前端变更**：

```typescript
// useCommandPreview.ts - 替换 Promise.all 为单次调用
const res = await call<{command: string; errors: string[]; warnings: string[]}>(
  "preview_command", config
)
```

**兼容性**：保留现有 `build_command` 和 `validate_config` API 不删除，供其他场景使用。

---

### 1.2 消除请求竞态条件

**来源**: Frontend Review [HIGH-1]

**现状问题**：
- `useCommandPreview` 中无请求标识或取消机制
- 用户快速输入时多个异步请求并行，慢响应可能覆盖新结果导致命令文本闪烁

**需求**：

添加单调递增请求计数器，丢弃过期响应：

```typescript
// useCommandPreview.ts
let requestId = 0
async function updatePreview() {
  const myId = ++requestId
  const res = await call("preview_command", configRef.value)
  if (myId !== requestId) return // 丢弃过期响应
  // 应用结果...
}
```

---

### 1.3 优化 Watch 策略

**来源**: Frontend Review [HIGH-2] + Python Review [MEDIUM]

**现状问题**：
- `watch(configRef, ..., { deep: true })` 中 `deep: true` 冗余：`configRef` 是 computed，已自动追踪依赖
- 300ms debounce 对所有参数类型一视同仁，下拉选择等不连续操作无谓等待
- 无 in-flight 请求保护，可能堆积请求

**需求**：

1. **移除 `deep: true`**：`configRef` 是 computed 返回新对象，Vue 已追踪其依赖，deep 是冗余的
2. **增加 debounce 到 500ms**，并添加 in-flight 保护：

```typescript
let validating = false
let pendingUpdate = false

function scheduleUpdate() {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (validating) {
    pendingUpdate = true
    return
  }
  debounceTimer = setTimeout(updatePreview, 500)
}

async function updatePreview() {
  validating = true
  const myId = ++requestId
  try {
    const res = await call("preview_command", configRef.value)
    if (myId === requestId) {
      // 应用结果...
    }
  } finally {
    validating = false
    if (pendingUpdate) {
      pendingUpdate = false
      scheduleUpdate()
    }
  }
}
```

---

### 1.4 批量字段变更

**来源**: Frontend Review [HIGH-4]

**现状问题**：
- `video_codec` 切换为 `copy/none` 时逐字段清除 8 个质量参数
- 每次赋值触发一次 Vue 响应式通知，产生 8 次中间 computed 重算

**需求**：

使用 `Object.assign` 原子化批量赋值：

```typescript
// TranscodeForm.vue - video_codec 切换时的清空逻辑
if (["copy", "none"].includes(value)) {
  Object.assign(config, {
    video_bitrate: "",
    resolution: "",
    framerate: "",
    quality_mode: "",
    quality_value: 0,
    preset: "",
    pixel_format: "",
    max_bitrate: "",
    bufsize: "",
  })
}
```

**影响范围**：
- `TranscodeForm.vue`：video_codec 切换
- `FilterForm.vue`：aspect_convert 互斥清空
- `MergePanel.vue`：merge_mode 切换

---

### 1.5 configRef 模式感知优化

**来源**: Frontend Review [MEDIUM-2] + Python Review [MEDIUM]

**现状问题**：
- `useGlobalConfig.configRef` 包含所有子配置（transcode + filters + clip + merge + avsmix + custom）
- 在非 merge 页面修改 merge 设置也会触发预览重建
- 任何全局状态属性变化（即使与当前 tab 无关）都触发一次预览更新

**需求**：

确保 `configRef` 仅包含当前 `activeMode` 相关的子配置。当前 2.1.0 的 `toTaskConfig()` 已有模式判断，确认是否完全过滤，如有遗漏则补充。

---

### 1.6 MergeFileList dragover 节流

**来源**: Frontend Review [MEDIUM-5]

**现状问题**：
- 每次约 60Hz 的 `dragover` 事件都创建新数组拷贝并 emit
- 触发不必要的响应式更新

**需求**：
- 仅在 `dragend` 时 emit 最终位置
- `dragover` 期间仅做视觉排序（不修改响应式数据）

---

### 1.7 性能优化效果预估

| 优化项 | 延迟减少 | 复杂度 | 来源 |
|--------|---------|--------|------|
| 合并 2 次 IPC 为 1 次 | ~40-50% 每次更新 | 中 | HIGH-3 |
| 请求竞态检查 | 消除闪烁 | 低 | HIGH-1 |
| 移除 deep: true | ~5-10% CPU | 极低 | HIGH-2 |
| debounce 500ms + in-flight 保护 | 减少总调用次数 | 极低 | MEDIUM-1 |
| 批量字段赋值 | 减少中间重算 | 低 | HIGH-4 |
| 模式感知 configRef | 减少无关更新 | 低 | MEDIUM-2 |
| dragover 节流 | 减少 DOM 更新 | 低 | MEDIUM-5 |

---

## 2. UX 可靠性改进

> 关联文档：`docs/BusinessRules.md`（错误处理规则、确认对话框规则）
> 参考文档：`references/Frontend-Code-Review-Report-20260425.md` Part 2

### 2.1 消除静默错误吞没

**来源**: Frontend Review [HIGH-5]

**现状问题**：
以下 4+ 组件的 `catch {}` 块吞没错误，用户操作失败后无任何反馈：

| 组件 | 文件 | 操作 |
|------|------|------|
| ClipForm | `ClipForm.vue:111` | 获取文件时长 |
| TaskRow | `TaskRow.vue:58` | 重置/重试任务 |
| MergeFileList | `MergeFileList.vue:37` | 文件操作 |
| PresetSelector | `PresetSelector.vue:41` | 预设管理 |

**需求**：

为所有 Bridge 调用的 `catch` 块添加用户反馈：

```typescript
// 方案: 使用 DaisyUI alert 或 toast 通知
try {
  await call("some_api", params)
} catch (err) {
  // 显示错误提示
  alertMessage.value = t('common.operationFailed') + ': ' + (err as Error).message
  setTimeout(() => alertMessage.value = '', 3000)
}
```

**实现要点**：
- 在受影响的组件中添加 `alertMessage` ref
- 错误提示 3 秒后自动消失
- 国际化支持：使用 `t()` 包装错误消息

---

### 2.2 破坏性操作确认对话框

**来源**: Frontend Review [HIGH-6]

**现状问题**：
`removeSelected`、`clearAll`、`stopAll` 等破坏性操作无确认对话框，误触即执行。

| 组件 | 文件 | 操作 |
|------|------|------|
| TaskToolbar | `TaskToolbar.vue:37-57` | 移除选中任务 |
| BatchControlBar | `BatchControlBar.vue:47-53` | 清空队列 / 全部停止 |

**需求**：

为所有破坏性操作添加 DaisyUI modal 确认对话框（与 `FFmpegSetup.vue` 中已有的确认模式保持一致）：

```vue
<!-- 确认对话框模板 -->
<dialog ref="confirmDialog" class="modal">
  <div class="modal-box">
    <h3 class="font-bold text-lg">{{ confirmTitle }}</h3>
    <p class="py-4">{{ confirmMessage }}</p>
    <div class="modal-action">
      <button class="btn btn-ghost" @click="confirmDialog.close()">{{ t('common.cancel') }}</button>
      <button class="btn btn-error" @click="handleConfirm()">{{ confirmAction }}</button>
    </div>
  </div>
  <form method="dialog" class="modal-backdrop"><button>close</button></form>
</dialog>
```

**需确认的操作列表**：

| 操作 | 确认标题 | 确认消息 |
|------|---------|---------|
| 移除选中任务 | 移除任务 | 确认移除选中的 N 个任务？此操作不可撤销。 |
| 清空队列 | 清空队列 | 确认清空所有任务？此操作不可撤销。 |
| 全部停止 | 停止所有 | 确认停止所有运行中的任务？ |

---

### 2.3 替换原生 confirm() 为 DaisyUI Modal

**来源**: Frontend Review [HIGH-7]

**现状问题**：
`PresetSelector.vue:56` 使用浏览器原生 `confirm()` 对话框，与应用整体 DaisyUI 主题不一致，无法样式化。

**需求**：
替换为 DaisyUI modal 确认对话框（同 2.2 节模式）。

---

### 2.4 命令复制反馈

**来源**: Frontend Review [HIGH-8]

**现状问题**：
`CommandPreview.vue:20-27` 点击复制后无视觉反馈，且使用 `document.getElementById` 获取数据不够健壮。`navigator.clipboard` 在 PyWebView 中可能不可用。

**需求**：
- 点击复制后显示 "Copied!" 文本反馈（1.5 秒后消失）
- 使用 prop 传递命令文本替代 `document.getElementById`
- 添加 clipboard API 不可用时的 fallback（textarea + execCommand）

---

### 2.5 FFmpeg 下载超时修复

**来源**: Frontend Review [HIGH-9]

**现状问题**：
`FFmpegSetup.vue:49-55` 使用 `setTimeout(() => isDownloading.value = false, 5000)` 硬编码 5 秒超时。慢速网络下 spinner 提前消失。

**需求**：
- 后端 `download_ffmpeg` 完成后触发事件（如复用 `ffmpeg_version_changed`）
- 前端监听事件而非固定超时
- 添加下载失败事件处理

---

## 3. 后端响应性改进

> 关联文档：`docs/Procedure.md`（文件探测流程、硬件编码器检测流程）
> 参考文档：`references/Python Code Review Report-20260425.md` 第四节

### 3.1 add_tasks 中 probe_file 异步化

**来源**: Python Review [MEDIUM]

**现状问题**：
`main.py:241-257` 中 `probe_file` 对每个文件同步调用 ffprobe 子进程，批量添加文件时阻塞主线程：
- 10 个文件: ~0.5-2s 阻塞
- 50 个文件: ~2.5-10s 阻塞
- 无效文件 30s timeout: 更严重

**需求**：

将 probe 改为后台线程批量执行：

```python
import threading

def add_tasks(self, paths: list[str], config: dict = None) -> list[dict]:
    tasks = []
    # 创建占位任务（不含 probe 信息）
    for path in paths:
        task = Task(file_path=path, ...)
        tasks.append(task)
    # 后台线程批量 probe
    def _probe_bg():
        for task in tasks:
            try:
                info = probe_file(task.file_path) or {}
                task.file_name = info.get("file_name", ...)
                task.duration_seconds = info.get("duration", 0)
                task.file_size_bytes = info.get("file_size", 0)
                self._emit("task_info_updated", {...})
            except:
                pass
    threading.Thread(target=_probe_bg, daemon=True).start()
    return [t.to_dict() for t in tasks]
```

**前端适配**：
- 新增事件监听 `task_info_updated`，接收 probe 完成的文件信息
- 添加过程中显示 "Detecting..." 占位文本

---

### 3.2 validate_config 返回结构化数据

**来源**: Python Review [LOW]

**现状问题**：
`validate_config` 内部收集了 `param` 字段，但最终返回时仅保留 `message` 字符串：
```python
errors = [i["message"] for i in issues if i["level"] == "error"]
```

前端无法定位到具体的出错字段。

**需求**：

返回结构化列表：

```python
# 修改 validate_config 返回格式
return {
    "errors": [{"param": i["param"], "message": i["message"]} for i in issues if i["level"] == "error"],
    "warnings": [{"param": i["param"], "message": i["message"]} for i in issues if i["level"] == "warning"],
}
```

**前端利用**：
- `CommandPreview.vue` 接收 param 字段
- 可联动高亮对应表单字段（2.1.1 仅实现数据返回，字段高亮留待后续版本）

---

### 3.3 watermark 预览模式跳过文件系统检查

**来源**: Python Review [LOW]

**现状问题**：
`command_builder.py` watermark filter 的 validate 函数每次预览都执行 `Path(val).exists()`，用户输入路径过程中产生误导性 "file not found" 错误。

**需求**：

预览模式下跳过文件存在性检查。添加 `preview_mode` 参数：

```python
@api.expose
def preview_command(config: dict) -> dict:
    task_config = TaskConfig.from_dict(config)
    errors, warnings = validate_task_config(task_config, preview_mode=True)
    # ...
```

`validate_task_config` 在 `preview_mode=True` 时跳过 watermark 的 `Path(val).exists()` 检查。实际执行时（`task_runner.py` 调用）仍执行完整校验。

---

## 4. 代码质量与类型安全

> 关联文档：`docs/Structure.md`（composable 类型定义）
> 参考文档：`references/Frontend-Code-Review-Report-20260425.md` Part 3

### 4.1 Bridge 事件处理类型安全

**来源**: Frontend Review [HIGH-10]

**现状问题**：
`useTaskQueue.ts` 和 `useTaskProgress.ts` 中所有 Bridge 事件处理函数对 `unknown` 数据使用不安全的 `as` 强制转换，无运行时校验。

**需求**：

添加运行时类型守卫：

```typescript
// useTaskQueue.ts - 事件处理
function onTaskStateChanged(detail: unknown) {
  const payload = detail as Record<string, unknown>
  if (typeof payload.task_id !== 'string') return
  if (typeof payload.new_state !== 'string') return
  // 安全使用 payload
}
```

**影响文件**：
- `useTaskQueue.ts:105,114,123,157-161`
- `useTaskProgress.ts:25-32`

---

### 4.2 消除 `any` 类型

**来源**: Frontend Review [HIGH-11]

**现状问题**：
- `bridge.ts:29` 使用 `any` 作为返回类型
- `usePresets.ts:27,50,69` 使用 `any`

**需求**：
全部替换为 `unknown` + 类型收窄（type narrowing）。

---

### 4.3 修复 Floating Promises

**来源**: Frontend Review [HIGH-12]

**现状问题**：
以下位置异步函数被调用但未 `await` 或 `.catch()`：

| 文件 | 行号 | 调用 |
|------|------|------|
| `useTheme.ts` | 38 | `save_settings(...)` |
| `useLocale.ts` | 44 | `save_settings(...)` |
| `TaskQueuePage.vue` | 172-174 | 批量操作调用 |

**需求**：
为所有 async 调用添加 `.catch()` 或 `await`（静默操作使用 `.catch(() => {})` + 注释说明有意忽略）。

---

### 4.4 清理生产环境 console.log

**来源**: Frontend Review Part 4

**现状问题**：
以下文件包含 `console.log`，会输出用户文件路径和内部状态：

| 文件 | 行号 |
|------|------|
| `TaskQueuePage.vue` | 60, 62, 71, 74 |
| `useTaskQueue.ts` | 69, 72 |

**需求**：
- 移除所有生产环境 `console.log`
- 如需调试日志，使用 `import.meta.env.DEV` 守卫：`if (import.meta.env.DEV) console.log(...)`

---

### 4.5 MergeFileList key 修复

**来源**: Frontend Review [MEDIUM-3]

**现状问题**：
`MergeFileList.vue:149` 使用数组索引 `:key="index"` 作为拖拽项的 key。Vue 在列表重排时无法正确追踪元素。

**需求**：
为文件列表项生成唯一 ID（如使用自增计数器或文件路径 hash）作为 key。

---

### 4.6 i18n 硬编码字符串修复

**来源**: Frontend Review [MEDIUM-4, M-4, M-13]

**现状问题**：
以下位置存在未国际化的硬编码英文字符串：

| 组件 | 位置 | 硬编码文本 |
|------|------|-----------|
| `MergeFileList.vue` | 173, 183, 193 | `title` 属性 |
| `FFmpegSetup.vue` | 171 | "close" 按钮 |

**需求**：
替换为 `t()` 调用。新增对应 i18n key 到 `zh-CN.ts` 和 `en-US.ts`。

---

### 4.7 PresetSelector loading 状态

**来源**: Frontend Review [M-6]

**现状问题**：
`PresetSelector.vue` 定义了 `loading` ref 但模板中未使用，加载过程中无视觉反馈。

**需求**：
在模板中使用 `loading` 状态显示 spinner。

---

### 4.8 AppAbout 模块级 t() 调用修复

**来源**: Frontend Review [M-14]

**现状问题**：
`AppAbout.vue:12-17` 在模块顶层调用 `t()`，此时 i18n 实例可能尚未挂载，导致 locale 切换时不会更新。

**需求**：
将模块级 `t()` 调用移入组件内部（setup 函数或 computed）。

---

### 4.9 Props 直接修改修复

**来源**: Frontend Review [M-9]

**现状问题**：
`FilterForm.vue`、`TranscodeForm.vue`、`MergePanel.vue` 直接修改 props 对象的属性（Vue 单向数据流违反）。

**需求**：
确保所有表单修改通过 `emit('update:xxx', value)` 或直接操作 reactive 引用（非 props）。审查确认当前 `config` 是否为 reactive 引用而非 props。

---

## 5. 细节优化 (Polish)

> 参考文档：`references/Frontend-Code-Review-Report-20260425.md` LOW issues

### 5.1 无障碍访问 (Accessibility)

| 问题 | 文件 | 修复 |
|------|------|------|
| 图标按钮缺少 aria-label | `TaskLogPanel.vue:37`, `TaskRow.vue:123-142` | 添加 `aria-label` 属性，使用 `t()` 国际化 |
| TranscodeForm 空 div 用于网格对齐 | `TranscodeForm.vue:266,280,281` | 使用 CSS `grid-column` 或 `visibility: hidden` |

### 5.2 404 Catch-All 路由

**来源**: Frontend Review LOW

**现状问题**：Router 缺少 catch-all 路由，用户访问不存在的 URL 显示空白页。

**需求**：
```typescript
// router/index.ts
{
  path: '/:pathMatch(.*)*',
  redirect: '/',
}
```

### 5.3 ComboInput Escape 键

**来源**: Frontend Review LOW

**现状问题**：`ComboInput` 下拉菜单不响应 Escape 键关闭。

**需求**：监听 `@keydown.escape` 事件关闭下拉菜单。

### 5.4 FFmpeg Badge 闪烁修复

**来源**: Frontend Review [M-7]

**现状问题**：`AppNavbar.vue:26-37` 在 mount 时 FFmpeg 状态从红色闪烁到绿色。

**需求**：初始状态设为 `unknown`（灰色），仅在校验完成后设为 `ready`（绿色）或 `not_found`（红色）。

### 5.5 EncoderSelect 自定义输入保持

**来源**: Frontend Review [M-8]

**现状问题**：`EncoderSelect.vue:121-128` 自定义编码器输入框在输入过程中可能消失。

**需求**：确保输入框在聚焦状态下不会被条件渲染移除。

### 5.6 TaskQueue 空状态布局

**来源**: Frontend Review [M-11]

**现状问题**：`TaskList.vue:33-82` 空状态提示渲染在表格表头下方，视觉位置不佳。

**需求**：空状态提示应在表格区域居中显示，或使用 `v-if/v-else` 在无表格时独立渲染。

### 5.7 TranscodeForm 空占位 div

**来源**: Frontend Review [M-10]

**现状问题**：`TranscodeForm.vue:266,280,281` 使用空 `<div>` 进行 CSS Grid 对齐。

**需求**：使用 `grid-column` 属性或 `invisible` class 替代空 div。

---

## 6. 数据模型变更

### 6.1 Bridge API 新增

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `preview_command` | config: dict | `{command: str, errors: [{param, message}], warnings: [{param, message}]}` | 合并命令预览+校验，单次 IPC |

### 6.2 Bridge API 修改

| 方法 | 变更说明 |
|------|---------|
| `validate_config` | 返回格式变更：`errors/warnings` 从 `string[]` 改为 `[{param: str, message: str}]` |
| `add_tasks` | 改为异步 probe（后台线程），新增 `task_info_updated` 事件 |

### 6.3 Bridge API 新增事件

| 事件名 | 数据 | 触发时机 |
|--------|------|----------|
| `task_info_updated` | `{task_id, file_name, duration_seconds, file_size_bytes}` | probe 完成后逐个触发 |

### 6.4 docs/fields/ 变更

无新增字段。`validate_config` 返回格式变更不涉及持久化数据模型。

---

## 7. 实施阶段

### Phase 1: 命令预览性能优化（最高优先级）

| 编号 | 任务 | 关联文档 | 复杂度 |
|------|------|---------|--------|
| 1.1 | 新增 `preview_command` API（合并 build + validate） | `docs/Structure.md` | 中 |
| 1.2 | useCommandPreview 请求竞态保护（requestId） | `docs/Procedure.md` | 低 |
| 1.3 | 移除 deep: true + debounce 500ms + in-flight 保护 | `docs/Structure.md` | 低 |
| 1.4 | 批量字段赋值（TranscodeForm/FilterForm/MergePanel） | - | 低 |
| 1.5 | 确认 configRef 模式感知过滤完整 | `docs/Structure.md` | 低 |
| 1.6 | MergeFileList dragover 节流 | - | 低 |

### Phase 2: UX 可靠性

| 编号 | 任务 | 关联文档 | 复杂度 |
|------|------|---------|--------|
| 2.1 | 静默 catch 块添加用户反馈（4 组件） | `docs/BusinessRules.md` | 低 |
| 2.2 | 破坏性操作添加确认对话框 | `docs/BusinessRules.md` | 中 |
| 2.3 | PresetSelector 替换原生 confirm() | `docs/BusinessRules.md` | 低 |
| 2.4 | CommandPreview 复制反馈 + clipboard fallback | `docs/BusinessRules.md` | 低 |
| 2.5 | FFmpeg 下载超时改用事件驱动 | `docs/Procedure.md` | 中 |

### Phase 3: 后端响应性

| 编号 | 任务 | 关联文档 | 复杂度 |
|------|------|---------|--------|
| 3.1 | add_tasks probe_file 异步化 | `docs/Procedure.md` | 中 |
| 3.2 | validate_config 返回结构化 {param, message} | `docs/Structure.md` | 低 |
| 3.3 | watermark 预览模式跳过文件系统检查 | `docs/BusinessRules.md` | 低 |

### Phase 4: 代码质量

| 编号 | 任务 | 关联文档 | 复杂度 |
|------|------|---------|--------|
| 4.1 | Bridge 事件处理运行时类型守卫 | `docs/Structure.md` | 低 |
| 4.2 | 消除 `any` 类型 | `docs/Structure.md` | 低 |
| 4.3 | 修复 floating promises | - | 低 |
| 4.4 | 清理 console.log | - | 极低 |
| 4.5 | MergeFileList key 修复 | - | 低 |
| 4.6 | i18n 硬编码字符串修复 | `docs/fields/` | 低 |
| 4.7 | PresetSelector loading 状态 | - | 极低 |
| 4.8 | AppAbout 模块级 t() 修复 | - | 极低 |
| 4.9 | Props 直接修改审查 | `docs/Structure.md` | 低 |

### Phase 5: Polish

| 编号 | 任务 | 关联文档 | 复杂度 |
|------|------|---------|--------|
| 5.1 | aria-label on icon-only buttons | - | 极低 |
| 5.2 | 404 catch-all route | - | 极低 |
| 5.3 | ComboInput Escape key | - | 极低 |
| 5.4 | FFmpeg badge 初始状态修复 | `docs/Procedure.md` | 极低 |
| 5.5 | EncoderSelect 自定义输入保持 | - | 极低 |
| 5.6 | TaskQueue 空状态布局 | - | 极低 |
| 5.7 | TranscodeForm 空占位 div | - | 极低 |

---

## 附录 A: 文档变更追踪

> 开发时参照此附录，确认对应 docs 文件已更新后再开始编码。

### A.1 docs/Structure.md 变更

**状态**: 已完成 (2026-04-25)

**变更位置**: 文件末尾追加 `## v2.1.1: 性能优化与质量改进` 章节（约行 766 起）

**变更内容摘要**:

| 章节 | 内容 |
|------|------|
| useCommandPreview 优化 | 合并 IPC、竞态保护、移除 deep: true、debounce 500ms、in-flight 保护、批量字段赋值 |
| configRef 模式感知确认 | 审查确认 v2.1.0 已正确实现，无需修改 |
| MergeFileList 优化 | dragover 节流 + key 修复 |
| Bridge API 变更 | preview_command 新增、validate_config 返回格式修改、add_tasks 异步化、task_info_updated 事件 |
| Bridge 事件类型安全 | useTaskQueue/useTaskProgress 添加运行时类型守卫 |
| bridge.ts 类型安全 | call 返回类型 unknown 替代 any |
| 前端组件变更 | 列出所有受影响组件及其变更说明 |

**详细内容**: 参见 `docs/Structure.md` 末尾 `## v2.1.1: 性能优化与质量改进` 章节

---

### A.2 docs/BusinessRules.md 变更

**状态**: 已完成 (2026-04-25)

**变更位置**: 文件末尾追加 `## v2.1.1: UX 可靠性与错误处理规则` 章节（约行 424 起）

**变更内容摘要**:

| 规则 | 类型 | 内容 |
|------|------|------|
| 错误处理规则 | 新增 | 禁止静默吞没，DaisyUI alert 反馈，3 秒消失，国际化 |
| 破坏性操作确认规则 | 新增 | 3 项操作需 DaisyUI modal 确认，与 FFmpegSetup 风格一致 |
| 命令复制反馈规则 | 新增 | "Copied!" 反馈 1.5 秒，clipboard API + fallback |
| FFmpeg 下载超时规则 | 修改 | 固定 5 秒超时 -> 事件驱动 |
| 命令预览 debounce 规则 | 新增 | 500ms + in-flight 保护 + 竞态保护 |
| FFmpeg 状态徽标初始值规则 | 新增 | 初始 unknown（灰色），消除 mount 闪烁 |

**详细内容**: 参见 `docs/BusinessRules.md` 末尾 `## v2.1.1: UX 可靠性与错误处理规则` 章节

---

### A.3 docs/Procedure.md 变更

**状态**: 已完成 (2026-04-25)

**变更位置**:
1. 文件末尾追加 `## v2.1.1: 性能优化与改进流程` 章节（约行 676 起）
2. 修改 `## Download FFmpeg 流程` 章节，添加 v2.1.1 注释

**变更内容摘要**:

| 流程 | 类型 | 内容 |
|------|------|------|
| 命令预览流程 | 重写 | 合并 IPC + 竞态保护 + in-flight 保护，完整伪代码流程 + 延迟预估 |
| 文件探测异步流程 | 新增 | 后台线程 probe + task_info_updated 事件，对比 v2.1.0 同步阻塞 |
| FFmpeg 下载完成流程 | 修改 | Download FFmpeg 流程图和说明中标注 v2.1.1 事件驱动变更 |

**详细内容**: 参见 `docs/Procedure.md` 末尾 `## v2.1.1: 性能优化与改进流程` 章节

---

### A.4 docs/StateMachine.md 变更

**状态**: 无变更

2.1.1 不涉及状态机变更。

---

## 附录 B: 参考文档索引

| 文档 | 路径 | 用途 |
|------|------|------|
| PRD 2.1.0 | `references/PRD-2.1.0.md` | 基础功能设计参考 |
| Python Code Review | `references/Python Code Review Report-20260425.md` | 后端问题来源 |
| Frontend Code Review | `references/Frontend-Code-Review-Report-20260425.md` | 前端问题来源 |

---

## 附录 C: Issue 追踪矩阵

> 本矩阵确保所有 Code Review 发现的问题都被本 PRD 覆盖。

### Python Code Review Report 覆盖

| Review ID | 严重度 | PRD 章节 | 状态 |
|-----------|--------|---------|------|
| 两次 IPC 可合并 | HIGH | 1.1 | 覆盖 |
| 命令构建可前端化 | HIGH | 不含（长期目标，非 2.1.1 范围） | 记录 |
| 300ms debounce 一视同仁 | MEDIUM | 1.3 | 覆盖 |
| configRef 完整拷贝 | MEDIUM | 1.5 | 覆盖 |
| watch deep GC 压力 | LOW | 1.3 (移除 deep) | 覆盖 |
| probe_file 阻塞主线程 | MEDIUM | 3.1 | 覆盖 |
| check_hw_encoders 阻塞 | MEDIUM | 不含（一次性初始化，风险可接受） | 记录 |
| validate 缺 param 字段 | LOW | 3.2 | 覆盖 |
| watermark preview 检查文件 | LOW | 3.3 | 覆盖 |
| callable 类型注解 | LOW | 不含（内部模块，不影响功能） | 跳过 |

### Frontend Code Review Report 覆盖

| Review ID | 严重度 | PRD 章节 | 状态 |
|-----------|--------|---------|------|
| HIGH-1 Race condition | HIGH | 1.2 | 覆盖 |
| HIGH-2 deep:true 冗余 | HIGH | 1.3 | 覆盖 |
| HIGH-3 两次后端调用 | HIGH | 1.1 | 覆盖 |
| HIGH-4 逐字段赋值 | HIGH | 1.4 | 覆盖 |
| HIGH-5 静默错误 | HIGH | 2.1 | 覆盖 |
| HIGH-6 破坏性操作无确认 | HIGH | 2.2 | 覆盖 |
| HIGH-7 原生 confirm() | HIGH | 2.3 | 覆盖 |
| HIGH-8 复制无反馈 | HIGH | 2.4 | 覆盖 |
| HIGH-9 下载硬编码超时 | HIGH | 2.5 | 覆盖 |
| HIGH-10 unsafe as cast | HIGH | 4.1 | 覆盖 |
| HIGH-11 any 类型 | HIGH | 4.2 | 覆盖 |
| HIGH-12 floating promises | HIGH | 4.3 | 覆盖 |
| MEDIUM-1 debounce 太短 | MEDIUM | 1.3 | 覆盖 |
| MEDIUM-2 config 非模式感知 | MEDIUM | 1.5 | 覆盖 |
| MEDIUM-3 MergeFileList key | MEDIUM | 4.5 | 覆盖 |
| MEDIUM-4 硬编码 title | MEDIUM | 4.6 | 覆盖 |
| MEDIUM-5 dragover 频率 | MEDIUM | 1.6 | 覆盖 |
| M-6 loading 未使用 | MEDIUM | 4.7 | 覆盖 |
| M-7 badge 闪烁 | MEDIUM | 5.4 | 覆盖 |
| M-8 EncoderSelect 输入消失 | MEDIUM | 5.5 | 覆盖 |
| M-9 props 直接修改 | MEDIUM | 4.9 | 覆盖 |
| M-10 空 div 对齐 | MEDIUM | 5.7 | 覆盖 |
| M-11 空状态布局 | MEDIUM | 5.6 | 覆盖 |
| M-12 aria-label | MEDIUM | 5.1 | 覆盖 |
| M-13 硬编码 "close" | MEDIUM | 4.6 | 覆盖 |
| M-14 模块级 t() | MEDIUM | 4.8 | 覆盖 |
| LOW issues (8 items) | LOW | 5.x | 覆盖 |
| console.log | - | 4.4 | 覆盖 |
