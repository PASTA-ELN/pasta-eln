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

## Open issues

Open issues are the union of:

- [GitHub Issues](https://github.com/PASTA-ELN/pasta-eln/issues), which tracks actionable bugs, enhancements, and discussion; and
- this README section, which records repository-wide maintenance items that need visibility before or alongside an issue.

### Repository maintenance items

- Order of open issues that do not have a question
  - Version 3.3
    1.  647 – Test extraction of a file does not agree with actual extraction
    2.  646 – Assignment of item type for “unknown” items when re-running extractors
    3.  602 – Saving image preview leads to an empty text box

  - Version 3.3.1: New features that require minimal changes, possibly some config changes
    1.  609 – Re-ordering of list after re-run extractor?
    2.  612 – Restarting Pasta resets visibility setting
    3.  381 – Visualization of linked items
    4.  570 – Version control for extractors
    5.  41 – Spellcheck in form
    6.  566 – Create GUI for attachments
    7.  436 – Re-running of extractors whenever measurement details are saved
    8.  528 – Feature Request: easily visible changelog
    9.  608 – Feature Request: Color implementation
    10. 430 – Creating templates for items

  - Redesign of Pasta
    1.  421 – Data hierarchy structure
    2.  451 – Should items with the same ...
    3.  644 – Linking multiple items = list


- Tutorial
  - Create an interactive tutorial runner as a separate program launched from the main program. It should use a read-only SQLite connection, define a clear busy-timeout/WAL strategy for concurrent access, and maintain its own JSON file to track tutorial progress.
  - Rewrite the tutorial content with more steps, details, screenshots, contextual help, and clear expected results.
