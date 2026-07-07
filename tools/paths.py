from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def env_path(name: str, default: str | Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else Path(default)


def cds_scripts_dir() -> Path:
    return env_path("CODEX_CDS_SCRIPTS", r"C:\Users\user\.codex\skills\cds\scripts")


def cds_memory_db() -> Path:
    return env_path("CODEX_MEMORY_DB", r"D:\agiletact\codex-memory\index\memory.sqlite")


def brain_python() -> Path:
    return env_path("CODEX_BRAIN_PYTHON", ROOT / ".venv" / "Scripts" / "python.exe")
