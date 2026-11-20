[![PyPI version](https://badge.fury.io/py/pasta-eln.svg)](https://badge.fury.io/py/pasta-eln)
[![GitHub version](https://badge.fury.io/gh/PASTA-ELN%2Fpasta-eln.svg)](https://badge.fury.io/gh/PASTA-ELN%2Fpasta-eln)
[![PyPI build](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pypi.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pypi.yml)
[![Verify Linux install](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/installLinux.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/installLinux.yml)
[![Documentation building](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/docbuild.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/docbuild.yml)
[![Linting](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pylint.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pylint.yml)
[![MyPy](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/mypy.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/mypy.yml)

# PASTA-ELN

<img src="docs/source/_static/pasta_logo.svg" alt="PASTA-ELN logo" width="120" align="right" style="margin-left: 20px;">

PASTA-ELN is a local electronic lab notebook for experimental scientists. It organizes raw data, metadata, projects, and associated files in a desktop application built with Python and PySide6.

The full user and developer documentation is available at [PASTA-ELN documentation](https://pasta-eln.github.io/pasta-eln/).

## Quick start

PASTA-ELN supports Python 3.12 and later.

```bash
pip install -r requirements-linux.txt  # or requirements-windows.txt
pip install -e .
python -m pasta_eln.gui
```

For development tools, install `requirements-devel.txt`. Run the following commands from the repository root:

```bash
QT_QPA_PLATFORM=offscreen python -m pytest tests/
python -m mypy pasta_eln
python -m pylint pasta_eln
```

Build the documentation with `make -C docs html`.

For maintainer release work, `releaseVersion.py` provides a broader verification run; invoke it manually only.

## Issues

Open issues are the union of
1. [GitHub Issues](https://github.com/PASTA-ELN/pasta-eln/issues), which tracks actionable bugs, enhancements, and discussion; and
2. this README section, which records repository-wide maintenance items that need visibility before or alongside an issue.

### Repository maintenance items
- Broad and inconsistent exception handling: create and document a consistent exception handling
  The package contains many except Exception blocks, including paths that merely print, log, return an empty value, or silently pass. This erases distinctions between expected operational failures and programming defects. Callers cannot consistently determine whether an operation succeeded, and corrupted intermediate state may continue through the application after the original error context has been lost.
  Examples:
  - Add-on failures become {} in [`callAddOn()` (line 201)](/home/steffen/FZJ/PASTA/pasta-eln/pasta_eln/addons.py:201)
  - Auto-comment failures are suppressed in [`Form.execute()` (line 644)](/home/steffen/FZJ/PASTA/pasta-eln/pasta_eln/ui/form/form.py:644)
  - Download errors are only printed in [`callDataExtractor()` (line 227)](/home/steffen/FZJ/PASTA/pasta-eln/pasta_eln/addons.py:227)
- Case-insensitive scan exclusions (branch `new_version`)
  - `scanExcludePatterns` are matched case-sensitively on Linux, because `fnmatch.fnmatch()` follows the case rules of the operating system. The pattern `*.exe` therefore does not exclude `SETUP.EXE` on Linux, but it does on Windows, so the same data folder gives different databases. Affected on `new_version`: `pasta_eln/backend_worker/backend.py` line 355 (folders) and line 406 (files). Fix: compare `name.lower()` with `pattern.lower()`, and store patterns in lower case when they are saved in the configuration.
  - `checkDB()` does not use `scanExcludePatterns`. Excluded files that still exist on disk may therefore be reported as missing from the database. `checkDB()` should share the matching function with the scan.
- ELN export reads each file completely into memory to compute its SHA-256 and size, so exporting projects with multi-GB files can run out of memory or crash (`pasta_eln/backend_worker/input_output.py`, local files and remote `response.content`). Fix: take the size from `stat()` and hash in chunks; stream remote files.
- Add `path` and `location` columns to the "Select list columns" dialog (~25 lines). `location` shows the stack as project/folder names (e.g. `Pasta / Sicily`), not raw IDs. Items with several branches show all values comma-joined, like tags; `getView` currently keeps only the first branch (`df.index.duplicated(keep='first')`). Changes: `pasta_eln/ui/table/table_header.py` (offer both, save without `.` prefix); `getView` in `pasta_eln/backend_worker/sqlite.py` (exclude both from the properties query, one branches query with the hidden/project filters, one name lookup for all stack IDs).
- Data-hierarchy should be a real data hierarchy: a class like device/instrument should have all properties of device; ensure/test in editor only
- env-variable - migration guard: should be a GUI question
- Release beta version, only then address github issues

## Notes
- Tutorial
  - Create an interactive tutorial runner as a separate program launched from the main program. It should use a read-only SQLite connection, define a clear busy-timeout/WAL strategy for concurrent access, and maintain its own JSON file to track tutorial progress.
  - Rewrite the tutorial content with more steps, details, screenshots, contextual help, and clear expected results
