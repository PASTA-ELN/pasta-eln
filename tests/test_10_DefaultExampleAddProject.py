#!/usr/bin/python3
"""TEST the form """
import logging, warnings, shutil
from pathlib import Path
from PySide6.QtCore import QEventLoop, Slot
from pasta_eln.backendWorker.backend import Backend
from pasta_eln.backendWorker.worker import Task
from pasta_eln.installationTools import exampleData
from pasta_eln.miscTools import getConfiguration
from pasta_eln.UI.form import Form
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.palette import Palette
from .skip_test_03_dragDrop import verify

def test_simple(qtbot, caplog):
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
  logging.info('Start 10 test')

  # start app and create project
  configuration, _ = getConfiguration('research')
  exampleData(True, None, 'research', '')
  comm = Communicate('research')
  window = Form(comm, {'_projectID': '', 'type': ['x0']})
  qtbot.addWidget(window)
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)
  for idx, (key, _) in enumerate(window.allUserElements):
    elementName = f"key_{idx}"
    if key=='name':
      getattr(window, elementName).setText('A testing project')
  window.saveBtn.click()

  # add a comment
  qtbot.wait(1000)  # wait for backend to finish
  df = comm.backendThread.worker.backend.db.getView(f'viewDocType/x0')               # easy method for testing
  projID = df[df['name']=='A testing project']['id'].values[0]
  doc = {'comment':'# PASTA-ELN | The favorite ELN for experimental scientists\n - This is an example .eln output for sharing between different ELNs.',
         'id': projID}
  comm.uiRequestTask.emit(Task.EDIT_DOC, {'doc':doc, 'newProjID':''})

  # test scanning
  qtbot.wait(1000)  # wait for backend to finish
  loop = QEventLoop()# now use event loop to wait for backend to finish, nicer if using functions
  @Slot(dict)
  def getDoc(doc):
    dirName = comm.basePath/doc['branch'][0]['path']
    shutil.copy(Path(__file__).parent.parent/'pasta_eln'/'Resources'/'Icons'/'pasta512.png', dirName)
    loop.quit()
  comm.backendThread.worker.beSendDoc.connect(getDoc)
  comm.uiRequestDoc.emit(projID)
  loop.exec()
  @Slot(str)
  def didScan(_):
    loop.quit()
  comm.backendThread.worker.beSendTaskReport.connect(didScan)
  comm.uiRequestTask.emit(Task.SCAN, {'docID':projID})
  loop.exec()

  # move to top: directly in the database: not sure why
  cmd = "UPDATE branches SET child='-1' WHERE path=='PastasExampleProject/pasta512.png'"
  comm.uiSendSQL.emit([{'type':'one', 'cmd':cmd}])

  qtbot.wait(1000)  # wait for backend to finish
  verify(comm, projID, 0)
  print(f'{"*"*40}\nEND TEST 10\n{"*"*40}')
  comm.shutdownBackendThread()

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
  return
