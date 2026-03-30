## 1. Fix DOM event bubbling (core fix)

- [x] 1.1 Add `bubbles: true` to CustomEvent in `pywebvue/bridge.py` `_emit()`

## 2. Fix cancelled tasks not updated in frontend

- [x] 2.1 Emit `task_progress` event when task is cancelled in `core/batch_runner.py`
- [x] 2.2 Update `batch_cancelled` handler in `frontend/src/composables/useBatchProcess.ts` to update `taskProgressMap` for cancelled tasks

## 3. Fix progress panel not disappearing after cancel

- [x] 3.1 Reset `overallTotal` to 0 in `batch_cancelled` handler in `useBatchProcess.ts`
