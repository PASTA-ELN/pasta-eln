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
QT_QPA_PLATFORM=offscreen python -m pytest tests/test_XX_name.py
python -m mypy pasta_eln
python -m pylint pasta_eln
codespell
pre-commit run --all-files
make -C docs html
```

Before editing, run `git status --short`; preserve unrelated changes. Do not run pytest (focused or full), mypy, or pylint unless the user explicitly requests that check in the current task; an instruction to implement or verify does not authorize these commands. Run the standard pytest suite only when the user explicitly requests the full suite: it is long and has been killed for running out of resources. When explicitly authorized, run pytest and pylint outside the sandbox: tests use multiprocessing and pylint writes its cache under the user home. Use Qt's offscreen platform for headless GUI tests. Numbered `test_XX_` modules must retain their order. `test_99_verifyAPIs.py` (OLS and other web lookups) is flaky due to HTTP time-outs; rerun before investigating. Do not run `releaseVersion.py` routinely: it regenerates files and may prompt for release actions.

For coverage-guided iteration, use `python -c "import releaseVersion; raise SystemExit(0 if releaseVersion.runTests() else 1)"`. Inspect `htmlcov/index.html`, target useful uncovered regions with minimal reversible workflow steps in the appropriate numbered test, and retain changes only when coverage improves without regressions. Leave API-dependent paths to `testsComplicated/`; do not target copied third-party source or the human-only GUI entry point.

## Engineering

- Make the minimum change required to achieve the goal. Never overengineer: do not add handling, workflows, abstractions, or validation for unlikely or impossible cases.
- Trust internal data passed between application components. Validate it only when needed for correct typing/mypy; do not add defensive runtime validation.
- Inline every one-call function unless it is a required framework override, signal/slot, callback, or makes a materially complex expression clearer. For functions called `N > 1` times, inline when their executable length `L` satisfies `L < 4N/(N-1)`; do not count docstrings or comments. Do not introduce a function solely to wrap one expression.
- Prefer proximity and a linear, front-to-back reading experience over decomposition for its own sake. A long method is not a defect when its workflow is locally comprehensible; extract only when reuse, a framework boundary, or genuine complexity warrants it.
- Keep user-defined `metaUser` and `metaVendor` dictionaries flexible: their hierarchy is intentionally not schema-bound. For stable internal dictionaries, reliable producers, consumers, and tests are sufficient unless stronger types or validation materially improve correctness.
- Add type hints to new and changed public code; keep mypy and pylint clean. Use descriptive names.
- Store paths in the database in POSIX notation (`Path.as_posix()`), never `str(Path)`, which yields backslashes on Windows and breaks path checks and data transfer between systems. Compare paths as `Path` objects, not as strings, since `os.walk` roots are OS-native.
- `checkDB` levels (`outputString`): `perfect` (green) and `ok` (blue) are explained in the legend; `unsure`, `warning`, `error` get `**` prefixes; `info` has no prefix or color and is for plain statistics (e.g. number of documents). Report expected, harmless findings as `ok`, not `info`.
- Exceptions: broad `except Exception` is the default when the handler reports the failure and stops the operation; separate branches that differ only in their message add nothing beyond the traceback. Every handler logs the traceback (`logging.exception`); never `pass` silently. Catch a specific exception only when the handler substitutes a fallback that is correct for that one cause (e.g. `FileNotFoundError` -> create a default configuration). Add-ons contain no exception handling; Pasta catches their failures where it calls them.
- Use `logging`, not `print`. Exceptions: add-ons, interactive command-line dialogs (`tools.py`, the `installation_tools` command line, prompts when no GUI exists), and vendored code (`minisign`, `markdown2html`). Never log secrets.
- Use parameterized SQL. Treat SQLite data, user files, configuration, and repository uploads as durable; destructive changes require explicit validation and authorization.
- Handle filesystem and SQLite consistency proportionately to the realistic risk. Do not add elaborate pseudo-atomic workflows for merely theoretical failures; retain repair paths and add ordering, recovery, or validation only where likely divergence or destructive impact justifies the complexity.
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
