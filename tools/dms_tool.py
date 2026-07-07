from __future__ import annotations

from tools import baseline_registry


ARCHITECTURE_TERMS = {
    "codex-brain", "codex brain", "local ai brain", "ai brain", "architecture",
    "langgraph", "langchain", "workflow", "orchestration", "agent graph",
    "本地ai大脑", "本地 ai 大脑", "ai大脑", "架构", "系统设计", "编排",
    "æœ¬åœ°aiå¤§è„‘", "æœ¬åœ° ai å¤§è„‘", "aiå¤§è„‘", "æž¶æž„", "ç³»ç»Ÿè®¾è®¡", "ç¼–æŽ’",
}
MEMORY_TERMS = {
    "cds", "memory", "rag", "retrieval", "ranking", "feedback", "domain", "scope",
    "记忆库", "长期记忆", "检索", "排序", "反馈", "评价", "去重", "召回",
    "è®°å¿†åº“", "é•¿æœŸè®°å¿†", "æ£€ç´¢", "æŽ’åº", "åé¦ˆ", "è¯„ä»·", "åŽ»é‡", "å¬å›ž",
}
WORKFLOW_TERMS = {
    "dms", "supervisor", "247", "automation", "thread", "worker", "lifecycle",
    "自动化", "线程", "任务管理", "生命周期", "监督", "加载dms",
    "è‡ªåŠ¨åŒ–", "çº¿ç¨‹", "ä»»åŠ¡ç®¡ç†", "ç”Ÿå‘½å‘¨æœŸ", "ç›‘ç£", "åŠ è½½dms",
}
VISION_TERMS = {
    "hamer", "vitpose", "bbox", "keypoint", "d435i", "camera", "hand tracking",
    "识别", "视觉", "手势框", "检测框", "摄像头", "标注",
    "è¯†åˆ«", "è§†è§‰", "æ‰‹åŠ¿æ¡†", "æ£€æµ‹æ¡†", "æ‘„åƒå¤´", "æ ‡æ³¨",
}
UNITY_TERMS = {
    "unity", "imu", "tactile", "serial", "com port", "com4", "palm", "0x0a", "onlytip", "2.2", "stable baseline",
    "触觉", "串口", "手套", "手掌", "手腕", "映射",
    "è§¦è§‰", "ä¸²å£", "æ‰‹å¥—", "æ‰‹æŽŒ", "æ‰‹è…•", "æ˜ å°„",
}
FUSION_TERMS = {
    "ekf", "openvins", "fusion", "kalman", "vio", "factor graph",
    "滤波", "融合", "协方差", "门控", "互补滤波",
    "æ»¤æ³¢", "èžåˆ", "åæ–¹å·®", "é—¨æŽ§", "äº’è¡¥æ»¤æ³¢",
}
COURSE_TERMS = {
    "spml", "ntu", "course", "ee6", "ee7", "exam", "timetable",
    "课程", "考试", "选课", "南洋理工", "硕士",
    "è¯¾ç¨‹", "è€ƒè¯•", "é€‰è¯¾", "å—æ´‹ç†å·¥", "ç¡•å£«",
}
RUNTIME_TERMS = {
    "fps", "latency", "gpu", "pipeline", "realtime", "real-time",
    "503", "provider", "channel", "deepseek", "allrealai", "api", "service unavailable",
    "实时", "迟钝", "很慢", "延迟", "性能", "速度",
    "å®žæ—¶", "è¿Ÿé’", "å¾ˆæ…¢", "å»¶è¿Ÿ", "æ€§èƒ½", "é€Ÿåº¦",
}
RELATIONSHIP_TERMS = {
    "relationship", "girlfriend", "dating", "boundary", "consent", "game theory",
    "reciprocity", "signal ledger", "女朋友", "恋爱", "关系", "边界", "博弈论",
    "reciprocity", "signal ledger", "å¥³æœ‹å‹", "æ‹çˆ±", "å…³ç³»", "è¾¹ç•Œ", "åšå¼ˆè®º",
}
PROVIDER_TERMS = {
    "503", "provider", "channel", "deepseek", "allrealai", "api", "service unavailable",
    "no available channel", "model_provider", "base_url", "openai_api_key",
}
SKILL_SYNTHESIS_ACTION_TERMS = {
    "create", "make", "build", "generate", "update", "refresh",
    "造", "更新", "创建", "生成", "造skill", "造 skill", "造人", "蒸馏", "更新skill", "更新 skill",
    "é€ ", "æ›´æ–°", "é€ skill", "é€  skill", "é€ äºº", "è’¸é¦", "æ›´æ–°skill", "æ›´æ–° skill",
    "skill synthesis",
}
SKILL_SYNTHESIS_CONTEXT_TERMS = {
    "nuwa", "女娲", "perspective", "人物skill", "人物 skill",
    "思维框架", "思维方式",
    "nuwa", "å¥³å¨²", "perspective", "äººç‰©skill", "äººç‰© skill",
    "æ€ç»´æ¡†æž¶", "æ€ç»´æ–¹å¼",
}
LEARNING_TERMS = {
    "feynman", "learning", "study", "interview", "explain", "费曼", "学习", "面试", "解释", "复习",
    "feynman", "learning", "study", "interview", "explain", "è´¹æ›¼", "å­¦ä¹ ", "é¢è¯•", "è§£é‡Š", "å¤ä¹ ",
}
CAREER_TERMS = {
    "career", "salary", "million", "portfolio", "百万年薪", "职业", "年薪", "简历", "求职",
    "career", "salary", "million", "portfolio", "ç™¾ä¸‡å¹´è–ª", "èŒä¸š", "å¹´è–ª", "ç®€åŽ†", "æ±‚èŒ",
}
RISK_TERMS = {
    "risk", "reversible", "opportunity cost", "audit", "downside", "风险", "可逆", "机会成本", "审计",
    "risk", "reversible", "opportunity cost", "audit", "downside", "é£Žé™©", "å¯é€†", "æœºä¼šæˆæœ¬", "å®¡è®¡",
}
PRODUCT_TERMS = {
    "ui", "ux", "dashboard", "interface", "product review", "user experience", "界面", "仪表盘", "用户体验", "交互",
    "ui", "ux", "dashboard", "interface", "product review", "user experience", "ç•Œé¢", "ä»ªè¡¨ç›˜", "ç”¨æˆ·ä½“éªŒ", "äº¤äº’",
}
MEDIA_TRANSCRIPTION_TERMS = {
    "douyin", "tiktok", "youtube", "yt-dlp", "ytdlp", "whisper", "faster-whisper",
    "ffmpeg", "subtitle", "subtitles", "transcript", "transcription", "asr",
    "cookies.txt", "cookies-from-browser", "audio extraction", "video download",
    "srt", "vtt", "抖音", "字幕", "音频", "转写", "文字稿", "提取音频", "提取字幕",
    "srt", "vtt", "æŠ–éŸ³", "å­—å¹•", "éŸ³é¢‘", "è½¬å†™", "æ–‡å­—ç¨¿", "æå–éŸ³é¢‘", "æå–å­—å¹•",
}


def classify(task: str, project: str = "") -> dict:
    text = task.lower()
    matches: list[str] = []

    if _has(text, ARCHITECTURE_TERMS):
        matches.append("architecture")
    if _has(text, MEMORY_TERMS):
        matches.append("memory-quality" if "architecture" in matches else "rag")
    if _has(text, WORKFLOW_TERMS):
        matches.append("workflow")
    if _has(text, VISION_TERMS):
        matches.append("vision")
    if _has(text, UNITY_TERMS):
        matches.append("unity-hardware")
    if _has(text, FUSION_TERMS):
        matches.append("fusion")
    if _has(text, COURSE_TERMS):
        matches.append("planning")
    if _has(text, RUNTIME_TERMS):
        matches.append("runtime")
    if _has(text, PROVIDER_TERMS):
        matches.append("provider-routing")
    if _has(text, RELATIONSHIP_TERMS):
        matches.append("relationship")
    if _has_skill_synthesis_intent(text):
        matches.append("skill-synthesis")
    if _has(text, LEARNING_TERMS):
        matches.append("learning")
    if _has(text, CAREER_TERMS):
        matches.append("career")
    if _has(text, RISK_TERMS):
        matches.append("risk")
    if _has(text, PRODUCT_TERMS):
        matches.append("product")
    if _has(text, MEDIA_TRANSCRIPTION_TERMS):
        matches.append("media-transcription")

    domain = _choose_domain(matches)
    risk = _risk(text)
    protected = _protected_baselines(text)
    for baseline in baseline_registry.matching_baselines(task):
        entry = f"{baseline.get('name', baseline.get('id', 'baseline'))}: {baseline.get('path', '')}"
        if entry not in protected:
            protected.append(entry)

    return {
        "domain": domain,
        "risk": risk,
        "project": project,
        "protected_baselines": protected,
        "matched_domains": matches,
    }


def is_meta_domain(route: dict) -> bool:
    domains = {route.get("domain", "")}
    domains.update(route.get("matched_domains", []))
    return bool(domains & {"architecture", "memory-quality", "rag", "workflow"})


def _choose_domain(matches: list[str]) -> str:
    if not matches:
        return "general"
    priority = [
        "architecture",
        "memory-quality",
        "rag",
        "workflow",
        "vision",
        "unity-hardware",
        "fusion",
        "provider-routing",
        "media-transcription",
        "runtime",
        "planning",
        "relationship",
        "skill-synthesis",
        "learning",
        "career",
        "risk",
        "product",
    ]
    ordered = [name for name in priority if name in matches]
    if len(ordered) == 1:
        return ordered[0]
    if ordered[:2] == ["architecture", "memory-quality"]:
        return "architecture+memory-quality"
    return "+".join(ordered[:3])


def _risk(text: str) -> str:
    risk = "inspect"
    if any(word in text for word in ["修改", "fix", "改代码", "实现", "执行", "安装", "部署到本地", "ä¿®æ”¹", "æ”¹ä»£ç ", "å®žçŽ°", "æ‰§è¡Œ", "å®‰è£…", "éƒ¨ç½²åˆ°æœ¬åœ°"]):
        risk = "modify"
    if any(word in text for word in ["unity play", "硬件", "真实", "发送", "push", "deploy", "commit", "删除", "ç¡¬ä»¶", "çœŸå®ž", "å‘é€", "åˆ é™¤"]):
        risk = "level1-boundary"
    return risk


def _protected_baselines(text: str) -> list[str]:
    protected = []
    if "2.2" in text:
        protected.append("<PROJECT_C_ONLYTIP_2_2>")
    if "v4" in text:
        protected.append("HaMeR V4 stable variants")
    if "onlytip" in text and ("稳定" in text or "ç¨³å®š" in text):
        protected.append("User-tested onlytip stable version")
    return protected


def _has(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _has_skill_synthesis_intent(text: str) -> bool:
    if _has(text, SKILL_SYNTHESIS_ACTION_TERMS) and _has(text, SKILL_SYNTHESIS_CONTEXT_TERMS):
        return True
    if "skill synthesis" in text:
        return True
    return False
