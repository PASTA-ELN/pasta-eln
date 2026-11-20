""" Main methods that start the gui """
import logging
import json
import sys
import subprocess
from pathlib import Path
from urllib import request
import qdarktheme
from packaging.version import parse as parse_version
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox
from pasta_eln import __version__
from .installation_tools import hardRestart, testDataFolder
from .ui.gui_communicate import Communicate
from .ui.main_window import MainWindow


def mainGUI(projectGroup:str='') -> tuple[QCoreApplication | None, MainWindow]:
  """  Main method and entry point for commands

  Args:
      projectGroup (str): project group to load

  Returns:
    MainWindow: main window
  """
  # logging has to be started first
  logPath = Path.home() / 'pastaELN.log'
  #  old versions of basicConfig do not know "encoding='utf-8'"
  logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d:%(message)s',
                      datefmt='%m-%d %H:%M:%S')
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib','pudb']:
    logging.getLogger(package).setLevel(logging.WARNING)
  # uncaught exceptions, also from Qt slots and the backend thread, go to the log file
  sys.excepthook = lambda excType, value, tb: logging.critical('Uncaught exception', exc_info=(excType, value, tb))
  logging.info('Start PASTA GUI')
  # remainder
  if not QApplication.instance():
    application = QApplication().instance()
  else:
    application = QApplication.instance()
  comm = Communicate(projectGroup=projectGroup)
  mainWindow = MainWindow(comm)
  if 'develop' in comm.configuration:                                       # developers: copy the log to the terminal
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.getLogger().handlers[0].formatter)
    logging.getLogger().addHandler(consoleHandler)
  logging.getLogger().setLevel(getattr(logging, comm.configuration.get('GUI',{'loggingLevel':'DEBUG'})['loggingLevel']))
  import qtawesome as qta  # qtawesome and matplot cannot coexist
  if not isinstance(qta.icon('fa5s.times'), QIcon):
    logging.error('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
  # end test coexistence
  # Test if database in data folder can be written
  if comm.configuration and (problems := testDataFolder(comm.basePath)):
    logging.error('Data folder problems: %s', ' '.join(problems))
    url = 'https://pasta-eln.github.io/pasta-eln/install.html#troubleshooting'
    QMessageBox.warning(mainWindow, 'Data folder problem',
                        f'{"<br>".join(problems)}<br><br>Saving data will likely fail. Solutions are described in the '
                        f'<a href="{url}">troubleshooting instructions</a>.')
  # Test for new version
  if comm.configuration.get('GUI', {'checkForUpdates':'No'})['checkForUpdates']=='Yes' and not testNewPastaVersion(False):
    button = QMessageBox.question(mainWindow, 'Update?', 'There is a new PASTA-ELN version available. Do you want to update?',
                                  QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
    if button == QMessageBox.StandardButton.Yes:
      testNewPastaVersion(update=True)
  return application, mainWindow


def startMain(projectGroup:str='') -> None:
  """
  Main function to start GUI. Extra function is required to allow starting in module fashion

  Args:
    projectGroup (str): project group to load
  """
  qdarktheme.enable_hi_dpi()
  app, window = mainGUI(projectGroup=projectGroup)                      # exceptions: logged by sys.excepthook
  window.show()
  if app:
    app.exec()


def testNewPastaVersion(update: bool = False) -> bool:
  """Check whether this version matches the latest non-beta PyPI release
    Args:
      update (bool): whether to check for updates
    Returns:
      bool: Whether the installed version is current (true) or a beta (false) release
  """
  try:
    with request.urlopen('https://pypi.org/pypi/pasta-eln/json') as response:
      data = json.loads(response.read())
  except OSError:                                                                  # offline: treat as current
    return True
  if update:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pasta-eln'])
    hardRestart()
  releases = [release for release in data['releases'] if 'b' not in release]
  return max(releases, key=parse_version) == __version__ or 'b' in __version__


# called by python3 -m pasta_eln.gui
if __name__ == '__main__':
  startMain(sys.argv[1] if len(sys.argv)>1 else '')
