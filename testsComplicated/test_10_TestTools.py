#!/usr/bin/python3
"""TEST the form """
import logging, warnings
from pathlib import Path
from pasta_eln.installationTools import exampleData
from pasta_eln.tools import Tools
from .misc import verify, handleReport

def test_simple(qtbot):
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

  #set up
  print()
  tools = Tools()
  tools.run(['research','h','cp','v','q'])

  #remove everything and create example data
  tools.run(['research','pL','pR','q'])
  exampleData(True, None, 'research', '')

  tools.run(['research','v','ss','v','q']) #sync to server
  tools.run(['research','pL','sg','v','q']) #sync from server

  return
