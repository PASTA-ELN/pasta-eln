import logging
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.form.form import Form
from .helpers import waitForBackend, waitForWorker

def getTable(qtbot, comm, docType):
  return waitForWorker(qtbot, comm.backendThread.worker.beSendTable, lambda: comm.uiRequestTable.emit(docType,'',True),
                       lambda _, tableDocType: tableDocType==docType)[0]


def test_simple(qtbot, caplog):

  comm = Communicate('research')
  waitForBackend(qtbot, comm)

  table = getTable(qtbot, comm, 'measurement')
  docID = table[table['name']=='simple.png']['id'].values[0]
  dialog = Form(comm, {'id':docID})
  dialog.setMinimumSize(1024,800)
  dialog.show()
  qtbot.addWidget(dialog)
  while True:
    qtbot.wait(100)
    if len(dialog.doc) > 2 and dialog.docTypeComboBox.count()>2:
      break
  qtbot.wait(1000)
  path = qtbot.screenshot(dialog)
  print(path)
  comm.shutdownBackendThread()

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
