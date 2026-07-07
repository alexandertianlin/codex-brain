from __future__ import annotations

from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "protected-baselines.yml"


def matching_baselines(task: str) -> list[dict]:
    text = task.lower()
    matches = []
    for baseline in load_baselines():
        terms = [str(term).lower() for term in baseline.get("terms", [])]
        if any(term and term in text for term in terms):
            matches.append(baseline)
    return matches


def load_baselines() -> list[dict]:
    if not CONFIG_PATH.exists():
        return []
    rows = _read_baseline_yaml(CONFIG_PATH)
    return rows


def _read_baseline_yaml(path: Path) -> list[dict]:
    baselines: list[dict] = []
    current: dict | None = None
    list_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "baselines:" or stripped.startswith("name:"):
            continue
        if stripped.startswith("- id:"):
            current = {"id": stripped.split(":", 1)[1].strip()}
            baselines.append(current)
            list_key = None
            continue
        if current is None:
            continue
        if stripped.startswith("- "):
            if list_key:
                current.setdefault(list_key, [])
                current[list_key].append(stripped[2:].strip())
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                current[key] = value
                list_key = None
            else:
                current[key] = []
                list_key = key
    return baselines
