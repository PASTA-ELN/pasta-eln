"""Test a realistic, stateful workflow through the main GUI.
- Aim to increase the coverage
  - ignore external python code like markdown2html.py, etc
- Every workflow step must be followed immediately by capture_step().
"""
import io
import logging
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PySide6.QtCore import QBuffer, QIODevice, QTimer, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QDialog, QWidget

from pasta_eln.installation_tools import exampleData
from pasta_eln.ui.form.form import Form
from pasta_eln.ui.config.main import Configuration
from pasta_eln.ui.data_hierarchy.editor import SchemeEditor
from pasta_eln.ui.definitions.editor import Editor as DefinitionsEditor
from pasta_eln.ui.main_window import MainWindow
from pasta_eln.ui.project.project import Project
from pasta_eln.ui.sidebar.project_card import ProjectCard
from pasta_eln.ui.table.table import TableView
from pasta_eln.ui.workplan_creator.procedure_list_item import ProcedureListItem
from pasta_eln.ui.workplan_creator.workplan_creator_dialog import WorkplanCreatorDialog


def wait_for_backend(qtbot, comm) -> None:
  """Wait until the communication object has a usable backend."""
  qtbot.waitUntil(lambda: comm.backendThread.worker.backend.dbRaw is not None, timeout=30_000)


def table_for(window: MainWindow, docType: str) -> TableView:
  """Return the table widget for a document type from the main window."""
  for index in range(window.body.tabWidget.count()):
    widget = window.body.tabWidget.widget(index)
    if isinstance(widget, TableView) and widget.docType == docType:
      return widget
  raise AssertionError(f'No table for document type {docType!r}')


def wait_for_table(qtbot, table: TableView, predicate) -> None:
  """Wait until a table has received data satisfying ``predicate``."""
  qtbot.waitUntil(lambda: not table.data.empty and predicate(table.data), timeout=30_000)


def trigger_menu_action(menu, text: str) -> None:
  """Trigger the first menu action containing the requested text."""
  menuAction = next(action for action in menu.actions() if text in action.text())
  menuAction.trigger()


def run_modal_step(qtbot, trigger, dialogClass: type[QDialog], frames: list[Image.Image], action=None) -> None:
  """Open a modal dialog, exercise its supplied action, capture it, and cancel."""
  def interact() -> None:
    dialog = QApplication.activeModalWidget()
    if not isinstance(dialog, dialogClass):
      QTimer.singleShot(50, interact)
      return
    if action is not None:
      action(dialog)
    capture_step(dialog, frames)
    dialog.reject()

  QTimer.singleShot(0, interact)
  trigger.trigger()
  qtbot.waitUntil(lambda: QApplication.activeModalWidget() is None, timeout=30_000)


def exercise_schema_editor(qtbot, dialog: SchemeEditor, frames: list[Image.Image]) -> None:
  """Exercise reversible schema table edits before the dialog is cancelled."""
  qtbot.waitUntil(lambda: dialog.tabW.count() > 1, timeout=30_000)
  capture_step(dialog, frames)
  table = next(dialog.tabW.widget(index) for index in range(dialog.tabW.count() - 1)
               if dialog.tabW.widget(index).rowCount() > 1)
  editableRows = [row for row in range(table.rowCount() - 1)
                  if table.item(row, 0) is not None and table.item(row, 0).text() not in {'name', 'tags', 'comment'}]
  row = editableRows[0]
  # Edit a field description in the schema table.
  table.item(row, 1).setText('Temporary coverage description')
  capture_step(dialog, frames)
  # Toggle the field's mandatory radio-button delegate.
  qtbot.mouseClick(table.viewport(), Qt.LeftButton,
                   pos=table.visualRect(table.model().index(row, 3)).center())
  capture_step(dialog, frames)
  # Move the editable field upward with the arrow delegate.
  qtbot.mouseClick(table.viewport(), Qt.LeftButton,
                   pos=table.visualRect(table.model().index(row, 6)).center())
  capture_step(dialog, frames)
  # Delete the temporary field with the trash delegate.
  qtbot.mouseClick(table.viewport(), Qt.LeftButton,
                   pos=table.visualRect(table.model().index(row, 7)).center())
  capture_step(dialog, frames)


def click_form_trigger_and_save(qtbot, trigger, formName: str, comment: str) -> None:
  """Click a real GUI trigger, fill the modal form, and click Save."""
  def fill() -> None:
    dialog = QApplication.activeModalWidget()
    if (not isinstance(dialog, Form) or not dialog.allUserElements
        or dialog.projectTableData is None or dialog.projectComboBox.currentData() is None):
      QTimer.singleShot(50, fill)
      return
    nameIndex = dialog.allUserElements.index(('name', 'LineEdit'))
    getattr(dialog, f'key_{nameIndex}').setText(formName)
    if hasattr(dialog, 'textEdit_comment'):
      dialog.textEdit_comment.setPlainText(comment)
    dialog.saveBtn.click()

  QTimer.singleShot(0, fill)
  trigger.click()
  qtbot.waitUntil(lambda: QApplication.activeModalWidget() is None, timeout=30_000)


def capture_step(window: QWidget, frames: list[Image.Image]) -> None:
  """Capture a workflow step in memory for the final GIF."""
  buffer = QBuffer()
  buffer.open(QIODevice.OpenModeFlag.WriteOnly)
  window.grab().save(buffer, 'PNG')
  frame = Image.open(io.BytesIO(bytes(buffer.data()))).convert('RGB').copy()
  frameNumber = len(frames) + 1
  draw = ImageDraw.Draw(frame)
  label = f'Frame {frameNumber}'
  font = ImageFont.load_default(size=16)
  textBox = draw.textbbox((0, 0), label, font=font)
  labelHeight = textBox[3] - textBox[1]
  labelWidth = textBox[2] - textBox[0]
  left = 10
  top = frame.height - labelHeight - 10
  draw.rectangle((left - 4, top - 2, left + labelWidth + 4, frame.height - 6), fill='black')
  draw.text((left, top), label, fill='white', font=font)
  frames.append(frame)


def test_core_gui_workflow(qtbot, caplog):
  """Create and edit an entry through the composed application GUI."""
  # Reset the disposable research project group to the standard example data.
  exampleData(True, None, 'research', '')
  comm = None
  window = None
  frames: list[Image.Image] = []
  try:
    from pasta_eln.ui.gui_communicate import Communicate

    # Start communication with the backend and wait for it to initialize.
    comm = Communicate('research')
    wait_for_backend(qtbot, comm)
    # Open the main window and wait until the project sidebar is populated.
    window = MainWindow(comm)
    window.setMinimumSize(1600, 1200)
    window.show()
    qtbot.addWidget(window)
    qtbot.waitUntil(lambda: window.sidebar.projectListL.count() > 0, timeout=30_000)
    capture_step(window, frames)

    # Select the example project through its real sidebar card.
    projectCard = window.sidebar.projectListL.itemAt(0).widget()
    assert isinstance(projectCard, ProjectCard)
    qtbot.mouseClick(projectCard, Qt.LeftButton)
    qtbot.waitUntil(lambda: isinstance(window.body.tabWidget.widget(0), Project), timeout=30_000)
    project = window.body.tabWidget.widget(0)
    assert isinstance(project, Project)
    qtbot.waitUntil(lambda: project.docProj.get('name') == 'PASTAs Example Project', timeout=30_000)
    # Toggle project details and the full tree view through the visibility menu.
    project.btnVisibility.click()
    trigger_menu_action(project.btnVisibility.menu(), 'project details')
    capture_step(window, frames)
    project.btnVisibility.click()
    trigger_menu_action(project.btnVisibility.menu(), 'project details')
    capture_step(window, frames)
    project.btnVisibility.click()
    trigger_menu_action(project.btnVisibility.menu(), 'view')
    capture_step(window, frames)
    project.btnVisibility.click()
    trigger_menu_action(project.btnVisibility.menu(), 'view')
    capture_step(window, frames)
    # Toggle hidden projects and restore the normal sidebar state.
    qtbot.mouseClick(window.sidebar.showHiddenBtn, Qt.LeftButton)
    capture_step(window, frames)
    qtbot.mouseClick(window.sidebar.showHiddenBtn, Qt.LeftButton)
    capture_step(window, frames)
    # Visit the Tags list and return to the selected project.
    trigger_menu_action(window.viewMenu, 'Tags')
    capture_step(window, frames)
    qtbot.wait(500)
    projectCard = window.sidebar.projectListL.itemAt(0).widget()
    assert isinstance(projectCard, ProjectCard)
    qtbot.mouseClick(projectCard, Qt.LeftButton)
    qtbot.waitUntil(lambda: project.docProj.get('name') == 'PASTAs Example Project', timeout=30_000)
    capture_step(window, frames)

    # Open the measurement table and wait for its initial data.
    table = table_for(window, 'measurement')
    comm.changeTable.emit('measurement', comm.projectID, '')
    qtbot.waitUntil(lambda: not table.data.empty, timeout=30_000)
    capture_step(window, frames)
    # Create a new measurement through the table's New Entry button.
    originalNames = set(table.data['name'])
    # Add and remove a table filter without changing the displayed data.
    table.viewButton.click()
    trigger_menu_action(table.viewMenu, 'Add filter')
    qtbot.waitUntil(lambda: len(table.filterRows) == 1, timeout=30_000)
    capture_step(window, frames)
    table.filterRows[0].removeButton.click()
    qtbot.waitUntil(lambda: not table.filterRows, timeout=30_000)
    capture_step(window, frames)
    # Switch to gallery view and return to the table view.
    table.viewButton.click()
    trigger_menu_action(table.viewMenu, 'Gallery view')
    qtbot.waitUntil(table.gallery.isVisible, timeout=30_000)
    capture_step(window, frames)
    table.viewButton.click()
    trigger_menu_action(table.viewMenu, 'Gallery view')
    qtbot.waitUntil(table.table.isVisible, timeout=30_000)
    capture_step(window, frames)
    click_form_trigger_and_save(qtbot, table.newEntryButton, 'GUI workflow entry',
                                'Created by the core GUI workflow test.')
    capture_step(window, frames)
    # Refresh the table after the worker commits the new document.
    comm.changeTable.emit('measurement', comm.projectID, '')
    wait_for_table(qtbot, table, lambda data: 'GUI workflow entry' in set(data['name']))
    capture_step(window, frames)

    # Select the created row to display it in the Details pane.
    createdID = table.data.loc[table.data['name'] == 'GUI workflow entry', 'id'].iloc[0]
    modelRow = table.table.model().documentIds.index(createdID)
    index = table.table.model().index(modelRow, 0)
    qtbot.mouseClick(table.table.viewport(), Qt.LeftButton, pos=table.table.visualRect(index).center())
    details = window.body.detailsW
    qtbot.waitUntil(lambda: details.data.get('name') == 'GUI workflow entry', timeout=30_000)
    assert details.isVisible()
    capture_step(window, frames)
    # Close and reopen the details pane through its Actions menu.
    details.actionsButton.click()
    trigger_menu_action(details.actionsMenu, 'Close details')
    qtbot.waitUntil(lambda: not details.isVisible(), timeout=30_000)
    capture_step(window, frames)
    modelRow = table.table.model().documentIds.index(createdID)
    index = table.table.model().index(modelRow, 0)
    qtbot.mouseClick(table.table.viewport(), Qt.LeftButton, pos=table.table.visualRect(index).center())
    qtbot.waitUntil(lambda: details.data.get('name') == 'GUI workflow entry', timeout=30_000)
    capture_step(window, frames)

    # Edit the selected document through the Details pane's Edit button.
    click_form_trigger_and_save(qtbot, details.editButton, 'GUI workflow entry edited',
                                'Edited through the Details pane.')
    capture_step(window, frames)
    # Refresh after the worker commits the edited document.
    comm.changeTable.emit('measurement', comm.projectID, '')
    wait_for_table(qtbot, table, lambda data: 'GUI workflow entry edited' in set(data['name']))
    capture_step(window, frames)

    # Verify the original data remains and the edited entry is persisted.
    assert originalNames <= set(table.data['name'])
    assert 'GUI workflow entry edited' in set(table.data['name'])
    assert 'GUI workflow entry' not in set(table.data['name'])

    # Open the item type editor and cancel without changing the example schema.
    run_modal_step(qtbot, next(action for action in window.findChildren(QAction)
                               if 'Item type editor' in action.text()),
                   SchemeEditor, frames, lambda dialog: exercise_schema_editor(qtbot, dialog, frames))

    # Open the definitions editor and cancel without changing definitions.
    run_modal_step(qtbot, next(action for action in window.findChildren(QAction)
                               if 'Definitions editor' in action.text()),
                   DefinitionsEditor, frames)

    # Open every configuration tab and cancel without persisting settings.
    configAction = next(action for action in window.findChildren(QAction)
                        if 'Configuration' in action.text())
    def visitConfigurationTabs(dialog: Configuration) -> None:
      for index in range(dialog.tabW.count()):
        dialog.tabW.setCurrentIndex(index)
        qtbot.wait(100)
        capture_step(dialog, frames)
    run_modal_step(qtbot, configAction, Configuration, frames, visitConfigurationTabs)

    # Open the workplan editor, select a procedure, and add it to the workplan.
    workplanDialog = WorkplanCreatorDialog(comm)
    qtbot.addWidget(workplanDialog)
    workplanDialog.show()
    comm.storageUpdated.emit(comm.projectID)
    qtbot.waitUntil(lambda: bool(workplanDialog.leftMainWidget.procedures),
                    timeout=30_000)
    capture_step(workplanDialog, frames)
    procedureItem = workplanDialog.leftMainWidget.procedureListLayout.itemAt(1).widget()
    assert isinstance(procedureItem, ProcedureListItem)
    qtbot.mouseClick(procedureItem, Qt.LeftButton)
    qtbot.wait(500)
    capture_step(workplanDialog, frames)
    workplanDialog.centerMainWidget.addToWorkplanButton.click()
    qtbot.wait(500)
    capture_step(workplanDialog, frames)
    workplanDialog.reject()
  except BaseException:
    if window is not None:
      failurePath = Path(tempfile.gettempdir()) / 'pasta-eln-test-50-failure.png'
      window.grab().save(str(failurePath))
      logging.error('GUI workflow failed; main-window screenshot saved to %s', failurePath)
    raise
  finally:
    # Save the captured workflow steps as one inspectable repository artifact.
    if frames:
      animationPath = Path('artifacts') / 'pasta-eln-test-50-workflow.gif'
      animationPath.parent.mkdir(exist_ok=True)
      frames[0].save(animationPath, save_all=True, append_images=frames[1:], duration=1500, loop=0)
      print(f'GUI workflow animation: {animationPath.resolve()}')
    if window is not None and window.isVisible():
      window.close()
    elif comm is not None:
      comm.shutdownBackendThread()

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f'Logging errors found: {[record.getMessage() for record in errors]}'
