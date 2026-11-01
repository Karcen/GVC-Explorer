# Codex project guidance — GVC Explorer

## Goal

Maintain a locally run, auditable Python WWZ 16-term decomposition engine and its Tk desktop application and offline HTML atlas. This repository contains research data and original MATLAB scripts; do not transmit those files to outside services or publish them without explicit permission.

## Non-negotiable mathematical contract

- Preserve original `valueadded2007.m` equations, matrix ordering, signed values, all 16 components, and bilateral/sector export identities.
- Verify changes with `PYTHONPATH=src pytest -q` and the 2007 historical CSV parity tests.
- OECD 2025 Extended (85×50) and the historical 2007 MATLAB input (48×17) are incompatible label dictionaries. Never apply OECD 2025 labels to legacy 2007 positions. Use the workbook hash and the audited Sheet1 labels for the legacy input, and actual economic-area/activity keys for the annual CSV adapter.
- Do not assert that future years, other datasets, TiVA or regional-link code have been migrated or numerically validated if they have not.

## UI and attribution

- Both `desktop.py` (Tk) and `build_offline_preview.py` / `offline_dashboard.html` must display `Jiacheng Zheng` as a clickable link to https://karcen.github.io/ .
- In the offline viewer distinguish the legacy numerical data selection from the separate official OECD 2025 economy/sector directory.
- Publication PDFs run the upstream nature-figure text auditor. Keep its blob hash and Apache license; do not describe this single check as full journal certification.

## Review instructions

After code modifications, regenerate the offline HTML using `PYTHONPATH=src python build_offline_preview.py`. Check GUI syntax, mapping tests, standalone HTML behavior, and archive contents. Keep raw source files byte-for-byte intact. Create explicit release notes and preserve the original 2007 source as a separate archive section.

## Codex execution status

This file is instructions for using Codex on this repository. The current packaged work has **not** been executed through Codex because the Codex CLI is not present in the execution environment.
