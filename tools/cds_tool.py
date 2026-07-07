from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from tools.paths import cds_scripts_dir

CDS_DIR = cds_scripts_dir()
RETRIEVE_CMD = CDS_DIR / "retrieve.cmd"
FEEDBACK_CMD = CDS_DIR / "feedback.cmd"
CDS_CMD = CDS_DIR / "cds.cmd"


@dataclass
class Memory:
    id: int
    title: str
    project: str = ""
    tags: str = ""
    text: str = ""


def retrieve(query: str, limit: int = 8) -> tuple[list[Memory], str]:
    output = _run([str(RETRIEVE_CMD), query, "--limit", str(limit)])
    return parse_memories(output), output


def write_feedback(query: str, returned: list[int], used: list[int], noise: list[int], note: str) -> str:
    return _run(
        [
            str(FEEDBACK_CMD),
            "--query",
            query,
            "--returned",
            ",".join(f"#{i}" for i in returned) or "none",
            "--used",
            ",".join(f"#{i}" for i in used) or "none",
            "--noise",
            ",".join(f"#{i}" for i in noise) or "none",
            "--outcome",
            "success",
            "--note",
            note,
        ]
    )


def update_memory(memory_id: int, append_note: str, importance: str = "high", recurrence: str = "high", priority: int = 90) -> str:
    return _run(
        [
            str(CDS_CMD),
            "update",
            str(memory_id),
            "--importance",
            importance,
            "--recurrence",
            recurrence,
            "--retrieval-priority",
            str(priority),
            "--append-note",
            append_note,
        ]
    )


def apply_memory_update_plan(update_plan: dict, max_updates: int = 3) -> dict:
    if update_plan.get("outcome") not in {"pass", "success"}:
        return {"status": "skipped", "reason": "Only pass/success outcomes are auto-applied."}

    applied = []
    errors = []
    for item in update_plan.get("update_existing", [])[:max_updates]:
        try:
            output = update_memory(
                int(item["id"]),
                append_note=f"Auto update from codex-brain: {item.get('reason', 'used in successful run')}",
                priority=95,
            )
            applied.append({"id": item["id"], "action": item.get("action"), "output": output.strip()})
        except Exception as exc:
            errors.append({"id": item.get("id"), "error": str(exc)})
    return {
        "status": "applied" if applied and not errors else "partial" if applied else "failed" if errors else "skipped",
        "applied": applied,
        "errors": errors,
        "create_new_candidates": update_plan.get("create_new_candidates", []),
        "note": "Create-new candidates remain manual/reviewed to avoid duplicate memory growth.",
    }


def parse_memories(output: str) -> list[Memory]:
    memories: list[Memory] = []
    blocks = re.split(r"\n(?=## #\d+ )", output)
    for block in blocks:
        match = re.search(r"## #(\d+) (.+)", block)
        if not match:
            continue
        meta = re.search(r"Project:\s*(.*?)\s*\|\s*Tags:\s*(.*?)\s*\|", block)
        memories.append(
            Memory(
                id=int(match.group(1)),
                title=match.group(2).strip(),
                project=meta.group(1).strip() if meta else "",
                tags=meta.group(2).strip() if meta else "",
                text=block.strip(),
            )
        )
    return memories


def _run(cmd: list[str]) -> str:
    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout
