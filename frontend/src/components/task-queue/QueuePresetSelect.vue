<script setup lang="ts">
/**
 * Compact preset selector for the queue page.
 *
 * Dropdown to quickly select and apply a processing preset.
 * Selecting a preset immediately loads its config into global config.
 */
import { ref, onMounted } from "vue"
import { useI18n } from "vue-i18n"
import { call } from "../../bridge"
import type { PresetDTO } from "../../types/preset"

const { t } = useI18n()

const emit = defineEmits<{
  (e: "apply", preset: PresetDTO): void
}>()

const presets = ref<PresetDTO[]>([])
const loading = ref(false)
const selectedId = ref("")

async function fetchPresets() {
  loading.value = true
  try {
    const res = await call<PresetDTO[]>("get_presets")
    if (res.success && res.data) {
      presets.value = res.data
    }
  } finally {
    loading.value = false
  }
}

function groupPresets() {
  const defaults = presets.value.filter((p) => p.is_default)
  const users = presets.value.filter((p) => !p.is_default)
  return { defaults, users }
}

function handleSelect() {
  const preset = presets.value.find((p) => p.id === selectedId.value)
  if (preset) {
    emit("apply", preset)
  }
}

onMounted(fetchPresets)
</script>

<template>
  <div class="flex items-center gap-2">
    <span class="text-sm font-semibold opacity-70">{{ t("taskQueue.preset.label") }}</span>
    <select
      v-model="selectedId"
      @change="handleSelect"
      class="select select-bordered select-sm w-72"
      :disabled="loading"
    >
      <option value="">{{ t("taskQueue.preset.selectPreset") }}</option>
      <optgroup
        v-if="groupPresets().defaults.length"
        :label="t('config.preset.builtIn')"
      >
        <option
          v-for="p in groupPresets().defaults"
          :key="p.id"
          :value="p.id"
        >
          {{ p.name }}
        </option>
      </optgroup>
      <optgroup
        v-if="groupPresets().users.length"
        :label="t('config.preset.custom')"
      >
        <option
          v-for="p in groupPresets().users"
          :key="p.id"
          :value="p.id"
        >
          {{ p.name }}
        </option>
      </optgroup>
    </select>
    <span v-if="loading" class="loading loading-spinner loading-xs" />
  </div>
</template>
