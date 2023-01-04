# PASTA-ELN | The favorite ELN for experimental scientists

[![PyPI version](https://badge.fury.io/py/pasta-eln.svg)](https://badge.fury.io/py/pasta-eln)
[![GitHub version](https://badge.fury.io/gh/PASTA-ELN%2Fpasta-eln.svg)](https://badge.fury.io/gh/PASTA-ELN%2Fpasta-eln)
[![PyPi build](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pypi.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pypi.yml)
[![Documentation building](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/docbuild.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/docbuild.yml)
[![Linting](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pylint.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pylint.yml)

**Users: all documentation can be found at [Github-pages](https://pasta-eln.github.io/pasta-eln/)**

**This page / area is for developers and contains some helpful information for them**

## Notes for developers

### Notes on windows installation
- Installation location windows:
  - C:\Users\...\AppData\Local\Programs\Python\Python311\Scripts
  - C:\Users\...\AppData\Local\Programs\Python\Python311\Lib\site-packages\pasta_eln

#### Restart windows
- uninstall couchdb, git, pythonx2
- remove directories
  - C:\Program Files\Apache CouchDB
  - C:\Program Files\Git
  - C:\Users\....\AppData\Local\Programs\Python
  - Pasta-Folder in Documents
- remove Users\...\pastaELN.json
- restart Windows


### Notes on all systems
- Run Pasta-ELN directly from commandline without installation
  -  python -m pasta_eln.installationTools
  - pastaELN.py in home directory of repository
- find qt-awesome icons: qta-browser

### How to create a new version
1. pylint pasta_eln
2. normal commit to test all actions: pylint, documentation, ...
3. create a new version: ./commit.py "Minimal viable product" 1

### How to write small python programs that do things
``` Python
from pasta_eln.backend import Pasta
pasta = Pasta()
viewProj = pasta.db.getView('viewDocType/x0')
projID1  = [i['id'] for i in viewProj if 'PASTA' in i['value'][0]][0]
pasta.changeHierarchy(projID1)
print(pasta.outputHierarchy())
```
