# Release notes v2.7.1

This document summarizes the changes included in the current iteration and the recent fixes made to the graph visualizer and project UI.

Highlights

- Fixed issue where compiled exe showed "Ошибок не найдено" in the "Errors and Trees" tab while the Results contained errors; normalization of paths and more robust report parsing added.
- Improved graph visualizer (`graph_visualizer_v2_6.py`): folder grouping by full relative path, colors per folder, Plotly customdata for reliable JS->Python events, PyVis support and simple progress dialog during render.
- Optional GPU layout via PyTorch for large graphs; fallback to NetworkX if not available.
- Added smoke-run script `smoke_run_cs_market_bot.py` that runs an audit on the specified project and saves a log to `%USERPROFILE%\.naudit\logs\latest.log`.

How to verify

1. Run smoke script (already executed in CI):
   - `python smoke_run_cs_market_bot.py` (writes to `%USERPROFILE%\.naudit\logs\latest.log`)

2. Rebuild exe with build script if needed:
   - `python build_v2_7_final.py` (run inside project's virtualenv)

Notes and known issues

- QWebEngine initialization requirement: the attribute `AA_ShareOpenGLContexts` must be set before creating `QApplication` in some environments. The smoke script handles this.
- For fully offline or air-gapped builds, ensure PyVis/Plotly resources are collected appropriately for PyInstaller.

