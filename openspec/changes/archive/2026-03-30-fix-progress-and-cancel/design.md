## Context

FF Intelligent is a PyWebVue (Python + pywebview + Vue 3) desktop app for batch FFmpeg conversions. The backend uses a `ThreadPoolExecutor` to run FFmpeg subprocesses, emitting events to the frontend via a pywebvue bridge.

Two bugs exist:

1. **Progress display**: The `on_log` callback in `ffmpeg_runner.py` forwards every stderr line to the frontend via `log_line` events. The frontend loguru sink (`logging.py`) also forwards all Python log lines (including DEBUG-level ffmpeg internals). Result: frontend log panel flooded with raw ffmpeg output, while the progress panel only shows a percentage bar. Users cannot see speed, elapsed/total time, or status at a glance.

2. **Cancel broken**: `BatchRunner.cancel()` sets a `threading.Event`, but `_run_all()` calls `f.result()` on each future which blocks until completion. Cancelled tasks still run because `proc.kill()` only fires after the cancel event is detected in the polling loop. The frontend never receives a `batch_complete` with cancellation status, so `processing` stays `true` and buttons remain in wrong state.

## Goals / Non-Goals

**Goals:**
- Frontend progress panel shows structured info: speed, elapsed time / total duration, FPS, status — replacing the raw log dump
- Cancel kills running FFmpeg processes promptly and resets frontend state correctly
- No more raw ffmpeg stderr flooding the frontend log panel

**Non-Goals:**
- Rewriting the event system architecture
- Adding pause/resume functionality
- Changing the ThreadPoolExecutor to asyncio or ProcessPoolExecutor
- Removing the LogViewer component (keep it for potential future use)

## Decisions

### D1: Remove `on_log` callback from batch processing pipeline

**Decision:** Remove the `on_log` callback wiring in `batch_runner.py` and stop passing `on_log` to `run_single()`. Keep loguru console logging at DEBUG level in `ffmpeg_runner.py`.

**Rationale:** The `on_log` callback's only purpose is forwarding raw ffmpeg stderr to the frontend. This floods the UI with unstructured output. Loguru already captures everything at DEBUG level for terminal debugging.

**Alternative considered:** Filtering `on_log` lines to only forward warnings/errors — rejected because the structured `task_progress` events already surface all meaningful info (speed, fps, progress) to the frontend.

### D2: Raise frontend sink log level to WARNING

**Decision:** Change the frontend loguru sink in `logging.py` from `level="DEBUG"` to `level="WARNING"`.

**Rationale:** The frontend sink forwards Python log messages as `log_line` events. At DEBUG level, every internal debug message (including ffmpeg runner internals) floods the frontend. Raising to WARNING ensures only actionable messages reach the frontend.

**Alternative considered:** Removing the frontend sink entirely — rejected because Python warnings/errors during processing should still be visible to the user.

### D3: Enrich progress events with elapsed/total time

**Decision:** Add `current_seconds` and `total_duration_seconds` fields to `TaskProgress` model and include them in `task_progress` events.

**Rationale:** The frontend currently receives `time_str` (raw ffmpeg string like `time=00:01:23.456`) and `speed`/`fps`. Adding numeric seconds values lets the frontend compute and display elapsed/total time cleanly without re-parsing the ffmpeg string.

### D4: Fix cancel by tracking subprocesses and emitting `batch_cancelled`

**Decision:** After setting `_cancel_event`, actively kill all running FFmpeg processes and wait for thread termination with timeout. Emit a new `batch_cancelled` event instead of `batch_complete`. In the `_run_all` finally block, skip `batch_complete` if cancellation was requested.

**Rationale:** The current cancel only sets an event flag — the polling loop in `_run_all` calls `f.result()` which blocks. We need to:
1. Track running subprocesses in a shared dict (`_running_procs`)
2. On cancel, iterate and `kill()` each subprocess
3. Wait for threads with a short timeout (3s), then give up on stragglers
4. Emit `batch_cancelled` so frontend can distinguish from normal completion

**Alternative considered:** Using `concurrent.futures.Future.cancel()` — rejected because it only prevents pending tasks from starting, it does not stop already-running subprocesses.

### D5: Add `cancelled` status to task progress

**Decision:** Add `"cancelled"` as a valid status value in `TaskProgress` and mark in-progress tasks as cancelled when batch is cancelled.

**Rationale:** Currently tasks killed during cancel are reported as `"error"` with error="Cancelled", which is semantically wrong. A distinct `"cancelled"` status allows the frontend to display appropriate UI.

### D6: Frontend listens for `batch_cancelled` event

**Decision:** Add a `batch_cancelled` event listener in `useBatchProcess.ts` that sets `processing = false`, matching `batch_complete` behavior.

**Rationale:** Without this, the frontend stays in processing state after cancel because `batch_complete` is no longer emitted on cancellation.

### D7: Frontend progress panel shows structured data instead of raw logs

**Decision:** Update `ProgressPanel.vue` to display: elapsed time / total duration, speed, FPS alongside the progress bar. Remove the FFmpeg Log collapsible section (or keep collapsed/hidden by default). Update `formatProgressInfo()` to include time data.

**Rationale:** The log dump section is replaced by structured progress info per task, which is what users actually want to see.

## Risks / Trade-offs

- **[Race condition on cancel]** Multiple threads may be writing to `_progress_map` when cancel fires → Mitigation: Use the existing `threading.Lock` in the completion counter section; add a lock around `_running_procs` access.
- **[Zombie subprocesses]** If `proc.kill()` fails (permissions, process already exited) → Mitigation: Wrap in try/except, use `proc.wait(timeout=3)` to ensure cleanup.
- **[Frontend sink level change may hide useful info]** Raising frontend sink to WARNING hides INFO messages from backend → Mitigation: Only Python-side INFO/WARNING/ERROR messages are useful in frontend; DEBUG messages are for terminal debugging. If needed, we can selectively re-enable specific loggers.
