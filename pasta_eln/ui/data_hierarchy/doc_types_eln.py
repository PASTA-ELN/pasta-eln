""" Share docTypes with ELN files

Every ELN export contains the docTypes of its items:
- a DefinedTermSet node per docType,
- a DefinedTerm node per field, and
- PropertyValue nodes for icon, shortcut, view and list.
The docType editor exports docTypes without items; the import compares them with the project group.
"""
import json
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFileDialog, QHeaderView, QLabel, QListWidget,
                               QListWidgetItem, QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)
from ...addons import waitForBackend
from ..message_dialog import showMessage

SCHEMA_COMPARE  = ['unit', 'mandatory', 'list']                          # field properties compared during import
SCHEMA_CMD      = 'SELECT docType, class, idx, name, unit, mandatory, list FROM docTypeSchema'


class ImportAction(Enum):
  """ Import actions for docTypes; the value is the label shown to the user """
  SKIP    = 'Skip'
  ADD     = 'Add'
  MERGE   = 'Add missing fields'
  REPLACE = 'Replace'


def importDocTypes(comm:Any, widget:QWidget, fileName:str='') -> list[tuple[str,str]]:
  """ Import docTypes from an ELN file, after a preview of the differences

  Args:
    comm (Communicate): Shared communication object.
    widget (QWidget): parent widget
    fileName (str): ELN file whose items are imported next: no dialog if the docTypes do not differ; if empty, ask

  Returns:
    list: docType and title of the imported docTypes; empty if nothing was imported
  """
  withItems = bool(fileName)
  if not fileName:
    fileName = QFileDialog.getOpenFileName(widget, 'Import item types from ELN', str(Path.home()),
                                           'ELN file (*.eln)')[0]
  if not fileName:
    return []
  # read content from file
  try:
    with ZipFile(fileName) as elnFile:
      metadataFile = next(i for i in elnFile.namelist() if PurePosixPath(i).parts[1:]==('ro-crate-metadata.json',))
      graph = json.loads(elnFile.read(metadataFile))['@graph']
    nodes = {i['@id']:i for i in graph}
    docTypeInfos = []                                                          # empty for ELN files of other ELNs
    for node in graph:
      if node['@type']!='DefinedTermSet' or not node['@id'].startswith('#itemtype-') or not node.get('name') or \
         not node.get('identifier') or node['identifier'].startswith('x'):              # projects and folders
        continue
      fields = []
      for term in (nodes[i['@id']] for i in node.get('hasDefinedTerm', [])):
        termSettings = {nodes[i['@id']]['propertyID']:nodes[i['@id']]['value']
                        for i in term.get('additionalProperty',[])}
        fields.append({'group':term['termCode'].removesuffix(f".{term['name']}"), 'name':term['name'],
                       'unit':term.get('unitText',''), 'mandatory':'T' if term.get('valueRequired') else '',
                       'list':termSettings.get('list',''), 'description':term.get('description',''),
                       'PURL':term.get('sameAs','')})
      typeSettings = {nodes[i['@id']]['propertyID']:nodes[i['@id']]['value']
                      for i in node.get('additionalProperty',[])}
      docTypeInfos.append({'docType':node['identifier'], 'title':node['name'], 'PURL':node.get('sameAs','')} |
                       {key:typeSettings.get(key,'') for key in ('icon','shortcut','view')} | {'fields':fields})
  except Exception as error:
    showMessage(widget, 'Cannot read ELN file', str(error), 'Critical')
    return []
  if not docTypeInfos:
    if not withItems:
      showMessage(widget, 'Nothing to import', 'This ELN file does not contain item types.')
    return []
  # read information from PASTA-Database
  _, schema = waitForBackend(comm.backendThread.worker.beSendSQL,
                             lambda: comm.uiSendSQL.emit([{'type':'get_df', 'cmd':SCHEMA_CMD}]),
                             lambda cmd, _: cmd==SCHEMA_CMD)
  schemas:dict[str, list[dict[str,Any]]] = {docType:[] for docType in comm.docTypesTitles}
  for row in schema.fillna('').to_dict('records'):
    if row['docType'] in schemas and row['name']:
      schemas[row['docType']].append(row)
  # compare with the project group
  comparison = []
  for docTypeInfo in docTypeInfos:
    entry:dict[str,Any] = {'docType':docTypeInfo['docType'], 'title':docTypeInfo['title'], 'added':[],
                           'removed':[], 'changed':[]}
    if docTypeInfo['docType'] not in schemas:
      comparison.append(entry | {'status':'new', 'actions':[ImportAction.ADD, ImportAction.SKIP]})
      continue
    current = {(i['class'], i['name']):i for i in schemas[docTypeInfo['docType']]}
    new     = {(i['group'], i['name']):i for i in docTypeInfo['fields']}
    label   = {key:f'{key[0]}.{key[1]}' if key[0] else key[1] for key in current | new}
    entry['added']   = [label[key] for key in new if key not in current]
    entry['removed'] = [label[key] for key in current if key not in new]
    entry['changed'] = [label[key] for key in new if key in current and
                        any(new[key][i]!=current[key][i] for i in SCHEMA_COMPARE)]
    if entry['added'] or entry['removed'] or entry['changed']:
      actions = [ImportAction.MERGE, ImportAction.REPLACE, ImportAction.SKIP] if entry['added'] else \
                [ImportAction.SKIP, ImportAction.REPLACE]                           # the first is the default
      comparison.append(entry | {'status':'different', 'actions':actions})
    else:
      comparison.append(entry | {'status':'identical', 'actions':[ImportAction.SKIP]})
  if withItems and all(entry['status']=='identical' for entry in comparison):
    return []
  importDialog = DocTypeImportDialog(comparison)
  if not importDialog.exec() or not importDialog.importActions:
    return []
  # SQL tasks; the dialog offers ADD only for new docTypes, MERGE and REPLACE only for existing ones
  tasks:list[dict[str,Any]] = []
  report = []
  for docTypeInfo in docTypeInfos:
    docType = docTypeInfo['docType']
    if (action := importDialog.importActions.get(docType)) is None:
      continue
    fields = docTypeInfo['fields']
    nextIdx:dict[str,int] = {}                                                       # next free idx per group
    if action is ImportAction.MERGE:
      existing = schemas[docType]
      fields = [i for i in fields if (i['group'], i['name']) not in {(e['class'], e['name']) for e in existing}]
      for field in existing:
        nextIdx[field['class']] = max(nextIdx.get(field['class'], 0), int(field['idx'])+1)
    else:
      if action is ImportAction.REPLACE:
        tasks += [{'type':'one', 'cmd':'DELETE FROM docTypeSchema WHERE docType=?', 'list':(docType,)},
                  {'type':'one', 'cmd':'DELETE FROM docTypes WHERE docType=?', 'list':(docType,)}]
      tasks.append({'type':'one', 'cmd':'INSERT INTO docTypes (docType, PURL, title, icon, shortcut, view) '
                    'VALUES (?, ?, ?, ?, ?, ?)', 'list':(docType, docTypeInfo['PURL'], docTypeInfo['title'],
                    docTypeInfo['icon'], docTypeInfo['shortcut'], docTypeInfo['view'])})
    for field in fields:
      idx = nextIdx.get(field['group'], 0)
      nextIdx[field['group']] = idx+1
      tasks.append({'type':'one', 'cmd':'INSERT INTO docTypeSchema (docType, class, idx, name, unit, mandatory, list) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?)', 'list':(docType, field['group'], str(idx), field['name'],
                    field['unit'], field['mandatory'], field['list'])})
      # descriptions are shared between docTypes: do not overwrite existing ones, except when replacing
      if field['description'] or field['PURL']:
        conflict = 'UPDATE SET long=excluded.long, PURL=excluded.PURL' if action is ImportAction.REPLACE \
                   else 'NOTHING'
        tasks.append({'type':'one', 'cmd':f'INSERT INTO definitions (key, long, PURL) VALUES (?, ?, ?) ON CONFLICT(key) '
                      f'DO {conflict}', 'list':(f"{field['group']}.{field['name']}", field['description'],
                      field['PURL'])})
    missingLinks = {i['list'] for i in fields if i['list'] and ',' not in i['list']}.difference(
                    set(schemas) | {i['docType'] for i in docTypeInfos})
    text = {ImportAction.ADD:'added', ImportAction.MERGE:f'{len(fields)} fields added',
            ImportAction.REPLACE:'replaced'}[action]
    report.append(f'- {docTypeInfo["title"]}: {text}')
    if missingLinks:
      report.append(f'  - links to item types that do not exist: {", ".join(sorted(missingLinks))}')
  comm.uiSendSQL.emit(tasks)
  comm.start()                                                                               # reload docTypes
  showMessage(widget, 'Import item types', 'Imported item types:\n' + '\n'.join(report))
  return [(i['docType'], i['title']) for i in docTypeInfos if i['docType'] in importDialog.importActions]


class DocTypeSelectDialog(QDialog):
  """ Select the docTypes that are exported """
  def __init__(self, comm:Any, current:str=''):
    """
    Initialization

    Args:
      comm (Communicate): Shared communication object.
      current (str): docType that is selected at the start
    """
    super().__init__()
    self.selected:list[str] = []
    self.setWindowTitle('Export item types')
    mainL = QVBoxLayout(self)
    mainL.addWidget(QLabel('Select the item types to export as ELN file'))
    self.listW = QListWidget()
    for docType, info in comm.docTypesTitles.items():
      if docType.startswith('x'):                                                       # projects and folders
        continue
      item = QListWidgetItem(f"{info['title']} ({docType})")
      item.setData(Qt.ItemDataRole.UserRole, docType)
      item.setCheckState(Qt.CheckState.Checked if docType==current else Qt.CheckState.Unchecked)
      self.listW.addItem(item)
    mainL.addWidget(self.listW)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    buttons.accepted.connect(self.accept)
    buttons.rejected.connect(self.reject)
    mainL.addWidget(buttons)


  def accept(self) -> None:
    """ Accept only if a docType is selected """
    self.selected = [self.listW.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.listW.count())
                     if self.listW.item(i).checkState()==Qt.CheckState.Checked]
    if not self.selected:
      showMessage(self, 'No item type selected', 'Select at least one item type.')
      return
    super().accept()


class DocTypeImportDialog(QDialog):
  """ Preview of the docTypes of an ELN file: what differs and what should be imported """
  def __init__(self, comparison:list[dict[str,Any]]):
    """
    Initialization

    Args:
      comparison (list): comparison of each docType with the project group, from importDocTypes
    """
    super().__init__()
    self.comparison = comparison
    self.importActions:dict[str,ImportAction] = {}                                       # docType: action
    self.setWindowTitle('Import item types')
    self.setMinimumWidth(800)
    mainL = QVBoxLayout(self)
    explanation = QLabel('Select what to import for each item type of the ELN file. "Add missing fields" keeps all '
                         'existing fields unchanged. "Replace" also removes fields that are not in the ELN file and '
                         'replaces the name, icon and shortcut of the item type.')
    explanation.setWordWrap(True)
    mainL.addWidget(explanation)
    # table
    self.table = QTableWidget(len(comparison), 4)
    self.table.setHorizontalHeaderLabels(['Item type', 'Status', 'Differences', 'Import'])
    self.table.verticalHeader().hide()
    self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    self.table.setWordWrap(True)
    self.comboBoxes:list[QComboBox] = []
    for row, entry in enumerate(comparison):
      self.table.setItem(row, 0, QTableWidgetItem(f"{entry['title']} ({entry['docType']})"))
      self.table.setItem(row, 1, QTableWidgetItem(entry['status'].capitalize()))
      differences = [f"{label}: {', '.join(entry[key])}" for key, label in
                     (('added','only in ELN file'), ('removed','only here'), ('changed','changed')) if entry[key]]
      self.table.setItem(row, 2, QTableWidgetItem('\n'.join(differences)))
      self.comboBoxes.append(QComboBox())
      for action in entry['actions']:
        self.comboBoxes[-1].addItem(action.value, action)
      self.table.setCellWidget(row, 3, self.comboBoxes[-1])
    header = self.table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
    self.table.resizeColumnsToContents()
    self.table.resizeRowsToContents()
    # button box
    mainL.addWidget(self.table)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
    buttons.addButton('Import', QDialogButtonBox.ButtonRole.AcceptRole)
    buttons.accepted.connect(self.accept)
    buttons.rejected.connect(self.reject)
    mainL.addWidget(buttons)


  def accept(self) -> None:
    """ Collect the selected actions; replacing docTypes has to be confirmed, since it removes fields """
    actions = {entry['docType']:comboBox.currentData() for entry, comboBox in zip(self.comparison, self.comboBoxes)
               if comboBox.currentData() is not ImportAction.SKIP}
    if replaced := [entry for entry in self.comparison if actions.get(entry['docType']) is ImportAction.REPLACE]:
      details = [f"- {entry['title']} ({entry['docType']}): " +
                 (f"removes {', '.join(entry['removed'])}" if entry['removed'] else 'no field is removed')
                 for entry in replaced]
      answer = QMessageBox.question(self, 'Replace item types', 'Replace changes the name, icon, shortcut, fields and '
                                    'descriptions of these item types to those of the ELN file, and removes the '
                                    'fields that are not in the ELN file. The values of existing items are kept.\n\n' +
                                    '\n'.join(details) + '\n\nReplace these item types?',
                                    defaultButton=QMessageBox.StandardButton.No)
      if answer != QMessageBox.StandardButton.Yes:
        return
    self.importActions = actions
    super().accept()
