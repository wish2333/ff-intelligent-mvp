<script setup lang="ts">
/**
 * Batch control bar: pause all, resume all, stop all, start all pending.
 */
import { ref } from "vue"
import { useI18n } from "vue-i18n"

const { t } = useI18n()

defineProps<{
  runningCount: number
  pausedCount: number
  pendingCount: number
}>()

const emit = defineEmits<{
  startAllPending: []
  stopAll: []
  pauseAll: []
  resumeAll: []
}>()

const confirmDialog = ref<HTMLDialogElement | null>(null)

function requestStopAll() {
  confirmDialog.value?.showModal()
}

function handleConfirm() {
  confirmDialog.value?.close()
  emit("stopAll")
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <span class="text-sm font-semibold opacity-70">{{ t("taskQueue.batch.label") }}</span>
    <button
      class="btn btn-sm btn-success btn-outline"
      :disabled="pendingCount === 0"
      @click="emit('startAllPending')"
    >
      {{ t("taskQueue.batch.startAll", { count: pendingCount }) }}
    </button>
    <button
      class="btn btn-sm btn-warning btn-outline"
      :disabled="runningCount === 0"
      @click="emit('pauseAll')"
    >
      {{ t("taskQueue.batch.pauseAll", { count: runningCount }) }}
    </button>
    <button
      class="btn btn-sm btn-info btn-outline"
      :disabled="pausedCount === 0"
      @click="emit('resumeAll')"
    >
      {{ t("taskQueue.batch.resumeAll", { count: pausedCount }) }}
    </button>
    <button
      class="btn btn-sm btn-error btn-outline"
      :disabled="runningCount === 0 && pausedCount === 0 && pendingCount === 0"
      @click="requestStopAll"
    >
      {{ t("taskQueue.batch.stopAll") }}
    </button>
  </div>

  <!-- Stop all confirmation modal -->
  <dialog ref="confirmDialog" class="modal">
    <div class="modal-box">
      <h3 class="font-bold text-lg">{{ t("common.stopAll") }}</h3>
      <p class="py-4">{{ t("common.stopAllConfirm") }}</p>
      <div class="modal-action">
        <button class="btn btn-ghost" @click="confirmDialog?.close()">{{ t("common.cancel") }}</button>
        <button class="btn btn-error" @click="handleConfirm()">{{ t("common.confirm") }}</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop"><button>close</button></form>
  </dialog>
</template>
