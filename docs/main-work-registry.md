# Main Work Registry

This file records the main local work streams that codex-brain should know about. It is an index, not a place to copy large project files.

## Core System

| Workstream | Path | Git Strategy | Notes |
| --- | --- | --- | --- |
| Codex Brain | `D:\agiletact\codex-brain` | Track in this repository | LangGraph routing, CDS integration, knowledge packs, benchmarks. |
| CDS Memory | `D:\agiletact\codex-memory` | Keep local; consider separate private repo later | Contains personal engineering memory. Do not publish without redaction. |
| DMS/CDS skills | `C:\Users\user\.codex\skills\dms`, `C:\Users\user\.codex\skills\cds` | Track only after privacy review | Operational skills used by Codex. |
| Nuwa skill | `C:\Users\user\.codex\skills\nuwa-skill` | Track only after privacy review | Skill synthesis framework. |

## Project C / Hand Tracking

| Workstream | Path | Git Strategy | Protection |
| --- | --- | --- | --- |
| onlytip 2.2 stable baseline | `D:\agiletact\onlytip - 2.2-mediapipe` | Do not include in codex-brain repo | Stable baseline; copy-first for experiments. |
| onlytip 3.4 OpenVINS-style fusion | `D:\agiletact\onlytip - 3.4-vio-style-fusion` | Separate repo only after cleanup | Current fusion mainline. |
| HaMeR / ViTPose Track A | `D:\agiletact\247-sandbox\onlytip-2.3-vitpose-trackA` | Separate repo only after large-model/data ignore rules | Protect v9.9, v9.12, v9.13. |
| OpenVINS reference | `D:\agiletact\reference-code\open_vins` | External reference; do not vendor | Use commit reference in notes. |

## Utilities

| Workstream | Path | Git Strategy | Notes |
| --- | --- | --- | --- |
| Douyin transcript tool | `D:\agiletact\douyin-transcript-tool` | Candidate separate small repo | Uses yt-dlp, imageio-ffmpeg, faster-whisper. Do not commit cookies or downloaded media. |

## Current Git Policy

- `codex-brain` is the first repo to initialize.
- Other workstreams stay as path references until their `.gitignore`, size, and privacy risks are audited.
- Commit and push require explicit user approval.
- Generated logs, Unity artifacts, model files, cookies, API keys, and `MANO_RIGHT.pkl` must never be committed.
