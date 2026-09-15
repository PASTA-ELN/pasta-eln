# Contributor and Agent Guidance

## Repository

- `pasta_eln/`: application package: `backend_worker/` (SQLite, import/export, repositories, workers), `ui/` (Qt UI), `add_ons/` (extractors/extensions), and `text_tools/` (Markdown/HTML/string helpers).
- `tests/`: ordered standard pytest suite. `testsComplicated/`: environment-dependent/integration tests; keep out of the default suite unless isolated.
- `docs/`: Sphinx documentation.
- Start the GUI with `python -m pasta_eln.gui`; it creates `ui.main_window.MainWindow`.

## Development

```bash
pip install -r requirements-linux.txt
pip install -r requirements-windows.txt
pip install -r requirements-devel.txt
pip install -e .
python -m pasta_eln.gui
QT_QPA_PLATFORM=offscreen python -m pytest tests/
python -m mypy pasta_eln
python -m pylint pasta_eln
codespell
pre-commit run --all-files
make -C docs html
```

Numbered `test_XX_` modules must retain their order. Run pytest and pylint outside the sandbox: tests use multiprocessing and pylint writes its cache under the user home. Use Qt's offscreen platform for headless GUI tests. Do not run `releaseVersion.py` routinely: it regenerates files and may prompt for release actions.

For coverage-guided iteration, use `python -c "import releaseVersion; raise SystemExit(0 if releaseVersion.runTests() else 1)"`. Inspect `htmlcov/index.html`, target useful uncovered regions with minimal reversible workflow steps in the appropriate numbered test, and retain changes only when coverage improves without regressions. Leave API-dependent paths to `testsComplicated/`; do not target copied third-party source or the human-only GUI entry point.

## Engineering

- Use parameterized SQL. Treat SQLite data, user files, configuration, and repository uploads as durable; destructive changes require explicit validation and authorization.
- Keep the README concise and user-facing; put detail in `docs/`. Update this file if commands, structure, or safety constraints change.

## UI

- Prefer standard PySide6 widgets and `palette.py`; style only for readability or a clear need. Use icon plus text when practical, and check light/dark themes with empty, short, and long content. Theme changes require reload.
- Use uppercase names for file types in user-visible text (for example, CSV and ELN); retain lowercase extensions only where required by filenames, filters, or APIs.
- “Details” is the name of the Details pane; preserve that capitalization in user-visible references.
- Visibility controls should use state-specific labels when clear; otherwise use “Hide/show”. Prefer “Select” over “Choose”.
- Keep project, table, sample, and edit/view context clear. Important actions should be visible, low-click, and usually available by context menu. Prefer native Qt behaviour, resilient layouts, and resizable columns.
- At most one button per area may have the `default` property.
- Keep substantial widgets focused and colocated; create a custom widget when warranted. Define/configure widgets, assemble layouts, connect signals, then run immediate code in `__init__`. Make runtime changes in `paint`.
- Interactive hosts inherit `ui.widget.Widget` and implement `execute`; command buttons use `ui.widget.Button` roles. Use enums for actions and keep intrinsic data on the component; attach typed payloads only for unrecoverable target data.

## GitHub Issues

The authoritative issue set is GitHub Issues plus the **Repository maintenance items** in `README.md`; record actionable findings in the appropriate place. For issue writes, use authenticated `gh` if the connector cannot write: check `gh auth status`, preserve real line breaks, and remove labels with `gh issue edit <number> --remove-label "<exact label>"` followed by verification.

Before implementing `#<number>`, read its body and every comment in chronological order; later comments may supersede earlier text. Implement and verify every explicitly scoped surface, and report unmet or ambiguous requirements rather than silently narrowing scope.
