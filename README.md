
[![PyPI version](https://badge.fury.io/py/pasta-eln.svg)](https://badge.fury.io/py/pasta-eln)
[![GitHub version](https://badge.fury.io/gh/PASTA-ELN%2Fpasta-eln.svg)](https://badge.fury.io/gh/PASTA-ELN%2Fpasta-eln)
[![PyPi build](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pypi.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pypi.yml)
[![Verify Linux install](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/installLinux.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/installLinux.yml)
[![Documentation building](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/docbuild.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/docbuild.yml)
[![Linting](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pylint.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pylint.yml)
[![MyPy](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/mypy.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/mypy.yml)

# PASTA-ELN | The favorite ELN for experimental scientists

> :warning: **Users: all documentation can be found at [Github-pages](https://pasta-eln.github.io/pasta-eln/)**
>
> **This page / area is for developers and contains some helpful information for them**

---

<!-- readme: contributors -start -->
<!-- readme: contributors -end -->

---

## Developers: notes on windows installation

### How to start Pasta ELN
- Anaconda
  - python -m pasta_eln.gui
  - DOES NOT WORK "pastaELN"

### Installation location windows:
- Default installation
  - C:\Users\...\AppData\Local\Programs\Python\Python311\Scripts
  - C:\Users\...\AppData\Local\Programs\Python\Python311\Lib\site-packages\pasta_eln
- Anaconda
  - C:\Users\...\anaconda3\envs\...\Scripts>
  - C:\Users\...\anaconda3\envs\...\Lib\site-packages\pasta_eln

### Restart windows
- (possibly) uninstall python x2
- uninstall couchdb
- remove directories
  - **C:\Program Files\Apache CouchDB**
  - C:\Users\....\AppData\Local\Programs\Python [If deleted python]
  - Pasta-Folder in Documents
- remove Users\...\.pastaELN.json
- remove shortcut on Windows desktop
- restart Windows
- **python -m pasta_eln.gui**
- go through steps and wait for restart
- after restart go to System->Configuration (ctrl-0) ->Setup-> start again
  - or have a separate button for that

---

## Developers: notes on linux installation
### Installation location:
- Default
  - /usr/local/lib/python3.10/dist-packages/pasta_eln

### Restart Linux
``` bash
rm .pastaELN.json pastaELN.log
rm -rf pastaELN/PastasExampleProject pastaELN/StandardOperatingProcedures
sudo snap stop couchdb
sudo snap remove couchdb
```

---

## Notes on all systems
### Run Pasta-ELN directly from commandline without installation
- python3 -m pasta_eln.gui
- python3 -m pasta_eln.installationTools
- python3 -m pasta_eln.Tests.3Projects
- pastaELN.py in home directory of repository

---

## How to write code
### How to create a new version
1. Lint
1. Type checking: ignore extractors to keep them simple, some mistake might still remain
2. test documentation building. The documentation can be viewed with "firefox docs/build/html/index.html"
3. run test
4. ensure extractors updated
5. do normal commit
6. create a new version:
``` bash
pylint pasta_eln
mypy pasta_eln/*.py
make -C docs html
pytest -s Tests
diff -q ../Extractors/ pasta_eln/Extractors/ |grep differ

git commit -a -m 'linting and testing'

./commit.py "Minimal viable product" 1
```
   **THIS STEP IS NECESSARY FOR ALL GITHUB-Actions TO WORK**

### Create git-commit-hook
To automatically run many tests, create a file '.git/hooks/pre-commit' and make it executable
``` bash
#!/bin/sh
#
# Test if extractors updated
if [ "$(diff -q ../Extractors/ pasta_eln/Extractors/ |grep differ |grep extractor)" ]; then
  echo "Differences in EXTRACTOR EXIST"
  exit 1
else
  echo "All is correct: extractors match"
fi
# Run pylint
exec pylint pasta_eln
# Run mypy
exec mypy pasta_eln/*.py
# Test document creation
exec make -C docs html
# Run pytest
exec pytest -s tests
#
echo 'Pre-commit-tests are finished'
```

### How to write small python programs that do things
#### Backend
``` Python
from pasta_eln.backend import Pasta
pasta = Pasta()
viewProj = pasta.db.getView('viewDocType/x0')
projID1  = [i['id'] for i in viewProj if 'PASTA' in i['value'][0]][0]
pasta.changeHierarchy(projID1)
print(pasta.outputHierarchy())
```

#### Frontend
For testing widgets put this code into "pasta_eln/test.py":
``` Python
from PySide6.QtWidgets import QApplication, QMainWindow
from .backend import Backend
from .communicate import Communicate
from .widgetDetails import Details

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.backend = Backend()
    comm = Communicate(self.backend)
    widget = Details(comm)
    self.setCentralWidget(widget)
    comm.changeDetails.emit('m-a23019163b9c4fccb4edaab0feb2b5ee')

app = QApplication()
window = MainWindow()
window.show()
app.exec()
```
and execute "python -m pasta_eln.test"

For testing dialogs put this code into "pasta_eln/test.py":
``` Python
import sys
from PySide6.QtWidgets import QApplication
from .dialogForm import Form
from .backend import Backend
from .communicate import Communicate

app = QApplication(sys.argv)
backend = Backend()
doc = {'_id': 's-4cf85492d9684601b70e057c278e4ab5', '_rev': '1-3fbe417334a18b29e9f3180847dbae2b'}
dialog = Form(backend, doc)
dialog.show()
sys.exit(app.exec())
```
and execute "python -m pasta_eln.test"

#### General notes
- Find qt-awesome icons: qta-browser
- print works great in frondend and backend
- magic order of creating widgets and layouts
  1. define widget
  2. define layout and immediately assign widget
  3. define and add immediately subwidgets to layout


#### HOW TO DIFF Version-1 and Version-2
**COMPARE BOTH DIRECTIONS**
at .. pasta-eln$ and remember the changes required to Version2 in first change. If nothing to remember, do not execute 2nd command
``` bash
kdiff pasta_eln/miscTools.py ../Python/miscTools.py
kdiff ../Python/miscTools.py pasta_eln/miscTools.py
kdiff pasta_eln/inputOutput.py ../Python/inputOutput.py
kdiff ../Python/inputOutput.py pasta_eln/inputOutput.py
kdiff pasta_eln/database.py ../Python/database.py
kdiff ../Python/database.py pasta_eln/database.py
kdiff pasta_eln/backend.py ../Python/backend.py
kdiff ../Python/backend.py pasta_eln/backend.py
```
Desired Differences:
- miscTools:
  - Version1 has colors at the beginning and few additional functions at the end
- inputOutput:
  - NO differences
- database:
  - imports are different
  - __init__ arguments are different
  - Version1 has testUser
  - colorDefinition is small-case in one and upper-case in the other
- backend:
  - imports and base-class different


Differences don't matter:
- subdirectories
- __init__.py
-



---

## Test couchDB running
- CouchDB at HTTP! [http://127.0.0.1:5984/_utils/#login](http://127.0.0.1:5984/_utils/#login)
- curl -f http://127.0.0.1:5984/
- curl -X POST -H "Content-Type: application/json; charset=utf-8" -d '{"name": "*+*", "password": "*+*"}' http://127.0.0.1:5984/_session
