from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.form import Form


def test_simple(qtbot):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)

  df = comm.backendThread.worker.backend.db.getView('viewDocType/measurement')
  docID = df[df['name']=='simple.png']['id'].values[0]
  dialog = Form(comm, {'docID':docID})
  dialog.setMinimumSize(1024,800)
  dialog.show()
  qtbot.addWidget(dialog)
  path = qtbot.screenshot(dialog)
  print(path)

  comm.shutdownBackendThread()
