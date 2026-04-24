<script setup lang="ts">
/**
 * Filter configuration form.
 *
 * Controls for rotate, crop, watermark, volume, speed,
 * audio normalization, and aspect ratio conversion.
 * Phase 3.5.2: Freeze watermark + clear on aspect_convert,
 * fullscreen-drop for watermark, context-dependent bg_image.
 */

import { computed, watch } from "vue"
import type { FilterConfigDTO } from "../../types/config"
import FileDropInput from "../common/FileDropInput.vue"

const props = defineProps<{
  config: FilterConfigDTO
}>()

const ROTATE_OPTIONS = [
  { value: "", label: "None" },
  { value: "transpose=1", label: "Clockwise 90" },
  { value: "transpose=2", label: "Clockwise 180" },
  { value: "transpose=3", label: "Clockwise 270" },
]

const WATERMARK_POSITIONS = [
  { value: "top-left", label: "Top Left" },
  { value: "top-right", label: "Top Right" },
  { value: "bottom-left", label: "Bottom Left" },
  { value: "bottom-right", label: "Bottom Right" },
]

const ASPECT_MODES = [
  { value: "", label: "None" },
  { value: "H2V-I", label: "Horizontal to Vertical - Insert" },
  { value: "H2V-T", label: "Horizontal to Vertical - Top/Bottom" },
  { value: "H2V-B", label: "Horizontal to Vertical - Bottom padding" },
  { value: "V2H-I", label: "Vertical to Horizontal - Insert" },
  { value: "V2H-T", label: "Vertical to Horizontal - Top/Bottom" },
  { value: "V2H-B", label: "Vertical to Horizontal - Bottom padding" },
]

const hasAspectConvert = computed(() => !!props.config.aspect_convert)
const hasAudioNormalize = computed(() => props.config.audio_normalize)

// I modes need background image, T/B modes don't
const needsBgImage = computed(() => {
  const mode = props.config.aspect_convert
  return mode === "H2V-I" || mode === "V2H-I"
})

// Determine fullscreen drop target based on context
const fullscreenDropTarget = computed(() => {
  if (!hasAspectConvert.value) return "watermark"
  if (needsBgImage.value) return "bg_image"
  return null // T/B modes: no fullscreen drop needed
})

// Auto-fill default target_resolution when aspect_convert is selected
watch(() => props.config.aspect_convert, (val) => {
  if (val) {
    props.config.rotate = ""
    props.config.watermark_path = ""
    // Auto-fill a default target_resolution if empty
    if (!props.config.target_resolution) {
      // Determine default: if mode starts with "H" (horizontal), default to 1080x1920
      // if starts with "V" (vertical), default to 1920x1080
      props.config.target_resolution = val.startsWith("H") ? "1080x1920" : "1920x1080"
    }
  }
})
watch(() => props.config.rotate, (val) => {
  if (val) props.config.aspect_convert = ""
})

const speedWarning = computed(() => {
  const val = props.config.speed
  if (!val) return ""
  const num = parseFloat(val)
  if (isNaN(num)) return "Invalid speed value"
  if (num < 0.25 || num > 4) return "Speed must be between 0.25 and 4"
  if (num < 0.5 || num > 2) return "Speed < 0.5 or > 2.0 may cause desync"
  return ""
})
</script>

<template>
  <div class="card bg-base-200 shadow-sm">
    <div class="card-body p-4">
      <h2 class="card-title text-sm font-semibold mb-3">Filters</h2>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Column 1: Aspect Convert, Rotate, Crop -->
        <div class="space-y-3">
          <!-- Aspect Convert -->
          <div class="form-control">
            <label class="label py-1">
              <span class="label-text text-xs">Aspect Ratio Convert</span>
            </label>
            <select
              v-model="config.aspect_convert"
              class="select select-bordered select-sm w-full"
              :disabled="!!config.rotate"
            >
              <option
                v-for="mode in ASPECT_MODES"
                :key="mode.value"
                :value="mode.value"
              >
                {{ mode.label }}
              </option>
            </select>
            <label v-if="hasAspectConvert" class="label py-0.5">
              <span class="label-text-alt text-xs text-warning">
                Aspect convert active -- crop, rotate, and watermark disabled
              </span>
            </label>
          </div>

          <!-- Aspect Convert: Target Resolution -->
          <div v-if="hasAspectConvert" class="form-control">
            <label class="label py-1">
              <span class="label-text text-xs">Target Resolution</span>
            </label>
            <input
              v-model="config.target_resolution"
              type="text"
              placeholder="e.g. 1080x1920"
              class="input input-bordered input-sm w-full"
            />
          </div>

          <!-- Aspect Convert: Background Image (only for I modes) -->
          <div v-if="hasAspectConvert && needsBgImage" class="form-control">
            <label class="label py-1">
              <span class="label-text text-xs">Background Image</span>
            </label>
            <FileDropInput
              :model-value="config.bg_image_path"
              accept=".png,.jpg,.jpeg,.bmp,.webp"
              placeholder="Drop background image here or click to select (required for Insert mode)"
              :fullscreen-drop="fullscreenDropTarget === 'bg_image'"
              @update:model-value="config.bg_image_path = $event"
            />
          </div>

          <!-- Aspect Convert: Info for T/B modes (no bg image needed) -->
          <div v-if="hasAspectConvert && !needsBgImage" class="form-control">
            <div class="rounded-lg border border-base-300 bg-base-300/30 px-3 py-3 text-center">
              <p class="text-xs text-base-content/50">
                {{ typeof props.config.aspect_convert === 'string' && props.config.aspect_convert.endsWith("-T")
                  ? "Using blurred background. No external image needed."
                  : "Using black padding background. No external image needed." }}
              </p>
            </div>
          </div>

          <!-- Rotate -->
          <div class="form-control">
            <label class="label py-1">
              <span class="label-text text-xs">Rotate</span>
            </label>
            <select
              v-model="config.rotate"
              class="select select-bordered select-sm w-full"
              :disabled="hasAspectConvert"
            >
              <option
                v-for="opt in ROTATE_OPTIONS"
                :key="opt.value"
                :value="opt.value"
              >
                {{ opt.label }}
              </option>
            </select>
          </div>

          <!-- Crop -->
          <div class="form-control">
            <label class="label py-1">
              <span class="label-text text-xs">Crop</span>
            </label>
            <input
              v-model="config.crop"
              type="text"
              placeholder="W:H:X:Y e.g. 1920:800:0:140"
              class="input input-bordered input-sm w-full"
              :disabled="hasAspectConvert"
            />
            <label class="label py-0.5">
              <span class="label-text-alt text-xs text-base-content/50">
                Format: W:H:X:Y
              </span>
            </label>
            <div class="pl-4 space-y-0.5">
              <span class="block text-xs text-base-content/40">out_w: Width of the cropped area</span>
              <span class="block text-xs text-base-content/40">out_h: Height of the cropped area</span>
              <span class="block text-xs text-base-content/40">x: X-coordinate of top-left corner</span>
              <span class="block text-xs text-base-content/40">y: Y-coordinate of top-left corner</span>
            </div>
          </div>
        </div>

        <!-- Column 2: Watermark -->
        <div class="space-y-3">
          <div class="divider my-0 text-xs">Watermark</div>

          <!-- Watermark Path (hidden when aspect_convert active) -->
          <div v-if="!hasAspectConvert">
            <div class="form-control">
              <label class="label py-1">
                <span class="label-text text-xs">Watermark Image</span>
              </label>
              <FileDropInput
                :model-value="config.watermark_path"
                accept=".png,.jpg,.jpeg,.bmp,.webp"
                placeholder="Drop image here or click to select"
                :fullscreen-drop="fullscreenDropTarget === 'watermark'"
                @update:model-value="config.watermark_path = $event"
              />
            </div>

            <!-- Watermark Position -->
            <div v-if="config.watermark_path" class="form-control">
              <label class="label py-1">
                <span class="label-text text-xs">Position</span>
              </label>
              <select
                v-model="config.watermark_position"
                class="select select-bordered select-sm w-full"
              >
                <option
                  v-for="pos in WATERMARK_POSITIONS"
                  :key="pos.value"
                  :value="pos.value"
                >
                  {{ pos.label }}
                </option>
              </select>
            </div>

            <!-- Watermark Margin -->
            <div v-if="config.watermark_path" class="form-control">
              <label class="label py-1">
                <span class="label-text text-xs">Margin (px)</span>
              </label>
              <input
                v-model.number="config.watermark_margin"
                type="number"
                min="0"
                max="100"
                class="input input-bordered input-sm w-full"
              />
            </div>
          </div>
        </div>

        <!-- Column 3: Audio -->
        <div class="space-y-3">
          <div class="divider my-0 text-xs">Audio</div>

          <!-- Volume -->
          <div class="form-control">
            <label class="label py-1">
              <span class="label-text text-xs">Volume</span>
            </label>
            <input
              v-model="config.volume"
              type="text"
              placeholder="e.g. 1.5 (boost), 0.5 (reduce)"
              class="input input-bordered input-sm w-full"
              :disabled="hasAudioNormalize"
            />
            <label class="label py-0.5">
              <span class="label-text-alt text-xs text-base-content/50">
                Leave empty for original volume
                <span v-if="hasAudioNormalize" class="text-warning"> -- disabled when normalize is active</span>
              </span>
            </label>
          </div>

          <!-- Audio Normalization -->
          <div class="form-control">
            <label class="label cursor-pointer justify-start gap-2 py-1">
              <input
                v-model="config.audio_normalize"
                type="checkbox"
                class="checkbox checkbox-sm checkbox-primary"
              />
              <div>
                <span class="label-text text-xs">Audio Normalization (loudnorm)</span>
                <p class="text-xs text-base-content/50 mt-0.5">Apply EBU R128 loudness normalization</p>
              </div>
            </label>
          </div>

          <!-- Normalize Params -->
          <div v-if="config.audio_normalize" class="ml-4 space-y-2">
            <div class="form-control">
              <label class="label py-0">
                <span class="label-text text-xs">Integrated Loudness (LUFS)</span>
              </label>
              <input
                v-model.number="config.target_loudness"
                type="number"
                min="-70"
                max="-5"
                class="input input-bordered input-sm w-full"
              />
            </div>
            <div class="form-control">
              <label class="label py-0">
                <span class="label-text text-xs">True Peak (dBTP)</span>
              </label>
              <input
                v-model.number="config.true_peak"
                type="number"
                min="-9"
                max="0"
                class="input input-bordered input-sm w-full"
              />
            </div>
            <div class="form-control">
              <label class="label py-0">
                <span class="label-text text-xs">LRA (dB)</span>
              </label>
              <input
                v-model.number="config.lra"
                type="number"
                min="1"
                max="50"
                class="input input-bordered input-sm w-full"
              />
            </div>
          </div>

          <div class="divider my-0 text-xs">Speed</div>

          <!-- Speed -->
          <div class="form-control">
            <label class="label py-1">
              <span class="label-text text-xs">Speed</span>
            </label>
            <input
              v-model="config.speed"
              type="text"
              placeholder="e.g. 2.0 (faster), 0.5 (slower)"
              class="input input-bordered input-sm w-full"
            />
            <label class="label py-0.5">
              <span
                class="label-text-alt text-xs"
                :class="speedWarning && speedWarning.includes('must') ? 'text-error' : speedWarning ? 'text-warning' : 'text-base-content/50'"
              >
                {{ speedWarning || 'Leave empty for original speed (range 0.25 - 4)' }}
              </span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
