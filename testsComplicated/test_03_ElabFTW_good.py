#!/usr/bin/python3
"""TEST elabFTW server: do things that should be possible """
import logging, warnings, unittest, random, os, shutil
from datetime import datetime
from pathlib import Path
import requests
from PySide6.QtWidgets import QApplication
from anytree import PreOrderIter
from pasta_eln.backend import Backend
from pasta_eln.elabFTWsync import Pasta2Elab
from .misc import verify, handleReports


class TestStringMethods(unittest.TestCase):
  """
  derived class for this test
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.be = None
    self.dirName = ''



  def test_main(self):
    """
    main function
    """
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)
    logPath = Path.home()/'pastaELN.log'
    logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                        datefmt='%m-%d %H:%M:%S')   #This logging is always info, since for installation only
    for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib.font_manager']:
      logging.getLogger(package).setLevel(logging.WARNING)
    logging.info('Start test')

    # setup and sync to server
    try:
      _ = QApplication()
    except RuntimeError:
      pass
    self.be = Backend('research')
    projID = self.be.output('x0').split('|')[-1].strip()
    self.be.changeHierarchy(projID)
    output = self.be.outputHierarchy(False, True)
    print(output)

    # CHANGE CONTENT ON SERVER
    print('\n\n=============================\nSTART TEST\n============================')
    choices = random.choices(range(100), k=10)
    choices = [34,16,40,25,70,68,77,65,7,53]
    print(f'Current choice: [{",".join([str(i) for i in choices])}]')

    # remove content in pasta: 1+1 entry
    hierarchy, _ = self.be.db.getHierarchy(projID)
    leaves    = [i for i in PreOrderIter(hierarchy) if not i.children]
    validChoices = [i.id for i in leaves if i.docType[0]=='measurement']
    choiceExp = validChoices[choices.pop(0)%len(validChoices)]
    validChoices = [i.id for i in leaves if i.docType[0]!='measurement']
    choiceItem= validChoices[choices.pop(0)%len(validChoices)]
    validChoices = self.be.db.getDoc(choiceExp)['branch']
    branchExp = validChoices[choices.pop(0)%len(validChoices)]
    validChoices = self.be.db.getDoc(choiceItem)['branch']
    branchItem= validChoices[choices.pop(0)%len(validChoices)]
    print('Delete experiment',choiceExp)
    print('Delete item', choiceItem)
    if branchExp['path'] is not None and not branchExp['path'].startswith('http'):
      os.unlink(self.be.basePath/branchExp['path'])
    if branchItem['path'] is not None:
      if Path(self.be.basePath/branchItem['path']).is_file():
        os.unlink(self.be.basePath/branchItem['path'])
      else:
        shutil.rmtree(self.be.basePath/branchItem['path'])
    self.be.db.remove(choiceExp,  '/'.join(branchExp['stack']))
    self.be.db.remove(choiceItem, '/'.join(branchItem['stack']))

    # add in pasta: 1+1 entry
    hierarchy, _ = self.be.db.getHierarchy(projID)
    allNodes    = [i for i in PreOrderIter(hierarchy)]
    validChoices = [i.id for i in allNodes if i.docType[0]=='x1']
    choiceFolder= validChoices[choices.pop(0)%len(validChoices)]
    self.be.changeHierarchy(choiceFolder)
    self.be.addData('x1',    {'name': 'task to test elab','comment': 'Random comment 3'})
    validChoices = [i.id for i in allNodes if i.docType[0]=='x1']
    choiceFolder= validChoices[choices.pop(0)%len(validChoices)]
    self.be.changeHierarchy(choiceFolder)
    self.be.addData('measurement', {
      'name'   :'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Medieval_south-east_Wales_map_Lloyd.jpg/800px-Medieval_south-east_Wales_map_Lloyd.jpg',\
      'comment':'Random image', 'tags':['_3']})

    # change in pasta: 1 entry
    validChoices = [i.id for i in PreOrderIter(hierarchy)]
    choice= validChoices[choices.pop(0)%len(validChoices)]
    doc = self.be.db.getDoc(choice)
    self.be.editData(doc | {'comment':f'a very random comment to test elabFTW at {datetime.now().isoformat()}'})
    print(f'Changed docID {choice}')

    sync = Pasta2Elab(self.be, 'research')
    sync.verbose = True

    # change on server: 1+1 entry
    data = sync.api.readEntry('items', sync.elabProjGroupID)[0]
    for entry in ['experiments','items']:
      validChoices = data[f'related_{entry}_links']
      idx  = validChoices[choices.pop(0)%len(validChoices)]['entityid']
      sync.api.updateEntry(entry, idx, {'body':f'CHANGED BY test_03-elabFTW_good {entry}'})
      print(f'Changed on server {entry} {idx}')
    projIDElab = [i['entityid'] for i in data['related_items_links'] if i['title']=='PASTAs Example Project'][0]
    sync.api.updateEntry('items', projIDElab, {'body':f'PROJECT CHANGED ADDITIONALLY BY test_03-elabFTW_good'})
    print(f'Changed on server items {projIDElab}')

    # change on server and on pasta
    validChoices = [i.id for i in PreOrderIter(hierarchy)]
    choice= validChoices[choices.pop(0)%len(validChoices)]
    docPasta = self.be.db.getDoc(choice)
    entry = 'experiments' if docPasta['type'][0]=='measurement' else 'items'
    sync.api.updateEntry(entry, docPasta['externalId'], {'body':f'CHANGED ELAB server (but also client) at {datetime.now().isoformat()}'})
    self.be.editData(docPasta | {'comment':f'CHANGE CLIENT (but also elab server) at {datetime.now().isoformat()}'})
    print(f'Changed both for docID {choice}')

    # Sync & verify
    reports = sync.sync('sA')
    print('\n')
    handleReports(reports)
    verify(self.be)
    return

  def tearDown(self):
    logging.info('End test')
    return


if __name__ == '__main__':
  unittest.main()
