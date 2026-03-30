## 1. Backend Model Changes

- [x] 1.1 Add `current_seconds: float = 0.0` and `total_duration_seconds: float = 0.0` fields to `TaskProgress` in `core/models.py`
- [x] 1.2 Add `"cancelled"` as a valid status value comment in `TaskProgress`

## 2. Backend FFmpeg Runner

- [x] 2.1 In `ffmpeg_runner.py`, pass `current_seconds` and `duration` through `on_progress` callback signature
- [x] 2.2 Update `on_progress` call site to include `current_seconds` and `total_duration_seconds=duration`

## 3. Backend Batch Runner - Progress

- [x] 3.1 Update `on_progress` callback in `_run_task` to include `current_seconds` and `total_duration_seconds` in the `task_progress` event payload
- [x] 3.2 Update `TaskProgress` construction in `on_progress` to include `current_seconds` and `total_duration_seconds`
- [x] 3.3 Remove `on_log` callback definition in `_run_task` (stop emitting `log_line` events)
- [x] 3.4 Stop passing `on_log` to `run_single()` call

## 4. Backend Batch Runner - Cancel

- [x] 4.1 Add `_running_procs: dict[int, subprocess.Popen]` instance variable to `BatchRunner` to track running subprocesses
- [x] 4.2 Register subprocess in `_running_procs` when FFmpeg starts; remove it when task completes or errors
- [x] 4.3 Update `cancel()` to iterate `_running_procs` and call `proc.kill()` on each running subprocess
- [x] 4.4 Update `_run_all` finally block: skip `batch_complete` emission if `_cancel_event.is_set()`, emit `batch_cancelled` instead
- [x] 4.5 Mark in-progress tasks as `"cancelled"` status in progress map when cancellation is detected

## 5. Backend Logging

- [x] 5.1 Change frontend sink log level from `DEBUG` to `WARNING` in `core/logging.py`

## 6. Frontend State Management

- [x] 6.1 Remove `log_line` event listener from `useBatchProcess.ts`
- [x] 6.2 Remove `logLines` ref and its cleanup from `useBatchProcess.ts`
- [x] 6.3 Add `current_seconds` and `total_duration_seconds` to `TaskProgressData` interface
- [x] 6.4 Add `batch_cancelled` event listener in `useBatchProcess.ts` that sets `processing = false`
- [x] 6.5 Update `task_progress` event handler to store `current_seconds` and `total_duration_seconds`
- [x] 6.6 Remove `logLines` from the composable's return object

## 7. Frontend UI

- [x] 7.1 Update `ProgressPanel.vue` to display elapsed time / total duration for running tasks
- [x] 7.2 Add a "Cancelled" status badge style in `ProgressPanel.vue` and handle `"cancelled"` status
- [x] 7.3 Remove the FFmpeg Log collapsible section from `ProgressPanel.vue`
- [x] 7.4 Remove the `LogViewer` import from `ProgressPanel.vue`
- [x] 7.5 Remove global `pywebvue:log_line` event listener from `App.vue`
