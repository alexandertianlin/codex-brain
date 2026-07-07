from __future__ import annotations

import re
from pathlib import Path


PACK_DIR = Path(__file__).resolve().parents[1] / "knowledge-packs"


def load_packs() -> list[dict]:
    packs: list[dict] = []
    for path in sorted(PACK_DIR.glob("*.yml")):
        packs.append(_normalize_pack(_read_simple_yaml(path)))
    if not packs:
        raise RuntimeError(f"No knowledge packs found in {PACK_DIR}")
    return packs


def select_packs(task: str, route: dict | None = None, spml_lenses: list[str] | None = None) -> list[dict]:
    route = route or {}
    spml_lenses = spml_lenses or []
    text = task.lower()
    domains = _infer_domains(text, route)

    selected: list[dict] = []
    for pack in PACKS:
        pack_domains = pack["domains"]
        if "all" in pack_domains:
            selected.append(_public_pack(pack))
            continue
        if domains & pack_domains and _pack_matches(pack, text, domains, spml_lenses):
            selected.append(_public_pack(pack))

    if spml_lenses and not any(pack["name"] == "NTU SPML Project Knowledge" for pack in selected):
        selected.append(_public_pack(_pack_by_name("NTU SPML Project Knowledge")))

    selected = _add_pack_dependencies(selected, text)
    return selected[:6]


def query_terms(packs: list[dict]) -> list[str]:
    return [pack["query_terms"] for pack in packs if pack.get("query_terms")]


def names(packs: list[dict]) -> list[str]:
    return [pack["name"] for pack in packs]


def _infer_domains(text: str, route: dict) -> set[str]:
    domains = set(str(route.get("domain", "")).split("+"))
    domains.update(route.get("matched_domains", []))
    domains.discard("")

    if _has_pack_terms(text, "Relationship Game Theory") or _has_pack_terms(text, "Boundary Consent Communication"):
        domains.add("relationship")
    if _has_pack_terms(text, "Career Million-Yuan Track"):
        domains.add("career")
    if _has_pack_terms(text, "Learning and Feynman Mastery"):
        domains.add("learning")
    if _has_pack_terms(text, "Product and Taste Review"):
        domains.add("product")
    if _has_pack_terms(text, "Media Transcription Pipeline"):
        domains.add("media-transcription")
    if _has_pack_terms(text, "Risk and Decision Audit"):
        domains.add("risk")
    if _mentions_nuwa_skill_synthesis(text):
        domains.add("skill-synthesis")
    if not domains:
        domains.add("general")
    return domains


def _pack_matches(pack: dict, text: str, domains: set[str], spml_lenses: list[str]) -> bool:
    if pack["name"] == "NTU SPML Project Knowledge":
        return bool(spml_lenses) or ("architecture" not in domains and _has_any(text, pack["terms"])) or _mentions_concrete_spml_context(text)
    if pack["name"] in {
        "Career Million-Yuan Track",
        "Learning and Feynman Mastery",
        "Risk and Decision Audit",
        "Boundary Consent Communication",
        "Nuwa Skill Synthesis",
        "Media Transcription Pipeline",
    }:
        return _has_any(text, pack["terms"])
    if pack["name"] == "Product and Taste Review":
        return _mentions_product_experience_context(text)
    return bool(domains & pack["domains"]) or _has_any(text, pack["terms"])


def _add_pack_dependencies(selected: list[dict], text: str) -> list[dict]:
    names_seen = {pack["name"] for pack in selected}
    dependency_names: list[str] = []
    if any(name in names_seen for name in ["NTU SPML Project Knowledge"]):
        dependency_names.append("Core DMS/CDS Memory")
    if "Nuwa Skill Synthesis" in names_seen:
        dependency_names.append("Core DMS/CDS Memory")
    if "Relationship Game Theory" in names_seen:
        dependency_names.append("Boundary Consent Communication")
    if "Product and Taste Review" in names_seen:
        dependency_names.append("Risk and Decision Audit")
    if "Media Transcription Pipeline" in names_seen:
        dependency_names.append("Core DMS/CDS Memory")

    result = list(selected)
    for name in dependency_names:
        if name not in {pack["name"] for pack in result}:
            result.append(_public_pack(_pack_by_name(name)))
    return result


def _pack_by_name(name: str) -> dict:
    for pack in PACKS:
        if pack["name"] == name:
            return pack
    raise KeyError(name)


def _has_pack_terms(text: str, name: str) -> bool:
    return _has_any(text, _pack_by_name(name)["terms"])


def _public_pack(pack: dict) -> dict:
    return {
        "name": pack["name"],
        "query_terms": pack["query_terms"],
        "use_for": pack["use_for"],
    }


def _has_any(text: str, terms: set[str]) -> bool:
    return any(_term_matches(text, term.lower()) for term in terms)


def _term_matches(text: str, term: str) -> bool:
    if term.isascii() and term.replace("-", "").replace(" ", "").isalnum() and len(term) <= 3:
        return term in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", text)
    return term in text


def _mentions_concrete_spml_context(text: str) -> bool:
    concrete_terms = {
        "onlytip", "project c", "hamer", "vitpose", "unity", "imu", "tactile",
        "d435i", "openvins", "bbox", "camera", "course", "exam", "ee6", "ee7",
        "课程", "选课", "考试", "手套", "视觉", "触觉", "融合", "传感器", "回放",
    }
    return any(term in text for term in concrete_terms)


def _mentions_product_experience_context(text: str) -> bool:
    exact_terms = {
        "ui", "ux", "dashboard", "interface", "front-end", "frontend", "product review",
        "user experience", "landing page", "界面", "交互", "用户体验", "工作台", "仪表盘",
    }
    return _has_any(text, exact_terms)


def _mentions_nuwa_skill_synthesis(text: str) -> bool:
    creation_terms = {
        "create", "make", "build", "generate", "update", "refresh",
        "造", "蒸馏", "更新", "生成", "创建",
        "é€ ", "è’¸é¦", "æ›´æ–°", "ç”Ÿæˆ", "åˆ›å»º",
        "é€ skill", "é€  skill", "é€ äºº", "skill synthesis",
    }
    context_terms = {"nuwa", "女娲", "perspective", "人物skill", "人物 skill", "å¥³å¨²", "äººç‰©skill", "äººç‰© skill"}
    return _has_any(text, creation_terms) and _has_any(text, context_terms)


def _normalize_pack(pack: dict) -> dict:
    required = ["name", "domains", "terms", "query_terms", "use_for"]
    missing = [key for key in required if key not in pack]
    if missing:
        raise ValueError(f"Knowledge pack missing keys {missing}: {pack}")
    return {
        "name": str(pack["name"]),
        "domains": set(str(item).lower() for item in pack["domains"]),
        "terms": set(str(item).lower() for item in pack["terms"]),
        "query_terms": str(pack["query_terms"]),
        "use_for": str(pack["use_for"]),
    }


def _read_simple_yaml(path: Path) -> dict:
    data: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            if current_key is None:
                raise ValueError(f"List item without key in {path}: {line}")
            data.setdefault(current_key, [])
            assert isinstance(data[current_key], list)
            data[current_key].append(stripped[2:].strip())
            continue
        if ":" not in stripped:
            raise ValueError(f"Unsupported YAML line in {path}: {line}")
        key, value = stripped.split(":", 1)
        current_key = key.strip()
        value = value.strip()
        if value == "[]":
            data[current_key] = []
        elif value:
            data[current_key] = value
            current_key = None
        else:
            data[current_key] = []
    return data


PACKS: list[dict] = load_packs()
