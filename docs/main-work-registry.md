# Main Work Registry

This file records the main local work streams that codex-brain should know about. It is an index, not a place to copy large project files.

Use environment placeholders in public docs. Keep real machine paths in your local `.env` or private notes.

## Core System

| Workstream | Path Placeholder | Git Strategy | Notes |
| --- | --- | --- | --- |
| Codex Brain | `<CODEX_BRAIN_ROOT>` | Track in this repository | LangGraph routing, CDS integration, knowledge packs, benchmarks. |
| CDS Memory | `<CODEX_MEMORY_DB>` | Keep local; consider separate private repo later | Contains personal engineering memory. Do not publish without redaction. |
| DMS/CDS skills | `<CODEX_SKILLS_ROOT>\dms`, `<CODEX_SKILLS_ROOT>\cds` | Track only after privacy review | Operational skills used by Codex. |
| Nuwa skill | `<CODEX_SKILLS_ROOT>\nuwa-skill` | Track only after privacy review | Skill synthesis framework. |

## Project C / Hand Tracking

| Workstream | Path Placeholder | Git Strategy | Protection |
| --- | --- | --- | --- |
| onlytip 2.2 stable baseline | `<PROJECT_C_ONLYTIP_2_2>` | Do not include in codex-brain repo | Stable baseline; copy-first for experiments. |
| onlytip 3.4 OpenVINS-style fusion | `<PROJECT_C_FUSION_MAINLINE>` | Separate repo only after cleanup | Current fusion mainline. |
| HaMeR / ViTPose Track A | `<PROJECT_C_TRACK_A>` | Separate repo only after large-model/data ignore rules | Protect v9.9, v9.12, v9.13. |
| OpenVINS reference | `<REFERENCE_OPENVINS_ROOT>` | External reference; do not vendor | Use commit reference in notes. |

## Utilities

| Workstream | Path Placeholder | Git Strategy | Notes |
| --- | --- | --- | --- |
| Douyin transcript tool | `<DOUYIN_TRANSCRIPT_TOOL_ROOT>` | Candidate separate small repo | Uses yt-dlp, imageio-ffmpeg, faster-whisper. Do not commit cookies or downloaded media. |

## Current Git Policy

- `codex-brain` is the first repo to initialize.
- Other workstreams stay as path references until their `.gitignore`, size, and privacy risks are audited.
- Commit and push require explicit user approval.
- Generated logs, Unity artifacts, model files, cookies, API keys, and `MANO_RIGHT.pkl` must never be committed.
