<script setup lang="ts">
/**
 * Task toolbar with add/remove/clear actions and select-all checkbox.
 */
import { ref } from "vue"
import { useI18n } from "vue-i18n"

const { t } = useI18n()

const props = defineProps<{
  selectedCount: number
  totalCount: number
  isAllSelected: boolean
}>()

const emit = defineEmits<{
  addFiles: []
  removeSelected: []
  clearCompleted: []
  clearAll: []
  toggleSelectAll: []
}>()

const confirmDialog = ref<HTMLDialogElement | null>(null)
const pendingAction = ref<"removeSelected" | "clearAll" | null>(null)
const confirmTitle = ref("")
const confirmMessage = ref("")

function requestRemoveSelected() {
  if (props.selectedCount === 0) return
  pendingAction.value = "removeSelected"
  confirmTitle.value = t("common.removeTasks")
  confirmMessage.value = t("common.removeTasksConfirm", { count: props.selectedCount })
  confirmDialog.value?.showModal()
}

function requestClearAll() {
  pendingAction.value = "clearAll"
  confirmTitle.value = t("common.clearQueue")
  confirmMessage.value = t("common.clearQueueConfirm")
  confirmDialog.value?.showModal()
}

function handleConfirm() {
  confirmDialog.value?.close()
  if (pendingAction.value === "removeSelected") {
    emit("removeSelected")
  } else if (pendingAction.value === "clearAll") {
    emit("clearAll")
  }
  pendingAction.value = null
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <button class="btn btn-sm btn-primary" @click="emit('addFiles')">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="17 8 12 3 7 8" />
        <line x1="12" y1="3" x2="12" y2="15" />
      </svg>
      {{ t("taskQueue.toolbar.addFiles") }}
    </button>

    <div class="divider divider-horizontal m-0" />

    <button
      class="btn btn-sm btn-ghost"
      :disabled="selectedCount === 0"
      @click="requestRemoveSelected"
    >
      {{ t("taskQueue.toolbar.removeSelected", { count: selectedCount }) }}
    </button>

    <button
      class="btn btn-sm btn-ghost"
      @click="emit('clearCompleted')"
    >
      {{ t("taskQueue.toolbar.clearDone") }}
    </button>

    <button
      class="btn btn-sm btn-ghost text-error"
      @click="requestClearAll"
    >
      {{ t("taskQueue.toolbar.clearAll") }}
    </button>

    <div class="divider divider-horizontal m-0" />

    <label class="flex items-center gap-2 text-sm">
      <input
        type="checkbox"
        class="checkbox checkbox-sm checkbox-primary"
        :checked="isAllSelected"
        @change="emit('toggleSelectAll')"
      />
      <span class="text-base-content/60">
        {{ selectedCount }}/{{ totalCount }}
      </span>
    </label>
  </div>

  <!-- Confirmation modal -->
  <dialog ref="confirmDialog" class="modal">
    <div class="modal-box">
      <h3 class="font-bold text-lg">{{ confirmTitle }}</h3>
      <p class="py-4">{{ confirmMessage }}</p>
      <div class="modal-action">
        <button class="btn btn-ghost" @click="confirmDialog?.close()">{{ t("common.cancel") }}</button>
        <button class="btn btn-error" @click="handleConfirm()">{{ t("common.confirm") }}</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop"><button>close</button></form>
  </dialog>
</template>
