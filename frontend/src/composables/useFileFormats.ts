/**
 * File format configuration composable.
 *
 * Loads supported file extensions from presets/file_formats.json
 * via backend API on first access, then caches in memory.
 * Used by FileDropInput, SplitDropZone and other components
 * for drag-and-drop and click-to-select format validation.
 */

import { ref } from "vue"
import { call } from "../bridge"

export type FileFormatCategory = "audio" | "subtitle" | "video" | "image"

const fileFormats = ref<Record<FileFormatCategory, string>>({
  audio: ".mp3,.aac,.flac,.wav,.m4a,.ogg,.wma",
  subtitle: ".srt,.ass,.ssa",
  video: ".mp4,.mkv,.avi,.mov,.ts,.m2ts",
  image: ".png,.jpg,.jpeg,.bmp,.webp",
})

let loaded = false

/**
 * Convert accept string to pywebview file_types parameter.
 *
 * pywebview create_file_dialog expects a tuple of strings:
 *   ("Description (*.ext1;*.ext2)", "All files (*.*)")
 */
export function toWebViewFileTypes(accept: string | undefined): string[] | undefined {
  if (!accept) return undefined
  const exts = accept
    .split(",")
    .map((e) => e.trim().toLowerCase())
    .filter(Boolean)
  if (exts.length === 0) return undefined
  const filter = exts.map((e) => e.replace(/^\./, "*")).join(";")
  return [`Media Files (${filter})`, "All files (*.*)"]
}

async function loadFileFormats(): Promise<void> {
  if (loaded) return
  loaded = true
  try {
    const res = await call<Record<FileFormatCategory, string>>("get_file_formats")
    if (res.success && res.data) {
      fileFormats.value = res.data
    }
  } catch {
    // Use built-in defaults on failure
  }
}

/**
 * Composable that provides centralized file format strings.
 * Loads from backend on first call, then serves from cache.
 */
export function useFileFormats() {
  loadFileFormats()
  return {
    fileFormats,
  }
}
