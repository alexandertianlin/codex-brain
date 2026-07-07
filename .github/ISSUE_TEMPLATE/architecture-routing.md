---
name: Architecture / Routing Issue
about: Track codex-brain routing, knowledge-pack, CDS, or DMS behavior
title: "[routing] "
labels: architecture,routing
assignees: ""
---

## Symptom

What did codex-brain route, retrieve, or plan incorrectly?

## Expected Behavior

What route, knowledge packs, memories, or verification should have been selected?

## Evidence

- Command:
- Run report:
- Key retrieved memories:
- Noise memories:

## Risk Gate

- [ ] No secrets, cookies, API keys, private database contents, or large files included.
- [ ] Architecture/RAG task is not dominated by unrelated project memories.
- [ ] CDS feedback should be updated after the fix.

## Verification

- [ ] `python -m compileall app.py graphs tools tests`
- [ ] `.venv\Scripts\python.exe tools\run_retrieval_benchmark.py`
- [ ] Relevant `run.cmd "...task..." --no-feedback --no-report`
