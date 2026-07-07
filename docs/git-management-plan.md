# Codex Brain Git Management Plan

This repository tracks the local AI-brain control layer, not every large working project.

## Repository Scope

Track:

- `app.py`, `run.cmd`, `requirements.txt`
- `graphs/`, `tools/`, `knowledge-packs/`, `config/`, `benchmarks/`, `tests/`
- architecture docs and task registries under `docs/`

Do not track:

- `.venv/`
- generated `runs/`
- local status files such as `brain_status.md`
- secrets, cookies, API keys, provider credentials
- large models, datasets, media, Unity build artifacts, or binary glove assets

## Main Workflow

1. Inspect:
   - `git status --short`
   - run codex-brain with `--no-feedback` for architecture checks when needed.
2. Change:
   - edit only codex-brain control files or docs in this repository.
   - keep onlytip/Unity/HaMeR source projects outside this repository unless a separate repo is created for them.
3. Verify:
   - `python -m compileall app.py graphs tools`
   - `.venv\Scripts\python.exe tools\run_retrieval_benchmark.py`
4. Review:
   - inspect `git diff`
   - update CDS feedback if routing or memory behavior changed.
5. Commit:
   - commit only after explicit user approval.
   - never commit secrets, cookies, large binary assets, or generated run reports.

## Repository Strategy For Main Work

Use separate repositories or separate protected folders for major projects:

- `codex-brain`: AI-brain routing, memory integration, knowledge packs, benchmarks.
- `douyin-transcript-tool`: media transcript utility, should become its own small repo if it grows.
- `onlytip` / HaMeR / Unity versions: keep copy-first version folders; do not merge into codex-brain.
- `codex-memory`: keep as local memory backend; do not blindly publish.

This keeps the brain small, auditable, and easy to roll back.
