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

    # CHANGE CONTENT ON SERVER
    print('\n\n=============================\nChange content\n============================')
    # remove content in pasta: 1+1 entry
    projID = self.be.output('x0').split('|')[-1].strip()
    hierarchy = self.be.db.getHierarchy(projID)
    leaves    = [i for i in PreOrderIter(hierarchy) if not i.children]
    choiceExp = random.choice([i.id for i in leaves if i.docType[0]=='measurement'])
    choiceItem= random.choice([i.id for i in leaves if i.docType[0]!='measurement'])
    branchExp = random.choice(self.be.db.getDoc(choiceExp)['branch'])
    branchItem= random.choice(self.be.db.getDoc(choiceItem)['branch'])
    print('Delete experiment',choiceExp, branchExp)
    print('Delete item', choiceItem,branchItem)
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
    choiceFolder= random.choice([i.id for i in leaves if i.docType[0]=='x1'])
    self.be.changeHierarchy(choiceFolder)
    self.be.addData('x1',    {'name': 'task to test elab','comment': 'Random comment 3'})
    choiceFolder= random.choice([i.id for i in leaves if i.docType[0]=='x1'])
    self.be.changeHierarchy(choiceFolder)
    self.be.addData('measurement', {
      'name'   :'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Medieval_south-east_Wales_map_Lloyd.jpg/800px-Medieval_south-east_Wales_map_Lloyd.jpg',\
      'comment':'Random image', 'tags':['_3']})

    # change in pasta: 1 entry
    choice= random.choice([i.id for i in PreOrderIter(hierarchy)])
    doc = self.be.db.getDoc(choice)
    self.be.editData(doc | {'comment':f'a very random comment to test elabFTW at {datetime.now().isoformat()}'})
    print(f'\nChanged docID {choice}')

    sync = Pasta2Elab(self.be, 'research')

    # change on server: 1+1 entry
    data = sync.api.readEntry('items', sync.elabProjGroupID)[0]
    for entry in ['experiments','items']:
      idx  = random.choice(data[f'related_{entry}_links'])['entityid']
      sync.api.updateEntry(entry, idx, {'body':f'CHANGED BY test_03-elabFTW_good {entry}'})
      print(f'Changed on server {entry} {idx}')

    # change on server and on pasta
    choice= random.choice([i.id for i in PreOrderIter(hierarchy)])
    docPasta = self.be.db.getDoc(choice)
    entry = 'experiments' if docPasta['type'][0]=='measurement' else 'items'
    sync.api.updateEntry(entry, docPasta['externalId'], {'body':f'CHANGED ELAB server (but also client) at {datetime.now().isoformat()}'})
    self.be.editData(docPasta | {'comment':f'CHANGE CLIENT (but also elab server) at {datetime.now().isoformat()}'})
    print(f'\n Changed both for docID {choice}')

    # Sync
    reports = sync.sync()
    handleReports(reports)
    sync.compareCounts()    # TODO count documents on both instances and compare

    # TODO experiments have no links from folders
    # TODO read-access incorrect

    # verify
    verify(self.be)
    return


  def tearDown(self):
    logging.info('End test')
    return


if __name__ == '__main__':
  unittest.main()

# for entityType in ['experiments','items']:
#   response = requests.get(f'{sync.api.url}{entityType}?archived=on', **self.param)
# allIDs = [i['id'] for i in json.loads(response.content.decode('utf-8'))]
# for identifier in :
#   response = requests.delete(f'{self.url}{entityType}/{identifier}', **self.param)
#   if response.status_code != 204:
#     print(f'**ERROR purge delete {entityType}: {identifier}')
