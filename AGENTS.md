# Guidance for contributors and agents

## Repository map

- `pasta_eln/`: application package.
  - `backend_worker/`: SQLite storage, import/export, repository clients, and worker tasks.
  - `ui/`: current Qt user interface, including shared widgets, configuration dialogs, communication, project sidebar, details, table view, and workplan creator.
  - `add_ons/`: extractors and optional project/table extensions.
  - `text_tools/`: Markdown/HTML and string helpers.
- `tests/`: standard pytest suite.
- `testsComplicated/`: environment-dependent or integration-style tests; do not add these to the default test run without a clear isolation strategy.
- `docs/`: Sphinx documentation.

The GUI entry point is `python -m pasta_eln.gui`. Its startup module creates `ui.main_window.MainWindow`.

## Development commands

Run commands from the repository root. Python 3.10 or later is required.

```bash
# Install
pip install -r requirements-linux.txt       # Linux
pip install -r requirements-windows.txt     # Windows
pip install -r requirements-devel.txt       # development tools
pip install -e .

# Run
python -m pasta_eln.gui

# Verify
QT_QPA_PLATFORM=offscreen python -m pytest tests/
python -m mypy pasta_eln
python -m pylint pasta_eln
codespell
pre-commit run --all-files

# Documentation
make -C docs html
```

`releaseVersion.py` performs broader release-maintenance checks, including tests, static analysis, Sourcery, and documentation. Invoke it manually only; do not run it as routine agent verification because it regenerates files and can prompt for release actions.

Before editing, run `git status --short`. Do not overwrite, reset, or remove unrelated user changes. Run the smallest relevant test first, then the standard suite when practical. The standard test suite is intentionally stateful: keep numbered `test_XX_` modules in their required execution order; `tests/conftest.py` enforces that order. Run pytest and pylint outside the execution sandbox: extractor tests use multiprocessing and the sandbox prevents its forkserver from starting; pylint writes its cache under the user home directory. GUI tests must use Qt's offscreen platform in headless environments.

For visual review of the user's actual desktop layout, ask them to press `F12` in PASTA-ELN. It saves a direct capture of the live main window as `pasta-eln-current-window.png` in the system temporary directory and shows its location. Inspect that image instead of relying only on offscreen test screenshots, which can differ in theme, scaling, and font rendering.

## Engineering conventions

- Use Python type hints for new and changed public code; maintain the configured mypy and pylint standards.
- Prefer clear, descriptive names over abbreviated names. Split large widgets into focused functions, classes, or modules.
- Keep related subwidgets in the same directory and create a dedicated custom widget when a subwidget becomes substantial.
- Use parameterized SQL for values; never build SQL from user- or document-provided strings.
- Treat SQLite data, user files, configuration, and external repository uploads as durable user data. Avoid destructive operations unless explicitly requested and validated.
- Keep README concise and user-facing; put detailed documentation in `docs/`. Update this file when commands, package structure, or safety constraints change.

## UI development guidelines

- Prefer standard PySide6 widgets and `palette.py`; add styling only for readability or a clear design need. Use icon plus text where practical (`ri.iconname`), and test light/dark themes with empty, short, and long content.
- A theme change requires an application reload; immediate theme-switch updates are not supported.
- Highlight at most one button per area with its `default` property. Other controls may use a primary-coloured icon but must not compete with that action.
- Keep the current project, table, sample, and editing/viewing context clear. Important actions must be visible, require few clicks, and usually also be available in a context menu.
- Recreate Figma where practical, but prefer useful native Qt behaviour (for example, a splitter over a duplicate sidebar-toggle control). Use resilient layouts and user-resizable columns instead of hard truncation.

### UI code design

- Keep components focused and colocate their related files; create a custom widget when a subwidget becomes substantial. `ui/sidebar/sidebar.py` is a good example.
- In `__init__`, define instance variables; configure widgets; build layouts; apply necessary style; assemble the main layout; connect signals; then run immediate code. Comment widget/layout blocks and non-obvious behaviour.
- In UI files, order methods as: `__init__`, `onGetData`, `paint`, `execute`, then other slots, event handlers, and helpers. Omit inapplicable methods.
- Make runtime widget changes in `paint`; use descriptive names and type hints.

### Commands and controls

- Interactive hosts inherit `ui.widget.Widget` and implement `execute`; use `ui.widget.Button` for command buttons and its `DEFAULT`, `HIGHLIGHTED`, and `PRIMARY` roles.
- Identify actions with enums, not positional lists or opaque string codes. Read operational data from authoritative current state where possible.
- Attach typed enum/dataclass payloads only when the clicked control provides unrecoverable target information (for example, a document type, add-on, repository, or formatting target). Keep intrinsic component data, such as a filter ID, on that component instead.

## Open issues

The authoritative open-issues set is the union of [GitHub Issues](https://github.com/PASTA-ELN/pasta-eln/issues) and the **Repository maintenance items** section of `README.md`. Create or update the appropriate record when discovering an actionable defect, improvement, or repository-wide maintenance concern.
