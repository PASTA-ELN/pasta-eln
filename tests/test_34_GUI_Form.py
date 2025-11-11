import logging
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.form import Form

def getTable(qtbot, comm, docType):
  table = None
  def receiveTable(t):
    nonlocal table
    table = t
  comm.backendThread.worker.beSendTable.connect(receiveTable)
  comm.uiRequestTable.emit(docType,'',True)
  while table is None:
    qtbot.wait(100)
  return table


def test_simple(qtbot, caplog):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)

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
