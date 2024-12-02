
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

## Developers: Windows

### How to start Pasta ELN
- Anaconda
  - python -m pasta_eln.gui
  - DOES NOT WORK "pastaELN"

### Installation location:
- Default installation
  - C:\Users\...\AppData\Local\Programs\Python\Python311\Scripts
  - C:\Users\...\AppData\Local\Programs\Python\Python311\Lib\site-packages\pasta_eln
- Anaconda
  - C:\Users\...\anaconda3\envs\...\Scripts>
  - C:\Users\...\anaconda3\envs\...\Lib\site-packages\pasta_eln

### Reinstall /retry windows installation
- uninstall couchdb in Settings
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

### Create an installer using pyInstaller
- Anacoda -> new environment and install "pip install pyinstaller" and dependencies
- In terminal
  - cd Documents\PastaELN_src: all files in pasta-eln
  - pyinstaller pastaELN.py -F
- File is in /dist/ folder


---

## Developers: Linux
### Installation location:
- Default
  - /usr/local/lib/python3.10/dist-packages/pasta_eln

### Installation - Test - Removal
!! Be sure to have an additional backup of your previous ~/.pastaELN_v3.json !!
Installation:
``` bash
python -m venv venvPastaTest
. venvPastaTest/bin/activate
mv ~/.pastaELN_v3.json ~/.pastaELN_v3.backup.json
pip install git+https://github.com/PASTA-ELN/pasta-eln@sb_sqlite
```

Test (you can edit the code in venvPastaTest/lib/python3.12/site-packages/pasta_eln):
``` bash
python -m pasta_eln.gui
```

Removal:
``` bash
mv ~/.pastaELN_v3.backup.json ~/.pastaELN_v3.json
deactivate
rm -rf venvPastaTest/ pastaTEST/
```

---
## Convert couchdb to sqlite version
- python -m pasta_eln.serverActions
---

## Notes on all systems
Run Pasta-ELN directly from commandline without installation
- python3 -m pasta_eln.gui
- python3 -m pasta_eln.installationTools
- python3 -m pasta_eln.Tests.3Projects
- pastaELN.py in home directory of repository

---

## How to write code
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
For testing WIDGETS put this code into "pasta_eln/test.py":
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

For testing DIALOGS put this code into "pasta_eln/test.py":
``` Python
import sys
from PySide6.QtWidgets import QApplication
from .GUI.form import Form
from .backend import Backend
from .guiCommunicate import Communicate
from .GUI.palette import Palette

app = QApplication(sys.argv)
backend = Backend()
palette = Palette(app,'none')
comm = Communicate(backend,palette)
doc = backend.db.getDoc("m-3a43570c4fd84b1ab81a8863ae058fb0")
dialog = Form(comm, doc)
dialog.show()
sys.exit(app.exec())
```
and execute "python -m pasta_eln.test"

---

### Profiling
Begin...

      from cProfile import Profile
      from pstats import SortKey, Stats
      with Profile() as profile:

End...

      (Stats(profile).strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(100)) #end cProfile

For example: to profile the start of the program

      def startMain() -> None:
        """
        Main function to start GUI. Extra function is required to allow starting in module fashion
        """
        from cProfile import Profile
        from pstats import SortKey, Stats
        with Profile() as profile:
          app, window = mainGUI()
          window.show()
        (Stats(profile).strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(100)) #end cProfile
        # if app:
        #   app.exec()


### Debugging on a conventional install: linux
- 'sudo apt install python3-pudb' (not pip install)
- create small 'temp.py' into any folder, with this content
  from pasta_eln.gui import startMain
  startMain()
- start with 'pudb3 temp.py'

### Running pytests (3.12)
- python3 -m tests.test_01_3Projects

### General notes
- Find qt-awesome icons: qta-browser
- print works great in frontend and backend
