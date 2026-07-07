from __future__ import annotations

import json
import sqlite3
import subprocess

from tools.paths import ROOT, brain_python, cds_memory_db

MEMORY_DB = cds_memory_db()


def build_status() -> str:
    lines = ["# Codex Brain Status", ""]
    lines.append("## Recent Runs")
    runs = sorted((ROOT / "runs").glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)[:5] if (ROOT / "runs").exists() else []
    if runs:
        for run in runs:
            lines.append(f"- {run.name}")
    else:
        lines.append("- No run reports found.")
    lines.append("")
    lines.append("## Memory")
    lines.extend(_memory_summary())
    lines.append("")
    lines.append("## Retrieval Benchmark")
    lines.extend(_benchmark_summary())
    return "\n".join(lines).rstrip() + "\n"


def _memory_summary() -> list[str]:
    if not MEMORY_DB.exists():
        return [f"- Memory DB not found: {MEMORY_DB}"]
    try:
        with sqlite3.connect(MEMORY_DB) as conn:
            total = conn.execute("select count(*) from memories").fetchone()[0]
            noisy = conn.execute(
                "select id, title, noise_count, useful_count from memories order by noise_count desc limit 5"
            ).fetchall()
        lines = [f"- Total memories: {total}", "- High-noise memories:"]
        lines.extend(f"  - #{row[0]} {row[1]} noise={row[2]} useful={row[3]}" for row in noisy)
        return lines
    except Exception as exc:
        return [f"- Could not read memory DB: {exc}"]


def _benchmark_summary() -> list[str]:
    try:
        proc = subprocess.run(
            [str(brain_python()), str(ROOT / "tools" / "run_retrieval_benchmark.py"), "--json"],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        if proc.returncode != 0:
            return [f"- Benchmark failed: {proc.stderr.strip() or proc.stdout.strip()}"]
        data = json.loads(proc.stdout)
        return [f"- Score: {data['passed']}/{data['total']} passed"]
    except Exception as exc:
        return [f"- Benchmark unavailable: {exc}"]


def main() -> int:
    target = ROOT / "brain_status.md"
    target.write_text(build_status(), encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
