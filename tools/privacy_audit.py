from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BLOCKED_CONTENT_PATTERNS = [
    re.compile(r"[A-Za-z]:\\(?:Users|agiletact)\\", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*=\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
]

BLOCKED_TRACKED_SUFFIXES = {
    ".pkl",
    ".pt",
    ".pth",
    ".onnx",
    ".ckpt",
    ".safetensors",
    ".mp4",
    ".mov",
    ".mkv",
    ".webm",
    ".wav",
    ".mp3",
    ".sqlite",
    ".db",
}

TEXT_SUFFIXES = {
    ".cmd",
    ".example",
    ".gitattributes",
    ".gitignore",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True, encoding="utf-8")
    return [ROOT / line.strip() for line in output.splitlines() if line.strip()]


def should_scan_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {".env.example", "README.md"}


def audit() -> list[str]:
    findings: list[str] = []
    for path in tracked_files():
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in BLOCKED_TRACKED_SUFFIXES:
            findings.append(f"blocked tracked file type: {rel}")
            continue
        if not should_scan_text(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in BLOCKED_CONTENT_PATTERNS:
            if pattern.search(text):
                findings.append(f"blocked content pattern {pattern.pattern!r}: {rel}")
    return findings


def main() -> int:
    findings = audit()
    if findings:
        print("privacy audit failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("privacy audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
