# Contributor and agent guidance

## Repository

- `pasta_eln/`: application package: `backend_worker/` (SQLite, import/export, repositories, workers), `ui/` (Qt UI), `add_ons/` (extractors/extensions), and `text_tools/` (Markdown/HTML/string helpers).
- `tests/`: ordered standard pytest suite. `testsComplicated/`: environment-dependent/integration tests; keep out of the default suite unless isolated.
- `docs/`: Sphinx documentation.

Start the GUI with `python -m pasta_eln.gui`; it creates `ui.main_window.MainWindow`.

## Development

Run from the repository root with Python 3.10+.

```bash
pip install -r requirements-linux.txt       # Linux
pip install -r requirements-windows.txt     # Windows
pip install -r requirements-devel.txt       # development tools
pip install -e .

python -m pasta_eln.gui
QT_QPA_PLATFORM=offscreen python -m pytest tests/
python -m mypy pasta_eln
python -m pylint pasta_eln
codespell
pre-commit run --all-files
make -C docs html
```

Before editing, run `git status --short`; preserve unrelated changes. Run the smallest relevant test, then the standard suite when practical. Numbered `test_XX_` modules must retain their order. Run pytest and pylint outside the sandbox: tests use multiprocessing and pylint writes its cache under the user home. Use Qt's offscreen platform for headless GUI tests.

Do not run `releaseVersion.py` routinely: it regenerates files and may prompt for release actions.

For coverage-guided iteration, use the test runner without invoking the release script:

```bash
python -c "import releaseVersion; raise SystemExit(0 if releaseVersion.runTests() else 1)"
```

After each run, inspect `htmlcov/index.html`, identify the largest useful uncovered regions, and add one minimal, reversible workflow step to the appropriate numbered test. Run that focused test first, then repeat the coverage command and retain changes only when coverage improves without regressions. Leave API-dependent paths to `testsComplicated/` and do not target copied third-party source files or the human-only GUI entry point.

For a visual check of the user's actual desktop, ask them to press `F12` in PASTA-ELN and inspect the resulting temporary `pasta-eln-current-window.png` rather than relying only on offscreen screenshots.

## Engineering

- Make the minimum change required to achieve the goal. Never overengineer: do not add handling, workflows, abstractions, or validation for unlikely or impossible cases.
- Trust internal data passed between application components. Validate it only when needed for correct typing/mypy; do not add defensive runtime validation.
- Inline a short function when its length `L` satisfies `L < 4N/(N-1)`, where `N > 1` is its number of calls.
- Add type hints to new and changed public code; keep mypy and pylint clean. Use descriptive names.
- Use parameterized SQL. Treat SQLite data, user files, configuration, and repository uploads as durable; destructive changes require explicit validation and authorization.
- Keep the README concise and user-facing; put detail in `docs/`. Update this file if commands, structure, or safety constraints change.

## UI

- Prefer standard PySide6 widgets and `palette.py`; style only for readability or a clear need. Use icon plus text when practical, and check light/dark themes with empty, short, and long content. Theme changes require reload.
- Use uppercase names for file types in user-visible text (for example, CSV and ELN); retain lowercase extensions only where required by filenames, filters, or APIs.
- “Details” is the name of the Details pane; preserve that capitalization in user-visible references to the pane.
- Visibility controls should use state-specific labels when the resulting state is clear; otherwise use the general “Hide/show” form for toggles.
- Prefer “Select” over “Choose” in user-facing controls and prompts.
- Keep project, table, sample, and edit/view context clear. Important actions should be visible, low-click, and usually available by context menu. Prefer native Qt behaviour, resilient layouts, and resizable columns.
- At most one button per area may have the `default` property.
- Keep substantial widgets focused and colocated; create a custom widget when warranted. In UI classes, order methods as `__init__`, `onGetData`, `paint`, `execute`, then slots, events, and helpers. Define/configure widgets, assemble layouts, connect signals, then run immediate code in `__init__`. Make runtime changes in `paint`.
- Interactive hosts inherit `ui.widget.Widget` and implement `execute`; command buttons use `ui.widget.Button` roles. Use enums for actions and keep intrinsic data on the component; attach typed payloads only for unrecoverable target data.

## GitHub issues

The authoritative issue set is GitHub Issues plus the **Repository maintenance items** in `README.md`; record actionable findings in the appropriate place. For issue writes, use authenticated `gh` if the connector cannot write: check `gh auth status`, preserve real line breaks, and remove labels with `gh issue edit <number> --remove-label "<exact label>"` followed by verification.

Before implementing `#<number>`, read its body and every comment in chronological order; later comments may supersede earlier text. Implement and verify every explicitly scoped surface, and report any unmet or ambiguous requirement rather than silently narrowing the scope.
