## ADDED Requirements

### Requirement: No raw ffmpeg stderr in frontend log panel
The system SHALL NOT forward raw FFmpeg stderr lines to the frontend via `log_line` events. The `on_log` callback SHALL NOT be wired in the batch processing pipeline.

#### Scenario: Batch processing with multiple files
- **WHEN** a batch of files is being processed
- **THEN** no raw FFmpeg stderr lines appear in the frontend log panel

#### Scenario: Loguru DEBUG logging still works in terminal
- **WHEN** batch processing is running
- **THEN** FFmpeg runner debug messages (e.g. progress, command execution) are still visible in the terminal via loguru

### Requirement: Frontend sink filters to WARNING level
The loguru frontend sink SHALL use log level WARNING or higher, preventing DEBUG and INFO Python log messages from reaching the frontend.

#### Scenario: Backend warning during processing
- **WHEN** a WARNING-level log message is emitted by the Python backend during batch processing
- **THEN** the message is forwarded to the frontend as a `log_line` event

#### Scenario: Backend debug message suppressed from frontend
- **WHEN** a DEBUG-level log message is emitted by the Python backend during batch processing
- **THEN** the message is NOT forwarded to the frontend

### Requirement: Progress events include elapsed and total time
The `TaskProgress` model SHALL include `current_seconds` (float) and `total_duration_seconds` (float) fields. The `task_progress` event payload SHALL include both fields.

#### Scenario: Progress event contains time data
- **WHEN** a task is being processed and FFmpeg reports progress
- **THEN** the `task_progress` event includes `current_seconds`, `total_duration_seconds`, `speed`, and `fps`

#### Scenario: Duration is zero or unknown
- **WHEN** ffprobe cannot determine the file duration
- **THEN** `total_duration_seconds` is 0.0 and no progress percentage events are emitted (existing behavior)

### Requirement: Frontend progress panel displays structured progress info
The `ProgressPanel.vue` component SHALL display, for each running task: progress percentage, speed, FPS, elapsed time, and total duration. The component SHALL NOT display a raw FFmpeg log section by default.

#### Scenario: Running task shows progress details
- **WHEN** a task is running and progress events are received
- **THEN** the progress panel shows: percentage bar, speed value, FPS value, elapsed time, total duration, and status badge

#### Scenario: Elapsed time formatted as MM:SS or HH:MM:SS
- **WHEN** current_seconds is provided in the progress event
- **THEN** the frontend displays the elapsed time formatted as MM:SS (under 1 hour) or HH:MM:SS (1 hour or more)

#### Scenario: Total duration formatted same way
- **WHEN** total_duration_seconds is provided in the progress event
- **THEN** the frontend displays the total duration formatted as MM:SS (under 1 hour) or HH:MM:SS (1 hour or more)
