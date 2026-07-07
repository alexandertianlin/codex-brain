from __future__ import annotations


META_DOMAINS = {"architecture", "memory-quality", "rag", "workflow"}

LENS_BY_KEYWORD = [
    ("Machine Vision", {"bbox", "keypoint", "hamer", "vitpose", "recognition", "vision", "crop", "识别", "视觉", "手势框", "检测框"}),
    ("Video Analysis", {"jitter", "tracking", "bbox", "video", "frame", "抖动", "候选", "视频"}),
    ("Advanced DSP", {"smooth", "filter", "ema", "lag", "jitter", "滤波", "平滑", "延迟"}),
    ("Statistical Signal Processing", {"ekf", "kalman", "openvins", "gating", "fusion", "covariance", "融合", "协方差"}),
    ("Real-Time DSP", {"latency", "fps", "gpu", "pipeline", "realtime", "real-time", "实时", "迟钝", "很慢"}),
    ("Deep Learning", {"domain", "training", "fine-tune", "model", "深度学习", "模型", "黑手套"}),
    ("Robotics & Intelligent Sensors", {"imu", "tactile", "serial", "com port", "com4", "palm", "触觉", "手套", "传感器"}),
    ("Ensemble ML Quality Gate", {"quality", "gate", "anomaly", "confidence", "置信度", "异常"}),
]


def select_lenses(task: str, route: dict | None = None) -> list[str]:
    route = route or {}
    route_domains = set(str(route.get("domain", "")).split("+"))
    route_domains.update(route.get("matched_domains", []))
    text = task.lower()

    if "relationship" in route_domains:
        return []
    if "media-transcription" in route_domains:
        return []
    if route_domains & META_DOMAINS and not _mentions_project_system(text):
        return []
    if route_domains & META_DOMAINS and not _mentions_concrete_spml_context(text):
        return []

    selected = []
    for name, terms in LENS_BY_KEYWORD:
        if any(term in text for term in terms):
            selected.append(name)

    if not selected and _mentions_project_system(text):
        selected.append("SPML Course Catalog")
    return selected[:5]


def query_for_lenses(task: str, lenses: list[str]) -> str:
    return " ".join(["NTU SPML", task, *lenses])


def _mentions_project_system(text: str) -> bool:
    project_terms = {
        "onlytip", "hamer", "vitpose", "unity", "imu", "tactile", "d435i",
        "openvins", "bbox", "camera", "手套", "视觉", "触觉", "融合", "课程", "spml",
    }
    return any(term in text for term in project_terms)


def _mentions_concrete_spml_context(text: str) -> bool:
    concrete_terms = {
        "onlytip", "project c", "hamer", "vitpose", "unity", "imu", "tactile",
        "d435i", "openvins", "bbox", "camera", "course", "exam", "ee6", "ee7",
        "课程", "选课", "考试", "手套", "视觉", "触觉", "融合", "传感器", "回放",
    }
    return any(term in text for term in concrete_terms)
