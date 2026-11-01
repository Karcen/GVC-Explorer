> Historical note from the earlier release. For the current importer, workbook label audit, and figure checks, see [the release README](../README_EN.md) and [design notes](studio_design.md).

# Codex continuation

Use Codex locally from the project root after examining `AGENTS.md`. The current workspace has no Codex executable, so the changes in this delivery were implemented and tested directly, not through a Codex session.

Suggested continuation: (1) run `PYTHONPATH=src pytest -q`, (2) verify Streamlit with a browser on macOS, (3) inspect original OECD ICIO CSV layout and build a separate adapter that constructs the canonical Z/Y/VA/X arrays, (4) benchmark the 85×50 engine before making performance promises, (5) load the local Nature Skills instructions for publication figures and audit exported PDFs.

Do not instruct Codex to force the new labels onto the historical 2007 sample. Avoid publishing the data/raw-source folders until redistribution permissions are checked.
