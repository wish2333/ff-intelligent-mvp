## ADDED Requirements

### Requirement: Cancel kills running FFmpeg subprocesses
When cancel is requested, the system SHALL actively kill all running FFmpeg subprocesses, not just set a flag. `BatchRunner` SHALL track running subprocesses and iterate over them to call `proc.kill()`.

#### Scenario: Cancel while single task is running
- **WHEN** user clicks Cancel while a single FFmpeg task is in progress
- **THEN** the FFmpeg subprocess is killed within 1 second and the task is marked as cancelled

#### Scenario: Cancel while multiple tasks are running concurrently
- **WHEN** user clicks Cancel while multiple FFmpeg tasks are running in the thread pool
- **THEN** all running FFmpeg subprocesses are killed

### Requirement: Cancel waits for thread termination with timeout
After killing subprocesses, the system SHALL wait for worker threads to terminate with a timeout of 3 seconds. Threads that do not terminate within the timeout SHALL be abandoned (daemon threads will be cleaned up on process exit).

#### Scenario: Threads terminate within timeout
- **WHEN** cancel kills all subprocesses and threads terminate within 3 seconds
- **THEN** the batch runner transitions to idle state

#### Scenario: Threads do not terminate within timeout
- **WHEN** a thread hangs after subprocess kill
- **THEN** the batch runner still transitions to idle state after the 3 second timeout

### Requirement: Cancel emits batch_cancelled event
When a batch is cancelled, the system SHALL emit a `batch_cancelled` event instead of `batch_complete`. The `batch_cancelled` event payload SHALL include `total`, `completed`, `errors`, and `cancelled` fields.

#### Scenario: Batch cancelled event emitted
- **WHEN** user cancels a running batch
- **THEN** a `batch_cancelled` event is emitted with total count, completed count, error count, and cancelled count

#### Scenario: batch_complete is NOT emitted on cancel
- **WHEN** a batch ends due to cancellation
- **THEN** `batch_complete` is NOT emitted

### Requirement: Cancelled tasks have cancelled status
Tasks that were in-progress when cancel was requested SHALL have status `"cancelled"` in the `TaskProgress` model, not `"error"`.

#### Scenario: In-progress task marked as cancelled
- **WHEN** a task was running when cancel was requested
- **THEN** its `TaskProgress` status is `"cancelled"`

#### Scenario: Pending tasks are not started
- **WHEN** cancel is requested before some tasks have started
- **THEN** those tasks remain in `"pending"` status and are not submitted to the thread pool

### Requirement: Frontend resets processing state on batch_cancelled
The frontend `useBatchProcess` composable SHALL listen for `batch_cancelled` events and set `processing = false`.

#### Scenario: Cancel resets button state
- **WHEN** user cancels a running batch
- **THEN** the frontend `processing` state becomes `false` and the Start button is re-enabled

#### Scenario: Cancel updates task progress display
- **WHEN** user cancels a running batch
- **THEN** tasks that were running show a "Cancelled" status badge

### Requirement: Frontend log_line listener removed
The `useBatchProcess` composable SHALL NOT listen for `log_line` events, and the `logLines` reactive ref SHALL be removed.

#### Scenario: No log accumulation during processing
- **WHEN** a batch is being processed
- **THEN** no log lines are accumulated in the frontend state

### Requirement: Global log_line listener removed from App.vue
The global `pywebvue:log_line` event listener in `App.vue` SHALL be removed.

#### Scenario: No console spam from log events
- **WHEN** a batch is being processed
- **THEN** the browser console does not receive `log_line` debug events
