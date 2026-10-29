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

PASTA-ELN supports Python 3.10 and later.

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

Open issue list:
- eLabFTW sync: project group must not be archived
  - The project-group resource is archived to hide it from users. In recent eLabFTW versions (checked against 5.6.15), archived resources reject every change except "unarchive", so Pasta can no longer store the data hierarchy in the project group's `metadata` (`syncDocTypes()` in `backend_worker/elab_ftw_sync.py`), and the Verify button in the project-group configuration fails.
  - Unarchive → change → re-archive is not a solution: in eLabFTW 5.6 only team admins (or whoever locked the resource) may unarchive, because archiving also locks the resource.
  - Path forward: use a non-archived, visible project group. Members need write access, so eLabFTW cannot stop them from editing it in the web interface; Pasta has to tolerate and validate manual edits (e.g. a note in the body asking users not to change it).
  - Reading the stored data hierarchy back from the project group is not implemented yet, but it is needed.
- Case-insensitive file handling
  - Everything that matches file names, folder names or extensions has to be case-insensitive: `SETUP.EXE`, `Setup.Exe` and `setup.exe` must behave the same on all operating systems.
  - Scan exclusions (`scanExcludePatterns`, branches `new_version` and `LLM_functions`) are matched case-sensitively on Linux, because `fnmatch.fnmatch()` follows the case rules of the operating system. The pattern `*.exe` therefore does not exclude `SETUP.EXE` on Linux, but it does on Windows. Affected on `new_version`: `pasta_eln/backend_worker/backend.py` line 355 (folders) and line 406 (files). Fix: compare `name.lower()` with `pattern.lower()`, and store patterns in lower case when they are saved in the configuration.
  - The hard-coded scan rules are case-sensitive, too: the `trash_` prefix and `__pycache__` in `backend.py`, `_PastaExport` in `isPastaExport()` (`backend_worker/extractor.py`), and the `.pastaELN_ignore` marker file, which is found only with exactly this spelling on Linux.
  - `checkDB()` does not use `scanExcludePatterns`, only the hard-coded rules. Excluded files that still exist on disk may therefore be reported as missing from the database. `checkDB()` should share one case-insensitive matching function with the scan.
  - Already case-insensitive: extractor selection (`extractor_{extension.lower()}.py`) and the stored `fileExtension`.
- Install dependabot according to ~/Dependabot.md


## Notes
- Tutorial
  - Create an interactive tutorial runner as a separate program launched from the main program. It should use a read-only SQLite connection, define a clear busy-timeout/WAL strategy for concurrent access, and maintain its own JSON file to track tutorial progress.
  - Rewrite the tutorial content with more steps, details, screenshots, contextual help, and clear expected results
