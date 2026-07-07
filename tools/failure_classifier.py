from __future__ import annotations


FAILURE_TYPES = [
    {
        "type": "vision-detector-bbox",
        "terms": ["bbox", "box", "框", "检测框", "手势框", "裁掉", "指尖", "太小"],
        "next": "Run offline annotated-image or recorded benchmark before live tuning; check fingertip coverage and bbox jump.",
    },
    {
        "type": "vision-latency",
        "terms": ["slow", "lag", "latency", "fps", "迟钝", "很慢", "延迟"],
        "next": "Measure loop_ms p50/p95, frame age, model time, queue depth, and UDP/Unity receive delay.",
    },
    {
        "type": "unity-mapping",
        "terms": ["mapping", "映射", "触觉", "imu", "小拇指", "大拇指", "食指", "无名指"],
        "next": "Verify SerialReceiver device IDs, IMU mapping, tactile mapping, and stable onlytip 2.2 interface before algorithm changes.",
    },
    {
        "type": "hardware-signal-missing",
        "terms": ["0x0a", "palm", "手掌", "没信号", "收不到", "com", "串口"],
        "next": "Use logs to distinguish Unity filtering from hardware/H7 output missing; do not assume algorithm failure.",
    },
    {
        "type": "fusion-filtering",
        "terms": ["ekf", "openvins", "fusion", "滤波", "融合", "漂移", "bias"],
        "next": "Check prediction/update separation, residual gating, covariance, delayed vision timestamp alignment, and fallback behavior.",
    },
    {
        "type": "dependency-install",
        "terms": ["install", "安装", "detectron2", "cuda", "torch", "依赖"],
        "next": "Check environment isolation, Python/Torch/CUDA compatibility, and run offline import tests before live scripts.",
    },
    {
        "type": "provider-channel",
        "terms": ["503", "service unavailable", "deepseek", "allrealai", "provider", "channel", "api"],
        "next": "Run provider health check and treat upstream channel outage separately from local code failures.",
    },
]


def classify_failure(task: str) -> list[dict]:
    text = task.lower()
    matches = []
    for item in FAILURE_TYPES:
        hit_terms = [term for term in item["terms"] if term.lower() in text]
        if hit_terms:
            matches.append({"type": item["type"], "matched_terms": hit_terms, "next": item["next"]})
    return matches
