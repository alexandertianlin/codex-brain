# Release Checklist

Use this checklist before tagging, pushing, or publishing `codex-brain`.

## Privacy

- [ ] `git status --short --ignored` shows only expected ignored local artifacts.
- [ ] `git ls-files` contains no `.env`, cookies, API keys, private browser data, databases, model files, videos, or run reports.
- [ ] CDS memory contents are not vendored into this repository.
- [ ] Project C / onlytip / Unity source folders are referenced by path only, not copied into this repository.

## Verification

Run:

```cmd
cd /d <CODEX_BRAIN_ROOT>
python -m compileall app.py graphs tools tests
python tools\privacy_audit.py
.venv\Scripts\python.exe tools\run_retrieval_benchmark.py
.venv\Scripts\python.exe -m pytest -q
run.cmd "upgrade codex-brain knowledge routing memory feedback" --no-feedback --no-report
```

Expected:

- compileall passes.
- privacy audit passes.
- retrieval benchmark passes or known failures are documented.
- smoke tests pass, or CI-only limitations are documented.
- architecture task retrieves codex-brain/CDS memories before unrelated project memories.

## Git

- [ ] Review `git diff`.
- [ ] Commit only after explicit user approval.
- [ ] Push only to a confirmed private remote unless the user explicitly approves public release.
- [ ] Tag stable versions after verification, for example `v0.1-router`.

## Post-Release

- [ ] Save CDS feedback for useful/noisy memories if routing changed.
- [ ] Update `docs/main-work-registry.md` if a new workstream or repository is introduced.
