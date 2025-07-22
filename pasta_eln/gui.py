""" Main methods that start the gui """
import logging
from pathlib import Path
from PySide6.QtCore import QCoreApplication                                # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon                                            # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QApplication                                 # pylint: disable=no-name-in-module
from pasta_eln import __version__
from .UI.guiCommunicate import Communicate
from .UI.mainWindow import MainWindow


def mainGUI(projectGroup:str='') -> tuple[QCoreApplication | None, MainWindow]:
  """  Main method and entry point for commands

  Args:
      projectGroup (str): project group to load

  Returns:
    MainWindow: main window
  """
  # logging has to be started first
  log_path = Path.home() / 'pastaELN.log'
  #  old versions of basicConfig do not know "encoding='utf-8'"
  logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d:%(message)s',
                      datefmt='%m-%d %H:%M:%S')
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib','pudb']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start PASTA GUI')
  # remainder
  if not QApplication.instance():
    application = QApplication().instance()
  else:
    application = QApplication.instance()
  comm = Communicate(projectGroup=projectGroup)
  mainWindow = MainWindow(comm)
  if not comm.configuration:
    raise ValueError('Configuration not loaded.')
  logging.getLogger().setLevel(getattr(logging, comm.configuration['GUI']['loggingLevel']))
  if mainWindow.comm.palette is not None and application is not None:
    mainWindow.comm.palette.setTheme(application)                                    # type: ignore [arg-type]
  import qtawesome as qta                                               # qtawesome and matplot cannot coexist
  if not isinstance(qta.icon('fa5s.times'), QIcon):
    logging.error('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
    print('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
  # end test coexistence
  logging.info('End PASTA GUI')
  return application, mainWindow


def startMain(projectGroup:str='') -> None:
  """
  Main function to start GUI. Extra function is required to allow starting in module fashion

  Args:
    projectGroup (str): project group to load
  """
  try:
    app, window = mainGUI(projectGroup=projectGroup)
    window.show()
    if app:
      app.exec()
  except Exception as e:
    logging.error(f'Error in mainGUI: {e}')


# called by python3 -m pasta_eln.gui
if __name__ == '__main__':
  startMain()
