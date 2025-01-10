#!/usr/bin/python3
"""TEST elabFTW server: do things that should be possible """
import logging, warnings, unittest, random, os, shutil
from datetime import datetime
from pathlib import Path
import requests
from PySide6.QtWidgets import QApplication
from anytree import PreOrderIter
from pasta_eln.backend import Backend
from pasta_eln.elabFTWsync import Pasta2Elab
from .misc import verify, handleReports


class TestStringMethods(unittest.TestCase):
  """
  derived class for this test
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.be = None
    self.dirName = ''



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
    logging.info('Start test')


    # setup and sync to server
    try:
      _ = QApplication()
    except RuntimeError:
      pass

    self.be = Backend('research')
    dirName = self.be.basePath
    self.be.exit()
    shutil.rmtree(dirName)
    os.makedirs(dirName)
    self.be = Backend('research')
    sync = Pasta2Elab(self.be, 'research')
    # sync.verbose = False

    # Sync & verify
    reports = sync.sync('gA')
    print('\n')
    handleReports(reports)
    verify(self.be)
    return

  def tearDown(self):
    logging.info('End test')
    return


if __name__ == '__main__':
  unittest.main()
