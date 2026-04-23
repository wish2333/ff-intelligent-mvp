## 设想

### 多平台兼容性问题

- FFmpeg下载、路径检测和选择功能兼容性审查
- Phase3.5 挂起、恢复、退出、权限功能兼容性审查

### 功能问题

- 命令构建功能不完善
  - 根据\references\command_builder.md自检
    - 里面包含的编码器设置、滤镜设置、横竖屏转换、视频剪辑等
    - 里面包含的音频字幕处理、多视频处理，需要单独的包含文件列表+命令构建的界面实现UI
- 任务完成后，Action处仍然显示log，但是内容已经被清除了，优化意见如下：
  - 如果是运行中FFmpeg内报错，则不要清除log内容，显示log按钮，直到手动删除记录时才同步删除log内容
  - 如果是完成、取消等无报错的运行完成，显示重置状态按钮代替log按钮，点击后重置为pending状态可以重新执行
  - 任务运行中软件关闭，已有提示和Retry功能无需修改
- 打包后发现，进入设置界面和FFmpeg切换时会短暂地弹出两个终端，即FFmpeg检测并非静默运行

### 前端优化问题

- 水印路径为一个可拖拽输入文件区域，点击是用文件选择器选择，输入后显示文件路径/文件名
- FFmpeg版本切换之后，右上角的标识没有改变。
- Settings page, FFmpeg section: "Download FFmpeg" 按钮应该始终存在（即便检测到已有ffmepg），点击后需再次确认下载才通过StaticFFmpeg尝试再次下载
- Settings page, FFmpeg应该检测软件同目录下ffmpeg文件夹，并将这个视为自定义路径以外的最高优先级或如果同目录ffmpeg文件夹中有有效文件则将其设为默认自定义路径。
- 浅色/深色主题切换（DaisyUI自带）
- i18n多语言支持（如果没有原生支持，则优先中文界面；如果支持，优先实现中英双语）

针对这些问题开发dev-2.1.0版本，现在请你针对此问题进行references\PRD-2.1.0.md撰写，PRD中需要强调，后续开发先修改docs\中的文档并标记清楚行数（或copy到PRD中），以便后续依照标准化文件进行开发

## 需求文档

● PRD-2.1.0.md 已撰写完成。文档涵盖以下内容：

### 结构概览：

  1. 开发流程规范（强制）— 文档先行原则，每个需求必须先更新 docs/ 并标记行号
  2. 多平台兼容性 — FFmpeg 下载/检测/路径选择的跨平台方案，暂停/恢复的 macOS/Linux 实现
  3. 功能问题 — 命令构建器完善（编码器库/滤镜/横竖屏/剪辑/音频字幕/多视频拼接），任务完成按钮优化（Reset 替代空
    Log），FFmpeg 静默检测
  4. 前端优化 — 水印拖拽组件，版本指示器更新，Download 按钮始终可见，本地 ffmpeg/ 检测，主题切换，i18n
  5. 数据模型变更 — AppSettings/FilterConfig 新字段，新增 Encoder/Merge/Clip/AudioSubtitle 配置
  6. Bridge API 变更汇总 — 新增 reset_task/check_hw_encoders/ffmpeg_version_changed 事件
  7. 4 个实施阶段 — 从高优先级兼容性修复到国际化的渐进路线
  8. 附录 A: 文档变更追踪 — 每个 docs 文件需要做的具体变更说明
  9. 附录 B: 参考文档索引

### CC-Mem-文档编写过程

```
     Legend: session-request | 🔴 bugfix | 🟣 feature | 🔄 refactor | ✅ change | 🔵 discovery | ⚖️ decision

     Column Key
       Read: Tokens to read this observation (cost to learn it now)
       Work: Tokens spent on work that produced this record ( research, building, deciding)

     Context Index: This semantic index (titles, types, files, tokens) is usually sufficient to understand past work.

     When you need implementation details, rationale, or debugging context:
       - Fetch by ID: get_observations([IDs]) for observations visible in this index
       - Search history: Use the mem-search skill for past decisions, bugs, and deeper research
       - Trust this index over re-reading code for past decisions and learnings

     Context Economics
       Loading: 50 observations (20,164 tokens to read)
       Work investment: 27,228 tokens spent on research, building, and decisions
       Your savings: 26% reduction from reuse

     Apr 23, 2026

     #S1 Audio transcoding parameter consistency fix - user requested explanation of changes made to ensure passed
     parameters match command preview (Apr 23, 12:50 AM)

     #S2 ComboInput component enhanced with improved filtering behavior (Apr 23, 12:54 AM)

     main.py
       #1274  5:50 PM  🔵  Entry point implements lazy initialization pattern with loguru frontend sink
     pyproject.toml
       #1275           🔵  Project uses uv for Python package management with pywebview desktop framework
     frontend/src/composables/useBridge.ts
       #1276  5:51 PM  🔵  Frontend uses Vue 3 composables pattern with reactive state management
     references/dev-archived/PRD-2.0.0-1st.md
       #1277  5:52 PM  🔵  Extensive PRD-2.0.0 documentation reveals 5-phase implementation plan with complete
     architecture redesign
     General
       #1278  5:58 PM  🔵  Project identified as hybrid Python-Vue desktop application
       #1279           🔵  Documentation planning task initiated for ff-intelligent-neo project
     ..\..\Git\GithubManager\ff-intelligent-neo\pyproject.toml
       #1280  6:00 PM  ⚖️  Comprehensive documentation strategy defined for ff-intelligent-neo v2.0.0
     C:\Users\10411\.claude\plans\sleepy-strolling-allen.md
       #1281  6:08 PM  ✅  Documentation plan revised for field inventory format
       #1282  6:09 PM  ⚖️  Documentation plan approved for ff-intelligent-neo project
     General
       #1283  6:10 PM  🟣  Background task initiated for BusinessRules.md documentation
       #1284  6:11 PM  🟣  Parallel documentation tasks created for ff-intelligent-neo project
       #1285           ✅  Task dependency established: Project.md blocked by README.md
     ..\..\Git\GithubManager\ff-intelligent-neo\core\models.py
       #1286           ✅  Task dependency chain established for documentation deliverables
       #1287  6:12 PM  🔵  Core module architecture identified through source code analysis
       #1288           🔵  Smart outline tool failed to parse Python source files
     ..\..\Git\GithubManager\ff-intelligent-neo\main.py
       #1289           🔵  Smart outline tool confirmed incompatible with Python codebase
     ..\..\Git\GithubManager\ff-intelligent-neo\core\models.py
       #1290           🔵  Documentation effort shifted from automated to manual code analysis
     General
       #1291  6:13 PM  ✅  Documentation directory structure created
     ..\..\Git\GithubManager\ff-intelligent-neo\README.md
       #1292  6:14 PM  🟣  README.md completely rewritten with comprehensive English documentation
     General
       #1293           ✅  Task workflow progression: README.md completed, Project.md started
     ..\..\Git\GithubManager\ff-intelligent-neo\references\issues-2.1.0.md
       #1294  6:15 PM  🔵  Reference materials accessed for Project.md documentation
     ..\..\Git\GithubManager\ff-intelligent-neo\docs\Project.md
       #1295  6:16 PM  🟣  docs/Project.md created with comprehensive Chinese project overview
     General
       #1296           ✅  Task 4 (Structure.md) entered in_progress status
       #1297           ✅  Task 2 (Project.md) marked completed
     ..\..\Git\GithubManager\ff-intelligent-neo\docs\Structure.md
       #1298  6:18 PM  🟣  docs/Structure.md created with comprehensive system architecture documentation
     General
       #1299           ✅  Task 6 (Procedure.md) entered in_progress status
       #1300           ✅  Task 4 (Structure.md) marked completed
     ..\..\Git\GithubManager\ff-intelligent-neo\docs\Procedure.md
       #1301  6:19 PM  🟣  docs/Procedure.md created with comprehensive business process flow documentation
     General
       #1302  6:20 PM  ✅  Task 7 (CSV field inventory) entered in_progress status
       #1303           ✅  Task 6 (Procedure.md) marked completed
     ..\..\Git\GithubManager\ff-intelligent-neo\docs\fields\Task.csv
       #1304  6:21 PM  🟣  docs/fields/Task.csv created with Task model field documentation
     ..\..\Git\GithubManager\ff-intelligent-neo\docs\fields\TaskConfig.csv
       #1305           🟣  4 additional CSV field files created: TaskConfig, TranscodeConfig, FilterConfig, TaskProgress

     ..\..\Git\GithubManager\ff-intelligent-neo\docs\fields\Preset.csv
       #1306           🟣  Final 3 CSV field files created completing data model documentation
     General
       #1307           ✅  Task 5 (BusinessRules.md) entered in_progress status
       #1308  6:22 PM  ✅  Task 7 (CSV field inventory) completed; Task 8 (StateMachine.md) entered in_progress
     ..\..\Git\GithubManager\ff-intelligent-neo\docs\BusinessRules.md
       #1309  6:24 PM  🟣  docs/BusinessRules.md created with comprehensive business logic documentation
     ..\..\Git\GithubManager\ff-intelligent-neo\docs\StateMachine.md
       #1310           🟣  docs/StateMachine.md created with complete task lifecycle state machine documentation
     General
       #1311  6:25 PM  🟣  Documentation plan fully completed: All 7 tasks finished
       #1312           🔵  Documentation file inventory verified: 13 files in docs/ directory
     references/PRD-2.1.0.md
       #1313  6:44 PM  ✅  PRD-2.1.0 requirements documented
     ..\..\Git\GithubManager\ff-intelligent-neo\references\PRD-2.0.0-fin.md
       #1314           🔵  Reference documentation structure identified
     ..\..\Git\GithubManager\ff-intelligent-neo\references\command_builder.md
       #1315           🔵  Command builder specification reviewed
     ..\..\Git\GithubManager\ff-intelligent-neo\references\issues-2.1.0.md
       #1316           🔵  Issues list and prior PRD reviewed for context
     ..\..\Git\GithubManager\ff-intelligent-neo\references\PRD-2.1.0.md
       #1318           ✅  PRD-2.1.0.md created with comprehensive requirements
     ..\..\Git\GithubManager\ff-intelligent-neo\references\issues-2.1.0.md
       #1319  6:45 PM  🔵  Reference materials analyzed for PRD structure
     ..\..\Git\GithubManager\ff-intelligent-neo\references\PRD-2.0.0-fin.md
       #1320  6:47 PM  🔵  PRD-2.0.0 task control and configuration design analyzed
     ..\..\Git\GithubManager\ff-intelligent-neo\references\command_builder.md
       #1321           🔵  Command builder specification details analyzed
       #1322           🔵  Advanced filter operations and backend architecture analyzed
     ..\..\Git\GithubManager\ff-intelligent-neo\docs\StateMachine.md
       #1323           🔵  State machine and merge operations documentation reviewed
     ..\..\Git\GithubManager\ff-intelligent-neo\references\PRD-2.1.0.md
       #1324  6:49 PM  ✅  PRD-2.1.0.md created with comprehensive requirements
```

## Phase1

```
  Phase 1 (多平台兼容性与基础修复) 实现完成。修改了 6 个文件：

  变更清单

  ┌─────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────┐
  │          文件           │                                          变更                                          │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ core/process_control.py │ CREATE_NO_WINDOW for taskkill; os.killpg + os.getpgid for Unix kill/suspend/resume     │
  │                         │ targeting process groups; ProcessLookupError catch                                     │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ core/ffmpeg_runner.py   │ CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP on Windows Popen; start_new_session=True   │
  │                         │ on Unix Popen; CREATE_NO_WINDOW for ffprobe duration probe                             │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │                         │ New _find_local_ffmpeg_bin() for ./ffmpeg/ folder; updated priority chain (user ->     │
  │ core/ffmpeg_setup.py    │ bundled -> local -> platform -> PATH -> static); Linux paths in _find_platform_bin();  │
  │                         │ CREATE_NO_WINDOW for version detection; skip local check when frozen                   │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ core/task_runner.py     │ pause_task degradation fallback: kill + mark failed with progress preserved when OS    │
  │                         │ suspend fails; proper _cancel_events cleanup                                           │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ core/file_info.py       │ CREATE_NO_WINDOW for ffprobe probe; added sys import                                   │
  ├─────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ core/app_info.py        │ CREATE_NO_WINDOW for version detection subprocess calls                                │
  └─────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────┘

  手动测试项

  1. Windows: 确认运行 FFmpeg 任务时不再弹出终端窗口
  2. Windows: 确认设置页面 FFmpeg 版本切换不弹出终端
  3. Windows: 确认任务暂停/恢复正常工作
  4. Windows: 在应用同目录放置 ffmpeg/ffmpeg.exe，确认启动时自动检测
  5. macOS: 确认 SIGSTOP/SIGCONT 正常暂停/恢复
  6. Linux: 确认通过 apt/dnf/pacman 安装的 FFmpeg 可被检测
  7. Linux: 确认 os.killpg 正确终止整个进程组
  8. Linux: 测试权限不足时暂停降级（任务标记为 failed，进度保留）
```

### 新增需求

- build.py打包时不默认自带FFmpeg二进制文件，可通过--with-ffmpeg参数传入打包时带上

```
  - build.py default build no longer downloads/bundles FFmpeg
  - --with-ffmpeg flag triggers _pre_download_ffmpeg() which downloads binaries to ffmpeg_binaries/, and since both
  app.spec and the onefile spec generator already conditionally include binaries based on file existence (if
  _bin_path.exists()), the packaging logic needs no other changes
  - Users get FFmpeg either from their system, local ./ffmpeg/ folder (Task 1.2), or the runtime download button in
  Settings
```

### CC-Mem

```
     Legend: session-request | 🔴 bugfix | 🟣 feature | 🔄 refactor | ✅ change | 🔵 discovery | ⚖️ decision

     Column Key
       Read: Tokens to read this observation (cost to learn it now)
       Work: Tokens spent on work that produced this record ( research, building, deciding)

     Context Index: This semantic index (titles, types, files, tokens) is usually sufficient to understand past work.

     When you need implementation details, rationale, or debugging context:
       - Fetch by ID: get_observations([IDs]) for observations visible in this index
       - Search history: Use the mem-search skill for past decisions, bugs, and deeper research
       - Trust this index over re-reading code for past decisions and learnings

     Context Economics
       Loading: 50 observations (13,097 tokens to read)
       Work investment: 0 tokens spent on research, building, and decisions

     Apr 23, 2026

     #S1 Audio transcoding parameter consistency fix - user requested explanation of changes made to ensure passed
     parameters match command preview (Apr 23, 12:50 AM)

     #S2 ComboInput component enhanced with improved filtering behavior (Apr 23, 12:54 AM)

     General
       #1347  7:08 PM  🔵  Phase 1 target identified in FFmpeg runner subprocess call
       #1351  7:09 PM  🔵  Core module architecture comprises four specialized components
       #1352           🔵  Core module implementation spans 1,128 lines across four files
       #1353           🔵  Version detection subprocess also requires window suppression
       #1354           🔵  Three additional subprocess locations require window suppression fixes
       #1355           🔵  FFmpeg runner uses CREATE_NEW_PROCESS_GROUP for process isolation
       #1356           🔵  Task runner orchestrates FFmpeg execution with process tracking
       #1357  7:10 PM  🔵  Five subprocess.run locations identified requiring window suppression
       #1358           🔵  Main.py orchestrates all bridge APIs for FFmpeg management
       #1359           🔵  App_info.py subprocess.run lacks window suppression for version queries
       #1360           🔵  File_info.py subprocess.run lacks window suppression for media probing
       #1361           ⚖️  Phase 1 scope defined: Six subprocess locations require CREATE_NO_WINDOW fixes
       #1362  7:11 PM  ⚖️  Phase 1 development plan comprises four tasks for Windows compatibility and cross-platform
     improvements
     core/ffmpeg_runner.py
       #1363           🟣  FFmpeg runner subprocess now suppresses terminal windows on Windows
       #1364           🟣  FFprobe duration query now suppresses terminal windows on Windows
     General
       #1365           🔵  App_info.py module provides version detection for FFmpeg and FFprobe binaries
       #1366           🔵  File_info.py module extracts media metadata via ffprobe subprocess calls
     core/file_info.py
       #1367           🟣  File_info.py subprocess.run now suppresses terminal windows on Windows
     core/app_info.py
       #1368           🟣  App_info.py subprocess.run now suppresses terminal windows on Windows
     core/file_info.py
       #1369  7:12 PM  🟣  File_info.py subprocess.run now suppresses terminal windows on Windows
       #1370           🔴  File_info.py missing sys import added for platform check
     core/ffmpeg_setup.py
       #1371           🟣  FFmpeg_setup.py subprocess.run now suppresses terminal windows on Windows
     core/process_control.py
       #1372           🟣  Process_control.py subprocess.run now suppresses terminal windows on Windows
     core/ffmpeg_runner.py
       #1373           🟣  Task 1.1 completed: All subprocess calls now suppress terminal windows on Windows
     General
       #1374           🔵  Task 1.2 started: FFmpeg path detection cross-platform enhancement
     core/ffmpeg_setup.py
       #1375           ✅  FFmpeg_setup.py module docstring updated with new priority chain
       #1376  7:13 PM  🟣  FFmpeg_setup.py adds Linux common paths to platform binary detection
       #1377           🟣  FFmpeg_setup.py adds local ./ffmpeg/ folder detection
       #1378           🟣  FFmpeg_setup.py integrates local folder into priority chain
       #1379           🟣  FFmpeg_setup.py adds local folder to ffprobe fallback resolution
       #1380  7:14 PM  🟣  FFmpeg_setup.py adds local folder to version discovery
       #1381           🟣  Task 1.2 completed: FFmpeg path detection enhanced with cross-platform support
     core/process_control.py
       #1382           🟣  Process_control.py adds permission error handling for Unix pause/resume
     core/task_runner.py
       #1383           🟣  Task_runner.py implements permission degradation for Unix pause failures
     core/process_control.py
       #1384  7:15 PM  🟣  Task 1.3 completed: Permission degradation handling implemented for Unix pause/resume
     General
       #1385           ✅  Phase 1 task progression: Tasks 1.1, 1.2, and 1.3 completed; Task 1.4 started
     core/ffmpeg_runner.py
       #1386           🟣  FFmpeg_runner.py adds Unix process group isolation for tree termination
     core/process_control.py
       #1387           🟣  Process_control.py enhances Unix process tree termination with process group detection
     core/ffmpeg_runner.py
       #1388           🟣  Task 1.4 completed: Cross-platform process tree termination implemented
     General
       #1389  7:17 PM  🔵  Phase 1 development completed with four tasks finished
       #1390  7:18 PM  🔵  Phase 1 verification confirms all modified modules import successfully
       #1391           🟣  Phase 1 development completed and verified
       #1392  7:24 PM  🔵  Core module imports verified for Phase 1 development
     ..\..\Git\GithubManager\ff-intelligent-neo\core\app_info.py
       #1393  7:32 PM  🔄  Subprocess execution refactored for cross-platform compatibility
     ..\..\Git\GithubManager\ff-intelligent-neo\core\ffmpeg_setup.py
       #1394           🟣  Local FFmpeg folder support added to binary discovery
     ..\..\Git\GithubManager\ff-intelligent-neo\core\task_runner.py
       #1395           🔴  Task pause failure handling improved with graceful degradation
     ..\..\Git\GithubManager\ff-intelligent-neo\core\process_control.py
       #1398  7:41 PM  🔵  Cross-platform compatibility review completed
       #1399           🔴  Fixed Unix suspend/resume process group handling
     ..\..\Git\GithubManager\ff-intelligent-neo\core\task_runner.py
       #1400           🔴  Fixed pause_task degradation cleanup race condition
     ..\..\Git\GithubManager\ff-intelligent-neo\core\ffmpeg_setup.py
       #1401  7:42 PM  🔴  Added PyInstaller frozen environment guard
```

### 📝 Commit Message

```
feat(core): 多平台兼容性与基础修复完成

- 修复Windows下FFmpeg运行终端窗口弹出问题
- 增强Unix系统进程组管理，支持kill/suspend/resume操作
- 添加本地./ffmpeg/文件夹检测与优先级支持
- 实现权限不足时的降级处理逻辑
- 优化跨平台进程树终止机制
- 新增build.py--with-ffmpeg参数，可选打包FFmpeg二进制文件
```

### 🚀 Release Notes

```
## 2026-04-23 - 多平台兼容性大幅提升

### ✨ 新增
- 支持本地FFmpeg文件夹：可在应用同目录放置ffmpeg/文件夹自动检测
- 灵活打包选项：可通过--with-ffmpeg参数选择是否在打包时包含FFmpeg二进制文件
- 进程组管理：改进Unix系统下进程树控制和暂停/恢复功能

### 🐛 修复
- 终端窗口弹出：解决了Windows下运行FFmpeg任务时终端窗口意外弹出的问题
- 进程控制可靠性：修复了权限不足时任务暂停失败的问题，增加优雅降级机制
- 跨平台兼容：解决了各系统下进程终止不一致的问题，确保任务能够被正确清理
```

## Phase2

### Plan

```
 Phase 2: User Experience Optimization - Implementation Plan

 Context

 Phase 1 (multi-platform compatibility) is complete. Phase 2 focuses on UX improvements: task action buttons, drag-drop
  watermark input, FFmpeg version indicator updates, download button behavior, and theme switching. These are all
 frontend-heavy changes with minimal backend modifications.

 ---
 Task 2.1: Reset Button + Log Lifecycle

 Problem

 - completed/cancelled tasks show empty "Log" button (logs cleared)
 - failed task logs are also cleared too early
 - No way to re-run a completed/cancelled task

 Backend Changes

 core/models.py - Update VALID_TRANSITIONS (line 14-21):
 "completed": {"pending"},   # was set()
 "cancelled": {"pending"},   # was set()

 core/task_runner.py - Add reset_task method (after retry_task ~line 300):
 - Only for completed/cancelled states
 - Clear log_lines, output_path, error, progress, timestamps
 - Transition to pending via queue
 - Emit task_state_changed and queue_changed
 - Does NOT auto-start (unlike retry_task)

 core/task_runner.py - Modify retry_task (~line 281):
 - Keep log_lines intact (don't clear them on retry)

 core/task_queue.py - Modify save_state (~line 185):
 - For failed tasks: keep log_lines in persistence (already saved via to_dict)

 main.py - Add reset_task bridge method (after retry_task ~line 322):
 @expose
 def reset_task(self, task_id: str) -> dict:

 Frontend Changes

 frontend/src/composables/useTaskControl.ts - Add resetTask method:
 async function resetTask(taskId: string): Promise<boolean> {
   const res = await call<null>("reset_task", taskId)
   return res.success
 }

 frontend/src/components/task-queue/TaskRow.vue - Update action buttons (line 116-198):
 - completed/cancelled: Show "Reset" button instead of "Log" button
 - failed: Keep "Retry" + "Log" (logs preserved)
 - running/paused: Keep existing buttons + Log
 - pending: No Log button (unchanged)
 - Add reset emit

 frontend/src/pages/TaskQueuePage.vue - Wire up reset handler:
 - Pass control.resetTask to TaskList/TaskRow

 Files Modified

 - core/models.py (VALID_TRANSITIONS)
 - core/task_runner.py (new reset_task, modify retry_task)
 - core/task_queue.py (log persistence - verify existing)
 - main.py (new reset_task bridge)
 - frontend/src/composables/useTaskControl.ts (new resetTask)
 - frontend/src/components/task-queue/TaskRow.vue (Reset button)
 - frontend/src/pages/TaskQueuePage.vue (wire reset)
 - frontend/src/components/task-queue/TaskList.vue (pass reset event)

 ---
 Task 2.2: FileDropInput.vue Component

 Problem

 - Watermark path is a plain text input, requires manual path typing

 New Component: frontend/src/components/common/FileDropInput.vue

 Props:
 - accept: string - file type filter (e.g. ".png,.jpg,.jpeg,.bmp,.webp")
 - modelValue: string - file path (v-model)
 - placeholder: string - placeholder text

 Behavior:
 - Click zone opens file dialog via call("select_file_filtered", accept)
 - Drag & drop zone with highlight border
 - Shows filename (not full path), hover shows full path via title
 - Clear button (x) to remove selection
 - Uses useFileDrop pattern but scoped to the component area

 Backend Addition

 main.py - Add select_file_filtered method:
 @expose
 def select_file_filtered(self, file_types: str = "") -> dict:
     # Use webview.create_file_dialog with file_types filter

 Frontend Changes

 frontend/src/components/config/FilterForm.vue (line 75-85):
 - Replace <input> for watermark_path with <FileDropInput>
 - Pass accept=".png,.jpg,.jpeg,.bmp,.webp"

 Files Modified

 - NEW frontend/src/components/common/FileDropInput.vue
 - main.py (new select_file_filtered)
 - frontend/src/components/config/FilterForm.vue (use FileDropInput)

 ---
 Task 2.3: FFmpeg Version Indicator Real-time Update

 Problem

 - Navbar FFmpeg badge doesn't update when switching versions in Settings

 Backend Changes

 main.py - Add _emit call in switch_ffmpeg (~line 437):
 @expose
 def switch_ffmpeg(self, path: str) -> dict:
     info = switch_ffmpeg(path)
     # Emit version change event for navbar
     self._emit("ffmpeg_version_changed", {
         "version": info.get("version", ""),
         "path": info.get("path", ""),
         "status": "ready",
     })
     return {"success": True, "data": info}

 Frontend Changes

 frontend/src/components/layout/AppNavbar.vue (line 1-42):
 - Import onEvent from bridge
 - Add event listener for ffmpeg_version_changed in onMounted
 - Update ffmpegReady, ffmpegVersion, ffmpegError on event
 - Cleanup listener on unmount

 Files Modified

 - main.py (add _emit in switch_ffmpeg)
 - frontend/src/components/layout/AppNavbar.vue (listen to event)

 ---
 Task 2.4: Download FFmpeg Button Always Visible + Confirmation

 Problem

 - Download button hidden when FFmpeg detected
 - No confirmation before overwriting existing FFmpeg

 Frontend Changes

 frontend/src/components/settings/FFmpegSetup.vue (line 65-71):
 - Remove v-if="versions.length === 0" condition
 - Add confirmation modal (DaisyUI dialog)
 - Add loading state during download

 Before: <button v-if="versions.length === 0 && status !== 'detecting'" ...>
 After:  <button :disabled="isDownloading" @click="showConfirm = true" ...>

 Add DaisyUI modal:
 <dialog class="modal" :class="{ 'modal-open': showConfirm }">
   <div class="modal-box">
     <h3>Confirm Download</h3>
     <p>This will overwrite the current FFmpeg version. Continue?</p>
     <div class="modal-action">
       <button @click="showConfirm = false">Cancel</button>
       <button @click="confirmDownload">Confirm</button>
     </div>
   </div>
 </dialog>

 Files Modified

 - frontend/src/components/settings/FFmpegSetup.vue

 ---
 Task 2.5: Light/Dark Theme Switching

 Problem

 - Only dark theme available
 - No way to switch themes

 Backend Changes

 core/models.py - Add theme field to AppSettings (~line 311):
 theme: str = "auto"  # auto/light/dark

 Update to_dict and from_dict accordingly.

 Frontend Changes

 NEW frontend/src/composables/useTheme.ts:
 - Read theme from settings (via call("get_settings"))
 - Apply theme: set document.documentElement.setAttribute("data-theme", value)
 - Resolve "auto" via prefers-color-scheme media query
 - Listen for system theme changes when in "auto" mode
 - Save theme preference via call("save_settings", { theme })

 frontend/src/components/layout/AppNavbar.vue:
 - Add theme toggle button (sun/moon icon) in navbar-end
 - Import and use useTheme

 frontend/src/style.css - Update DaisyUI config:
 @import "tailwindcss";
 @plugin "daisyui" {
   themes: light --default, dark;
 }
 Remove --prefersdark since we handle it manually in useTheme.

 Files Modified

 - core/models.py (AppSettings.theme)
 - NEW frontend/src/composables/useTheme.ts
 - frontend/src/components/layout/AppNavbar.vue (theme toggle)
 - frontend/src/style.css (update DaisyUI config)

 ---
 Implementation Order

 1. Task 2.1 - Reset button + log lifecycle (backend + frontend, most complex)
 2. Task 2.3 - FFmpeg version indicator update (small, backend + frontend)
 3. Task 2.4 - Download button + confirmation (frontend only)
 4. Task 2.5 - Theme switching (backend model + new composable + navbar)
 5. Task 2.2 - FileDropInput component (new component + backend)

 Tasks 2.3, 2.4, 2.5 are independent and can be done in parallel after 2.1. Task 2.2 is independent and can be done at
 any point.

 Verification

 Manual test items (no automated tests per project rules):
 1. Task 2.1: Add a task, run to completion -> verify "Reset" button appears (not "Log") -> click Reset -> verify task
 goes to pending -> verify can start again
 2. Task 2.1: Fail a task -> verify "Retry" + "Log" buttons appear -> Retry -> verify logs still present
 3. Task 2.2: In Command Config > Filters, drag an image onto watermark area -> verify filename shows -> verify
 position/margin controls appear
 4. Task 2.3: In Settings, switch FFmpeg version -> verify navbar badge updates immediately without page refresh
 5. Task 2.4: In Settings, verify Download FFmpeg button always visible -> click -> verify confirmation dialog ->
 confirm -> verify download starts
 6. Task 2.5: Click theme toggle in navbar -> verify light/dark theme switches -> verify persists across page reload ->
  verify "auto" follows system preference
```

### Complete

```
  Files Modified

  ┌──────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┐
  │                       File                       │                            Changes                            │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ core/models.py                                   │ Added completed->pending, cancelled->pending transitions;     │
  │                                                  │ added theme field to AppSettings                              │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ core/task_runner.py                              │ Added reset_task() method; retry_task() now preserves         │
  │                                                  │ log_lines                                                     │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │                                                  │ Added reset_task bridge; added                                │
  │ main.py                                          │ _emit("ffmpeg_version_changed") in switch_ffmpeg; added       │
  │                                                  │ select_file_filtered bridge                                   │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/types/settings.ts                   │ Added theme field to AppSettingsDTO                           │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/composables/useTaskControl.ts       │ Added resetTask()                                             │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/composables/useSettings.ts          │ Default theme: "auto" in settings reactive                    │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/composables/useTheme.ts             │ NEW - theme switching composable with auto/light/dark support │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/components/task-queue/TaskRow.vue   │ Added reset emit; Reset button for completed/cancelled; Log   │
  │                                                  │ only for failed/running/paused                                │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/components/task-queue/TaskList.vue  │ Pass through reset event                                      │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/pages/TaskQueuePage.vue             │ Wired resetTask handler                                       │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/components/layout/AppNavbar.vue     │ Listen ffmpeg_version_changed event; theme toggle button      │
  │                                                  │ (sun/moon)                                                    │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/components/settings/FFmpegSetup.vue │ Download button always visible; confirmation modal; loading   │
  │                                                  │ state                                                         │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/components/config/FilterForm.vue    │ Replaced watermark text input with FileDropInput              │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/components/common/FileDropInput.vue │ NEW - drag-drop + click-to-select file input component        │
  ├──────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/style.css                           │ Removed --prefersdark (handled by useTheme)                   │
  └──────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────┘

  Manual Test Items

    1. Task 2.1: Run task to completion -> verify "Reset" button appears -> click -> task goes to pending
    2. Task 2.1: Fail a task -> verify "Retry" + "Log" buttons -> Retry preserves logs
    3. Task 2.2: In Command Config > Filters, drag an image onto watermark area -> verify filename shows
    4. Task 2.3: In Settings, switch FFmpeg version -> navbar badge updates immediately
    5. Task 2.4: Download button always visible -> click -> confirmation dialog appears
    6. Task 2.5: Click sun/moon icon in navbar -> theme switches -> persists on reload


```

### 问题

- Fail a task如何做，要怎么样才能Fail a task
- 文件拖拽到非拖拽区域会调用默认浏览器打开，这不对
- In Command Config > Filters, drag an image onto watermark area -> 两种形式文件名都未显示，导出的文件无水印
- 重新下载FFmpeg之后，系统环境的FFmpeg在列表中消失了

```
  1. Fail a task - 添加了 fail_task 调试方法。测试步骤：在 TaskQueue 运行一个任务，然后在浏览器控制台调用
  window.pywebview.api.fail_task("task_id") 即可强制失败。更简单的方式：把编码器设为 fake_codec 后运行。

  2. 拖拽到非拖拽区域打开浏览器 - pywebvue/app.py 新增了 dragover 和 dragenter 的 prevent_default
  handler，阻止浏览器默认打开文件行为。

  3. FileDropInput 不显示文件名 - 根因是 e.stopPropagation() 阻止了事件冒泡到 document，导致 pywebview 的 _on_drop
  handler 无法捕获文件路径。移除了所有 stopPropagation，并将 get_dropped_files 延迟增加到 150ms
  确保文件路径已写入缓冲区。

  4. 系统 FFmpeg 消失 - download_ffmpeg 调用 static_ffmpeg.add_paths() 后，static_ffmpeg 的 bin 目录被注入到 PATH
  前面，导致 shutil.which("ffmpeg") 始终返回 static_ffmpeg 的版本。修复：在 discover_ffmpeg_versions 搜索系统 PATH
  时，临时从 PATH 中移除 static_ffmpeg 目录。

  手动测试项

  1. 在 TaskQueue 运行任务 -> 控制台调 fail_task(id) -> 确认任务变为 failed，显示 Retry + Log
  2. 将文件拖到页面任意位置 -> 确认不会打开浏览器
  3. 在 Command Config > Filters 拖拽图片到水印区域 -> 确认文件名显示
  4. 在 Settings 重新下载 FFmpeg -> 确认系统 FFmpeg 仍在版本列表中
```

### 问题

- 尝试把编码器改成fake，发现执行时仍是传入的x264编码器，也即显示在命令预览处的指令（fake，命令预览处已更新！）和实际传入的指令（x264）并不一致，请确保其完全一致
- 后台log没有保存到本地，这样会导致打包后的软件看不到软件日志
- 水印区域点击无效，拖拽进入过了很久才显示，而且界面明显有在卡

```
  Bug 1: 命令预览与实际执行不一致

  - 根因：start_task 使用的是任务创建时保存的 task.config，retry/reset 后 config 不会更新
  - 修复：start_task 接收可选 config 参数，执行前更新 task.config；前端 startTask/retryTask 调用时传入当前 global config

  Bug 2: 后台日志未保存到本地

  - 根因：logging.py 只有 stderr 和 frontend sink，没有文件输出
  - 修复：添加文件 sink，日志写入 %APPDATA%/ff-intelligent-neo/logs/app_{date}.log，10MB 轮转，保留 7 天

  Bug 3: 水印区域点击无效

  - 根因：select_file_filtered 的 file_types 参数格式错误，传了 | 分隔的 string，pywebview Windows 需要的是 list of
  tuples [("desc", "*.ext")]
  - 修复：将 file_types 改为 list of tuples 格式

  拖拽延迟和 UI 卡顿 — 点击修复后建议再测试一下，可能是由点击失败导致的连带现象。
```

### 问题

- 水印区域点击仍然无效，拖拽到那里不放手过了很久才显示高亮，松手之后过了一段时间才显示，而且界面明显有在卡。前后端控制台均无任何反应。

```
  Root causes:

  1. Click not working: select_file_filtered passed file_types to pywebview's create_file_dialog. On Windows, the
  space-separated pattern format (*.png *.jpg) doesn't work with the COM file dialog (needs semicolons). This caused the
   dialog to fail silently - the @expose decorator caught the exception but the frontend had no error handling so it was
   swallowed.
  2. Drag UI freeze: pywebvue/app.py registered Python DOMEventHandler noop callbacks for dragover and dragenter events.
   During a drag operation, these events fire every ~15ms. Each event required JS->Python IPC (serialize, call Python
  lambda, return), causing severe main-thread congestion. This explains the delayed highlight and overall UI lag.

  Fixes:

  - pywebvue/app.py: Replaced Python DOMEventHandler noop handlers with window.evaluate_js to add native JS
  addEventListener + preventDefault. Zero IPC overhead.
  - main.py: select_file_filtered no longer passes file_types to create_file_dialog. File type validation moved to
  frontend.
  - FileDropInput.vue: Added frontend extension validation, error state display, and proper try/catch with console.error
   for failed calls.
```

### 问题

- 你在整个Phase2做的修改都没有按照 @references/PRD-2.1.0.md 的要求，先同步到相关文档中

```
  ┌──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
  │             文件             │                                     更新内容                                      │
  ├──────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ docs/StateMachine.md         │ 完整状态转移矩阵、按钮映射（含 Reset）、日志可见性规则、Reset 与 Retry 区别       │
  ├──────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ docs/BusinessRules.md        │ 日志生命周期、Download FFmpeg 二次确认、版本切换事件、Reset                       │
  │                              │ 行为、主题切换、FileDropInput 规则                                                │
  ├──────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ docs/Structure.md            │ FileDropInput.vue 组件文档、useTheme.ts composable 文档、useTaskControl 新增      │
  │                              │ resetTask、ffmpeg_version_changed 事件                                            │
  ├──────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ docs/Procedure.md            │ FFmpeg 版本切换时序图、Reset 流程时序图、Download                                 │
  │                              │ 确认流程时序图、主题切换流程时序图                                                │
  ├──────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ docs/fields/Task.csv         │ log_lines/error 补充 Reset/Retry 行为说明，started_at/completed_at 补充 Reset     │
  │                              │ 清理说明                                                                          │
  ├──────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ docs/fields/AppSettings.csv  │ 新增 theme 字段（auto/light/dark）                                                │
  ├──────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ docs/fields/FilterConfig.csv │ watermark_path 补充 FileDropInput 组件输入方式说明                                │
  └──────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────┘

  所有变更均按 PRD 要求标注了 <!-- v2.1.0-CHANGE --> 行号标记。
  
  ● PRD 附录 A 已更新。每个章节都标注了同步状态：

  - A.1 StateMachine - Phase 2 已同步，包含完整状态转移矩阵、按钮映射、Reset vs Retry 区别、日志可见性规则
  - A.2 BusinessRules - Phase 2 已同步，包含 6
  个业务规则章节（日志生命周期、下载确认、版本事件、Reset、主题、FileDropInput）
  - A.3 fields/ - Phase 2 已同步（Task/AppSettings/FilterConfig），Phase 3 待新增/修改的文件也已列出
  - A.4 Structure - Phase 2 已同步（FileDropInput、useTheme、useTaskControl、事件系统），Phase 3/4 待变更已列出
  - A.5 Procedure - Phase 2 已同步（4 个时序图），Phase 1/3 待变更已列出
```

### 问题

- 打开Setting界面会转圈一段时间，甚至会一直转圈，按理来说应该实现秒开的啊

```
  根因：SettingsPage 在 onMounted 中 await 了三个 API 调用（fetchSettings、fetchFfmpegVersions、fetchAppInfo），页面被
  v-if="!isReady" 的 loading spinner 完全挡住。而：
  - fetchAppInfo 会执行 ffmpeg -version + ffprobe -version 子进程
  - fetchFfmpegVersions 做磁盘扫描 + 对每个发现的 ffmpeg 都 spawn 子进程取版本

  Python 后端单线程处理 bridge call，这些子进程调用加起来可能要好几秒。

  修复：
  1. 移除 isReady loading gate，页面立即渲染
  2. 三个 fetch 改为 fire-and-forget（不 await），数据到达后响应式更新 UI
  3. ffmpegStatus 初始值已经是 "detecting"，FFmpegSetup 组件会自动显示 "Detecting..." 状态，数据返回后自然过渡到实际状态
  
  SettingsPage.vue — 移除 loading spinner 门控，页面秒开，数据异步填充
  
最终搜索范围：

  ┌─────┬─────────────────┬──────────────────────────────┬───────────────┐
  │  #  │      来源       │           平台限制           │     开销      │
  ├─────┼─────────────────┼──────────────────────────────┼───────────────┤
  │ 1   │ User (settings) │ 全平台                       │ 解析路径      │
  ├─────┼─────────────────┼──────────────────────────────┼───────────────┤
  │ 2   │ Local ./ffmpeg/ │ 全平台（非 frozen）          │ is_file()     │
  ├─────┼─────────────────┼──────────────────────────────┼───────────────┤
  │ 3   │ Platform paths  │ macOS/Linux 各自几个固定路径 │ is_file()     │
  ├─────┼─────────────────┼──────────────────────────────┼───────────────┤
  │ 4   │ System PATH     │ 全平台                       │ shutil.which  │
  ├─────┼─────────────────┼──────────────────────────────┼───────────────┤
  │ 5   │ static_ffmpeg   │ 仅 Windows                   │ import + glob │
  ├─────┼─────────────────┼──────────────────────────────┼───────────────┤
  │ 6   │ Bundled         │ 仅 PyInstaller               │ is_file()     │
  └─────┴─────────────────┴──────────────────────────────┴───────────────┘

  去掉了原来 PATH 环境变量改写（_remove_static_ffmpeg_from_path）的开销，static_ffmpeg 在非 Windows 直接跳过。
  
  ● 顶部状态栏用的是 currentVersion，来自 find(v => v.active)?.version，只有 active 的才有版本号，已经有 v-if
  保护，没问题。

  完成。非 active 的条目不取版本、不显示版本号，只显示路径和来源标签。
```



### CC-Mem

```
     Legend: session-request | 🔴 bugfix | 🟣 feature | 🔄 refactor | ✅ change | 🔵 discovery | ⚖️ decision

     Column Key
       Read: Tokens to read this observation (cost to learn it now)
       Work: Tokens spent on work that produced this record ( research, building, deciding)

     Context Index: This semantic index (titles, types, files, tokens) is usually sufficient to understand past work.

     When you need implementation details, rationale, or debugging context:
       - Fetch by ID: get_observations([IDs]) for observations visible in this index
       - Search history: Use the mem-search skill for past decisions, bugs, and deeper research
       - Trust this index over re-reading code for past decisions and learnings

     Context Economics
       Loading: 50 observations (12,222 tokens to read)
       Work investment: 21,838 tokens spent on research, building, and decisions
       Your savings: 44% reduction from reuse

     Apr 23, 2026

     #S1 Audio transcoding parameter consistency fix - user requested explanation of changes made to ensure passed
     parameters match command preview (Apr 23, 12:50 AM)

     #S2 ComboInput component enhanced with improved filtering behavior (Apr 23, 12:54 AM)

     General
       #1506  11:12 PM  🔴  Video encoder preview-execution mismatch identified
       #1507            🔴  Backend logs not persisted to local filesystem
       #1508            🔴  Watermark UI interaction issues causing lag
       #1509            ✅  Task created for config sync, log persistence, and watermark UI fixes
     ..\..\Git\GithubManager\ff-intelligent-neo\frontend\src\pages\TaskQueuePage.vue
       #1510  11:13 PM  🔵  Task config flow uses globalConfig.toTaskConfig() method
     ..\..\Git\GithubManager\ff-intelligent-neo\main.py
       #1511            🔵  Task addition bridge method located in main.py
       #1512            🔵  Config parsing defaults video_codec to libx264 when missing
     ..\..\Git\GithubManager\ff-intelligent-neo\core\task_runner.py
       #1513  11:14 PM  🔵  Command building delegated to core.command_builder module
       #1514  11:16 PM  🔵  Task execution uses build_command with task.config
     ..\..\Git\GithubManager\ff-intelligent-neo\frontend\src\pages\CommandConfigPage.vue
       #1515            🔵  Command preview uses same toTaskConfig() as task queue
     ..\..\Git\GithubManager\ff-intelligent-neo\frontend\src\composables\useCommandPreview.ts
       #1516            🔵  Command preview calls backend build_command API endpoint
     ..\..\Git\GithubManager\ff-intelligent-neo\core\command_builder.py
       #1517            🔵  Two separate command building functions exist in command_builder.py
       #1518            🔵  build_command_preview wraps build_command with placeholder filenames
     ..\..\Git\GithubManager\ff-intelligent-neo\main.py
       #1519  11:17 PM  🔵  Config parsing differs between build_command bridge and add_tasks
     General
       #1520  11:20 PM  ✅  Task description refined with specific bug details
     ..\..\Git\GithubManager\ff-intelligent-neo\frontend\src\components\common\FileDropInput.vue
       #1521  11:21 PM  🔵  FileDropInput component uses 150ms delay for drag processing
     ..\..\Git\GithubManager\ff-intelligent-neo\main.py
       #1522            🔵  Confirmed dual config parsing paths in main.py bridge
     ..\..\Git\GithubManager\ff-intelligent-neo\frontend\src\composables\useGlobalConfig.ts
       #1523            🔵  Global config store uses Object.assign for mutations
     ..\..\Git\GithubManager\ff-intelligent-neo\pywebvue\bridge.py
       #1524            🔵  Bridge base class implements thread-safe event queue and file drop handling
     ..\..\Git\GithubManager\ff-intelligent-neo\pywebvue\app.py
       #1525            🔵  App class sets up bridge infrastructure with DOM event handlers and tick timer
     ..\..\Git\GithubManager\ff-intelligent-neo\frontend\src\composables\useFileDrop.ts
       #1526            🔵  Two different file drop composables with different delays
     ..\..\Git\GithubManager\ff-intelligent-neo\core\logging.py
       #1527  11:22 PM  🔵  Logging system lacks file sink for local persistence
     ..\..\Git\GithubManager\ff-intelligent-neo\frontend\src\pages\TaskQueuePage.vue
       #1528            🔵  TaskQueuePage passes globalConfig.toTaskConfig() to addTasks
     ..\..\Git\GithubManager\ff-intelligent-neo\core\ffmpeg_runner.py
       #1529            🔵  Task logs stored in memory, limited to 500 lines per task
     ..\..\Git\GithubManager\ff-intelligent-neo\core\config.py
       #1530            🔵  APPDATA directory structure exists for settings, presets, and queue state
     ..\..\Git\GithubManager\ff-intelligent-neo\frontend\src\components\common\FileDropInput.vue
       #1531            🔵  FileDropInput 150ms delay intentional for pywebvue event bubbling
       #1532            🔵  Explore agent identified root causes of watermark FileDropInput issues
     ..\..\Git\GithubManager\ff-intelligent-neo\core\task_queue.py
       #1533            🔵  Task queue persists to APPDATA with 50-task limit for terminal tasks
     ..\..\Git\GithubManager\ff-intelligent-neo\core\logging.py
       #1534  11:23 PM  🔵  Explore agent confirmed no persistent file logging exists in application
     ..\..\Git\GithubManager\ff-intelligent-neo\core\command_builder.py
       #1535  11:39 PM  🔵  VALID_VIDEO_CODECS does not include fake encoder
     General
       #1536            🔵  No fake codec exists in entire core codebase
     ..\..\Git\GithubManager\ff-intelligent-neo\core\models.py
       #1537            🔵  TranscodeConfig models.py defines video_codec with libx264 default
     ..\..\Git\GGithubManager\ff-intelligent-neo\core\task_runner.py
       #1538  11:46 PM  🔴  Added config parameter to start_task method to sync UI settings at execution time
     ..\..\Git\GithubManager\ff-intelligent-neo\core\task_runner.py
       #1539            🔴  retry_task method updated to accept config parameter
     ..\..\Git\GithubManager\ff-intelligent-neo\main.py
       #1540  11:47 PM  🔵  Bridge start_task method does not pass config to runner
     General
       #1541  11:54 PM  🔵  Pywebvue drag-drop infrastructure uses 50ms tick timer
       #1542  11:55 PM  🔵  FileDropInput uses hardcoded 150ms timeout for drop processing
       #1543            🔵  Bridge.ts provides frontend-Python communication layer
       #1544            🔵  Watermark area uses FileDropInput component with 150ms delay
       #1545  11:56 PM  🔵  Located useGlobalConfig.ts composable
       #1546  11:57 PM  🔵  Two different file drop implementations exist in codebase
       #1547            🔵  Watermark configuration managed by reactive singleton store
       #1548            🔵  Command preview adds 300ms debounce on watermark_path changes
       #1549  11:59 PM  🔵  Performance issue traced to multiple timeout layers

     Apr 24, 2026

     General
       #1550  12:00 AM  🔴  Fixed drag event performance by replacing Python DOMEventHandler with native JS listeners
     ..\..\Git\GithubManager\ff-intelligent-neo\main.py
       #1551            🔄  Moved file dialog filtering from Python backend to frontend
     ..\..\Git\GithubManager\ff-intelligent-neo\pywebvue\app.py
       #1552            🔴  Fixed drag-drop UI lag by replacing Python DOMEventHandler with native JavaScript event
     listeners
     ..\..\Git\GithubManager\ff-intelligent-neo\frontend\src\components\common\FileDropInput.vue
       #1553  12:01 AM  🔴  Optimized FileDropInput drop timeout and added frontend file type validation
     ..\..\Git\GithubManager\ff-intelligent-neo\pywebvue\app.py
       #1554            🔵  Watermark drag performance fixed with three-layer optimization
       #1555            🔴  Watermark drag performance fix deployed to production build
              #1556  12:03 AM  🔵  Phase2 modifications require PRD synchronization
     docs/Project.md
       #1557            🔵  Project documentation structure identified
     docs/Procedure.md
       #1558  12:04 AM  🔵  Codebase structure inventory completed
     frontend/src/App.vue
       #1559            🔵  Frontend Vue component structure mapped
     core/task_runner.py
       #1560  12:05 AM  🔵  Reset functionality distributed across core modules
     frontend/src/components/layout/AppNavbar.vue
       #1561            🔵  FFmpeg version change handling located in AppNavbar component
       #1562  12:06 AM  🔵  FFmpeg version change architecture split between frontend and backend entry point
     frontend/src/composables/useSettings.ts
       #1563            🔵  FFmpeg download functionality located in frontend settings composable
     core/task_runner.py
       #1564            🔵  Core backend architecture comprises 3 major modules totaling 1,360 lines
     frontend/src/composables/useTaskControl.ts
       #1565            🔵  Frontend task control composable discovered
     docs/StateMachine.md
       #1566            🔵  Core documentation files are empty despite Phase2 implementation completion
     frontend/src/components/task-queue/TaskRow.vue
       #1567            🔵  Frontend component and composable architecture detailed
     frontend/src/composables/useTaskControl.ts
       #1568            🔵  Frontend reset task integration pattern identified
     frontend/src/composables/useSettings.ts
       #1569            🔵  FFmpeg download and version change event architecture identified
     frontend/src/composables/useTheme.ts
       #1570            🔵  Theme system architecture implements auto/light/dark modes with system preference detection

     frontend/src/components/settings/FFmpegSetup.vue
       #1571  12:07 AM  🔵  FFmpeg download confirmation modal implemented in FFmpegSetup component
     core/task_runner.py
       #1572            🔵  All Phase 2 implementation changes mapped and verified complete
     frontend/src/components/common/FileDropInput.vue
       #1573  12:09 AM  🔵  FileDropInput component implementation details revealed
     frontend/src/components/task-queue/TaskRow.vue
       #1574            🔵  TaskRow component implements state-based action buttons with Reset functionality
     core/models.py
       #1575            🔵  Backend state machine implements reset transitions from completed/cancelled to pending
     core/task_runner.py
       #1576  12:10 AM  🔵  Reset task implementation clears all runtime data and emits state change events
     General
       #1577            ✅  Documentation synchronization tasks created for all 5 documentation files
     docs/StateMachine.md
       #1578            ✅  Documentation synchronization work started - StateMachine.md task in progress
       #1579  12:11 AM  ✅  StateMachine.md populated with comprehensive state machine documentation including Reset
     functionality
     docs/fields/FilterConfig.csv
       #1580  12:12 AM  🔵  FilterConfig.csv reviewed for FileDropInput integration update
     docs/fields/AppSettings.csv
       #1581            🔵  AppSettings.csv missing theme field required for Phase2 theme system
     docs/BusinessRules.md
       #1582  12:14 AM  ✅  BusinessRules.md populated with comprehensive Phase2 business rules documentation
     docs/Structure.md
       #1583            ✅  Complete documentation synchronization finished - All 4 main docs and 3 field CSVs updated
              #1584  12:19 AM  ✅  PRD-2.1.0 Appendix A updated with Phase 2 documentation tracking
     frontend/src/pages/SettingsPage.vue
       #1585  12:21 AM  🔵  Settings page performance investigation initiated
       #1586            🔵  Settings implementation structure identified
       #1587            🔵  Settings page loading implementation uses onMounted with blocking await
     frontend/src/composables/useSettings.ts
       #1588            🔵  useSettings composable fetches default settings from API endpoint
     frontend/src/pages/SettingsPage.vue
       #1589            🔵  SettingsPage awaits PyWebView bridge and three API calls before render
     frontend/src/composables/useSettings.ts
       #1590  12:22 AM  🔵  useSettings composable uses bridge call() for Python backend communication
     frontend/src/bridge.ts
       #1592            🔵  Bridge call() function lacks timeout mechanism for Python backend requests
     backend/**/*.py
       #1593            🔵  Python backend methods not found in backend directory
     frontend/src/bridge.ts
       #1594            🔵  waitForPyWebView implements 10-second timeout with 100ms polling
     frontend/src/pages/TaskQueuePage.vue
       #1595            🔵  TaskQueuePage uses identical loading pattern as SettingsPage
       #1596  12:23 AM  🔵  Systemic blocking loading pattern across multiple pages
     frontend/src/bridge.ts
       #1598  12:24 AM  ⚖️  Implementation plan approved for Settings page loading performance fix
     main.py
       #1599            🔵  Python backend API methods located in main.py
       #1600            🔵  get_app_info backend handler imports and executes core.app_info module
       #1601            🔵  Backend API implementations located in core modules with synchronous execution
     core/app_info.py
       #1602            🔵  get_app_info executes blocking subprocess calls to FFmpeg/FFprobe binaries
     core/ffmpeg_setup.py
       #1603            🔵  discover_ffmpeg_versions performs six sequential filesystem searches with subprocess calls
     frontend/src/pages/SettingsPage.vue
       #1604            🔴  Settings page now renders immediately with progressive data loading
     core/ffmpeg_setup.py
       #1605  12:26 AM  🔵  FFmpeg version discovery uses targeted location chain, not disk scanning
       #1606  12:27 AM  🔵  Located helper functions for FFmpeg binary discovery
       #1607            🔵  FFmpeg discovery functions use targeted lookups, no recursive disk scanning
     ..\..\Git\GithubManager\ff-intelligent-neo\core\ffmpeg_setup.py
       #1608  12:29 AM  🟣  Added platform-specific binary paths to FFmpeg discovery chain
       #1609            🔄  Restricted static_ffmpeg discovery to Windows only in version discovery
       #1610  12:30 AM  ✅  Updated discover_ffmpeg_versions docstring to reflect platform-specific discovery changes
       #1611  12:33 AM  🔴  Hide "unknown" version strings in FFmpeg discovery
     ..\..\Git\GithubManager\ff-intelligent-neo\frontend\src\components\settings\FFmpegSetup.vue
       #1612  12:34 AM  🔴  Conditionally render FFmpeg version in UI
       #1613            🔵  Status bar already conditionally renders version
```

