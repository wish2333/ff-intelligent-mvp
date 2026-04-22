# /// script
# requires-python = ">=3.10"
# dependencies = ["pywebview>=6.0", "static-ffmpeg", "loguru>=0.7"]
# ///
"""FF Intelligent Neo 2.0 - FFmpeg batch processing desktop tool."""

from __future__ import annotations

import warnings

import webview

# Suppress pywebview deprecation warnings (FOLDER_DIALOG / OPEN_DIALOG)
warnings.filterwarnings("ignore", message=".*deprecated.*", module="webview")

from pywebvue import App, Bridge, expose
from core.logging import get_logger, setup_frontend_sink
from core.ffmpeg_setup import ensure_ffmpeg, get_ffmpeg_path

logger = get_logger()


class FFmpegApi(Bridge):

    def __init__(self) -> None:
        super().__init__()
        self._loguru_initialized = False

    def _ensure_loguru(self) -> None:
        """Setup loguru frontend sink once the bridge emit is available."""
        if self._loguru_initialized:
            return
        self._loguru_initialized = True
        setup_frontend_sink(self._emit)
        logger.info("FF Intelligent Neo 2.0 started, loguru frontend sink connected")

    # ------------------------------------------------------------------
    # FFmpeg setup (Phase 1 stubs)
    # ------------------------------------------------------------------

    @expose
    def setup_ffmpeg(self) -> dict:
        self._ensure_loguru()
        try:
            ready = ensure_ffmpeg()
            ffmpeg_path = get_ffmpeg_path()
            logger.info("FFmpeg setup: ready={}, path={}", ready, ffmpeg_path)
            return {"success": True, "data": {"ready": ready, "ffmpeg_path": ffmpeg_path or ""}}
        except Exception as exc:
            logger.exception("FFmpeg setup failed: {}", exc)
            return {"success": False, "error": str(exc)}

    @expose
    def get_app_info(self) -> dict:
        """Return application metadata and FFmpeg/FFprobe versions."""
        try:
            from core.app_info import get_app_info as _get_info
            info = _get_info()
            return {"success": True, "data": info}
        except Exception as exc:
            logger.exception("get_app_info failed: {}", exc)
            return {"success": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # File dialogs (Phase 1 stubs)
    # ------------------------------------------------------------------

    @expose
    def select_files(self) -> dict:
        try:
            result = self._window.create_file_dialog(
                dialog_type=webview.FileDialog.OPEN,
                allow_multiple=True,
            )
            if result:
                return {"success": True, "data": list(result)}
            return {"success": True, "data": []}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @expose
    def select_output_dir(self) -> dict:
        try:
            result = self._window.create_file_dialog(
                dialog_type=webview.FileDialog.FOLDER,
            )
            if result and len(result) > 0:
                return {"success": True, "data": result[0]}
            return {"success": True, "data": None}
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    api = FFmpegApi()
    app = App(
        api,
        title="FF Intelligent Neo",
        width=960,
        height=720,
        min_size=(800, 600),
        frontend_dir="frontend_dist",
    )
    app.run()
