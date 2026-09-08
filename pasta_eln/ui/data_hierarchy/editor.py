""" dialog to edit docType schema """
from enum import Enum
import json
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Slot
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout, QInputDialog,
                               QListWidget, QListWidgetItem, QMessageBox, QTabBar, QTableWidget, QTableWidgetItem,
                               QTabWidget, QVBoxLayout, QWidget)
from ...constants import defaultDataHierarchyNode
from ..gui_communicate import Communicate
from ..gui_style import SPACE, Button, ButtonStyle, Label
from ..icon_button_delegate import IconButtonDelegate
from ..message_dialog import showMessage
from .doc_type_edit import DocTypeEditor
from .list_free_delegate import ListFreeDelegate
from .list_item_delegate import ListItemDelegate
from .mandatory_column_delegate import MandatoryColumnDelegate
from .name_column_delegate import NameColumnDelegate

#                0       1            2      3           4      5         6
COLUMN_NAMES = ['name','description','unit','mandatory','item list','free list','move up','remove']
COLUMN_WIDTH = [100,   250,          60,    80,         150,        200,        60,       50]
pd.options.mode.copy_on_write = True

# SQL strings for Export and Import
TEMPLATE_EXPORT_QUERY = ('SELECT docTypes.docType, docTypes.title, docTypes.icon,  docTypes.shortcut, docTypes.view, '
    'docTypeSchema.class,  docTypeSchema.idx, docTypeSchema.name, docTypeSchema.unit,  docTypeSchema.mandatory, '
    'docTypeSchema.list, definitions.long FROM docTypes JOIN docTypeSchema USING (docType)  LEFT JOIN definitions '
    'ON definitions.key = (docTypeSchema.class || "." || docTypeSchema.name)')
TEMPLATE_IMPORT_COMPLETE_QUERY = 'SELECT 1 AS templateImportComplete'     # void query at end: shows all done


class SchemeEditor(QDialog):
  """ dialog to edit docType schema """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      comm (Communicate): Shared communication object.
    """
    super().__init__()
    self.comm = comm
    self.comm.backendThread.worker.beSendSQL.connect(self.onGetData)
    self.finished.connect(self._cleanup)
    self.docType = ''
    self.docLabel= ''
    self.cmd     = ''
    self.pendingImport:list[tuple[str, str]] = []
    self.df      = pd.DataFrame()
    self.docTypesLabels = [(k,v['title']) for k,v in self.comm.docTypesTitles.items()]
    self.closeButtons:list[Button] = []                                                # close buttons of tabs
    self.setWindowTitle('Item type editor')

    # GUI elements
    self.setMinimumWidth(int(np.sum(COLUMN_WIDTH))+80)
    self.setMinimumHeight(500)
    mainL = QVBoxLayout(self)
    mainL.setContentsMargins(SPACE.M, SPACE.M, SPACE.M, SPACE.M)
    mainL.setSpacing(SPACE.S)
    Label('Item type editor', 'h1', mainL)
    Label('Changes to an item type are saved immediately.', 'h3', mainL)
    docTypeW = QWidget(self)
    docTypeL = QHBoxLayout(docTypeW)
    docTypeL.setSpacing(SPACE.S)
    docTypeL.setContentsMargins(0, 0, 0, 0)
    mainL.addWidget(docTypeW)
    Label('Item type:', '', docTypeL)
    self.selectDocType = QComboBox()
    self.selectDocType.currentTextChanged.connect(self.changeDocType)
    self.selectDocType.setStyleSheet(self.comm.palette.get('secondaryText','color'))
    docTypeL.addWidget(self.selectDocType)
    docTypeL.addStretch(1)
    Button('', self, Command.NEW, docTypeL, icon='ri.add-line', tooltip='New item type', flat=True)
    Button('', self, Command.EDIT, docTypeL, icon='ri.edit-line', tooltip='Edit item type', flat=True)
    Button('', self, Command.DEL, docTypeL, icon='ri.delete-bin-line', tooltip='Remove item type', flat=True)
    Button('', self, Command.IMPORT, docTypeL, icon='fa5s.download', tooltip='Import item type template', flat=True)
    Button('', self, Command.EXPORT, docTypeL, icon='fa5s.upload', tooltip='Export item type template', flat=True)

    # tabs: empty
    self.tabW = QTabWidget(self)
    self.tabW.tabBarDoubleClicked.connect(self.renameTab)
    self.tabW.tabBarClicked.connect(self.createNewTab)
    mainL.addWidget(self.tabW, stretch=10)
    self.nameColumnDelegates     :list[NameColumnDelegate]      = []
    self.mandatoryColumnDelegates:list[MandatoryColumnDelegate] = []
    self.listItemDelegates       :list[ListItemDelegate]        = []
    self.listFreeDelegates       :list[ListFreeDelegate]        = []
    self.iconButtonDelegates     :list[IconButtonDelegate]      = []
    self.newWidget = QTableWidget()
    # Final actions
    mainL.addStretch(1)
    footer = QHBoxLayout()
    footer.addStretch()
    Button('Cancel', self, Command.CANCEL, footer)
    Button('Save', self, Command.SAVE, footer, style=ButtonStyle.HIGHLIGHTED)
    mainL.addLayout(footer)
    #initialize
    _ = [self.selectDocType.addItem(v,k) for k,v in self.docTypesLabels]
    self.selectDocType.setCurrentIndex(0)
    return


  @Slot(str, pd.DataFrame)
  def onGetData(self, cmd:str, data:pd.DataFrame) -> None:
    """ Handle data received from backend worker
    Args:
      cmd (str): command that was sent
      data (pd.DataFrame): DataFrame containing the data
    """
    if cmd == TEMPLATE_EXPORT_QUERY:                  # Save all item types and their schemas as one JSON file
      if data.empty:
        return
      fileName = QFileDialog.getSaveFileName(self, 'Save item type templates', str(Path.home()),
                                            'PASTA item type templates (*.pasta-templates.json)')[0]
      if not fileName:
        return
      if not fileName.endswith('.pasta-templates.json'):
        fileName += '.pasta-templates.json'
      docTypes = []
      for docType, group in data.groupby('docType', sort=False):
        metadata = group.iloc[0]
        schema = group[['docType', 'class', 'idx', 'name', 'unit', 'mandatory', 'list', 'long']]
        docTypes.append({'docType': docType, 'title': metadata['title'], 'icon': metadata['icon'],
                         'shortcut': metadata['shortcut'], 'view': metadata['view'],
                         'schema': schema.fillna('').to_dict(orient='records')})
      template = {'format': 'PASTA-ELN item type templates', 'version': 1, 'docTypes': docTypes}
      try:
        with open(fileName, 'w', encoding='utf-8') as templateFile:
          json.dump(template, templateFile, indent=2)
      except (OSError, TypeError, ValueError) as error:
        showMessage(self, 'File write error', f'Cannot write item type template: {error}', 'Critical')
    elif cmd == TEMPLATE_IMPORT_COMPLETE_QUERY:               # all imports are done, communicate new schema
      importedTypes = self.pendingImport
      self.pendingImport = []
      self.comm.commSendConfiguration.emit(self.comm.configuration, self.comm.projectGroup)
      for docType, title in importedTypes:
        existingIndex = self.selectDocType.findData(docType)
        if existingIndex == -1:
          self.docTypesLabels.append((docType, title))
          self.selectDocType.addItem(title, docType)
        else:
          self.docTypesLabels[existingIndex] = (docType, title)
          self.selectDocType.setItemText(existingIndex, title)
      showMessage(self, 'Templates imported', f'Imported {len(importedTypes)} item types.', 'Information')
    elif cmd==self.cmd:                                                            # Get one docType and paint
      self.df = data
      self.paint()


  def changeDocType(self, label:str) -> None:
    """ Change the item / document type

    Args:
      label (str): label of item / document type
    """
    # get data frame
    if not label:
      return
    if self.docType:
      self.finishDocType()
    self.docLabel= label
    fittingDocTypes = [k for k,v in self.docTypesLabels if v==label]
    if not fittingDocTypes:                                        #nothing to save since docType just created
      self.df = pd.DataFrame(defaultDataHierarchyNode)
      self.df['docType'] = self.selectDocType.currentData()
      self.df.drop(['PURL'], axis=1, inplace=True)
      self.df.rename(columns={'query':'long'}, inplace=True)
      self.paint()
      return
    self.docType = fittingDocTypes[0]
    self.cmd = 'SELECT docTypeSchema.docType, docTypeSchema.class, docTypeSchema.idx, docTypeSchema.name, '\
          'docTypeSchema.unit, docTypeSchema.mandatory, docTypeSchema.list, definitions.long '\
          'FROM docTypeSchema LEFT JOIN definitions ON definitions.key = (docTypeSchema.class || "." || docTypeSchema.name) '\
          f'WHERE docTypeSchema.docType=="{self.docType}"'
    self.comm.uiSendSQL.emit([{'type':'get_df', 'cmd':self.cmd}])


  def paint(self) -> None:
    """ Paint the dialog with the data """
    df = self.df.rename(columns={'long':'description'})
    df['item list'] = df['list'].apply(lambda x: '' if ',' in x or not x else self.comm.docTypesTitles[x]['title']
                                       if x in self.comm.docTypesTitles else 'Unknown docType')
    df['free list'] = df['list'].apply(lambda x: x  if ',' in x else '')
    df = df.drop('list', axis=1)
    df['idx'] = df['idx'].astype('int')
    # GUI
    self.tabW.clear()
    self.iconButtonDelegates.clear()
    for group in df['class'].unique():
      data  = df[df['class']==group]
      table = QTableWidget(len(data)+1, 8)
      table.verticalHeader().hide()
      table.setAlternatingRowColors(True)
      table.setHorizontalHeaderLabels(COLUMN_NAMES)
      table.horizontalHeader().setStyleSheet('QHeaderView::section {padding: 1px; margin: 0px;}')
      for idx, width in enumerate(COLUMN_WIDTH[:-1]):
        table.setColumnWidth(idx, width)
      for _,row in data.iterrows():
        idx = int(row['idx'])
        for col in range(6):
          table.setItem(idx, col, QTableWidgetItem(row[COLUMN_NAMES[col]]))
      #Delegates to give function to row
      self.nameColumnDelegates.append(NameColumnDelegate())
      table.setItemDelegateForColumn(0, self.nameColumnDelegates[-1])
      self.mandatoryColumnDelegates.append(MandatoryColumnDelegate())
      table.setItemDelegateForColumn(3, self.mandatoryColumnDelegates[-1])
      self.listItemDelegates.append(ListItemDelegate(self.docTypesLabels))
      table.setItemDelegateForColumn(4, self.listItemDelegates[-1])
      self.listFreeDelegates.append(ListFreeDelegate())
      table.setItemDelegateForColumn(5, self.listFreeDelegates[-1])
      self.iconButtonDelegates.append(IconButtonDelegate('fa5s.arrow-up', _hasEditableName, _moveRowUp))
      table.setItemDelegateForColumn(6, self.iconButtonDelegates[-1])
      self.iconButtonDelegates.append(IconButtonDelegate('fa5s.trash', _canDeleteRow, _deleteRow))
      table.setItemDelegateForColumn(7, self.iconButtonDelegates[-1])
      self.tabW.addTab(table, group or 'default')
    # define close buttons on some of the tabs
    self.closeButtons.clear()
    for idx in range(1, self.tabW.count()):
      self.closeButtons.append(Button('', self, (Command.DEL_GROUP, idx), icon='ri.close-line',
                                      tooltip='Remove group', flat=True))
      self.tabW.tabBar().setTabButton(idx, QTabBar.ButtonPosition.RightSide, self.closeButtons[-1])
      header = table.horizontalHeader()
      header.setStretchLastSection(True)
    self.tabW.addTab(self.newWidget, '+')
    return


  def finishDocType(self) -> None:
    """
    Finish a docType and save to DB,
    - either by selecting another docType or by pressing save
    """
    df = self.table2schema()
    # verification: uniqueness in names. etc
    unique = ( df.groupby('class')['name'].nunique() == df.groupby('class')['name'].count()  ).all()
    if not unique:
      showMessage(self, 'Invalid item type', 'Within each item type, property names must be unique. For example, '
                  'two "tags" properties are not allowed.', 'Critical')
      return
    # SAVE DATA
    dfSchema = df.drop('description', axis=1)
    dfDef = df[['class','name','description']]
    dfDef['key'] = dfDef['class']+'.'+dfDef['name']
    dfDef = dfDef.drop(['name','class'], axis=1)[['key','description']]
    dfDef.rename(columns={'description':'long'}, inplace=True)
    nonUnique = dict(dfDef.groupby(['key'])['long'].apply(lambda x: len(np.unique(x))))
    if nonUniqueStr:= ', '.join(k for k,v in nonUnique.items() if v>1):
      button = QMessageBox.question(self, 'Flatten non-unique definitions?',
                                  f'The definitions are non-unique for {nonUniqueStr}. Do you want to flatten?',
                                  QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                                  QMessageBox.StandardButton.No)
      if button == QMessageBox.StandardButton.No:
        return
    dfDef = dfDef.groupby(['key']).first()
    listDef = list(dfDef.itertuples(name=None))
    # save to sqlite
    self.comm.uiSendSQL.emit([
      {'type':'many', 'cmd':'INSERT INTO definitions (key, long, PURL) VALUES (?, ?, "") ON CONFLICT(key) DO '
                            'UPDATE SET long = excluded.long;', 'list':listDef},
      {'type':'one',  'cmd':f"DELETE FROM docTypeSchema WHERE docType == '{self.docType}'"},
      {'type':'df',   'table':'docTypeSchema', 'df':dfSchema}])
    return


  def closeDialog(self, save:bool) -> None:
    """Close the editor, optionally persisting the current item type.
      Args:
        save (bool): whether to persist changes before closing
    """
    if not save:
      self.reject()
    else:
      self.finishDocType()
      self.comm.start()
      self.accept()
    return


  def execute(self, command:'Command | tuple[Command, int]') -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    action = command[0] if isinstance(command, tuple) else command
    if action is Command.NEW:
      dialog = DocTypeEditor(self.comm, '', self.createdNewDocType)
      dialog.exec()
    elif action is Command.IMPORT: # Load templates and let the user choose which item types to add/ overwrite
      fileName = QFileDialog.getOpenFileName(self, 'Load item type template', str(Path.home()),
                                            'PASTA item type templates (*.pasta-templates.json *.json)')[0]
      if not fileName:
        return
      try:
        with open(fileName, encoding='utf-8') as templateFile:
          template = json.load(templateFile)
        itemTypes = _validateItemTypeTemplate(template)
      except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        QMessageBox.critical(self, 'Import failed', f'Cannot load item type template: {error}')
        return
      # Let user choose which to add: create dialog on the fly
      choices = QListWidget(self)
      for itemType in itemTypes:
        existing = itemType['docType'] in self.comm.docTypesTitles
        suffix = ' - overwrite existing' if existing else ''
        item = QListWidgetItem(f"{itemType['title']} ({itemType['docType']}){suffix}", choices)
        item.setData(Qt.ItemDataRole.UserRole, itemType['docType'])
        if not existing:                                        # only auto-select those that do not overwrite
          item.setCheckState(Qt.CheckState.Checked)
      selection = QDialog(self)
      selection.setWindowTitle('Select item types to import')
      layout = QVBoxLayout(selection)
      layout.addWidget(choices)
      buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
      buttons.accepted.connect(selection.accept)
      buttons.rejected.connect(selection.reject)
      layout.addWidget(buttons)
      if selection.exec() != QDialog.DialogCode.Accepted:                                   # return if Cancel
        return
      # Import
      selected = {choices.item(row).data(Qt.ItemDataRole.UserRole) for row in range(choices.count())
                  if choices.item(row).checkState() == Qt.CheckState.Checked}
      selectedTypes = [itemType for itemType in itemTypes if itemType['docType'] in selected]
      if not selectedTypes:
        return
      self.pendingImport = [(itemType['docType'], itemType['title']) for itemType in selectedTypes]
      self.comm.uiSendSQL.emit([task for itemType in selectedTypes for task in [
          {'type': 'one', 'cmd': 'INSERT INTO docTypes VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(docType) DO UPDATE SET '
            'PURL=excluded.PURL, title=excluded.title, icon=excluded.icon, shortcut=excluded.shortcut, view=excluded.view',
          'list': [itemType['docType'], '', itemType['title'], itemType['icon'], itemType['shortcut'], itemType['view']]},
          {'type': 'one', 'cmd': 'DELETE FROM docTypeSchema WHERE docType=?', 'list': [itemType['docType']]},
          {'type': 'df', 'table': 'docTypeSchema', 'df': pd.DataFrame(itemType['schema']).drop(columns=['long'])},
          {'type': 'many', 'cmd': 'INSERT INTO definitions (key, long, PURL) VALUES (?, ?, "") ON CONFLICT(key) '
           'DO UPDATE SET long = excluded.long;',
           'list': [(f"{row['class']}.{row['name']}", row['long']) for row in itemType['schema']]}]] \
            + [{'type': 'get_df', 'cmd': TEMPLATE_IMPORT_COMPLETE_QUERY}])

    elif action is Command.EXPORT:                                         # Request all item types for export
      self.comm.uiSendSQL.emit([{'type': 'get_df', 'cmd': TEMPLATE_EXPORT_QUERY}])
    elif action is Command.EDIT:
      dialog = DocTypeEditor(self.comm, self.selectDocType.currentData())
      dialog.exec()
    elif action is Command.DEL:
      button = QMessageBox.question(self, 'Remove item type?', 'Do you really want to remove this item type?',
                                    QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                                    QMessageBox.StandardButton.No)
      if button == QMessageBox.StandardButton.No:
        return
      self.comm.uiSendSQL.emit([
        {'type':'one', 'cmd':f"DELETE FROM docTypes WHERE docType == '{self.selectDocType.currentData()}'"},
        {'type':'one', 'cmd':f"DELETE FROM docTypeSchema WHERE docType == '{self.selectDocType.currentData()}'"}
      ])
      self.comm.commSendConfiguration.emit(self.comm.configuration, self.comm.projectGroup)#reset docTypes, etc.
      self.selectDocType.clear()
    elif action is Command.DEL_GROUP:
      docLabel = str(self.docLabel)
      button = QMessageBox.question(self, 'Remove group?', 'Do you really want to remove this group?',
                                    QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                                    QMessageBox.StandardButton.No)
      if button == QMessageBox.StandardButton.Yes:
        group = self.tabW.tabBar().tabText(command[1])                                   # type: ignore[index]
        self.comm.uiSendSQL.emit([{'type':'one','cmd':
          f"DELETE FROM docTypeSchema WHERE docType == '{self.docType}' AND class == '{group}'"}])
        self.changeDocType(docLabel)
    elif action is Command.CANCEL:
      self.closeDialog(False)
    elif action is Command.SAVE:
      self.closeDialog(True)
    return


  def table2schema(self) -> pd.DataFrame:
    """ save text content of tables
      Returns:
        pd.DataFrame: Schema dataframe built from the editor table.
    """
    df = pd.DataFrame()
    lastRow = 0
    for tabID in range(self.tabW.count()-1):                                           # -1: ignore last tab +
      group = self.tabW.tabBar().tabText(tabID)
      group = '' if group=='default' else group
      widget:QTableWidget = self.tabW.widget(tabID)                                 # type: ignore[assignment]
      for row in range(widget.rowCount()-1):                   # -1: ignore last row as it is meant for adding
        df.at[lastRow, 'docType'] = self.docType
        df.at[lastRow, 'class']   = group
        df.at[lastRow, 'idx']     = str(row)
        for col in range(6):
          item = widget.item(row,col)
          value = '' if item is None else item.text()
          if COLUMN_NAMES[col]=='item list' and value:
            value = [k for k,v in self.comm.docTypesTitles.items() if v['title']==value][0]
          df.at[lastRow, COLUMN_NAMES[col]] = value
        lastRow += 1
    df['list'] = df['item list']+df['free list']
    df.drop(['item list','free list'], axis=1, inplace=True)
    return df


  def renameTab(self, idx:int) -> None:
    """ rename tab after double clicking

    Args:
      idx (int): index of the tab
    """
    if 0 < idx <self.tabW.count()-1:
      textOld = self.tabW.tabText(idx)
      textNew, ok = QInputDialog.getText(self, 'Rename group', 'Enter new group name:', text=textOld)
      if ok and textNew.strip():
        self.tabW.setTabText(idx, textNew.strip())
    return


  def createNewTab(self, idx:int) -> None:
    """ Create new group

    Args:
      idx (int): index of the tab
    """
    if idx == self.tabW.count()-1:
      textNew, ok = QInputDialog.getText(self, 'Create group', 'Enter new group name:', text='')
      if ok and textNew.strip():
        self.comm.uiSendSQL.emit([{'type':'one',
                                   'cmd':f"INSERT INTO docTypeSchema VALUES ({', '.join(['?']*7)})",
                                   'list':[self.docType, textNew.strip(), '0', 'item', '', '', '']}])
        self.docType = ''                               # prevent self.finishDocType from deleting new entries
        self.changeDocType(self.docLabel)
    return


  def createdNewDocType(self,label:str, docType:str) -> None:
    """ Callback function to change docType after creating a new one

    Args:
      label (str): label of the new docType
      docType (str): name of the new docType
    """
    if docType not in [self.selectDocType.itemData(i) for i in range(self.selectDocType.count())]:
      self.selectDocType.addItem(label, docType)
    self.selectDocType.setCurrentText(label)
    return

  def _cleanup(self, _result: int) -> None:
    """Disconnect backend signals when the dialog closes.
      Args:
        _result (int): dialog result code
    """
    self.comm.backendThread.worker.beSendSQL.disconnect(self.onGetData)


class Command(Enum):
  """ Commands used in this file """
  NEW          = 1
  DEL          = 2
  EDIT         = 3
  DEL_GROUP    = 4
  SAVE         = 5
  CANCEL       = 6
  IMPORT       = 7
  EXPORT       = 8


def _hasEditableName(index: QModelIndex) -> bool:
  """Return whether a schema row represents an editable property.
    Args:
      index (QModelIndex): model index associated with the event
    Returns:
      bool: Whether the schema row has an editable name.
  """
  return bool(index.model().index(index.row(), 0).data())


def _canDeleteRow(index: QModelIndex) -> bool:
  """Keep the schema's required name, tags, and comment rows.
    Args:
      index (QModelIndex): model index associated with the event
    Returns:
      bool: Whether the schema row may be deleted.
  """
  return index.model().index(index.row(), 0).data() not in ['name', 'tags', 'comment']


def _moveRowUp(model: QAbstractItemModel, index: QModelIndex) -> None:
  """Exchange a schema row with the preceding row.
    Args:
      model (QAbstractItemModel): model being queried or updated
      index (QModelIndex): model index associated with the event
  """
  for column in range(7):
    top = model.index(index.row() - 1, column)
    current = model.index(index.row(), column)
    value = model.data(top)
    model.setData(top, model.data(current))
    model.setData(current, value)
  model.layoutChanged.emit()


def _deleteRow(model: QAbstractItemModel, index: QModelIndex) -> None:
  """Remove the selected schema row.
    Args:
      model (QAbstractItemModel): model being queried or updated
      index (QModelIndex): model index associated with the event
  """
  model.removeRow(index.row())


def _validateItemTypeTemplate(template:Any) -> list[dict[str, Any]]:
  """Validate one item-type template and return valid

  Args:
    template (Any): Parsed JSON value from an item-type template file.

  Returns:
    The validated item-type records.

  Raises:
    ValueError: If the template cannot be imported safely.
  """
  # define local
  templateSchemeColumns = {'docType', 'class', 'idx', 'name', 'unit', 'mandatory', 'list', 'long'}
  expected = {'docType', 'title', 'icon', 'shortcut', 'view', 'schema'}
  # start testing
  if not isinstance(template, dict):
    raise ValueError('Template must be a JSON object')
  docTypes = template.get('docTypes')
  if (template.get('format') != 'PASTA-ELN item type templates' or template.get('version') != 1
      or not isinstance(docTypes, list)):
    raise ValueError('Unsupported template format')
  seenDocTypes:set[str] = set()
  for itemType in docTypes:
    if not isinstance(itemType, dict) or set(itemType) != expected:
      raise ValueError('Template item type has invalid fields')
    if not all(isinstance(itemType[key], str) for key in ('docType', 'title', 'icon', 'shortcut', 'view')):
      raise ValueError('Template metadata is invalid')
    docType = itemType['docType']
    if not docType or not itemType['title'] or len(itemType['shortcut']) > 1 or docType in seenDocTypes:
      raise ValueError('Template item type has invalid or duplicate metadata')
    seenDocTypes.add(docType)
    schema = itemType['schema']
    if not isinstance(schema, list) or not schema:
      raise ValueError(f'Item type {docType} has no schema')
    schemaKeys:set[tuple[str, str]] = set()
    schemaNames:set[tuple[str, str]] = set()
    for row in schema:
      if not isinstance(row, dict) or set(row) != templateSchemeColumns:
        raise ValueError(f'Item type {docType} has invalid schema fields')
      if not all(isinstance(row[column], str) for column in templateSchemeColumns):
        raise ValueError(f'Item type {docType} has invalid schema values')
      if row['docType'] != docType or not row['name'] or not row['idx'].isdigit() or row['mandatory'] not in {'', 'T'}:
        raise ValueError(f'Item type {docType} has invalid schema values')
      schemaKey = (row['class'], row['idx'])
      schemaName = (row['class'], row['name'])
      if schemaKey in schemaKeys or schemaName in schemaNames:
        raise ValueError(f'Item type {docType} has duplicate schema fields')
      schemaKeys.add(schemaKey)
      schemaNames.add(schemaName)
  return docTypes
