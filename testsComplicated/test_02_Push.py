#!/usr/bin/python3
"""TEST set up elabFTW server and test repetition of sync """
import logging, warnings, unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from pasta_eln.backend import Backend
from pasta_eln.elabFTWsync import Pasta2Elab
from .misc import verify, handleReport


class TestStringMethods(unittest.TestCase):
  """
  derived class for this test
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.be = None


  def test_main(self):
    """
    main function
    """
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)
    logPath = Path.home()/'pastaELN.log'
    logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                        datefmt='%m-%d %H:%M:%S')   #This logging is always info, since for installation only
    for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib.font_manager']:
      logging.getLogger(package).setLevel(logging.WARNING)

    # setup and sync to server
    try:
      _ = QApplication()
    except RuntimeError:
      pass
    self.be = Backend('research')
    sync = Pasta2Elab(self.be, 'research', True)
    sync.verbose = False
    report = sync.sync('sA')
    handleReport(report, [15,0,0,0,0])

    # sync again: nothing should change
    print('\n\n=============================\nSecond sync: everything the same since HARD SEND\n============================')
    report = sync.sync('sA')
    handleReport(report, [15,0,0,0,0])

    # verify
    verify(self.be)
    return


  def tearDown(self):
    logging.info('End test')
    return


if __name__ == '__main__':
  unittest.main()
