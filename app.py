from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from graphs.task_graph import run_task_graph


try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex Brain: DMS + CDS + SPML task router")
    parser.add_argument("task", help="Task or question to analyze")
    parser.add_argument("--project", default="", help="Optional project path or name")
    parser.add_argument("--no-feedback", action="store_true", help="Do not write CDS retrieval feedback")
    parser.add_argument("--no-report", action="store_true", help="Do not write a local run report")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args()

    result = run_task_graph(args.task, project=args.project, write_feedback=not args.no_feedback)
    if not args.no_report:
        result["report_dir"] = str(write_run_report(result))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result))
    return 0


def write_run_report(result: dict) -> Path:
    root = Path(__file__).resolve().parent / "runs"
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    report_dir = root / stamp
    counter = 1
    while report_dir.exists():
        counter += 1
        report_dir = root / f"{stamp}-{counter}"
    report_dir.mkdir(parents=True, exist_ok=True)

    (report_dir / "task.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (report_dir / "retrieved.md").write_text(render_retrieved(result), encoding="utf-8")
    (report_dir / "plan.md").write_text(render_markdown(result), encoding="utf-8")
    if result.get("feedback"):
        (report_dir / "feedback.md").write_text(str(result["feedback"]) + "\n", encoding="utf-8")
    return report_dir


def render_retrieved(result: dict) -> str:
    lines = [f"# Retrieved Memory", "", f"Query: {result.get('query', '')}", ""]
    for item in result.get("memories", []):
        lines.append(f"## #{item['id']} {item['title']}")
        lines.append(f"Project: {item.get('project', '')}")
        lines.append(f"Tags: {item.get('tags', '')}")
        lines.append("")
        lines.append(str(item.get("text", "")).strip())
        lines.append("")
    if not result.get("memories"):
        lines.append("No matching CDS memories.")
    return "\n".join(lines).rstrip() + "\n"


def render_markdown(result: dict) -> str:
    lines: list[str] = []
    lines.append("# Codex Brain Plan")
    lines.append("")
    lines.append(f"Task: {result['task']}")
    lines.append(f"Route: {result['route']['domain']} / {result['route']['risk']}")
    if result["route"].get("project"):
        lines.append(f"Project: {result['route']['project']}")
    lines.append("")
    lines.append("## Retrieved Memory")
    for item in result["memories"]:
        lines.append(f"- #{item['id']} {item['title']} ({item['project']})")
    if not result["memories"]:
        lines.append("- No matching CDS memories")
    lines.append("")
    lines.append("## SPML Lens")
    for lens in result["spml_lenses"]:
        lines.append(f"- {lens}")
    if not result["spml_lenses"]:
        lines.append("- No SPML lens selected")
    lines.append("")
    lines.append("## Knowledge Packs")
    for pack in result.get("knowledge_packs", []):
        lines.append(f"- {pack['name']}: {pack['use_for']}")
    if not result.get("knowledge_packs"):
        lines.append("- No knowledge pack selected")
    lines.append("")
    profile = result.get("task_profile", {})
    if profile:
        lines.append("## Task Profile")
        lines.append(f"- Objective: {profile.get('objective', 'inspect')}")
        if profile.get("domains"):
            lines.append("- Domains: " + ", ".join(profile["domains"]))
        if profile.get("risk_gates"):
            lines.append("- Risk Gates:")
            for gate in profile["risk_gates"]:
                lines.append(f"  - {gate}")
        if profile.get("success_metrics"):
            lines.append("- Success Metrics:")
            for metric in profile["success_metrics"]:
                lines.append(f"  - {metric}")
        lines.append("")
    if result.get("hard_constraints"):
        lines.append("## Hard Constraints")
        for item in result["hard_constraints"]:
            lines.append(f"- {item}")
        lines.append("")
    if result.get("failure_types"):
        lines.append("## Failure Classifier")
        for item in result["failure_types"]:
            terms = ", ".join(item.get("matched_terms", []))
            lines.append(f"- {item['type']}: {item['next']} (matched: {terms})")
        lines.append("")
    lines.append("## Recommended Next Steps")
    for idx, step in enumerate(result["plan"], 1):
        lines.append(f"{idx}. {step}")
    lines.append("")
    lines.append("## Verification")
    for check in result["verification"]:
        lines.append(f"- {check}")
    if result.get("evaluation"):
        evaluation = result["evaluation"]
        lines.append("")
        lines.append("## Evaluation")
        lines.append(f"- Status: {evaluation.get('status', 'unknown')}")
        lines.append(f"- Used Ratio: {evaluation.get('used_ratio', 0)}")
        lines.append(f"- Noise Ratio: {evaluation.get('noise_ratio', 0)}")
        for issue in evaluation.get("issues", []):
            lines.append(f"- Issue: {issue}")
        for step in evaluation.get("next_improvements", []):
            lines.append(f"- Next: {step}")
    if result.get("memory_update_plan"):
        update_plan = result["memory_update_plan"]
        lines.append("")
        lines.append("## Memory Update Plan")
        lines.append(f"- Outcome: {update_plan.get('outcome', 'partial')}")
        for item in update_plan.get("update_existing", []):
            lines.append(f"- Update #{item['id']}: {item['action']} - {item['title']}")
        for item in update_plan.get("demote_or_noise", []):
            lines.append(f"- Noise #{item['id']}: {item['title']}")
        for item in update_plan.get("create_new_candidates", []):
            lines.append(f"- Candidate: {item['title']}")
    if result.get("memory_update_result"):
        update_result = result["memory_update_result"]
        lines.append("")
        lines.append("## Memory Update Result")
        lines.append(f"- Status: {update_result.get('status', 'unknown')}")
        if update_result.get("reason"):
            lines.append(f"- Reason: {update_result['reason']}")
        for item in update_result.get("applied", []):
            lines.append(f"- Applied #{item['id']}: {item.get('action', 'update')}")
        for item in update_result.get("errors", []):
            lines.append(f"- Error #{item.get('id')}: {item.get('error')}")
    if result.get("feedback"):
        lines.append("")
        lines.append("## Memory Feedback")
        lines.append(result["feedback"])
    if result.get("report_dir"):
        lines.append("")
        lines.append("## Run Report")
        lines.append(result["report_dir"])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
