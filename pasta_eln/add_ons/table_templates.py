""" Templates: share item types and items between project groups and with other people

A template is a JSON file that can contain
- itemTypes: item types with their fields, as defined in the item type editor
- items: items with their key-value pairs, used to create new items. The item type of an item is also included,
  so that it can be imported into project groups that do not have it.

This table add-on (More > Table add-ons above a list) offers
- export the selected items of the list (all items, if none is selected) as template
- export item types as template
- import item types from a template, with a preview of the differences
- create a new item from a template in the current project. Workflow items are created as Markdown file, since the
  database only stores the beginning of the content.

The add-on runs in the frontend: it requests data from the backend worker with the signal system (see _query) and
changes the database with parameterized SQL commands.
"""
import json
import re
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable
import pandas as pd
from PySide6.QtCore import Qt, Slot
from shiboken6 import isValid
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFileDialog, QHeaderView, QInputDialog, QLabel,
                               QListWidget, QListWidgetItem, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)
from pasta_eln import __version__
from pasta_eln.backend_worker.worker import Task
from pasta_eln.misc_tools import getDoc, isDocID
from pasta_eln.ui.message_dialog import showMessage

# The following two variables are mandatory
description  = 'Templates: import and export…'  # short description shown in the menu
reqParameter:dict[str,str] = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}

TEMPLATE_FORMAT  = 'PASTA-ELN template'
TEMPLATE_VERSION = 1
SCHEMA_COMPARE   = ['unit', 'mandatory', 'list']                         # field properties compared during import
# groups of an item that are not part of a template: they belong to the specific file / measurement
SKIPPED_GROUPS   = ['metaVendor', 'metaUser']
DOC_TYPES_CMD    = 'SELECT docType, PURL, title, icon, shortcut, view FROM docTypes'
SCHEMA_CMD       = 'SELECT docType, class, idx, name, unit, mandatory, list FROM docTypeSchema'
DEFINITIONS_CMD  = 'SELECT key, long, PURL FROM definitions'
QUERY_TIMEOUT    = 20                                                    # seconds to wait for the backend


class ImportAction(Enum):
  """ Import actions for item types; the value is the label shown to the user """
  SKIP    = 'Skip'
  ADD     = 'Add'
  MERGE   = 'Add missing fields'
  REPLACE = 'Replace'


def main(comm:Any, data:pd.DataFrame, widget:QWidget, parameter:dict[str,Any]={}) -> bool:
  """ main function: has to exist and is called by the menu

  Args:
    comm (Communicate): Shared communication object.
    data (pd.DataFrame): selected rows of the list (all rows if none is selected), with a docID column
    widget (QWidget): table widget, allows to create new gui dialogs
    parameter (dict): ability to pass parameters

  Returns:
    bool: success
  """
  docIDs = [] if data is None or 'docID' not in data else [i for i in data['docID'] if not i.startswith('x')]
  dialog = TemplateDialog(comm, docIDs, widget)
  dialog.exec()
  return dialog.success


######################################################################
# Templates: independent of the GUI
######################################################################
def _text(value:Any) -> str:
  """ Database value as text: None is empty

  Args:
    value (Any): value from the database

  Returns:
    str: text
  """
  return '' if value is None else str(value)


def projectGroupSchemas(docTypes:pd.DataFrame, schema:pd.DataFrame) -> dict[str, list[dict[str,Any]]]:
  """ Fields of all item types of the project group

  Args:
    docTypes (pd.DataFrame): result of DOC_TYPES_CMD
    schema (pd.DataFrame): result of SCHEMA_CMD

  Returns:
    dict: docType: fields as in the docTypeSchema table (keys class, idx, name, unit, mandatory, list)
  """
  result:dict[str, list[dict[str,Any]]] = {docType:[] for docType in docTypes['docType']}
  for row in schema.to_dict('records'):
    if row['docType'] in result and row['name']:
      result[row['docType']].append(row)
  return result


def projectGroupDefinitions(definitions:pd.DataFrame) -> dict[str, tuple[str,str]]:
  """ Descriptions and PURLs of all keys of the project group

  Args:
    definitions (pd.DataFrame): result of DEFINITIONS_CMD

  Returns:
    dict: key: (description, PURL)
  """
  return {row['key']:(_text(row['long']), _text(row['PURL'])) for row in definitions.to_dict('records')}


def itemTypeTemplate(docType:str, docTypes:pd.DataFrame, schemas:dict[str, list[dict[str,Any]]],
                     definitions:dict[str, tuple[str,str]]) -> dict[str,Any]:
  """ Item type with its fields

  Args:
    docType (str): item type
    docTypes (pd.DataFrame): result of DOC_TYPES_CMD
    schemas (dict): result of projectGroupSchemas
    definitions (dict): result of projectGroupDefinitions

  Returns:
    dict: item type template
  """
  rows = docTypes[docTypes['docType']==docType].to_dict('records')
  if not rows:
    raise ValueError(f'Item type {docType} does not exist.')
  fields = []
  for field in sorted(schemas[docType], key=lambda i:(i['class'], int(i['idx']))):
    longText, purl = definitions.get(f"{field['class']}.{field['name']}", ('', ''))
    fields.append({'group':_text(field['class']), 'name':field['name'], 'unit':_text(field['unit']),
                   'mandatory':_text(field['mandatory']), 'list':_text(field['list']), 'description':longText,
                   'PURL':purl})
  return {'docType':docType} | {key:_text(rows[0][key]) for key in ('title', 'icon', 'shortcut', 'PURL', 'view')} | \
         {'fields':fields}


def itemTemplate(doc:dict[str,Any], withValues:bool) -> dict[str,Any]:
  """ Item with its key-value pairs

  Args:
    doc (dict): item as returned by the database
    withValues (bool): include values, comment, content and tags; otherwise only keys and units

  Returns:
    dict: item template
  """
  properties = []
  for group, content in doc.items():
    if not isinstance(content, dict) or group in SKIPPED_GROUPS or group in ['branch']:
      continue
    for key, value in content.items():
      if isinstance(value, tuple|list):
        value, unit = value[0], value[1]
      else:
        unit = ''
      value = '' if value is None else str(value)
      if not withValues or isDocID(value):                     # links to other items only exist in this database
        value = ''
      properties.append({'group':group, 'key':key, 'value':value, 'unit':unit or ''})
  item = {'docType':'/'.join(doc['type']), 'name':doc.get('name',''), 'properties':properties}
  if withValues:
    item |= {'comment':doc.get('comment',''), 'content':doc.get('content',''),
             'tags':[i for i in doc.get('tags',[]) if not i.startswith('_')]}               # without rating
  return item


def newTemplate(itemTypes:list[dict[str,Any]], items:list[dict[str,Any]]) -> dict[str,Any]:
  """ Template with header

  Args:
    itemTypes (list): result of itemTypeTemplate for each item type
    items (list): result of itemTemplate for each item

  Returns:
    dict: template
  """
  return {'format':TEMPLATE_FORMAT, 'version':TEMPLATE_VERSION, 'pastaELN':__version__,
          'exported':datetime.now().isoformat(timespec='seconds'), 'itemTypes':itemTypes, 'items':items}


def writeTemplate(template:dict[str,Any], fileName:str|Path) -> None:
  """ Write template to a JSON file

  Args:
    template (dict): template
    fileName (str, Path): file name
  """
  with open(fileName, 'w', encoding='utf-8') as fOut:
    json.dump(template, fOut, indent=2, ensure_ascii=False)


def readTemplate(fileName:str|Path) -> dict[str,Any]:
  """ Read and verify a template file

  Args:
    fileName (str, Path): file name

  Returns:
    dict: template

  Raises:
    ValueError: if the file is not a valid template
  """
  try:
    with open(fileName, encoding='utf-8') as fIn:
      template = json.load(fIn)
  except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
    raise ValueError(f'Cannot read template: {error}') from None
  if not isinstance(template, dict) or template.get('format')!=TEMPLATE_FORMAT:
    raise ValueError('This file is not a PASTA-ELN template.')
  if template.get('version', 0) > TEMPLATE_VERSION:
    raise ValueError('This template was created by a newer version of PASTA-ELN. Update PASTA-ELN to import it.')
  for itemType in template.get('itemTypes', []):
    if not itemType.get('docType') or not itemType.get('title') or not isinstance(itemType.get('fields'), list) or \
       any(not field.get('name') for field in itemType['fields']) or itemType['docType'].startswith('x'):
      raise ValueError('The template contains an invalid item type.')
  for item in template.get('items', []):
    if not item.get('docType') or not isinstance(item.get('properties', []), list):
      raise ValueError('The template contains an invalid item.')
  return template


def compareItemTypes(template:dict[str,Any], schemas:dict[str, list[dict[str,Any]]]) -> list[dict[str,Any]]:
  """ Compare the item types of a template with those in the project group

  Args:
    template (dict): template
    schemas (dict): result of projectGroupSchemas

  Returns:
    list: per item type of the template: docType, title, status ('new', 'identical', 'different'),
          added (fields only in template), removed (fields only in project group), changed (fields that differ)
          and the possible actions (first is the default)
  """
  result = []
  for itemType in template.get('itemTypes', []):
    entry:dict[str,Any] = {'docType':itemType['docType'], 'title':itemType['title'], 'added':[], 'removed':[],
                           'changed':[]}
    if itemType['docType'] not in schemas:
      result.append(entry | {'status':'new', 'actions':[ImportAction.ADD, ImportAction.SKIP]})
      continue
    current = {(i['class'], i['name']):i for i in schemas[itemType['docType']]}
    new     = {(i['group'], i['name']):i for i in itemType['fields']}
    entry['added']   = [_fieldLabel(key) for key in new if key not in current]
    entry['removed'] = [_fieldLabel(key) for key in current if key not in new]
    entry['changed'] = [_fieldLabel(key) for key in new if key in current and
                        any(_text(new[key].get(i))!=_text(current[key].get(i)) for i in SCHEMA_COMPARE)]
    if entry['added'] or entry['removed'] or entry['changed']:
      actions = [ImportAction.MERGE, ImportAction.REPLACE, ImportAction.SKIP] if entry['added'] else \
                [ImportAction.SKIP, ImportAction.REPLACE]
      result.append(entry | {'status':'different', 'actions':actions})
    else:
      result.append(entry | {'status':'identical', 'actions':[ImportAction.SKIP]})
  return result


def _fieldLabel(key:tuple[str,str]) -> str:
  """ Field name shown to the user: group.name or name in the default group

  Args:
    key (tuple): group, name

  Returns:
    str: label
  """
  return f'{key[0]}.{key[1]}' if key[0] else key[1]


def importTasks(template:dict[str,Any], actions:dict[str,ImportAction],
                schemas:dict[str, list[dict[str,Any]]]) -> tuple[list[dict[str,Any]], str]:
  """ SQL commands that import the item types of a template into the project group

  Args:
    template (dict): template
    actions (dict): docType: ImportAction. Item types that are not listed are skipped.
      - ADD: create the item type (only if it does not exist)
      - MERGE: add the fields that the item type does not have; existing fields are not changed
      - REPLACE: replace the fields and the title, icon, ... of the item type
    schemas (dict): result of projectGroupSchemas

  Returns:
    list: SQL tasks for comm.uiSendSQL
    str: report
  """
  tasks:list[dict[str,Any]] = []
  report = []
  for itemType in template.get('itemTypes', []):
    docType = itemType['docType']
    action = actions.get(docType, ImportAction.SKIP)
    if action is ImportAction.SKIP:
      continue
    if action is ImportAction.ADD and docType in schemas or \
       action in (ImportAction.MERGE, ImportAction.REPLACE) and docType not in schemas:
      report.append(f'- {itemType["title"]}: not imported, since the item type '
                    f'{"exists" if action is ImportAction.ADD else "does not exist"}')
      continue
    fields = itemType['fields']
    nextIdx:dict[str,int] = {}                                                    # next free idx per group
    if action is ImportAction.MERGE:
      current = schemas[docType]
      fields = [i for i in fields if (i['group'], i['name']) not in {(c['class'], c['name']) for c in current}]
      for field in current:
        nextIdx[field['class']] = max(nextIdx.get(field['class'], 0), int(field['idx'])+1)
    else:
      if action is ImportAction.REPLACE:
        tasks += [_sql('DELETE FROM docTypeSchema WHERE docType=?', (docType,)),
                  _sql('DELETE FROM docTypes WHERE docType=?', (docType,))]
      tasks.append(_sql('INSERT INTO docTypes (docType, PURL, title, icon, shortcut, view) VALUES (?, ?, ?, ?, ?, ?)',
                        (docType, itemType.get('PURL',''), itemType['title'], itemType.get('icon',''),
                         itemType.get('shortcut',''), itemType.get('view',''))))
    for field in fields:
      idx = nextIdx.get(field['group'], 0)
      nextIdx[field['group']] = idx+1
      tasks.append(_sql('INSERT INTO docTypeSchema (docType, class, idx, name, unit, mandatory, list) '
                        'VALUES (?, ?, ?, ?, ?, ?, ?)', (docType, field['group'], str(idx), field['name'],
                        field.get('unit',''), field.get('mandatory',''), field.get('list',''))))
      # descriptions are shared between item types: do not overwrite existing ones, except when replacing
      if field.get('description') or field.get('PURL'):
        conflict = 'UPDATE SET long=excluded.long, PURL=excluded.PURL' if action is ImportAction.REPLACE \
                   else 'NOTHING'
        tasks.append(_sql(f'INSERT INTO definitions (key, long, PURL) VALUES (?, ?, ?) ON CONFLICT(key) DO {conflict}',
                          (f"{field['group']}.{field['name']}", field.get('description',''), field.get('PURL',''))))
    missingLinks = {i['list'] for i in fields if i.get('list') and ',' not in i['list']}.difference(
                    set(schemas) | {i['docType'] for i in template.get('itemTypes', [])})
    text = {ImportAction.ADD:'added', ImportAction.MERGE:f'{len(fields)} fields added',
            ImportAction.REPLACE:'replaced'}[action]
    report.append(f'- {itemType["title"]}: {text}')
    if missingLinks:
      report.append(f'  - links to item types that do not exist: {", ".join(sorted(missingLinks))}')
  return tasks, '\n'.join(report) if report else 'Nothing imported.'


def _sql(cmd:str, parameters:tuple[Any,...]) -> dict[str,Any]:
  """ SQL task for comm.uiSendSQL

  Args:
    cmd (str): parameterized SQL command
    parameters (tuple): parameters

  Returns:
    dict: task
  """
  return {'type':'one', 'cmd':cmd, 'list':parameters}


def isMarkdownItem(item:dict[str,Any]) -> bool:
  """ Items of the template that are created as Markdown file: all workflow items

  Args:
    item (dict): item of a template

  Returns:
    bool: True if the item is created as Markdown file
  """
  return item['docType'].split('/')[0] == 'workflow'


def writeMarkdown(item:dict[str,Any], folder:Path) -> Path:
  """ Write the content of an item of a template to a new Markdown file

  Args:
    item (dict): item of a template
    folder (Path): folder in which the file is created; existing files are not overwritten

  Returns:
    Path: the new file
  """
  stem = re.sub(r'[^\w.-]+', '_', item.get('name') or '').strip('_.') or 'template'
  stem = stem[:-3] if stem.lower().endswith('.md') else stem
  path, number = folder/f'{stem}.md', 1
  while path.exists():
    path, number = folder/f'{stem}_{number}.md', number+1
  content = item.get('content') or f"# {item.get('name') or stem}\n"
  with open(path, 'x', encoding='utf-8') as fOut:
    fOut.write(content)
  return path


def templateToDoc(item:dict[str,Any], definitions:dict[str, tuple[str,str]]) -> dict[str,Any]:
  """ Convert an item of a template into a document that the backend saves as new item

  Args:
    item (dict): item of a template
    definitions (dict): result of projectGroupDefinitions; saving a key writes its description, so the existing
      description is passed along

  Returns:
    dict: document with type, tags, comment, content and the key-value pairs as (value, unit, description, PURL)
  """
  doc:dict[str,Any] = {'type':item['docType'].split('/'), 'tags':list(item.get('tags', []))}
  for key in ('comment', 'content'):
    if item.get(key):
      doc[key] = item[key]
  for prop in item.get('properties', []):
    group = prop.get('group','')
    longText, purl = definitions.get(f"{group}.{prop['key']}", ('', ''))
    doc.setdefault(group, {})[prop['key']] = (prop.get('value',''), prop.get('unit',''), longText, purl)
  return doc


######################################################################
# GUI: communication with the backend, actions and dialogs
######################################################################
def _query(comm:Any, cmd:str) -> pd.DataFrame:
  """ Request data from the database of the backend worker and wait for it

  Args:
    comm (Communicate): Shared communication object.
    cmd (str): SQL query

  Returns:
    pd.DataFrame: result
  """
  result:pd.DataFrame|None = None
  @Slot(str, pd.DataFrame)
  def receiveData(cmdReceived:str, data:pd.DataFrame) -> None:
    """ Slot to receive data
    Args:
      cmdReceived (str): SQL query of this data
      data (pd.DataFrame): result
    """
    nonlocal result
    if cmdReceived == cmd:
      result = data
  comm.backendThread.worker.beSendSQL.connect(receiveData)
  comm.uiSendSQL.emit([{'type':'get_df', 'cmd':cmd}])
  start = time.time()
  while result is None and time.time()-start < QUERY_TIMEOUT:
    time.sleep(0.05)
  comm.backendThread.worker.beSendSQL.disconnect(receiveData)
  if result is None:
    raise TimeoutError('The database did not answer.')
  return result


def _projectGroupData(comm:Any) -> tuple[pd.DataFrame, dict[str, list[dict[str,Any]]], dict[str, tuple[str,str]]]:
  """ Item types, their fields and the definitions of the project group

  Args:
    comm (Communicate): Shared communication object.

  Returns:
    tuple: result of DOC_TYPES_CMD, projectGroupSchemas, projectGroupDefinitions
  """
  docTypes = _query(comm, DOC_TYPES_CMD)
  return docTypes, projectGroupSchemas(docTypes, _query(comm, SCHEMA_CMD)), \
         projectGroupDefinitions(_query(comm, DEFINITIONS_CMD))


def _saveFileName(widget:QWidget, title:str, defaultName:str) -> str:
  """ Ask for the file name of a template

  Args:
    widget (QWidget): parent widget
    title (str): title of the dialog
    defaultName (str): proposed file name without extension

  Returns:
    str: file name ending with .json; empty if canceled
  """
  fileName = QFileDialog.getSaveFileName(widget, title, str(Path.home()/f'{defaultName}.json'), 'Template (*.json)')[0]
  return fileName + ('' if not fileName or fileName.endswith('.json') else '.json')


def _openTemplate(widget:QWidget, title:str) -> dict[str,Any]:
  """ Ask for a template file and read it

  Args:
    widget (QWidget): parent widget
    title (str): title of the dialog

  Returns:
    dict: template; empty if canceled or invalid
  """
  fileName = QFileDialog.getOpenFileName(widget, title, str(Path.home()), 'Template (*.json)')[0]
  if not fileName:
    return {}
  try:
    return readTemplate(fileName)
  except ValueError as error:
    showMessage(widget, 'Cannot use template', str(error), 'Critical')
    return {}


def exportItems(comm:Any, docIDs:list[str], widget:QWidget) -> bool:
  """ Export items as template, together with their item types

  Args:
    comm (Communicate): Shared communication object.
    docIDs (list): items to export
    widget (QWidget): parent widget

  Returns:
    bool: success
  """
  message = QMessageBox(widget)
  message.setWindowTitle('Export as template')
  message.setText(f'Export {len(docIDs)} item{"s" if len(docIDs)>1 else ""} as template for new items. Should the '
                  'template include the values, comment and tags, or only the keys and units?')
  valuesButton = message.addButton('With values', QMessageBox.ButtonRole.AcceptRole)
  keysButton = message.addButton('Keys and units only', QMessageBox.ButtonRole.AcceptRole)
  message.addButton(QMessageBox.StandardButton.Cancel)
  message.exec()
  if message.clickedButton() not in (valuesButton, keysButton):
    return False
  withValues = message.clickedButton() is valuesButton
  docs = [getDoc(comm, docID) for docID in docIDs]
  fileName = _saveFileName(widget, 'Export as template',
                           re.sub(r'[^\w.-]+', '_', docs[0]['name']).strip('_.') if len(docs)==1 else 'items')
  if not fileName:
    return False
  docTypes, schemas, definitions = _projectGroupData(comm)
  itemTypes:list[dict[str,Any]] = []
  for doc in docs:                                         # the item type of each item, once; subtypes if they exist
    docType = '/'.join(doc['type']) if '/'.join(doc['type']) in schemas else doc['type'][0]
    if docType in schemas and docType not in [i['docType'] for i in itemTypes]:
      itemTypes.append(itemTypeTemplate(docType, docTypes, schemas, definitions))
  try:
    writeTemplate(newTemplate(itemTypes, [itemTemplate(doc, withValues) for doc in docs]), fileName)
  except OSError as error:
    showMessage(widget, 'Template could not be exported', str(error), 'Critical')
    return False
  content = [f"- {i['name']} (item, {'with' if withValues else 'without'} values)" for i in docs] + \
            [f"- {i['title']} (item type)" for i in itemTypes]
  showMessage(widget, 'Export as template', f'Exported template to {fileName}:\n' + '\n'.join(content))
  return True


def exportItemTypes(comm:Any, widget:QWidget) -> bool:
  """ Export item types as template

  Args:
    comm (Communicate): Shared communication object.
    widget (QWidget): parent widget; its docType is selected at the start

  Returns:
    bool: success
  """
  selectDialog = ItemTypeSelectDialog(comm, getattr(widget, 'docType', ''))
  if not selectDialog.exec():
    return False
  selected = selectDialog.selected
  fileName = _saveFileName(widget, 'Export item types as template',
                           selected[0].replace('/', '_') if len(selected)==1 else 'item_types')
  if not fileName:
    return False
  docTypes, schemas, definitions = _projectGroupData(comm)
  itemTypes = [itemTypeTemplate(docType, docTypes, schemas, definitions) for docType in selected]
  try:
    writeTemplate(newTemplate(itemTypes, []), fileName)
  except OSError as error:
    showMessage(widget, 'Template could not be exported', str(error), 'Critical')
    return False
  showMessage(widget, 'Export item types', f'Exported template to {fileName}:\n' +
              '\n'.join(f"- {i['title']} (item type)" for i in itemTypes))
  return True


def importItemTypes(comm:Any, widget:QWidget) -> bool:
  """ Import item types from a template, after a preview of the differences

  Args:
    comm (Communicate): Shared communication object.
    widget (QWidget): parent widget

  Returns:
    bool: success
  """
  template = _openTemplate(widget, 'Import item types from template')
  if not template:
    return False
  if not template.get('itemTypes'):
    showMessage(widget, 'Nothing to import', 'This template does not contain item types.')
    return False
  schemas = _projectGroupData(comm)[1]
  importDialog = ItemTypeImportDialog(compareItemTypes(template, schemas))
  if not importDialog.exec() or not importDialog.importActions:
    return False
  tasks, report = importTasks(template, importDialog.importActions, schemas)
  if tasks:
    comm.uiSendSQL.emit(tasks)
    comm.start()                                                             # reload item types, as the editor does
  showMessage(widget, 'Import item types', f'Imported item types:\n{report}')
  return bool(tasks)


def newItem(comm:Any, widget:QWidget) -> bool:
  """ Create a new item from an item template in the current project

  Args:
    comm (Communicate): Shared communication object.
    widget (QWidget): parent widget

  Returns:
    bool: success
  """
  template = _openTemplate(widget, 'New item from template')
  if not template:
    return False
  items = template.get('items', [])
  if not items:
    showMessage(widget, 'No item in template', 'This template only contains item types. Import them with "Import '
                'item types…".')
    return False
  item = items[0]
  if len(items) > 1:
    names = [f"{i.get('name') or 'unnamed'} ({i['docType']})" for i in items]
    name, ok = QInputDialog.getItem(widget, 'Select item', 'This template contains several items:', names, 0, False)
    if not ok:
      return False
    item = items[names.index(name)]
  if item['docType'] not in comm.docTypesTitles:
    showMessage(widget, 'Item type is missing', f"The item type {item['docType']} of this template does not exist in "
                'this project group. Import it first with "Import item types…" and this template file.')
    return False
  doc = templateToDoc(item, _projectGroupData(comm)[2])
  if isMarkdownItem(item):
    # workflow items are created as Markdown file in the project: the database only stores the beginning
    if not comm.projectID:
      showMessage(widget, 'Select a project', 'Workflow items are created as Markdown file in a project. Select a '
                  'project first.')
      return False
    try:
      path = writeMarkdown(item, comm.basePath/getDoc(comm, comm.projectID)['branch'][0]['path'])
    except OSError as error:
      showMessage(widget, 'Item could not be created from the template', str(error), 'Critical')
      return False
    doc['name'] = path.relative_to(comm.basePath).as_posix()
  else:
    name, ok = QInputDialog.getText(widget, 'New item from template', 'Name of the new item:',
                                    text=item.get('name',''))
    if not ok or not name.strip():
      return False
    doc['name'] = name.strip()
  comm.uiRequestTask.emit(Task.ADD_DOC, {'hierStack':[comm.projectID] if comm.projectID else [],
                                         'docType':item['docType'], 'doc':doc})
  if hasattr(widget, 'refresh'):
    widget.refresh()
  return True


class TemplateDialog(QDialog):
  """ Main dialog of the add-on: select what to do """
  def __init__(self, comm:Any, docIDs:list[str], widget:QWidget):
    """
    Initialization

    Args:
      comm (Communicate): Shared communication object.
      docIDs (list): items that can be exported: selected items of the list or all items
      widget (QWidget): table widget
    """
    super().__init__(widget)
    self.success = False
    self.setWindowTitle('Templates')
    mainL = QVBoxLayout(self)
    explanation = QLabel('Templates are JSON files that share item types and items between project groups and with '
                         'other people.')
    explanation.setWordWrap(True)
    mainL.addWidget(explanation)
    actions = [(f'Export {len(docIDs)} item{"s" if len(docIDs)!=1 else ""} of the list as template…',
                'Selected items of the list, or all items if none is selected',
                lambda: exportItems(comm, docIDs, widget), bool(docIDs)),
               ('Export item types…', 'Item types with their fields, units and descriptions',
                lambda: exportItemTypes(comm, widget), True),
               ('Import item types…', 'Preview of the differences before anything is changed',
                lambda: importItemTypes(comm, widget), True),
               ('New item from template…', 'The item is created in the current project',
                lambda: newItem(comm, widget), True)]
    self.buttons:list[QPushButton] = []
    for label, tooltip, function, enabled in actions:
      self.buttons.append(QPushButton(label))
      self.buttons[-1].setToolTip(tooltip)
      self.buttons[-1].setEnabled(enabled)
      self.buttons[-1].clicked.connect(lambda _checked=False, function=function: self.run(function))
      mainL.addWidget(self.buttons[-1])
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
    buttons.rejected.connect(self.reject)
    mainL.addWidget(buttons)


  def run(self, function:Callable[[], bool]) -> None:
    """ Execute an action and close the dialog

    Args:
      function (Callable): action that returns its success
    """
    self.success = bool(function())
    if isValid(self):                       # reloading the item types rebuilds the table and deletes this dialog
      self.done(int(self.success))


class ItemTypeSelectDialog(QDialog):
  """ Select the item types that are exported as template """
  def __init__(self, comm:Any, current:str=''):
    """
    Initialization

    Args:
      comm (Communicate): Shared communication object.
      current (str): item type that is selected at the start
    """
    super().__init__()
    self.selected:list[str] = []
    self.setWindowTitle('Export item types')
    mainL = QVBoxLayout(self)
    mainL.addWidget(QLabel('Select the item types to export as template'))
    self.listW = QListWidget()
    for docType, info in comm.docTypesTitles.items():
      if docType.startswith('x'):                                                   # projects and folders
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
    """ Accept only if an item type is selected """
    self.selected = [self.listW.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.listW.count())
                     if self.listW.item(i).checkState()==Qt.CheckState.Checked]
    if not self.selected:
      showMessage(self, 'No item type selected', 'Select at least one item type.')
      return
    super().accept()


class ItemTypeImportDialog(QDialog):
  """ Preview of the item types of a template: what differs and what should be imported """
  def __init__(self, comparison:list[dict[str,Any]]):
    """
    Initialization

    Args:
      comparison (list): result of compareItemTypes
    """
    super().__init__()
    self.comparison = comparison
    self.importActions:dict[str,ImportAction] = {}                                       # docType: action
    self.setWindowTitle('Import item types')
    self.setMinimumWidth(800)
    mainL = QVBoxLayout(self)
    explanation = QLabel('Select what to import for each item type. "Add missing fields" keeps all existing fields '
                         'unchanged. "Replace" also removes fields that are not in the template and replaces the name, '
                         'icon and shortcut of the item type.')
    explanation.setWordWrap(True)
    mainL.addWidget(explanation)
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
                     (('added','only in template'), ('removed','only here'), ('changed','changed')) if entry[key]]
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
    mainL.addWidget(self.table)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
    buttons.addButton('Import', QDialogButtonBox.ButtonRole.AcceptRole)
    buttons.accepted.connect(self.accept)
    buttons.rejected.connect(self.reject)
    mainL.addWidget(buttons)


  def accept(self) -> None:
    """ Collect the selected actions """
    self.importActions = {entry['docType']:comboBox.currentData() for entry, comboBox in
                          zip(self.comparison, self.comboBoxes) if comboBox.currentData() is not ImportAction.SKIP}
    super().accept()
