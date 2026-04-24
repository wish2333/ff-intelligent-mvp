<script setup lang="ts">
/**
 * Audio/Subtitle mixing configuration form.
 *
 * Supports external audio replacement and subtitle embedding.
 * Phase 3.5.1: Half-screen layout with fullscreen drag-drop.
 */

import type { AudioSubtitleConfigDTO } from "../../types/config"
import FileDropInput from "../common/FileDropInput.vue"

defineProps<{
  config: AudioSubtitleConfigDTO
}>()
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Audio Section -->
    <div class="card bg-base-200 shadow-sm">
      <div class="card-body p-4">
        <h2 class="card-title text-sm font-semibold mb-3">Audio</h2>
        <p class="text-xs text-base-content/60 mb-3">
          External audio track. Replaces or mixes with original audio.
        </p>

        <!-- External Audio Path -->
        <div class="form-control mb-3">
          <label class="label py-1">
            <span class="label-text text-xs">External Audio</span>
          </label>
          <FileDropInput
            :model-value="config.external_audio_path"
            accept=".mp3,.aac,.flac,.wav,.m4a,.ogg,.wma"
            placeholder="Drop audio file here or click to select"
            fullscreen-drop
            @update:model-value="config.external_audio_path = $event"
          />
        </div>

        <!-- Replace Audio Toggle -->
        <div v-if="config.external_audio_path" class="form-control">
          <label class="label cursor-pointer justify-start gap-2 py-1">
            <input
              v-model="config.replace_audio"
              type="checkbox"
              class="checkbox checkbox-sm checkbox-primary"
            />
            <div>
              <span class="label-text text-xs">Replace original audio</span>
              <p class="text-xs text-base-content/50 mt-0.5">Disable to mix audio tracks instead</p>
            </div>
          </label>
        </div>
      </div>
    </div>

    <!-- Subtitle Section -->
    <div class="card bg-base-200 shadow-sm">
      <div class="card-body p-4">
        <h2 class="card-title text-sm font-semibold mb-3">Subtitle</h2>
        <p class="text-xs text-base-content/60 mb-3">
          Embed subtitle file into output video.
        </p>

        <!-- Subtitle Path -->
        <div class="form-control mb-3">
          <label class="label py-1">
            <span class="label-text text-xs">Subtitle File</span>
          </label>
          <FileDropInput
            :model-value="config.subtitle_path"
            accept=".srt,.ass,.ssa"
            placeholder="Drop subtitle file here or click to select"
            fullscreen-drop
            @update:model-value="config.subtitle_path = $event"
          />
        </div>

        <!-- Subtitle Language -->
        <div v-if="config.subtitle_path" class="form-control">
          <label class="label py-1">
            <span class="label-text text-xs">Subtitle Language Code</span>
          </label>
          <input
            v-model="config.subtitle_language"
            type="text"
            placeholder="e.g. eng, chi, jpn"
            class="input input-bordered input-sm w-full"
          />
          <label class="label py-0.5">
            <span class="label-text-alt text-xs text-base-content/50">
              ISO 639-2 language code for metadata (optional)
            </span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>
