<script setup lang="ts">
import { computed } from "vue"
import type { AppInfoDTO } from "../../composables/useSettings"
import { useI18n } from "vue-i18n"

defineProps<{
  info: AppInfoDTO | null
}>()

const { t } = useI18n()

const items = computed(() => [
  { label: t("settings.about.appVersion"), key: "app_version" as const },
  { label: t("settings.about.pythonVersion"), key: "python_version" as const },
  { label: t("settings.about.ffmpegVersion"), key: "ffmpeg_version" as const },
  { label: t("settings.about.ffprobeVersion"), key: "ffprobe_version" as const },
  { label: t("settings.about.platform"), key: "is_packaged" as const },
])
</script>

<template>
  <div class="space-y-3">
    <h3 class="text-lg font-semibold">{{ t("settings.about.title") }}</h3>

    <div v-if="info" class="space-y-1.5">
      <div v-for="item in items" :key="item.key" class="flex justify-between text-sm">
        <span class="opacity-60">{{ item.label }}</span>
        <span class="font-mono">
          <template v-if="item.key === 'is_packaged'">
            {{ info[item.key] ? t("settings.about.packaged") : t("settings.about.dev") }}
          </template>
          <template v-else-if="info[item.key]">
            {{ info[item.key] }}
          </template>
          <span v-else class="opacity-40">{{ t("settings.about.na") }}</span>
        </span>
      </div>
    </div>

    <p v-else class="text-xs opacity-40">{{ t("settings.about.loading") }}</p>
  </div>
</template>
