from graphs.task_graph import run_task_graph


def test_smoke_no_feedback():
    result = run_task_graph("HaMeR bbox too small, recognition slow, how to fix", write_feedback=False)
    assert result["memories"]
    assert result["plan"]
    assert result["evaluation"]["status"] in {"pass", "partial"}
    assert any("Machine Vision" in lens or "Real-Time" in lens for lens in result["spml_lenses"])


def test_relationship_uses_relationship_packs_not_spml():
    result = run_task_graph("girlfriend relationship game theory boundary communication next step", write_feedback=False)
    names = {pack["name"] for pack in result["knowledge_packs"]}
    assert "Relationship Game Theory" in names
    assert "Boundary Consent Communication" in names
    assert "NTU SPML Project Knowledge" not in names
    assert not result["spml_lenses"]


def test_architecture_uses_codex_brain_pack_and_update_plan():
    result = run_task_graph("upgrade codex-brain knowledge routing with LangGraph and CDS", write_feedback=False)
    names = {pack["name"] for pack in result["knowledge_packs"]}
    assert "Codex Brain Architecture" in names
    assert result["evaluation"]["status"] in {"pass", "partial"}
    assert result["memory_update_plan"]["outcome"] in {"pass", "partial"}


def test_knowledge_packs_load_from_yaml():
    from tools import knowledge_router

    names = {pack["name"] for pack in knowledge_router.PACKS}
    assert "Core DMS/CDS Memory" in names
    assert "Codex Brain Architecture" in names
    assert "NTU SPML Project Knowledge" in names
    assert "Nuwa Skill Synthesis" in names


def test_nuwa_skill_synthesis_pack_selected():
    result = run_task_graph("load Nuwa and create a Steve Jobs perspective skill", write_feedback=False)
    names = {pack["name"] for pack in result["knowledge_packs"]}
    assert "Nuwa Skill Synthesis" in names
    assert "Core DMS/CDS Memory" in names
    assert "skill-synthesis" in result["route"]["matched_domains"]
    assert result["task_profile"]["objective"] == "route-nuwa-skill-synthesis"


def test_architecture_does_not_select_product_pack_without_ui():
    result = run_task_graph("codex-brain architecture evaluator memory update planner benchmark", write_feedback=False)
    names = {pack["name"] for pack in result["knowledge_packs"]}
    assert "Codex Brain Architecture" in names
    assert "Product and Taste Review" not in names


def test_hard_constraints_and_failure_classifier_present():
    result = run_task_graph("HaMeR bbox too small and realtime latency is slow", write_feedback=False)
    assert result["hard_constraints"]
    assert result["failure_types"]
    failure_types = {item["type"] for item in result["failure_types"]}
    assert "vision-detector-bbox" in failure_types
    assert "vision-latency" in failure_types
