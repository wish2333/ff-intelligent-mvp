<script setup lang="ts">
/**
 * Merge configuration panel.
 *
 * Combines MergeFileList with merge mode and filter_complex settings.
 * Phase 3.5.1: Split target_resolution into W/H inputs, default 1920x1080, FPS default 30.
 */

import { computed } from "vue"
import type { MergeConfigDTO } from "../../types/config"
import MergeFileList from "./MergeFileList.vue"

const props = defineProps<{
  config: MergeConfigDTO
}>()

const MERGE_MODES = [
  { value: "concat_protocol", label: "Concat Protocol (fast, same container)" },
  { value: "ts_concat", label: "TS Concat (demuxer, same codec)" },
  { value: "filter_complex", label: "Filter Complex (re-encode, any format)" },
]

const isFilterComplex = computed(() => props.config.merge_mode === "filter_complex")

// Split target_resolution "WxH" into two number inputs
const mergeWidth = computed({
  get: () => {
    const res = props.config.target_resolution
    if (!res) return 1920
    return parseInt(res.split("x")[0]) || 1920
  },
  set: (val: number | undefined) => {
    const w = val || 1920
    const h = mergeHeight.value || 1080
    props.config.target_resolution = `${w}x${h}`
  },
})

const mergeHeight = computed({
  get: () => {
    const res = props.config.target_resolution
    if (!res) return 1080
    return parseInt(res.split("x")[1]) || 1080
  },
  set: (val: number | undefined) => {
    const w = mergeWidth.value || 1920
    const h = val || 1080
    props.config.target_resolution = `${w}x${h}`
  },
})
</script>

<template>
  <div class="card bg-base-200 shadow-sm">
    <div class="card-body p-4">
      <h2 class="card-title text-sm font-semibold mb-3">Merge / Concatenate</h2>
      <p class="text-xs text-base-content/60 mb-3">
        Combine multiple video files into one. Merge mode is independent of other settings.
      </p>

      <!-- Merge Mode -->
      <div class="form-control mb-3">
        <label class="label py-1">
          <span class="label-text text-xs">Merge Mode</span>
        </label>
        <select
          v-model="config.merge_mode"
          class="select select-bordered select-sm w-full"
        >
          <option
            v-for="mode in MERGE_MODES"
            :key="mode.value"
            :value="mode.value"
          >
            {{ mode.label }}
          </option>
        </select>
        <label class="label py-0.5">
          <span class="label-text-alt text-xs text-base-content/50">
            TS Concat is fastest; Filter Complex works with any format but re-encodes
          </span>
        </label>
      </div>

      <!-- File List -->
      <div class="form-control mb-3">
        <label class="label py-1">
          <span class="label-text text-xs">Files ({{ config.file_list.length }})</span>
        </label>
        <MergeFileList
          :model-value="config.file_list"
          @update:model-value="config.file_list = $event"
        />
      </div>

      <!-- Filter Complex Settings -->
      <template v-if="isFilterComplex">
        <div class="divider my-2 text-xs">Filter Complex Settings</div>

        <div class="form-control mb-3">
          <label class="label py-1">
            <span class="label-text text-xs">Target Resolution</span>
          </label>
          <div class="flex items-center gap-2">
            <input
              v-model.number="mergeWidth"
              type="number"
              placeholder="1920"
              class="input input-bordered input-sm flex-1"
              min="1"
            />
            <span class="text-xs text-base-content/50">x</span>
            <input
              v-model.number="mergeHeight"
              type="number"
              placeholder="1080"
              class="input input-bordered input-sm flex-1"
              min="1"
            />
          </div>
        </div>

        <div class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Target FPS</span>
          </label>
          <input
            v-model.number="config.target_fps"
            type="number"
            min="0"
            placeholder="30 (original if 0)"
            class="input input-bordered input-sm w-full"
          />
          <label class="label py-0.5">
            <span class="label-text-alt text-xs text-base-content/50">
              Normalizes all inputs to this framerate before concatenation
            </span>
          </label>
        </div>
      </template>
    </div>
  </div>
</template>
