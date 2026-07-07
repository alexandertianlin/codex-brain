# Codex Brain

Local MVP that connects DMS, CDS, NTU SPML project knowledge, and domain knowledge packs.

## Git Management

This folder is the first Git-managed control repository for the local AI brain.

- Git scope and ignore rules: `docs/git-management-plan.md`
- Main workstream registry: `docs/main-work-registry.md`
- Release safety checklist: `docs/release-checklist.md`
- GitHub templates: `.github/ISSUE_TEMPLATE/` and `.github/pull_request_template.md`
- Local environment example: `.env.example`
- Generated run reports under `runs/` are ignored by default.
- Commit/push should only happen after explicit user approval.

```cmd
cd /d D:\agiletact\codex-brain
run.cmd "HaMeR bbox太小，识别慢，怎么解决"
```

Architecture:

- DMS: task route, risk, protected baselines
- CDS: long-term local engineering memory and feedback
- SPML: course knowledge lenses for onlytip / HaMeR / ViTPose / IMU fusion
- Knowledge Router: chooses the smallest useful knowledge pack set for the task
- LangGraph task graph: classify -> select_spml -> select_knowledge -> profile -> retrieve -> plan -> verify -> evaluate -> memory_update_plan -> feedback
- LangChain bridge: `tools/langchain_cds.py` loads CDS SQLite memories as LangChain `Document` objects
- Knowledge packs live in `knowledge-packs/*.yml` instead of hard-coded Python lists.
- Retrieval benchmark cases live in `benchmarks/retrieval_cases.json`.
- Nuwa routing is represented by `knowledge-packs/nuwa-skill-synthesis.yml`; the full skill-creation workflow remains in `C:\Users\user\.codex\skills\nuwa-skill`.
- Protected baselines live in `config/protected-baselines.yml`.
- Provider/API diagnosis uses `knowledge-packs/provider-health.yml` and `tools/provider_health.py`.
- Task-end review template lives in `config/task-review-template.md`.

The MVP uses a local `.venv` with LangChain/LangGraph and the existing CDS scripts. CDS remains the long-term memory backend.

Local path defaults can be overridden without editing source code:

- `CODEX_MEMORY_DB`: CDS SQLite index path
- `CODEX_CDS_SCRIPTS`: CDS command script directory
- `CODEX_BRAIN_PYTHON`: Python executable used by local status tools

## Prompt Replacement

Old prompt:

```text
加载dms cds，加载女娲skill，加载ntu spml知识库，运行 codex-brain，用 LangGraph + CDS + SPML 分析
```

Use this general prompt instead:

```text
运行 codex-brain。先用 DMS 判断任务类型和风险，用 CDS 检索相关长期记忆，再由 Knowledge Router 自动选择最小合适知识包。只有当任务涉及 Project C、HaMeR、ViTPose、Unity、IMU、传感器融合、SPML课程或具身智能工程时才加载 NTU SPML；关系、人际、职业、学习、产品和风险问题加载对应理论包。输出：路由结果、选中的知识包、关键记忆、下一步计划、验证标准；最后写入 CDS 检索反馈。
```

Short task prompts:

```text
关系/人际：
运行 codex-brain，自动选择关系博弈论、边界沟通、行为信号和机会成本知识包，分析这件事。禁止操控、施压、嫉妒测试和读心式判断。

Project C / 工程：
运行 codex-brain，自动选择 DMS/CDS、NTU SPML、项目记忆和必要的视觉/IMU/Unity知识包，先保护稳定版本，再给最小实验和验证指标。

职业规划：
运行 codex-brain，自动选择职业规划、年薪百万路径、项目组合、面试叙事和风险审计知识包，结合我的长期记忆给计划。

学习/面试文档：
运行 codex-brain，自动选择学习计划、费曼解释、项目原理和面试展示知识包，输出问题、答案、项目描述和复习任务。

系统架构/知识库管理：
运行 codex-brain，自动选择 Codex Brain Architecture、DMS/CDS、RAG质量和Knowledge Router知识包，检查是否有知识库污染、错误路由和记忆噪声。
```

Check the LangChain bridge:

```cmd
cd /d D:\agiletact\codex-brain
.venv\Scripts\python.exe tools\langchain_cds.py
```

Run retrieval benchmark:

```cmd
cd /d D:\agiletact\codex-brain
.venv\Scripts\python.exe tools\run_retrieval_benchmark.py
```

Generate status dashboard:

```cmd
cd /d D:\agiletact\codex-brain
.venv\Scripts\python.exe tools\brain_status.py
```

Check provider health without exposing API keys:

```cmd
cd /d D:\agiletact\codex-brain
.venv\Scripts\python.exe tools\provider_health.py
```

Run a no-feedback architecture check:

```cmd
cd /d D:\agiletact\codex-brain
run.cmd "upgrade codex-brain knowledge routing memory feedback" --no-feedback
```

Run a Nuwa routing check:

```cmd
cd /d D:\agiletact\codex-brain
run.cmd "加载女娲skill，帮我造一个乔布斯视角的 perspective skill" --no-feedback
```
