from __future__ import annotations

from typing import TypedDict

from tools import baseline_registry, cds_tool, dms_tool, failure_classifier, knowledge_router, spml_tool


META_DOMAINS = {"architecture", "memory-quality", "rag", "workflow"}


class BrainState(TypedDict, total=False):
    task: str
    project: str
    write_feedback: bool
    route: dict
    spml_lenses: list[str]
    knowledge_packs: list[dict]
    task_profile: dict
    hard_constraints: list[str]
    failure_types: list[dict]
    query: str
    memories: list[dict]
    used_memory_ids: list[int]
    noise_memory_ids: list[int]
    plan: list[str]
    verification: list[str]
    evaluation: dict
    memory_update_plan: dict
    memory_update_result: dict
    feedback: str


def run_task_graph(task: str, project: str = "", write_feedback: bool = True) -> dict:
    try:
        return run_langgraph(task, project=project, write_feedback=write_feedback)
    except Exception as exc:
        result = run_fallback_graph(task, project=project, write_feedback=write_feedback)
        result["graph_warning"] = f"LangGraph fallback used: {exc}"
        return result


def run_langgraph(task: str, project: str = "", write_feedback: bool = True) -> dict:
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(BrainState)
    graph.add_node("classify", node_classify)
    graph.add_node("select_spml", node_select_spml)
    graph.add_node("select_knowledge", node_select_knowledge)
    graph.add_node("profile", node_profile)
    graph.add_node("retrieve", node_retrieve)
    graph.add_node("plan", node_plan)
    graph.add_node("verify", node_verify)
    graph.add_node("evaluate", node_evaluate)
    graph.add_node("memory_update_plan", node_memory_update_plan)
    graph.add_node("apply_memory_updates", node_apply_memory_updates)
    graph.add_node("feedback", node_feedback)

    graph.add_edge(START, "classify")
    graph.add_edge("classify", "select_spml")
    graph.add_edge("select_spml", "select_knowledge")
    graph.add_edge("select_knowledge", "profile")
    graph.add_edge("profile", "retrieve")
    graph.add_edge("retrieve", "plan")
    graph.add_edge("plan", "verify")
    graph.add_edge("verify", "evaluate")
    graph.add_edge("evaluate", "memory_update_plan")
    graph.add_edge("memory_update_plan", "apply_memory_updates")
    graph.add_edge("apply_memory_updates", "feedback")
    graph.add_edge("feedback", END)

    app = graph.compile()
    return app.invoke({"task": task, "project": project, "write_feedback": write_feedback})


def run_fallback_graph(task: str, project: str = "", write_feedback: bool = True) -> dict:
    route = dms_tool.classify(task, project=project)
    lenses = spml_tool.select_lenses(task, route=route)
    packs = knowledge_router.select_packs(task, route=route, spml_lenses=lenses)
    profile = build_task_profile(task, route, lenses, packs)
    hard_constraints = build_hard_constraints(task, route, profile)
    failure_types = failure_classifier.classify_failure(task)
    query = build_query(task, route, lenses, packs)
    memories, _raw = cds_tool.retrieve(query, limit=32)
    memories = rerank_memories(memories, packs, route, profile)[:8]
    used = choose_used(memories, lenses, route, packs, profile)
    noise = choose_noise(memories, used, route, packs, profile)
    plan = make_plan(task, route, lenses, memories, packs, profile)
    verification = make_verification(route, lenses, packs, profile)
    evaluation = evaluate_run(route, packs, profile, memories, used, noise, plan, verification)
    update_plan = plan_memory_updates(query, memories, used, noise, evaluation, route, packs, profile)
    update_result = {}
    if write_feedback:
        update_result = cds_tool.apply_memory_update_plan(update_plan)
    feedback = ""
    if write_feedback and memories:
        feedback = cds_tool.write_feedback(
            query=query,
            returned=[m.id for m in memories],
            used=used,
            noise=noise,
            note=feedback_note(route, packs, profile),
        ).strip()
    return {
        "task": task,
        "route": route,
        "spml_lenses": lenses,
        "knowledge_packs": packs,
        "task_profile": profile,
        "hard_constraints": hard_constraints,
        "failure_types": failure_types,
        "query": query,
        "memories": [m.__dict__ for m in memories],
        "used_memory_ids": used,
        "noise_memory_ids": noise,
        "plan": plan,
        "verification": verification,
        "evaluation": evaluation,
        "memory_update_plan": update_plan,
        "memory_update_result": update_result,
        "feedback": feedback,
    }


def node_classify(state: BrainState) -> BrainState:
    return {"route": dms_tool.classify(state["task"], project=state.get("project", ""))}


def node_select_spml(state: BrainState) -> BrainState:
    return {"spml_lenses": spml_tool.select_lenses(state["task"], route=state.get("route", {}))}


def node_select_knowledge(state: BrainState) -> BrainState:
    return {
        "knowledge_packs": knowledge_router.select_packs(
            state["task"],
            route=state.get("route", {}),
            spml_lenses=state.get("spml_lenses", []),
        )
    }


def node_profile(state: BrainState) -> BrainState:
    profile = build_task_profile(
        state["task"],
        state.get("route", {}),
        state.get("spml_lenses", []),
        state.get("knowledge_packs", []),
    )
    return {
        "task_profile": profile,
        "hard_constraints": build_hard_constraints(state["task"], state.get("route", {}), profile),
        "failure_types": failure_classifier.classify_failure(state["task"]),
    }


def node_retrieve(state: BrainState) -> BrainState:
    query = build_query(
        state["task"],
        state["route"],
        state["spml_lenses"],
        state.get("knowledge_packs", []),
    )
    memories, _raw = cds_tool.retrieve(query, limit=32)
    memories = rerank_memories(memories, state.get("knowledge_packs", []), state["route"], state.get("task_profile", {}))[:8]
    used = choose_used(memories, state["spml_lenses"], state["route"], state.get("knowledge_packs", []), state.get("task_profile", {}))
    noise = choose_noise(memories, used, state["route"], state.get("knowledge_packs", []), state.get("task_profile", {}))
    return {
        "query": query,
        "memories": [m.__dict__ for m in memories],
        "used_memory_ids": used,
        "noise_memory_ids": noise,
    }


def node_plan(state: BrainState) -> BrainState:
    memories = [cds_tool.Memory(**m) for m in state.get("memories", [])]
    return {
        "plan": make_plan(
            state["task"],
            state["route"],
            state["spml_lenses"],
            memories,
            state.get("knowledge_packs", []),
            state.get("task_profile", {}),
        )
    }


def node_verify(state: BrainState) -> BrainState:
    return {
        "verification": make_verification(
            state["route"],
            state["spml_lenses"],
            state.get("knowledge_packs", []),
            state.get("task_profile", {}),
        )
    }


def node_evaluate(state: BrainState) -> BrainState:
    memories = [cds_tool.Memory(**m) for m in state.get("memories", [])]
    return {
        "evaluation": evaluate_run(
            state.get("route", {}),
            state.get("knowledge_packs", []),
            state.get("task_profile", {}),
            memories,
            state.get("used_memory_ids", []),
            state.get("noise_memory_ids", []),
            state.get("plan", []),
            state.get("verification", []),
        )
    }


def node_memory_update_plan(state: BrainState) -> BrainState:
    memories = [cds_tool.Memory(**m) for m in state.get("memories", [])]
    return {
        "memory_update_plan": plan_memory_updates(
            state.get("query", ""),
            memories,
            state.get("used_memory_ids", []),
            state.get("noise_memory_ids", []),
            state.get("evaluation", {}),
            state.get("route", {}),
            state.get("knowledge_packs", []),
            state.get("task_profile", {}),
        )
    }


def node_apply_memory_updates(state: BrainState) -> BrainState:
    if not state.get("write_feedback", True):
        return {"memory_update_result": {"status": "skipped", "reason": "write_feedback is disabled"}}
    return {"memory_update_result": cds_tool.apply_memory_update_plan(state.get("memory_update_plan", {}))}


def node_feedback(state: BrainState) -> BrainState:
    if not state.get("write_feedback", True) or not state.get("memories"):
        return {"feedback": ""}
    output = cds_tool.write_feedback(
        query=state["query"],
        returned=[m["id"] for m in state["memories"]],
        used=state.get("used_memory_ids", []),
        noise=state.get("noise_memory_ids", []),
        note=feedback_note(state.get("route", {}), state.get("knowledge_packs", []), state.get("task_profile", {})),
    )
    return {"feedback": output.strip()}


def build_query(task: str, route: dict, lenses: list[str], packs: list[dict] | None = None) -> str:
    packs = packs or []
    route_domain = route.get("domain", "general")
    meta_domains = set(str(route_domain).split("+")) | set(route.get("matched_domains", []))
    pack_terms = knowledge_router.query_terms(packs)
    if "skill-synthesis" in meta_domains:
        return " ".join(
            [
                task,
                route_domain,
                "Nuwa skill synthesis perspective thinking framework skill creation update quality check",
                "codex-brain LangGraph LangChain DMS CDS architecture memory-quality RAG retrieval feedback routing",
                *pack_terms,
                "DMS CDS",
            ]
        )
    if meta_domains & META_DOMAINS:
        return " ".join(
            [
                task,
                route_domain,
                "codex-brain LangGraph LangChain DMS CDS architecture memory-quality RAG retrieval feedback routing domain scope task-profile evaluator",
                *pack_terms,
            ]
        )
    if "vision" in meta_domains:
        return " ".join(
            [
                task,
                route_domain,
                *lenses,
                "HaMeR ViTPose D435i visual gesture recognition failure-taxonomy benchmark bbox keypoints latency jitter baseline v9.7",
                "DMS CDS onlytip SPML",
                *pack_terms,
            ]
        )
    if "unity-hardware" in meta_domains:
        return " ".join(
            [
                task,
                route_domain,
                *lenses,
                "Unity SerialReceiver HandMotionManager COM port IMU tactile finger mapping palm 0x0A device IDs calibration onlytip 2.2 stable baseline",
                "DMS CDS onlytip unity-hardware",
            ]
        )
    if "fusion" in meta_domains:
        return " ".join(
            [
                "OpenVINS-style EKF adapter",
                "2.8 delayed vision bias",
                "fusion complementary filter covariance gating",
                route_domain,
                *lenses,
            ]
        )
    if "provider-routing" in meta_domains:
        return " ".join(
            [
                task,
                route_domain,
                "AllRealAI deepseek-chat 503 provider channel unavailable model_provider base_url config",
                *pack_terms,
                "DMS CDS",
            ]
        )
    if "media-transcription" in meta_domains:
        return " ".join(
            [
                task,
                route_domain,
                "Douyin TikTok yt-dlp cookies ffmpeg faster-whisper ASR subtitle transcript local video fallback media-transcription",
                *pack_terms,
                "DMS CDS",
            ]
        )
    return " ".join([task, route_domain, *lenses, *pack_terms, "DMS CDS"])


def build_task_profile(task: str, route: dict, lenses: list[str], packs: list[dict]) -> dict:
    domains = {route.get("domain", "")}
    domains.update(route.get("matched_domains", []))
    domains.discard("")
    objective = "inspect"
    if route.get("risk") == "modify":
        objective = "modify-and-verify"
    if "skill-synthesis" in domains:
        objective = "route-nuwa-skill-synthesis"
    elif dms_tool.is_meta_domain(route):
        objective = "improve-brain-routing-memory-quality"
    elif "vision" in domains:
        objective = "diagnose-visual-recognition-before-live-tuning"
    elif "unity-hardware" in domains:
        objective = "diagnose-unity-hardware-mapping-before-algorithm-changes"
    elif "fusion" in domains:
        objective = "evaluate-sensor-fusion-with-evidence"
    elif "media-transcription" in domains:
        objective = "extract-media-subtitle-or-asr-transcript"

    risk_gates = ["Do not read, print, copy, or store MANO_RIGHT.pkl contents."]
    if route.get("protected_baselines"):
        risk_gates.append("Protect baselines: " + "; ".join(route["protected_baselines"]))
    if route.get("risk") == "level1-boundary":
        risk_gates.append("Pause for explicit approval before Level 1 actions.")
    if dms_tool.is_meta_domain(route):
        risk_gates.append("Architecture/RAG tasks should not be dominated by project-specific HaMeR/SPML memories.")
    if "vision" in domains:
        risk_gates.append("Use offline image or recorded benchmark evidence before live-camera tuning.")
    if "skill-synthesis" in domains:
        risk_gates.append("Use Nuwa for routing and quality gates, but keep full skill creation in the external Nuwa skill directory.")
    matching_baselines = baseline_registry.matching_baselines(task)
    for baseline in matching_baselines:
        risk_gates.append(f"Protected baseline {baseline.get('id')}: {baseline.get('protect')}")

    success_metrics = ["Run report includes route, selected packs, retrieved memories, plan, verification, and feedback."]
    if dms_tool.is_meta_domain(route):
        success_metrics.extend(
            [
                "Architecture queries rank codex-brain/CDS memories above unrelated project memories.",
                "Noise memories are explicitly marked in CDS feedback.",
            ]
        )
    if "vision" in domains:
        success_metrics.append("Vision tasks name detect_rate, bbox jump, fingertip jitter, and latency p50/p95.")
    if "skill-synthesis" in domains:
        success_metrics.append("Nuwa tasks identify direct-vs-diagnostic path and whether a new skill/update is required.")
    if "provider-routing" in domains:
        success_metrics.append("Provider tasks separate upstream routing/channel failures from local project code failures.")
    if "media-transcription" in domains:
        risk_gates.append("Keep media transcription isolated from onlytip/Unity unless the task explicitly mentions that project.")
        success_metrics.extend(
            [
                "URL mode either downloads media/subtitles or reports cookies/browser-blocking clearly.",
                "Local video fallback produces transcript TXT/SRT/JSON when media is available.",
                "Outputs stay in a dedicated media tool folder, not inside onlytip/Unity projects.",
            ]
        )

    return {
        "objective": objective,
        "domains": sorted(domains),
        "selected_pack_names": knowledge_router.names(packs),
        "risk_gates": risk_gates,
        "success_metrics": success_metrics,
        "lenses": lenses,
        "protected_baselines": matching_baselines,
    }


def build_hard_constraints(task: str, route: dict, profile: dict) -> list[str]:
    constraints = [
        "Evidence first: retrieve CDS and inspect local files before changing code.",
        "Never read, print, copy, or store MANO_RIGHT.pkl contents.",
    ]
    if route.get("risk") == "level1-boundary":
        constraints.append("Pause before Level 1 actions: hardware writes, Unity Play validation, real sends, commit/push/deploy, destructive deletes.")
    if route.get("protected_baselines"):
        constraints.append("Protect baselines: " + "; ".join(route.get("protected_baselines", [])))
    domains = set(profile.get("domains", []))
    if "vision" in domains:
        constraints.append("Use offline benchmark or annotated image evidence before live camera tuning.")
    if "architecture" in domains or "memory-quality" in domains:
        constraints.append("Do not let project-specific onlytip/SPML memories dominate pure codex-brain architecture tasks.")
    if "provider-routing" in domains:
        constraints.append("Do not expose API keys; inspect provider/model/base_url names only.")
    if "media-transcription" in domains:
        constraints.append("Keep media extraction tools isolated from onlytip/Unity project folders.")
    return constraints


def choose_used(memories: list[cds_tool.Memory], lenses: list[str], route: dict | None = None, packs: list[dict] | None = None, profile: dict | None = None) -> list[int]:
    used: list[int] = []
    route = route or {}
    packs = packs or []
    profile = profile or {}
    pack_text = " ".join(knowledge_router.names(packs)).lower()
    if dms_tool.is_meta_domain(route):
        for memory in memories:
            haystack = memory_haystack(memory)
            if _score_memory(memory, route, packs, profile) > 0 and any(term in haystack for term in ["codex-brain", "codex brain", "cds", "dms", "langgraph", "langchain", "memory-quality", "retrieval-feedback"]):
                used.append(memory.id)
        return used[:5] or [m.id for m in memories[:3]]
    if "relationship" in pack_text:
        for memory in memories:
            haystack = memory_haystack(memory)
            if any(term in haystack for term in ["relationship", "boundary", "consent", "game theory", "signal ledger"]):
                used.append(memory.id)
        if used:
            return used[:5]
    scored = [memory.id for memory in memories if _score_memory(memory, route, packs, profile) > 0]
    if scored:
        return scored[:5]
    lens_text = " ".join(lenses).lower()
    for memory in memories:
        haystack = memory_haystack(memory)
        if any(part.lower() in haystack for part in lenses) or ("spml" in haystack and any(x in lens_text for x in ["vision", "dsp", "statistical", "robotics"])):
            used.append(memory.id)
    return used[:5] or [m.id for m in memories[:3]]


def choose_noise(memories: list[cds_tool.Memory], used: list[int], route: dict, packs: list[dict], profile: dict | None = None) -> list[int]:
    noise: list[int] = []
    for memory in memories:
        if memory.id in used:
            continue
        if _score_memory(memory, route, packs, profile or {}) < 0:
            noise.append(memory.id)
    for memory in memories:
        if len(noise) >= 3:
            break
        if memory.id not in used and memory.id not in noise:
            noise.append(memory.id)
    return noise[:3]


def rerank_memories(memories: list[cds_tool.Memory], packs: list[dict], route: dict, profile: dict | None = None) -> list[cds_tool.Memory]:
    if not memories:
        return memories
    if not (dms_tool.is_meta_domain(route) or packs):
        return memories
    return sorted(memories, key=lambda memory: _score_memory(memory, route, packs, profile or {}), reverse=True)


def _score_memory(memory: cds_tool.Memory, route: dict, packs: list[dict], profile: dict) -> int:
    pack_text = " ".join(knowledge_router.names(packs)).lower()
    haystack = memory_haystack(memory)
    value = 0
    if dms_tool.is_meta_domain(route):
        keywords = [
            "codex-brain", "codex brain", "cds", "dms", "langgraph", "langchain",
            "memory-quality", "memory quality", "retrieval-feedback", "retrieval feedback",
            "memory priority", "feedback table", "routing", "knowledge router",
        ]
        demote = [
            "hamer", "vitpose", "bbox", "d435i", "v9.", "unity imu",
            "serialreceiver", "handmotionmanager", "palm", "0x0a", "glove",
            "tactile", "provider channel", "deepseek", "allrealai", "api key",
            "onlytip", "onlytip-2.3",
        ]
        value += sum(12 for term in keywords if term in haystack)
        value -= sum(14 for term in demote if term in haystack)
    elif "nuwa skill synthesis" in pack_text:
        keywords = ["nuwa", "女娲", "skill", "perspective", "thinking framework", "思维框架", "蒸馏"]
        demote = ["hamer", "vitpose", "bbox", "unity", "spml", "provider channel"]
        value += sum(10 for term in keywords if term in haystack)
        value -= sum(8 for term in demote if term in haystack)
    elif "relationship" in pack_text:
        keywords = ["relationship", "boundary", "consent", "signal ledger", "game theory"]
        demote = ["hamer", "vitpose", "bbox", "d435i", "unity", "spml"]
        value += sum(10 for term in keywords if term in haystack)
        value -= sum(8 for term in demote if term in haystack)
    elif "career" in pack_text or "learning" in pack_text:
        keywords = ["career", "planning", "learning", "interview", "spml", "course"]
        demote = ["hamer", "bbox", "jitter"]
        value += sum(10 for term in keywords if term in haystack)
        value -= sum(8 for term in demote if term in haystack)
    elif "provider health check" in pack_text:
        keywords = ["provider", "allrealai", "deepseek", "503", "model_provider", "base_url", "api", "channel unavailable"]
        demote = ["hamer", "vitpose", "bbox", "unity", "spml", "glove"]
        value += sum(12 for term in keywords if term in haystack)
        value -= sum(8 for term in demote if term in haystack)
    elif "media transcription pipeline" in pack_text:
        keywords = [
            "douyin", "tiktok", "youtube", "yt-dlp", "ytdlp", "whisper",
            "faster-whisper", "ffmpeg", "subtitle", "transcript",
            "transcription", "asr", "cookies", "srt", "vtt",
            "media-transcription",
        ]
        demote = ["hamer", "vitpose", "bbox", "d435i", "unity", "imu", "spml", "glove", "onlytip"]
        value += sum(12 for term in keywords if term in haystack)
        value -= sum(10 for term in demote if term in haystack)
    elif "ntu spml project knowledge" in pack_text:
        domains = set(profile.get("domains", []))
        if "unity-hardware" in domains:
            keywords = ["unity", "serialreceiver", "handmotionmanager", "imu", "tactile", "com", "mapping", "palm", "0x0a", "2.2", "finger"]
            demote = ["hamer", "vitpose", "bbox", "d435i", "v9."]
        elif "vision" in domains:
            keywords = ["hamer", "vitpose", "bbox", "d435i", "keypoint", "jitter", "latency", "vision"]
            demote = ["serialreceiver", "tactile", "0x0a"]
        elif "fusion" in domains:
            keywords = ["openvins", "ekf", "fusion", "imu", "vision", "covariance", "gating", "delayed bias"]
            demote = ["course", "relationship"]
        else:
            keywords = ["spml", "onlytip", "hamer", "vitpose", "unity", "imu", "fusion", "bbox", "d435i"]
            demote = []
        value += sum(8 for term in keywords if term in haystack)
        value -= sum(8 for term in demote if term in haystack)
    for domain in profile.get("domains", []):
        if domain and domain in haystack:
            value += 3
    if "audit" in haystack or "no-retrieve" in haystack:
        value -= 20
    return value


def memory_haystack(memory: cds_tool.Memory) -> str:
    return f"{memory.title} {memory.project} {memory.tags} {memory.text}".lower()


def make_plan(task: str, route: dict, lenses: list[str], memories: list[cds_tool.Memory], packs: list[dict] | None = None, profile: dict | None = None) -> list[str]:
    packs = packs or []
    profile = profile or {}
    steps = ["Read the retrieved CDS memories before changing files."]
    pack_names = knowledge_router.names(packs)
    if pack_names:
        steps.append("Use selected knowledge packs only: " + "; ".join(pack_names) + ".")
    if profile:
        steps.append("Task profile objective: " + profile.get("objective", "inspect") + ".")
    if dms_tool.is_meta_domain(route):
        steps.extend(
            [
                "Inspect routing first: architecture/RAG questions should retrieve codex-brain and CDS quality memories before SPML project lenses.",
                "Create a task profile with objective, domains, risk gates, selected knowledge packs, and success metrics before planning execution.",
                "Check memory ranking and feedback counts; promote useful architecture memories and demote broad project memories when they are noise.",
                "Use issue-level memory schema: symptom, cause, fix, evidence, recurrence, priority, and whether it is allowed in normal retrieval.",
                "Keep LangGraph as workflow control, LangChain as tool/document glue, DMS as controller, and CDS as the only long-term memory backend.",
                "Write a lightweight run report so later tasks can audit query, retrieved memories, plan, and feedback without reading the whole database.",
            ]
        )
    for gate in profile.get("risk_gates", []):
        steps.append("Risk gate: " + gate)
    route_domains = {route.get("domain", "")}
    route_domains.update(route.get("matched_domains", []))
    if "vision" in route_domains:
        steps.extend(
            [
                "Classify the visual failure first: detector/bbox, crop/longest-finger coverage, 21-keypoint topology, handedness/candidate selection, temporal tracking, smoothing lag, realtime latency, or glove-domain shift.",
                "Use offline annotated glove images or recorded benchmark evidence before changing live-camera behavior.",
                "Track standard vision metrics: detect_rate, bbox center jump, bbox area change, fingertip jitter, static global jump, loop_ms p50/p95, ViTPose ms, HaMeR ms, and hold/relock/reject counts.",
            ]
        )
    if route["protected_baselines"]:
        steps.append("Protect known-good baselines: " + "; ".join(route["protected_baselines"]))
    if "Machine Vision" in lenses:
        steps.append("Run or inspect offline annotated images before tuning realtime camera code.")
    if "Video Analysis" in lenses:
        steps.append("Measure temporal metrics: detect rate, bbox jump, area change, fingertip jitter, and frame age.")
    if "Advanced DSP" in lenses:
        steps.append("Separate jitter reduction from control lag; test step response and fast finger motion.")
    if "Statistical Signal Processing" in lenses:
        steps.append("Use residuals, covariance, confidence, and gating before accepting visual corrections.")
    if "Real-Time DSP" in lenses:
        steps.append("Instrument D435i capture, inference, UDP, Unity receive, queue depth, FPS, and p95 latency.")
    if "Robotics & Intelligent Sensors" in lenses:
        steps.append("Verify COM/device IDs, calibration, tactile mapping, IMU mapping, and palm signal before algorithm changes.")
    if "Deep Learning" in lenses:
        steps.append("Classify model failure mode: detector miss, crop, topology, handedness, temporal association, or domain shift.")
    if "Ensemble ML Quality Gate" in lenses:
        steps.append("Build an accept/smooth/hold/fallback gate from confidence, geometry, latency, and IMU consistency.")
    if "Relationship Game Theory" in pack_names:
        steps.append("For relationship tasks, analyze observable behavior, reciprocity, repeated-game trust, opportunity cost, and boundaries; do not provide manipulation or pressure tactics.")
    if "Boundary Consent Communication" in pack_names:
        steps.append("For message drafting, use clear intent, non-pressure wording, and explicit refusal space.")
    if "Career Million-Yuan Track" in pack_names:
        steps.append("For career tasks, connect advice to portfolio evidence, interview narratives, compensation path, and current project milestones.")
    if "Learning and Feynman Mastery" in pack_names:
        steps.append("For learning tasks, produce questions, answers, first-principles explanations, and interview-facing project descriptions.")
    if "Risk and Decision Audit" in pack_names:
        steps.append("Audit downside, reversibility, opportunity cost, and the smallest safe next experiment before recommending commitment.")
    if "Nuwa Skill Synthesis" in pack_names:
        steps.append("For Nuwa tasks, route first: direct named-person skill creation, diagnostic recommendation, update existing skill, or quality review.")
    if "Provider Health Check" in pack_names:
        steps.append("For provider/API errors, check provider health and config names before touching project code; never print secrets.")
    if "Media Transcription Pipeline" in pack_names:
        steps.extend(
            [
                "For online video transcript tasks, try yt-dlp metadata/subtitle/media extraction first, but expect platform cookies or anti-bot blocking.",
                "If URL extraction is blocked, switch to cookies.txt, cookies-from-browser, or local downloaded video fallback.",
                "Use ffmpeg or imageio-ffmpeg for audio handling and faster-whisper for local ASR; save TXT/SRT/JSON reports to a dedicated output folder.",
            ]
        )
    steps.append("After verification, update or create the most specific CDS issue memory and write retrieval feedback.")
    return steps


def make_verification(route: dict, lenses: list[str], packs: list[dict] | None = None, profile: dict | None = None) -> list[str]:
    packs = packs or []
    profile = profile or {}
    pack_names = knowledge_router.names(packs)
    checks = ["Confirm retrieved memories are relevant; mark noise via CDS feedback."]
    if pack_names:
        checks.append("Confirm selected knowledge packs match the task and no unrelated pack dominates the answer.")
    if dms_tool.is_meta_domain(route):
        checks.append("Architecture queries should rank codex-brain/CDS memories above SPML/HaMeR technical memories unless the task explicitly mentions the project.")
        checks.append("Each codex-brain run should leave a report folder with task.json, retrieved.md, plan.md, and optional feedback.md.")
        checks.append("Task profile must include risk gates and success metrics so the next run can audit whether the brain actually improved.")
    if "Machine Vision" in lenses or "Deep Learning" in lenses:
        checks.append("Offline benchmark or annotated image output exists before live-camera judgment.")
    route_domains = {route.get("domain", "")}
    route_domains.update(route.get("matched_domains", []))
    if "vision" in route_domains:
        checks.append("A visual-gesture task should retrieve the failure-taxonomy/benchmark memory before version-specific tuning memories.")
    if "Real-Time DSP" in lenses:
        checks.append("Report frame age/FPS/loop_ms rather than subjective 'slow' only.")
    if "Robotics & Intelligent Sensors" in lenses:
        checks.append("Hardware/live Unity validation remains user-operated unless explicitly approved.")
    if route["risk"] == "level1-boundary":
        checks.append("Pause for Level 1 approval before hardware writes, real sending, deploy, commit, or destructive action.")
    if "Relationship Game Theory" in pack_names:
        checks.append("Relationship output must stay bounded: no coercion, jealousy tactics, hidden manipulation, or fake certainty about another person's mind.")
    if "Nuwa Skill Synthesis" in pack_names:
        checks.append("Nuwa routing should not create a skill unless the user explicitly asked for skill creation or update.")
    if "Provider Health Check" in pack_names:
        checks.append("Provider diagnosis should distinguish upstream channel outage, auth/model permission, base_url mismatch, and local code errors.")
    if "Media Transcription Pipeline" in pack_names:
        checks.append("Media transcription tasks should not retrieve HaMeR/SPML project memories unless the user explicitly mentions hand tracking or onlytip.")
        checks.append("Verify outputs include report.json/run_log.txt and either subtitle text or a clear cookies/local-video fallback reason.")
    for metric in profile.get("success_metrics", []):
        checks.append("Success metric: " + metric)
    return checks


def feedback_note(route: dict, packs: list[dict], profile: dict) -> str:
    if dms_tool.is_meta_domain(route):
        return "Codex Brain architecture run: promote codex-brain/CDS routing and memory-quality memories; demote unrelated HaMeR/SPML project memories when they appear as noise."
    if "NTU SPML Project Knowledge" in knowledge_router.names(packs):
        return "Codex Brain project run: promote selected SPML/project memories that match the task profile; demote unrelated architecture/meta memories."
    if "Media Transcription Pipeline" in knowledge_router.names(packs):
        return "Media transcription run: promote yt-dlp/ffmpeg/Whisper/cookies memories; demote unrelated onlytip/SPML/Unity memories."
    return "Codex Brain run: promote memories matching selected knowledge packs and task profile; demote unrelated retrieved memories."


def evaluate_run(route: dict, packs: list[dict], profile: dict, memories: list[cds_tool.Memory], used: list[int], noise: list[int], plan: list[str], verification: list[str]) -> dict:
    issues: list[str] = []
    strengths: list[str] = []
    pack_names = knowledge_router.names(packs)
    used_ratio = len(used) / max(len(memories), 1)
    noise_ratio = len(noise) / max(len(memories), 1)

    if not memories:
        issues.append("No CDS memories were retrieved.")
    else:
        strengths.append(f"Retrieved {len(memories)} CDS memories.")
    if not packs:
        issues.append("No knowledge pack was selected.")
    else:
        strengths.append("Selected packs: " + ", ".join(pack_names) + ".")
    if not profile.get("risk_gates"):
        issues.append("Task profile has no risk gates.")
    if not profile.get("success_metrics"):
        issues.append("Task profile has no success metrics.")
    if not plan:
        issues.append("No execution plan was generated.")
    if not verification:
        issues.append("No verification checklist was generated.")
    if used_ratio < 0.25 and memories:
        issues.append("Low useful-memory ratio; routing or query may be too broad.")
    if noise_ratio > 0.5:
        issues.append("High noise-memory ratio; selected packs or reranking need tightening.")
    if dms_tool.is_meta_domain(route) and any("NTU SPML Project Knowledge" == name for name in pack_names) and not profile.get("lenses"):
        issues.append("Meta architecture task selected SPML project pack without a concrete SPML lens.")

    status = "pass"
    if issues:
        status = "partial" if strengths else "fail"

    return {
        "status": status,
        "used_ratio": round(used_ratio, 3),
        "noise_ratio": round(noise_ratio, 3),
        "strengths": strengths,
        "issues": issues,
        "next_improvements": _evaluation_next_steps(issues),
    }


def plan_memory_updates(query: str, memories: list[cds_tool.Memory], used: list[int], noise: list[int], evaluation: dict, route: dict, packs: list[dict], profile: dict) -> dict:
    memory_by_id = {memory.id: memory for memory in memories}
    update_existing = []
    for memory_id in used[:5]:
        memory = memory_by_id.get(memory_id)
        if memory:
            update_existing.append(
                {
                    "id": memory_id,
                    "action": "promote-or-append-if-new-evidence",
                    "reason": f"Used for {profile.get('objective', route.get('domain', 'task'))}.",
                    "title": memory.title,
                }
            )
    demote = []
    for memory_id in noise[:5]:
        memory = memory_by_id.get(memory_id)
        if memory:
            demote.append(
                {
                    "id": memory_id,
                    "action": "mark-noise-for-this-query",
                    "reason": "Retrieved but did not match selected packs/task profile.",
                    "title": memory.title,
                }
            )
    create_new = []
    if evaluation.get("status") in {"pass", "partial"} and dms_tool.is_meta_domain(route):
        create_new.append(
            {
                "memory_type": "issue",
                "project": "codex-brain",
                "title": "Codex Brain evaluator and memory update planner should guide feedback",
                "create_only_if_missing": True,
                "reason": "Reusable architecture lesson for future codex-brain upgrades.",
            }
        )
    return {
        "query": query,
        "outcome": evaluation.get("status", "partial"),
        "update_existing": update_existing,
        "demote_or_noise": demote,
        "create_new_candidates": create_new,
        "duplicate_guard": "Before remember, retrieve similar codex-brain evaluator memory and update closest issue instead of creating a duplicate.",
    }


def _evaluation_next_steps(issues: list[str]) -> list[str]:
    if not issues:
        return ["No immediate architecture fix required; keep benchmark coverage current."]
    steps = []
    for issue in issues:
        if "No CDS memories" in issue:
            steps.append("Tighten query construction or add seed memory for this domain.")
        elif "No knowledge pack" in issue:
            steps.append("Add or retag a knowledge pack for this task domain.")
        elif "risk gates" in issue:
            steps.append("Add risk gates to task_profile for this route.")
        elif "success metrics" in issue:
            steps.append("Add measurable success metrics to task_profile for this route.")
        elif "Low useful-memory" in issue:
            steps.append("Adjust retrieval query and profile-based reranking for this domain.")
        elif "High noise-memory" in issue:
            steps.append("Demote noisy memories via CDS feedback and narrow selected packs.")
        elif "SPML project pack" in issue:
            steps.append("Prevent NTU SPML pack selection for pure architecture queries unless concrete project terms appear.")
    return steps or ["Inspect task report and add a domain-specific benchmark case."]
