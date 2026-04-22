"""Frozen dataclasses for type-safe data transfer between layers."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

TaskState = Literal[
    "pending", "running", "paused", "completed", "failed", "cancelled"
]

VALID_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    "pending": {"running", "cancelled"},
    "running": {"paused", "completed", "failed", "cancelled"},
    "paused": {"running", "cancelled"},
    "failed": {"pending"},
    "completed": set(),
    "cancelled": set(),
}


# ---------------------------------------------------------------------------
# Transcode parameters
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TranscodeConfig:
    """FFmpeg encoding parameters."""

    video_codec: str = "libx264"
    audio_codec: str = "aac"
    video_bitrate: str = ""
    audio_bitrate: str = ""
    resolution: str = ""
    framerate: str = ""
    output_extension: str = ".mp4"


# ---------------------------------------------------------------------------
# Filter parameters
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FilterConfig:
    """FFmpeg filter parameters."""

    rotate: str = ""
    crop: str = ""
    watermark_path: str = ""
    watermark_position: str = "bottom-right"
    watermark_margin: int = 10
    volume: str = ""
    speed: str = ""


# ---------------------------------------------------------------------------
# Task-level configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TaskConfig:
    """Complete configuration for a single conversion task."""

    transcode: TranscodeConfig = field(default_factory=TranscodeConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)
    output_dir: str = ""


# ---------------------------------------------------------------------------
# Task progress (immutable snapshot, created on each update)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TaskProgress:
    """Progress info for a single conversion task (immutable snapshot)."""

    percent: float = 0.0
    current_seconds: float = 0.0
    total_seconds: float = 0.0
    speed: str = ""
    fps: str = ""
    frame: int = 0
    estimated_remaining: str = ""


# ---------------------------------------------------------------------------
# Task entity (mutable -- state/progress/log_lines updated at runtime)
# ---------------------------------------------------------------------------


@dataclass
class Task:
    """A single conversion task with file info, config, and runtime state."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    file_path: str = ""
    file_name: str = ""
    file_size_bytes: int = 0
    duration_seconds: float = 0.0
    config: TaskConfig = field(default_factory=TaskConfig)
    state: TaskState = "pending"
    progress: TaskProgress = field(default_factory=TaskProgress)
    output_path: str = ""
    error: str = ""
    log_lines: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    started_at: str = ""
    completed_at: str = ""

    def can_transition(self, new_state: TaskState) -> bool:
        return new_state in VALID_TRANSITIONS.get(self.state, set())

    def transition(self, new_state: TaskState) -> None:
        if not self.can_transition(new_state):
            raise ValueError(
                f"Invalid transition: {self.state} -> {new_state}"
            )
        old_state = self.state
        self.state = new_state

        if new_state == "running" and not self.started_at:
            self.started_at = datetime.now().isoformat()

        if new_state in ("completed", "failed", "cancelled"):
            self.completed_at = datetime.now().isoformat()

        return old_state  # type: ignore[return-value]

    def update_progress(self, progress: TaskProgress) -> None:
        self.progress = progress

    def to_dict(self) -> dict:
        """Serialize to dict for JSON persistence and bridge transfer."""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size_bytes": self.file_size_bytes,
            "duration_seconds": self.duration_seconds,
            "config": {
                "transcode": {
                    "video_codec": self.config.transcode.video_codec,
                    "audio_codec": self.config.transcode.audio_codec,
                    "video_bitrate": self.config.transcode.video_bitrate,
                    "audio_bitrate": self.config.transcode.audio_bitrate,
                    "resolution": self.config.transcode.resolution,
                    "framerate": self.config.transcode.framerate,
                    "output_extension": self.config.transcode.output_extension,
                },
                "filters": {
                    "rotate": self.config.filters.rotate,
                    "crop": self.config.filters.crop,
                    "watermark_path": self.config.filters.watermark_path,
                    "watermark_position": self.config.filters.watermark_position,
                    "watermark_margin": self.config.filters.watermark_margin,
                    "volume": self.config.filters.volume,
                    "speed": self.config.filters.speed,
                },
                "output_dir": self.config.output_dir,
            },
            "state": self.state,
            "progress": {
                "percent": self.progress.percent,
                "current_seconds": self.progress.current_seconds,
                "total_seconds": self.progress.total_seconds,
                "speed": self.progress.speed,
                "fps": self.progress.fps,
                "frame": self.progress.frame,
                "estimated_remaining": self.progress.estimated_remaining,
            },
            "output_path": self.output_path,
            "error": self.error,
            "log_lines": self.log_lines[-100:],
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Deserialize from dict (JSON persistence / bridge transfer)."""
        tc = data.get("config", {}).get("transcode", {})
        fc = data.get("config", {}).get("filters", {})
        pr = data.get("progress", {})

        return cls(
            id=data.get("id", uuid.uuid4().hex[:12]),
            file_path=data.get("file_path", ""),
            file_name=data.get("file_name", ""),
            file_size_bytes=data.get("file_size_bytes", 0),
            duration_seconds=data.get("duration_seconds", 0.0),
            config=TaskConfig(
                transcode=TranscodeConfig(
                    video_codec=tc.get("video_codec", "libx264"),
                    audio_codec=tc.get("audio_codec", "aac"),
                    video_bitrate=tc.get("video_bitrate", ""),
                    audio_bitrate=tc.get("audio_bitrate", ""),
                    resolution=tc.get("resolution", ""),
                    framerate=tc.get("framerate", ""),
                    output_extension=tc.get("output_extension", ".mp4"),
                ),
                filters=FilterConfig(
                    rotate=fc.get("rotate", ""),
                    crop=fc.get("crop", ""),
                    watermark_path=fc.get("watermark_path", ""),
                    watermark_position=fc.get("watermark_position", "bottom-right"),
                    watermark_margin=fc.get("watermark_margin", 10),
                    volume=fc.get("volume", ""),
                    speed=fc.get("speed", ""),
                ),
                output_dir=data.get("config", {}).get("output_dir", ""),
            ),
            state=data.get("state", "pending"),
            progress=TaskProgress(
                percent=pr.get("percent", 0.0),
                current_seconds=pr.get("current_seconds", 0.0),
                total_seconds=pr.get("total_seconds", 0.0),
                speed=pr.get("speed", ""),
                fps=pr.get("fps", ""),
                frame=pr.get("frame", 0),
                estimated_remaining=pr.get("estimated_remaining", ""),
            ),
            output_path=data.get("output_path", ""),
            error=data.get("error", ""),
            log_lines=data.get("log_lines", []),
            created_at=data.get("created_at", ""),
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at", ""),
        )


# ---------------------------------------------------------------------------
# Preset (immutable)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Preset:
    """An FFmpeg conversion preset with embedded TaskConfig."""

    id: str
    name: str
    description: str = ""
    config: TaskConfig = field(default_factory=TaskConfig)
    is_default: bool = False

    def to_dict(self) -> dict:
        """Serialize to dict for bridge transfer and persistence."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "config": {
                "transcode": {
                    "video_codec": self.config.transcode.video_codec,
                    "audio_codec": self.config.transcode.audio_codec,
                    "video_bitrate": self.config.transcode.video_bitrate,
                    "audio_bitrate": self.config.transcode.audio_bitrate,
                    "resolution": self.config.transcode.resolution,
                    "framerate": self.config.transcode.framerate,
                    "output_extension": self.config.transcode.output_extension,
                },
                "filters": {
                    "rotate": self.config.filters.rotate,
                    "crop": self.config.filters.crop,
                    "watermark_path": self.config.filters.watermark_path,
                    "watermark_position": self.config.filters.watermark_position,
                    "watermark_margin": self.config.filters.watermark_margin,
                    "volume": self.config.filters.volume,
                    "speed": self.config.filters.speed,
                },
                "output_dir": self.config.output_dir,
            },
            "is_default": self.is_default,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Preset:
        """Deserialize from dict."""
        tc = data.get("config", {}).get("transcode", {})
        fc = data.get("config", {}).get("filters", {})

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            config=TaskConfig(
                transcode=TranscodeConfig(
                    video_codec=tc.get("video_codec", "libx264"),
                    audio_codec=tc.get("audio_codec", "aac"),
                    video_bitrate=tc.get("video_bitrate", ""),
                    audio_bitrate=tc.get("audio_bitrate", ""),
                    resolution=tc.get("resolution", ""),
                    framerate=tc.get("framerate", ""),
                    output_extension=tc.get("output_extension", ".mp4"),
                ),
                filters=FilterConfig(
                    rotate=fc.get("rotate", ""),
                    crop=fc.get("crop", ""),
                    watermark_path=fc.get("watermark_path", ""),
                    watermark_position=fc.get("watermark_position", "bottom-right"),
                    watermark_margin=fc.get("watermark_margin", 10),
                    volume=fc.get("volume", ""),
                    speed=fc.get("speed", ""),
                ),
                output_dir=data.get("config", {}).get("output_dir", ""),
            ),
            is_default=data.get("is_default", False),
        )


# ---------------------------------------------------------------------------
# App settings (immutable)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AppSettings:
    """Application-level settings persisted to settings.json."""

    max_workers: int = 2
    default_output_dir: str = ""
    ffmpeg_path: str = ""
    ffprobe_path: str = ""

    def to_dict(self) -> dict:
        return {
            "max_workers": self.max_workers,
            "default_output_dir": self.default_output_dir,
            "ffmpeg_path": self.ffmpeg_path,
            "ffprobe_path": self.ffprobe_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AppSettings:
        return cls(
            max_workers=data.get("max_workers", 2),
            default_output_dir=data.get("default_output_dir", ""),
            ffmpeg_path=data.get("ffmpeg_path", ""),
            ffprobe_path=data.get("ffprobe_path", ""),
        )
