import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("cinema_explorer.ingestion.checkpoint")

DEFAULT_CHECKPOINT_PATH = Path("ingestion/state/checkpoint.json")


class CheckpointService:
    """Lightweight, atomic file-based checkpoint tracker for resumable bulk ingestion."""

    def __init__(self, filepath: Optional[Path | str] = None, enabled: bool = True):
        self.filepath = Path(filepath) if filepath else DEFAULT_CHECKPOINT_PATH
        self.enabled = enabled
        self._state: dict[str, Any] = self._empty_state()

        if self.enabled:
            self._load()

    def _empty_state(self) -> dict[str, Any]:
        return {
            "version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated_at": datetime.now(timezone.utc).isoformat(),
            "completed_slices": [],
            "stats": {
                "discovered": 0,
                "created": 0,
                "updated": 0,
                "skipped": 0,
                "failed": 0,
            },
            "failures": [],
        }

    def _load(self) -> None:
        """Load checkpoint state from disk if present."""
        if not self.filepath.exists():
            logger.debug("No checkpoint file found at %s. Starting fresh.", self.filepath)
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data.get("version") == 1:
                    self._state = data
                    logger.info(
                        "Loaded checkpoint from %s: %d completed slices, stats=%s",
                        self.filepath,
                        len(self._state.get("completed_slices", [])),
                        self._state.get("stats", {}),
                    )
                else:
                    logger.warning(
                        "Checkpoint file %s has invalid schema. Starting fresh.",
                        self.filepath,
                    )
        except Exception as exc:
            logger.warning(
                "Failed to read checkpoint %s (%s). Starting fresh.",
                self.filepath,
                exc,
            )

    def save(self) -> None:
        """Atomically persist state to disk using a temporary file."""
        if not self.enabled:
            return

        self._state["last_updated_at"] = datetime.now(timezone.utc).isoformat()

        # Ensure parent directory exists
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        tmp_file = None
        try:
            # Write to temporary file in the same directory for atomic rename
            with tempfile.NamedTemporaryFile(
                "w",
                dir=str(self.filepath.parent),
                delete=False,
                encoding="utf-8",
            ) as f:
                tmp_file = f.name
                json.dump(self._state, f, indent=2)

            os.replace(tmp_file, self.filepath)
            logger.debug("Checkpoint safely saved to %s", self.filepath)
        except Exception as exc:
            logger.error("Failed to persist checkpoint to %s: %s", self.filepath, exc)
            if tmp_file and os.path.exists(tmp_file):
                try:
                    os.unlink(tmp_file)
                except OSError:
                    pass

    def is_slice_completed(self, slice_key: str) -> bool:
        """Check if a specific discovery slice (e.g. 'movie:te:2022:page_1') was completed."""
        if not self.enabled:
            return False
        return slice_key in self._state.get("completed_slices", [])

    def mark_slice_completed(self, slice_key: str, stats_delta: Optional[dict[str, int]] = None) -> None:
        """Mark a slice as completed and optionally add incremental statistics."""
        if not self.enabled:
            return

        completed = self._state.setdefault("completed_slices", [])
        if slice_key not in completed:
            completed.append(slice_key)

        if stats_delta:
            current_stats = self._state.setdefault("stats", {})
            for k, delta in stats_delta.items():
                current_stats[k] = current_stats.get(k, 0) + delta

        self.save()

    def record_failure(
        self,
        tmdb_id: int,
        content_type: str,
        error: str,
        slice_key: Optional[str] = None,
    ) -> None:
        """Record an isolated candidate ingestion failure."""
        if not self.enabled:
            return

        failures = self._state.setdefault("failures", [])
        failures.append({
            "tmdb_id": tmdb_id,
            "content_type": content_type,
            "error": error,
            "slice_key": slice_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.save()

    def get_stats(self) -> dict[str, int]:
        """Return cumulative statistics from checkpoint."""
        return dict(self._state.get("stats", {}))

    def reset(self) -> None:
        """Reset state and remove checkpoint file."""
        self._state = self._empty_state()
        if self.filepath.exists():
            try:
                self.filepath.unlink()
                logger.info("Removed checkpoint file at %s", self.filepath)
            except Exception as exc:
                logger.warning("Failed to delete checkpoint file %s: %s", self.filepath, exc)
