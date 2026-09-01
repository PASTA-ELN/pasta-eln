import logging
from pasta_eln.backend_worker.worker import Task
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.details.details import Command, Details
from pasta_eln.ui.details.context import DetailContext, DetailOrigin
from pasta_eln.ui.details.details_hier_item import DetailsHierItem
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


def test_advanced_folder_scan_action_toggles_ignore_marker(qtbot, tmp_path):
  """Advanced Details actions create and remove the scanner's existing marker."""
  comm = Communicate('research')
  while comm.backendThread.worker.backend is None or comm.backendThread.worker.backend.dbRaw is None:
    qtbot.wait(100)
  window = Details(comm)
  qtbot.addWidget(window)
  folder = tmp_path / 'folder'
  folder.mkdir()
  window.docID = 'folder'
  window.data = {'id': 'folder', 'name': 'folder', 'type': ['x1'],
                 'branch': [{'path': 'unused', 'stack': []}]}
  window.sourcePath = lambda onlyLocal=True: folder  # type: ignore[method-assign]

  comm.configuration['GUI']['detailsLevel'] = 'Default'
  window.paintActionsMenu()
  assert not any('folder in scans' in item.text() for item in window.actionsMenu.actions())

  comm.configuration['GUI']['detailsLevel'] = 'Advanced'
  window.paintActionsMenu()
  excludeAction = next(item for item in window.actionsMenu.actions() if 'Exclude folder' in item.text())
  excludeAction.trigger()
  assert (folder / '.pastaELN_ignore').is_file()

  window.paintActionsMenu()
  includeAction = next(item for item in window.actionsMenu.actions() if 'Include folder' in item.text())
  includeAction.trigger()
  assert not (folder / '.pastaELN_ignore').exists()
  comm.shutdownBackendThread()


def test_advanced_attachments_show_current_state_and_request_addition(qtbot):
  """Advanced device details expose the default example's immutable attachment history."""
  comm = Communicate('research')
  while comm.backendThread.worker.backend is None or comm.backendThread.worker.backend.dbRaw is None:
    qtbot.wait(100)
  window = Details(comm)
  qtbot.addWidget(window)
  deviceID = getTable(qtbot, comm, 'device').query("name == 'Big instrument'").iloc[0]['id']

  comm.configuration['GUI']['detailsLevel'] = 'Default'
  comm.changeDetails.emit(DetailContext(deviceID, origin=DetailOrigin.TABLE))
  qtbot.waitUntil(lambda: window.data.get('id') == deviceID)
  assert window.attachmentSection is None

  comm.configuration['GUI']['detailsLevel'] = 'Advanced'
  window.paint()
  assert window.attachmentSection is not None
  location = window.attachmentSection.findChild(DetailsHierItem, 'attachment:Right side of instrument')
  assert location is not None
  assert 'Service' in location.content

  requests: list[tuple[Task, dict[str, object]]] = []
  comm.uiRequestTask.disconnect(comm.backendThread.worker.returnTaskReport)
  comm.uiRequestTask.connect(lambda task, data: requests.append((task, data)))
  sensorID = window.data['_attachments'][0]['candidates'][0]['id']
  window.addAttachment('Right side of instrument', sensorID, 'Installed')
  assert requests == [(Task.ADD_ATTACHMENT, {'docID': deviceID, 'location': 'Right side of instrument',
                                              'attachmentID': sensorID, 'remark': 'Installed'})]
  comm.shutdownBackendThread()
