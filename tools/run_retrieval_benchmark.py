from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from graphs.task_graph import run_task_graph


def main() -> int:
    parser = argparse.ArgumentParser(description="Run codex-brain retrieval benchmark cases.")
    parser.add_argument("--cases", default=str(ROOT / "benchmarks" / "retrieval_cases.json"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    results = [run_case(case) for case in cases]
    passed = sum(1 for result in results if result["pass"])
    report = {"pass": passed == len(results), "passed": passed, "total": len(results), "cases": results}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"retrieval benchmark: {passed}/{len(results)} passed")
        for result in results:
            status = "PASS" if result["pass"] else "FAIL"
            print(f"{status} {result['name']}")
            for failure in result["failures"]:
                print(f"  - {failure}")
    return 0 if report["pass"] else 1


def run_case(case: dict) -> dict:
    result = run_task_graph(case["task"], write_feedback=False)
    failures: list[str] = []
    route = result.get("route", {})
    domain_text = " ".join([str(route.get("domain", "")), *route.get("matched_domains", [])])
    pack_names = {pack["name"] for pack in result.get("knowledge_packs", [])}
    lens_names = set(result.get("spml_lenses", []))
    memory_ids = {memory["id"] for memory in result.get("memories", [])}

    for expected in case.get("expected_domain_contains", []):
        if expected not in domain_text:
            failures.append(f"domain missing {expected}; got {domain_text}")
    for expected in case.get("expected_packs", []):
        if expected not in pack_names:
            failures.append(f"pack missing {expected}; got {sorted(pack_names)}")
    for forbidden in case.get("forbidden_packs", []):
        if forbidden in pack_names:
            failures.append(f"forbidden pack selected {forbidden}")
    expected_lenses_any = set(case.get("expected_lenses_any", []))
    if expected_lenses_any and not (expected_lenses_any & lens_names):
        failures.append(f"none of expected lenses {sorted(expected_lenses_any)} found; got {sorted(lens_names)}")
    expected_memory_ids_any = set(case.get("expected_memory_ids_any", []))
    if expected_memory_ids_any and not (expected_memory_ids_any & memory_ids):
        failures.append(f"none of expected memories {sorted(expected_memory_ids_any)} found; got {sorted(memory_ids)}")
    return {
        "name": case["name"],
        "pass": not failures,
        "failures": failures,
        "route": route,
        "packs": sorted(pack_names),
        "lenses": sorted(lens_names),
        "memory_ids": sorted(memory_ids),
        "evaluation": result.get("evaluation", {}),
    }


if __name__ == "__main__":
    raise SystemExit(main())
