#!/usr/bin/python3
"""TEST the form """
import logging, shutil
from pathlib import Path
from pasta_eln.backend_worker.worker import Task
from pasta_eln.installation_tools import exampleData
from pasta_eln.configuration_file import getConfiguration
from pasta_eln.ui.form.form import Form
from pasta_eln.ui.gui_communicate import Communicate
from .test_03_dragDrop import verify
from .helpers import waitForBackend, waitForWorker

def test_simple(qtbot, caplog, request):
  """
  main function
  """
  logging.info('Start 10 test')

  # start app and create project
  configuration, _ = getConfiguration('research')
  # WARNING: force=True intentionally deletes the configured research storage
  # This test requires the dedicated test project group configured for this checkout
  exampleData(True, None, 'research', '')
  comm = Communicate('research')
  request.addfinalizer(comm.shutdownBackendThread)
  window = Form(comm, {'_projectID': '', 'type': ['x0']})
  qtbot.addWidget(window)
  waitForBackend(qtbot, comm)
  for idx, (key, _) in enumerate(window.allUserElements):
    elementName = f"key_{idx}"
    if key=='name':
      getattr(window, elementName).setText('A testing project')
  df, _ = waitForWorker(qtbot, comm.backendThread.worker.beSendTable, window.saveBtn.click,  # backend only in worker thread
                        lambda df, docType: docType=='x0' and (df['name']=='A testing project').any())

  # add a comment
  projID = df[df['name']=='A testing project']['id'].values[0]
  doc = {'comment':'# PASTA-ELN | The favorite ELN for experimental scientists\n - This is an example .eln output for sharing between different ELNs.',
         'id': projID}
  waitForWorker(qtbot, comm.backendThread.worker.beSendDoc,          # its reply must not be taken as the next one
                lambda: comm.uiRequestTask.emit(Task.EDIT_DOC, {'doc':doc, 'newProjID':''}))

  # test scanning
  doc = waitForWorker(qtbot, comm.backendThread.worker.beSendDoc, lambda: comm.uiRequestDoc.emit(projID))[0]
  shutil.copy(Path(__file__).parent.parent/'pasta_eln'/'Resources'/'Icons'/'pasta512.png',
              comm.basePath/doc['branch'][0]['path'])
  waitForWorker(qtbot, comm.backendThread.worker.beSendTaskReport,
                lambda: comm.uiRequestTask.emit(Task.SCAN, {'docID':projID}), lambda task, *_: task is Task.SCAN)

  # move to top: directly in the database: not sure why
  cmd = "UPDATE branches SET child='-1' WHERE path=='PastasExampleProject/pasta512.png'"
  comm.uiSendSQL.emit([{'type':'one', 'cmd':cmd}])     # no reply; worker handles verify's requests after it
  verify(qtbot, comm, projID, 0)
  print(f'{"*"*40}\nEND TEST 10\n{"*"*40}')

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
  return
