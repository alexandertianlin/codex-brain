from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_WORK_ROOT = Path("D:" + "\\") / "agiletact"


def env_path(name: str, default: str | Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else Path(default)


def first_existing_env_path(name: str, candidates: list[Path]) -> Path:
    value = os.environ.get(name)
    if value:
        return Path(value).expanduser()
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def cds_scripts_dir() -> Path:
    return first_existing_env_path(
        "CODEX_CDS_SCRIPTS",
        [Path.home() / ".codex" / "skills" / "cds" / "scripts"],
    )


def cds_memory_db() -> Path:
    return first_existing_env_path(
        "CODEX_MEMORY_DB",
        [
            LOCAL_WORK_ROOT / "codex-memory" / "index" / "memory.sqlite",
            Path.home() / "codex-memory" / "index" / "memory.sqlite",
        ],
    )


def brain_python() -> Path:
    return env_path("CODEX_BRAIN_PYTHON", ROOT / ".venv" / "Scripts" / "python.exe")
