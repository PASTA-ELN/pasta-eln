# Guidance for LLMs


## Development Commands

### Basic Development
- **Start the application**: `python -m pasta_eln.gui` or `python pastaMain.py`
- **Start research version**: `python pastaResearch.py`
- **Run tests**: `python -m pytest tests/` or `python -m pytest` (specific test: `python -m pytest tests/test_01_DefaultExample.py`)

### Code Quality
- **Linting**: `pylint pasta_eln/` or `pylint $(git ls-files 'pasta_eln/*.py')`
- **Type checking**: `mypy pasta_eln/`
- **Code spell check**: `codespell`
- **Pre-commit hooks**: `pre-commit run --all-files`

### Documentation
- **Build docs**: `make -C docs html`
- **View docs**: Open `docs/build/html/index.html` after building

### Installation & Dependencies
- **Install development requirements**: `pip install -r requirements-devel.txt`
- **Install runtime requirements**: `pip install -r requirements-linux.txt` (Linux) or `pip install -r requirements-windows.txt` (Windows)
- **Install package**: `pip install -e .`

## Architecture Overview

PASTA-ELN is a Qt-based Electronic Lab Notebook (ELN) application built with Python and PySide6.

### Core Components

**Backend (`pasta_eln/backendWorker/backend.py`)**
- Main data access layer using SQLite database
- Handles all filesystem operations
- Manages document hierarchy and project structure
- Inherits from `CLI_Mixin` for command-line functionality

**GUI (`pasta_eln/gui.py`)**
- Main application window (`MainWindow` class)
- Orchestrates all GUI components
- Handles application lifecycle and window management

**Database (`pasta_eln/backendWorker/sqlite.py`)**
- SQLite database abstraction layer
- Document storage and retrieval
- Database schema management

**Communication (`pasta_eln/UI/guiCommunicate.py`)**
- Qt signal-slot communication between GUI components
- Centralized event handling system

### GUI Components (`pasta_eln/UI/`)

**Main Interface**
- `body.py`: Main content area
- `sidebar.py`: Navigation sidebar
- `details.py`: Document details view
- `form.py`: Document editing forms
- `table.py`: Tabular data display

**Configuration**
- `config/main.py`: Main configuration dialog
- `config/gui.py`: GUI-specific settings
- `config/projectGroup.py`: Project group management
- `config/setup.py`: Initial setup configuration

**Data Management**
- `data_hierarchy/`: Document type hierarchy editor
- `definitions/`: Terminology and definitions management
- `repositories/`: External repository integrations (Dataverse, Zenodo)

**Specialized Components**
- `gallery.py`: Image and media gallery
- `palette.py`: Color scheme management
- `textEditor.py`: Rich text editing
- `projectTreeView.py`: Project tree navigation

### Key Modules

**Add-ons (`pasta_eln/AddOns/`)**
- Extensible plugin system
- File extractors for different formats
- Custom form generators
- Data visualization tools

**External Integrations**
- `backendWorker/elabFTWapi.py`: eLabFTW API integration
- `backendWorker/elabFTWsync.py`: eLabFTW synchronization
- `backendWorker/inputOutput.py`: Import/export functionality

## Development Patterns

### Testing
- Tests are located in `tests/` directory
- Use pytest for running tests
- GUI tests use `QT_QPA_PLATFORM=offscreen` environment variable
- Complex integration tests are in `testsComplicated/`

### Configuration
- Main config file: `~/.pastaELN.json`
- Configuration structure defined in `fixedStringsJson.py`
- Project groups allow multiple configurations

### Database
- SQLite database with document-based storage
- Documents have hierarchical structure
- Views for different document types
- Metadata and file attachments stored together

### GUI Development
- PySide6 (Qt6) framework
- Signal-slot architecture for component communication
- Material design theming (`qt-material`)
- Custom delegates for table editing

### Code Quality Standards
- Python 3.10+ required
- Type hints enforced via mypy
- Code style enforced via pylint
- Pre-commit hooks for code quality
- Comprehensive docstrings required

## Important Notes

- The application uses a document-based database approach where each entry is a document with metadata
- All GUI components communicate through the central `Communicate` class
- The backend handles all data operations and filesystem interactions
- File extractors in AddOns/ automatically process different file types
- The application supports both standalone and research project group configurations
