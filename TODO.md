# Steps
- diff current and windows version
- in database.py remove link to serverTools and temporarily remove serverTools
- Stack is incorrect, and branch-path should always be in linux notation
  stack should not include own-id

## Optimize installation
- QtPy-2.3.0 (should be installed in the dependency tree)
- Perhaps: fixed version number gitannex and datalad

## Cleaning
- reduce self.
- commenting, pylint
- (HT) replace documentation
- rename backend. -> be.; don't call it pasta

## Optimize everything
- separate backend.py into CLI
- edit

# General hints
- setup.cfg: pytest


