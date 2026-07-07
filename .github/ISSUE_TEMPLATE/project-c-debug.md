---
name: Project C Debug Issue
about: Track hand tracking, Unity, IMU, sensor fusion, or replay debugging
title: "[project-c] "
labels: project-c,debug
assignees: ""
---

## Failure Class

Choose the closest class:

- [ ] detector / bbox
- [ ] crop / fingertip coverage
- [ ] 21-keypoint topology
- [ ] handedness / candidate selection
- [ ] temporal tracking / jitter
- [ ] smoothing lag / realtime latency
- [ ] IMU / serial / calibration
- [ ] timestamp alignment / replay
- [ ] fusion / gating / residuals

## Evidence

- Project path:
- Version / baseline:
- Command:
- Log / report:
- Screenshot / video path:

## Protected Baseline

Which known-good version must not be edited directly?

## Verification

- [ ] Offline benchmark before live tuning.
- [ ] Metrics recorded: detect rate, bbox jump, fingertip jitter, frame age, p95 latency.
- [ ] Unity/hardware live validation remains user-operated unless explicitly approved.
