"""GUI test of the templates add-on: export/import of item types, export of items and creation of new items from a
template"""
# pylint: disable=invalid-name
import json
import logging
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox
from pasta_eln.add_ons import table_templates as templates
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.table.table import TableView


def waitFor(qtbot, condition, timeout=20000):
  """Wait until condition() is true"""
  qtbot.waitUntil(condition, timeout=timeout)


def removeTestData(db, basePath):
  """Remove what this test adds, also if an earlier run did not finish"""
  rows = db.cursor.execute("SELECT main.id, branches.path FROM main LEFT JOIN branches ON main.id=branches.id WHERE "
                           "(main.name IN ('MTS XP', 'MTS XP copy') AND main.comment='Lab 2') OR "
                           "(main.name LIKE 'run_1%.md' AND main.comment='from PYRAMID')").fetchall()
  for docID, path in rows:
    for table in ('main', 'properties', 'tags', 'branches', 'qrCodes', 'attachments', 'changes'):
      db.cursor.execute(f"DELETE FROM {table} WHERE id=?", (docID,))
    if path and path != '*':
      (basePath/path).unlink(missing_ok=True)
  db.cursor.execute("DELETE FROM docTypeSchema WHERE docType='measurement/indentation' OR "
                    "(docType='device' AND class='calibration' AND name='max load')")
  db.cursor.execute("DELETE FROM docTypes WHERE docType='measurement/indentation'")
  db.connection.commit()


def test_templates(qtbot, caplog, monkeypatch, tmp_path):
  """Export, import and new items from templates, as a user would do it in the add-on"""
  comm = Communicate('research')
  while comm.backendThread.worker.backend is None or comm.backendThread.worker.backend.dbRaw is None:
    qtbot.wait(100)
  waitFor(qtbot, lambda: 'device' in comm.dataHierarchyNodes)
  db = comm.backendThread.worker.backend.db
  removeTestData(db, comm.basePath)
  typesFile, itemFile = tmp_path/'types.json', tmp_path/'item.json'
  messages = []
  monkeypatch.setattr(templates, 'showMessage', lambda _widget, title, text, *_args: messages.append((title, text)))
  tableView = TableView(comm, 'device')
  qtbot.addWidget(tableView)

  # main dialog: exporting items needs items
  dialog = templates.TemplateDialog(comm, [], tableView)
  assert not dialog.buttons[0].isEnabled()

  # export devices
  monkeypatch.setattr(templates.ItemTypeSelectDialog, 'exec', lambda self: setattr(self, 'selected', ['device']) or True)
  monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *_args, **_kwargs: (str(typesFile), ''))
  assert templates.exportItemTypes(comm, tableView)
  template = json.loads(typesFile.read_text(encoding='utf-8'))
  assert [i['docType'] for i in template['itemTypes']] == ['device']

  # change the template: devices get a calibration group, and a new subtype of measurements
  template['itemTypes'][0]['fields'].append({'group':'calibration', 'name':'max load', 'unit':'mN', 'mandatory':'',
                                             'list':'', 'description':'Maximum load', 'PURL':''})
  template['itemTypes'].append({'docType':'measurement/indentation', 'title':'Indentations', 'icon':'',
                                'shortcut':'', 'PURL':'', 'view':'name,tags',
                                'fields':[{'group':'', 'name':'name', 'unit':'', 'mandatory':'T', 'list':''},
                                          {'group':'', 'name':'tip', 'unit':'', 'mandatory':'', 'list':''}]})
  typesFile.write_text(json.dumps(template), encoding='utf-8')

  # import with preview; the default action of each item type is used
  previews = []
  def acceptPreview(self):
    previews.extend(self.comparison)
    self.importActions = {i['docType']:i['actions'][0] for i in self.comparison
                          if i['actions'][0] is not templates.ImportAction.SKIP}
    return True
  monkeypatch.setattr(templates.ItemTypeImportDialog, 'exec', acceptPreview)
  monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *_args, **_kwargs: (str(typesFile), ''))
  assert templates.importItemTypes(comm, tableView)
  waitFor(qtbot, lambda: 'measurement/indentation' in comm.dataHierarchyNodes)            # item types reloaded
  assert {i['docType']:i['status'] for i in previews} == {'device':'different', 'measurement/indentation':'new'}
  assert ('calibration', 'max load', 'mN') in [(i['class'], i['name'], i['unit']) for i in db.dataHierarchy('device', 'meta')]

  # export a device with values as item template
  db.saveDoc({'id':'d-'+'7'*32, 'name':'MTS XP', 'type':['device'], 'tags':[], 'user':'u', 'gui':[True,True],
              'dateCreated':'x', 'dateModified':'x', 'comment':'Lab 2', '.vendor':'MTS',
              'branch':{'stack':[], 'child':0, 'path':None, 'show':[True], 'op':'c'},
              'calibration':{'max load':('500', 'mN', '', ''), 'temperature':('23', 'degC', '', '')},
              '.serial':('A12', '', '', '')})
  db.cursor.execute("INSERT OR REPLACE INTO definitions VALUES ('calibration.max load', 'Maximum load', '')")
  db.connection.commit()
  monkeypatch.setattr(QMessageBox, 'exec', lambda self: 0)
  monkeypatch.setattr(QMessageBox, 'clickedButton', lambda self: [i for i in self.buttons() if i.text()=='With values'][0])
  monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *_args, **_kwargs: (str(itemFile), ''))
  assert templates.exportItems(comm, ['d-'+'7'*32], tableView)
  template = json.loads(itemFile.read_text(encoding='utf-8'))
  assert {'group':'calibration', 'key':'max load', 'value':'500', 'unit':'mN'} in template['items'][0]['properties']
  assert [i['docType'] for i in template['itemTypes']] == ['device']

  # new item from the template: units are kept, also of keys that are not in the item type, and descriptions stay
  monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *_args, **_kwargs: (str(itemFile), ''))
  monkeypatch.setattr(QInputDialog, 'getText', lambda *_args, **_kwargs: ('MTS XP copy', True))
  comm.projectID = ''
  assert templates.newItem(comm, tableView)
  def newDoc():
    rows = db.cursor.execute("SELECT id FROM main WHERE name='MTS XP copy'").fetchall()
    return db.getDoc(rows[0][0]) if rows else None
  waitFor(qtbot, lambda: newDoc() is not None)
  doc = newDoc()
  assert doc['calibration']['max load'][:2] == ('500', 'mN')
  assert doc['calibration']['temperature'][:2] == ('23', 'degC')
  assert doc['']['serial'][0] == 'A12'
  assert doc['comment'] == 'Lab 2'
  assert db.cursor.execute("SELECT long FROM definitions WHERE key='calibration.max load'").fetchone() == ('Maximum load',)

  # a workflow item is created as Markdown file in the project, with the complete content
  workflowFile = tmp_path/'workflow.json'
  content = '# Run\n\n' + '| parameter | value |\n'*50
  workflowFile.write_text(json.dumps({'format':'PASTA-ELN template', 'version':1, 'itemTypes':[],
                                      'items':[{'docType':'workflow', 'name':'run 1', 'properties':[],
                                                'comment':'from PYRAMID', 'content':content, 'tags':['PYRAMID']}]}),
                          encoding='utf-8')
  comm.projectID = db.cursor.execute("SELECT id FROM main WHERE type='x0'").fetchone()[0]
  monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *_args, **_kwargs: (str(workflowFile), ''))
  assert templates.newItem(comm, tableView)
  def workflowDoc():
    rows = db.cursor.execute("SELECT id FROM main WHERE name='run_1.md'").fetchall()
    return db.getDoc(rows[0][0]) if rows else None
  waitFor(qtbot, lambda: workflowDoc() is not None)
  doc = workflowDoc()
  path = comm.basePath/doc['branch'][0]['path']
  assert path.name == 'run_1.md' and path.parent == comm.basePath/db.getDoc(comm.projectID)['branch'][0]['path']
  assert path.read_text(encoding='utf-8') == content
  assert doc['type'][0] == 'workflow' and doc['comment'] == 'from PYRAMID' and 'PYRAMID' in doc['tags']
  removeTestData(db, comm.basePath)
  comm.shutdownBackendThread()

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f'Logging errors found: {[record.getMessage() for record in errors]}'
