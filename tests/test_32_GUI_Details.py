import logging
from pathlib import Path
from types import SimpleNamespace
from pasta_eln.backend_worker.worker import Task
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.details.details import Command, Details
from pasta_eln.ui.details.context import DetailContext, DetailOrigin
from .test_34_GUI_Form import getTable

def test_simple(qtbot, caplog):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None or comm.backendThread.worker.backend.dbRaw is None:
    qtbot.wait(100)
  window = Details(comm)
  window.setMinimumSize(300, 800)
  window.show()
  qtbot.addWidget(window)

  table = getTable(qtbot, comm, 'measurement')
  docIDs = table['id'].values[:3].tolist()
  print(docIDs)

  for i in range(3):
    window.comm.changeDetails.emit(DetailContext(docIDs[i], origin=DetailOrigin.TABLE))
    qtbot.wait(1000)
    path = qtbot.screenshot(window)
    print(path)

  comm.shutdownBackendThread()

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"


def test_edit_requests_document_by_id(qtbot):
  """The form must fetch the full document instead of treating it as a group edit."""
  comm = Communicate('research')
  while comm.backendThread.worker.backend is None or comm.backendThread.worker.backend.dbRaw is None:
    qtbot.wait(100)
  window = Details(comm)
  qtbot.addWidget(window)
  formDocs: list[dict[str, str]] = []
  comm.formDoc.connect(formDocs.append)

  docID = getTable(qtbot, comm, 'measurement').iloc[0]['id']
  comm.changeDetails.emit(DetailContext(docID, origin=DetailOrigin.TABLE))
  qtbot.waitUntil(lambda: window.docID == docID and window.data.get('id') == docID)
  window.onEditButtonClicked()

  assert formDocs == [{'id': docID}]
  comm.shutdownBackendThread()


def test_rerun_extractors_uses_table_request(qtbot):
  """Rerunning from Details uses the same all-recipes request as the table."""
  comm = Communicate('research')
  while comm.backendThread.worker.backend is None or comm.backendThread.worker.backend.dbRaw is None:
    qtbot.wait(100)
  window = Details(comm)
  qtbot.addWidget(window)
  requests: list[tuple[Task, dict[str, object]]] = []
  comm.uiRequestTask.connect(lambda task, data: requests.append((task, data)))

  docID = getTable(qtbot, comm, 'measurement').iloc[0]['id']
  window.docID = docID
  window.execute(Command.RERUN_EXTRACTOR)

  assert requests == [(Task.EXTRACTOR_RERUN, {'docIDs': [docID], 'recipe': ''})]
  comm.shutdownBackendThread()


def test_shared_locations_use_selected_project_branch():
  """Details describes and acts on the branch selected in the project tree."""
  class DetailState:
    currentBranch = Details.currentBranch
    sourcePath = Details.sourcePath

  window = DetailState()
  docID = 'm-shared'
  firstBranch = {'stack': ['x-project', 'x-analysis'], 'path': 'Project/Analysis/first.csv', 'child': 0, 'show': [True]}
  secondBranch = {'stack': ['x-project', 'x-archive'], 'path': 'Project/Archive/second.csv', 'child': 1, 'show': [True]}
  window.docID = docID
  window.context = DetailContext(docID, 'x-project/x-archive/m-shared', DetailOrigin.PROJECT)
  window.comm = SimpleNamespace(basePath=Path('/database'))
  window.data = {'id': docID, 'name': 'shared data', 'type': ['measurement'],
                 'branch': [firstBranch, secondBranch], 'tags': []}

  assert window.sourcePath() == window.comm.basePath / secondBranch['path']
