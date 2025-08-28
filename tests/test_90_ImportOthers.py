#!/usr/bin/python3
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.project import Project
from .test_34_GUI_Form import getTable

import logging, warnings, os, shutil, tempfile
from pathlib import Path
from urllib import request
from pasta_eln.backendWorker.backend import Backend
from pasta_eln.backendWorker.worker import Task
from pasta_eln.backendWorker.inputOutput import importELN
from pasta_eln.miscTools import getConfiguration


def test_simple(qtbot):

  # remove old data
  configuration, _ = getConfiguration('research')
  backend = Backend(configuration, 'research')
  dirName = backend.basePath
  backend.exit()
  try:
    shutil.rmtree(dirName)
    os.makedirs(dirName)
  except Exception:
    pass

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)
  window = Project(comm)
  window.setMinimumSize(1024,800)
  window.show()

  # location of data and temp
  tempDir = tempfile.gettempdir()
  allELNs = {'Pasta.eln'          :'PASTA/PASTA.eln',
             'elabFTW.eln'        :'elabftw/export.eln',
             'SampleDB.eln'       :'SampleDB/sampledb_export.eln',
             'kadi4mat_1.eln'     :'kadi4mat/collections-example.eln',
             'kadi4mat_2.eln'     :'kadi4mat/records-example.eln',
             'openSemanticLab.eln':'OpenSemanticLab/MinimalExample.osl.eln'
            }
  urlBase = 'https://github.com/TheELNConsortium/TheELNFileFormat/raw/refs/heads/master/examples/'


  for eln, pathName in allELNs.items():
    elnFileName = f'{tempDir}/{eln}'
    request.urlretrieve(f'{urlBase}{pathName}', elnFileName)
    print(f'\n\n{"="*30}\nStart with {eln} on {elnFileName}')
    projName = f'{eln[:-4]} Import'
    comm.uiRequestTask.emit(Task.ADD_DOC, {'docType':'x0', 'doc':{'name':projName}, 'hierStack':[]})
    df = getTable(qtbot, comm, 'x0')
    projID = df[df['name']==projName]['id'].values[0]
    comm.uiRequestTask.emit(Task.IMPORT_ELN, {'fileName':elnFileName, 'projID':projID})
    qtbot.wait(2000)  # wait until import is done

    comm.changeProject.emit(projID, '')
    qtbot.addWidget(window)
    qtbot.wait(1000)
    path = qtbot.screenshot(window)
    print(path)

  comm.shutdownBackendThread()



  #   reply, statistics = importELN(backend, elnFileName, projID)
  #   print(reply,'\n',statistics)
  #   assert statistics['num. files']<=statistics['types'].get('File',0) ,'Files do not make sense'
  #   #statistics type File can be larger than num.Files because there are remote files which are not Files but in the @type
  #   print(backend.checkDB(minimal=True))

  return
