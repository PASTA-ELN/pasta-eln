# Guidance for contributors and agents

## Repository map

- `pasta_eln/`: application package.
  - `backend_worker/`: SQLite storage, import/export, repository clients, and worker tasks.
  - `ui/`: shared and established Qt widgets, configuration dialogs, and communication.
  - `ui_new/`: current UI implementation, including project sidebar, details, table view, and workplan creator.
  - `add_ons/`: extractors and optional project/table extensions.
  - `text_tools/`: Markdown/HTML and string helpers.
- `tests/`: standard pytest suite.
- `testsComplicated/`: environment-dependent or integration-style tests; do not add these to the default test run without a clear isolation strategy.
- `docs/`: Sphinx documentation.

The GUI entry point is `python -m pasta_eln.gui`. Its startup module creates `ui_new.main_window.MainWindow`; keep old and new UI imports explicit while the migration is in progress.

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

Before editing, run `git status --short`. Do not overwrite, reset, or remove unrelated user changes. Run the smallest relevant test first, then the standard suite when practical. Run pytest outside the execution sandbox: extractor tests use multiprocessing and the sandbox prevents its forkserver from starting. GUI tests must use Qt's offscreen platform in headless environments.

## Engineering conventions

- Use Python type hints for new and changed public code; maintain the configured mypy and pylint standards.
- Prefer clear, descriptive names over abbreviated names. Split large widgets into focused functions, classes, or modules.
- Keep related subwidgets in the same directory and create a dedicated custom widget when a subwidget becomes substantial.
- Use parameterized SQL for values; never build SQL from user- or document-provided strings.
- Treat SQLite data, user files, configuration, and external repository uploads as durable user data. Avoid destructive operations unless explicitly requested and validated.
- Keep README concise and user-facing; put detailed documentation in `docs/`. Update this file when commands, package structure, or safety constraints change.

## UI development guidelines

Follow [`pasta_eln/ui_new/development_guidelines.md`](pasta_eln/ui_new/development_guidelines.md) for UI-specific design and implementation rules. In short: use standard PySide6 widgets and theme colours; test light and dark themes with empty, short, and long content; keep the user’s current context and important actions visible; and organize widgets into clear, typed, focused components.

## Open issues

The authoritative open-issues set is the union of [GitHub Issues](https://github.com/PASTA-ELN/pasta-eln/issues) and the **Repository maintenance items** section of `README.md`. Create or update the appropriate record when discovering an actionable defect, improvement, or repository-wide maintenance concern.
