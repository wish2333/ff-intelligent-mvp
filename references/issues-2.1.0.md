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

