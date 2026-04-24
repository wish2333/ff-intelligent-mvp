<script setup lang="ts">
/**
 * Transcode configuration form.
 *
 * Provides controls for video/audio codec, bitrate, resolution,
 * framerate, quality parameters, and output format selection.
 * Uses grouped EncoderSelect for codec selection with hardware detection.
 * Clears dependent fields when codec changes to copy/none.
 *
 * Phase 3.5.2: Resolution split to W/H, field reorder.
 */

import { computed, watch } from "vue"
import type { TranscodeConfigDTO } from "../../types/config"
import { useGlobalConfig } from "../../composables/useGlobalConfig"
import EncoderSelect from "./EncoderSelect.vue"
import ComboInput from "../common/ComboInput.vue"

const props = defineProps<{
  config: TranscodeConfigDTO
}>()

const { supportedEncoders } = useGlobalConfig()

const OUTPUT_FORMAT_SUGGESTIONS = [
  ".mp4", ".mkv", ".avi", ".mov", ".mp3", ".aac", ".flac", ".wav",
]

const QUALITY_MODE_SUGGESTIONS = [
  { value: "crf", label: "CRF (Constant Rate Factor)" },
  { value: "cq", label: "CQ (Constant Quality)" },
  { value: "qp", label: "QP (Constant Quantization)" },
]

const PRESET_SUGGESTIONS = [
  "ultrafast", "superfast", "veryfast", "faster", "fast",
  "medium", "slow", "slower", "veryslow",
]

const PIXEL_FORMAT_SUGGESTIONS = [
  "yuv420p", "yuv420p10le", "yuv422p", "yuv444p",
]

const isVideoReencode = () =>
  props.config.video_codec !== "copy" && props.config.video_codec !== "none"

// Split resolution "WxH" into two number inputs
const resWidth = computed({
  get: () => {
    const res = props.config.resolution
    if (!res) return 0
    return parseInt(res.split("x")[0]) || 0
  },
  set: (val: number | undefined) => {
    const w = val || 0
    const h = resHeight.value || 0
    props.config.resolution = w && h ? `${w}x${h}` : ""
  },
})

const resHeight = computed({
  get: () => {
    const res = props.config.resolution
    if (!res) return 0
    return parseInt(res.split("x")[1]) || 0
  },
  set: (val: number | undefined) => {
    const w = resWidth.value || 0
    const h = val || 0
    props.config.resolution = w && h ? `${w}x${h}` : ""
  },
})

// Clear video-related fields when codec switches to copy/none
watch(() => props.config.video_codec, (newVal) => {
  if (newVal === "copy" || newVal === "none") {
    props.config.video_bitrate = ""
    props.config.resolution = ""
    props.config.framerate = ""
    props.config.quality_mode = ""
    props.config.quality_value = 0
    props.config.preset = ""
    props.config.pixel_format = ""
    props.config.max_bitrate = ""
    props.config.bufsize = ""
  }
})

// Clear audio bitrate when codec switches to copy/none
watch(() => props.config.audio_codec, (newVal) => {
  if (newVal === "copy" || newVal === "none") {
    props.config.audio_bitrate = ""
  }
})

function handleQualityChange(payload: { quality: number; mode: string } | null) {
  if (payload) {
    props.config.quality_mode = payload.mode
    props.config.quality_value = payload.quality
  }
  // null = custom encoder, don't auto-fill
}
</script>

<template>
  <div class="card bg-base-200 shadow-sm">
    <div class="card-body p-4">
      <h2 class="card-title text-sm font-semibold mb-3">Encoding Config</h2>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-x-6 gap-y-2">
        <!-- Row 1: VC | Resolution | AC -->
        <div class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Video Codec</span>
          </label>
          <EncoderSelect
            :model-value="config.video_codec"
            category="video"
            :supported-encoders="supportedEncoders"
            @update:model-value="config.video_codec = $event"
            @quality-change="handleQualityChange"
          />
        </div>

        <div v-if="isVideoReencode()" class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Resolution</span>
          </label>
          <div class="flex items-center gap-2">
            <input
              v-model.number="resWidth"
              type="number"
              placeholder="1920"
              class="input input-bordered input-sm flex-1"
              min="1"
            />
            <span class="text-xs text-base-content/50">x</span>
            <input
              v-model.number="resHeight"
              type="number"
              placeholder="1080"
              class="input input-bordered input-sm flex-1"
              min="1"
            />
          </div>
        </div>

        <div class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Audio Codec</span>
          </label>
          <EncoderSelect
            :model-value="config.audio_codec"
            category="audio"
            :supported-encoders="supportedEncoders"
            @update:model-value="config.audio_codec = $event"
          />
        </div>

        <!-- Row 2: QM | Framerate | AB -->
        <div v-if="isVideoReencode()" class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Quality Mode</span>
          </label>
          <select
            v-model="config.quality_mode"
            class="select select-bordered select-sm w-full"
          >
            <option value="" disabled>Select quality mode...</option>
            <option v-for="q in QUALITY_MODE_SUGGESTIONS" :key="q.value" :value="q.value">
              {{ q.label }}
            </option>
          </select>
        </div>

        <div v-if="isVideoReencode()" class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Framerate</span>
          </label>
          <input
            v-model="config.framerate"
            type="text"
            placeholder="e.g. 30, 60 (original if empty)"
            class="input input-bordered input-sm w-full"
          />
        </div>

        <div v-if="config.audio_codec !== 'copy' && config.audio_codec !== 'none'" class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Audio Bitrate</span>
          </label>
          <input
            v-model="config.audio_bitrate"
            type="text"
            placeholder="e.g. 128k, 320k"
            class="input input-bordered input-sm w-full"
          />
        </div>

        <!-- Row 3: QV | VB | OutputFormat -->
        <div v-if="isVideoReencode() && config.quality_mode" class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Quality Value</span>
          </label>
          <input
            v-model.number="config.quality_value"
            type="number"
            min="0"
            max="51"
            placeholder="0-51 (auto-filled by encoder)"
            class="input input-bordered input-sm w-full"
          />
        </div>

        <div v-if="isVideoReencode()" class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Video Bitrate</span>
          </label>
          <input
            v-model="config.video_bitrate"
            type="text"
            placeholder="e.g. 5M, 8000k (auto if empty)"
            class="input input-bordered input-sm w-full"
          />
        </div>

        <div class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Output Format</span>
          </label>
          <ComboInput
            :model-value="config.output_extension"
            :suggestions="OUTPUT_FORMAT_SUGGESTIONS"
            placeholder="e.g. .mp4, .mkv, .mp3..."
            @update:model-value="config.output_extension = $event"
          />
        </div>

        <!-- Row 4: EP | MB -->
        <div v-if="isVideoReencode()" class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Encoding Preset</span>
          </label>
          <ComboInput
            :model-value="config.preset"
            :suggestions="PRESET_SUGGESTIONS"
            placeholder="e.g. medium (speed vs compression)"
            @update:model-value="config.preset = $event"
          />
        </div>

        <div v-if="isVideoReencode()" class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Max Bitrate</span>
          </label>
          <input
            v-model="config.max_bitrate"
            type="text"
            placeholder="e.g. 8M"
            class="input input-bordered input-sm w-full"
          />
        </div>
        <div></div>

        <!-- Row 5: PF -->
        <div v-if="isVideoReencode()" class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Pixel Format</span>
          </label>
          <ComboInput
            :model-value="config.pixel_format"
            :suggestions="PIXEL_FORMAT_SUGGESTIONS"
            placeholder="e.g. yuv420p (auto if empty)"
            @update:model-value="config.pixel_format = $event"
          />
        </div>
        <div></div>
        <div></div>

        <!-- Buffer Size (full width, conditional) -->
        <div v-if="isVideoReencode() && config.max_bitrate" class="form-control col-span-3">
          <label class="label py-1">
            <span class="label-text text-xs">Buffer Size</span>
          </label>
          <input
            v-model="config.bufsize"
            type="text"
            placeholder="e.g. 2M (default 2M)"
            class="input input-bordered input-sm w-full max-w-xs"
          />
        </div>
      </div>
    </div>
  </div>
</template>
