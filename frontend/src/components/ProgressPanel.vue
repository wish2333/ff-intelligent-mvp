<script setup lang="ts">
import { inject } from "vue";
import { useBatchProcess, type TaskProgressData } from "../composables/useBatchProcess";

const batchProcess = inject<ReturnType<typeof useBatchProcess>>("batchProcess");
if (!batchProcess) {
  throw new Error("ProgressPanel: batchProcess not provided. Make sure App.vue provides it.");
}

const {
  processing,
  overallProgress,
  overallTotal,
  overallCompleted,
  taskProgressMap,
} = batchProcess;

function statusBadge(status: string): string {
  switch (status) {
    case "running": return "badge-info";
    case "done": return "badge-success";
    case "error": return "badge-error";
    case "cancelled": return "badge-warning";
    default: return "badge-ghost";
  }
}

function statusLabel(status: string): string {
  switch (status) {
    case "done": return "Done";
    case "error": return "Error";
    case "running": return "Running";
    case "cancelled": return "Cancelled";
    default: return status;
  }
}

function formatProgressInfo(task: TaskProgressData): string {
  const parts: string[] = [];
  if (task.speed) parts.push(`speed=${task.speed}`);
  if (task.fps) parts.push(`fps=${task.fps}`);
  return parts.join(" | ");
}

function formatTime(seconds: number | undefined): string {
  if (seconds == null || seconds < 0) return "--:--";
  const totalSec = Math.floor(seconds);
  const h = Math.floor(totalSec / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = totalSec % 60;
  if (h > 0) {
    return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  }
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

const tasksList = () => Object.values(taskProgressMap.value);
</script>

<template>
  <div v-if="processing || overallTotal > 0" class="border-t border-base-300 px-4 py-2">
    <!-- Overall progress -->
    <div class="flex items-center gap-3 mb-2">
      <span class="text-xs text-base-content/50 w-16">Overall</span>
      <progress
        class="progress progress-primary flex-1"
        :value="overallProgress"
        max="100"
      ></progress>
      <span class="text-xs text-base-content/50 w-12 text-right">
        {{ overallCompleted }}/{{ overallTotal }}
      </span>
    </div>

    <!-- Per-file progress -->
    <div v-if="tasksList().length > 0" class="flex flex-col gap-1 mb-2">
      <div
        v-for="task in tasksList()"
        :key="task.file_index"
        class="flex items-center gap-2"
      >
        <span class="badge badge-sm" :class="statusBadge(task.status)">{{ statusLabel(task.status) }}</span>
        <span class="text-xs truncate max-w-32" :title="task.file_name">{{ task.file_name }}</span>
        <progress
          v-if="task.status === 'running'"
          class="progress progress-info flex-1"
          :value="task.percent"
          max="100"
        ></progress>
        <span v-if="task.status === 'running'" class="text-xs text-base-content/50 whitespace-nowrap">
          {{ formatTime(task.current_seconds) }}/{{ formatTime(task.total_duration_seconds) }}
        </span>
        <span v-if="task.status === 'running' && formatProgressInfo(task)" class="text-xs text-base-content/50 whitespace-nowrap">
          {{ formatProgressInfo(task) }}
        </span>
        <span v-if="task.status === 'running'" class="text-xs text-base-content/50 w-10 text-right">
          {{ task.percent.toFixed(0) }}%
        </span>
        <span v-if="task.status === 'error'" class="text-xs text-error truncate max-w-xs" :title="task.error">
          {{ task.error }}
        </span>
      </div>
    </div>
  </div>
</template>
