#!/usr/bin/python3
import logging, warnings, os, shutil, tempfile
from pathlib import Path
from urllib import request
from pasta_eln.backendWorker.backend import Backend
from pasta_eln.backendWorker.inputOutput import importELN
from pasta_eln.miscTools import getConfiguration


def test_simple():
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
  logging.info('Start 03 test')

  # start app and load project
  configuration, _ = getConfiguration('research')
  backend = Backend(configuration, 'research')

  # remove old and recreate empty
  dirName = backend.basePath
  backend.exit()
  try:
    shutil.rmtree(dirName)
    os.makedirs(dirName)
  except Exception:
    pass
  backend = Backend(configuration, 'research')
  tempDir = tempfile.gettempdir()

  allELNs = {'Pasta.eln'          :'PASTA/PASTA.eln',
             'SampleDB.eln'       :'SampleDB/sampledb_export.eln',
             'kadi4mat_1.eln'     :'kadi4mat/collections-example.eln',
             'kadi4mat_2.eln'     :'kadi4mat/records-example.eln',
             'openSemanticLab.eln':'OpenSemanticLab/MinimalExample.osl.eln'
            }
  urlBase = 'https://github.com/SteffenBrinckmann/TheELNFileFormat/raw/refs/heads/new_PastaELN/examples/'
  # 'https://github.com/TheELNConsortium/TheELNFileFormat/raw/refs/heads/master/examples/'
  localDir= '/home/xyz/TheELNConsortium/TheELNFileFormat/examples/'
  local = False
  for eln, pathName in allELNs.items():
    if local:
      elnFileName = f'{localDir}/{pathName}'
    else:
      elnFileName = f'{tempDir}/{eln}'
      request.urlretrieve(f'{urlBase}{pathName}', elnFileName)
    print(f'\nStart with {eln}')
    projName = f'{eln[:-4]} Import'
    backend.addData('x0', {'name': projName})
    df = backend.db.getView('viewDocType/x0')
    projID = df[df['name']==projName]['id'].values[0]
    reply, statistics = importELN(backend, elnFileName, projID)
    print(reply,'\n',statistics)
    assert statistics['num. files']<=statistics['types'].get('File',0) ,'Files do not make sense'
    #statistics type File can be larger than num.Files because there are remote files which are not Files but in the @type
    print(backend.checkDB(minimal=True))

  return
