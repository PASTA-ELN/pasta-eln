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

## Open issues

Open issues are the union of:

- [GitHub Issues](https://github.com/PASTA-ELN/pasta-eln/issues), which tracks actionable bugs, enhancements, and discussion; and
- this README section, which records repository-wide maintenance items that need visibility before or alongside an issue.

### Repository maintenance items

- Reconcile the ongoing `camelCase` to `snake_case` module rename across the test suite, legacy UI imports, packaging entry points, and development documentation.
- Restore a passing, configured default test command after the rename is complete.
- Details-edit is bugged
- Table selection sometimes deselects everything or is lagging
- new Entry - Workplan Creator Interaction → not obvious enough
- Table-view What is the Gallery?

