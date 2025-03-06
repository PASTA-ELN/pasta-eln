#!/usr/bin/python3
"""Commandline utility to admin local installation and convert from Pasta-ELN version 2"""
import json
import os, re, platform, shutil
import traceback
from pathlib import Path
from typing import Any, Callable, Union
from PySide6.QtWidgets import QApplication
import requests
from requests.structures import CaseInsensitiveDict
from pasta_eln.backend import Backend
from pasta_eln.fixedStringsJson import CONF_FILE_NAME
from pasta_eln.miscTools import DummyProgressBar
from pasta_eln.sqlite import SqlLiteDB
from pasta_eln.stringChanges import outputString
from pasta_eln.elabFTWsync import Pasta2Elab


def couchDB2SQLite(userName:str='', password:str='', database:str='', path:str='') -> None:
  """
  Backup everything of the CouchDB installation (local couchdb instance)

  Args:
    userName (str): username
    password (str): password
    database (str): database
    path     (str): path to location of sqlite file
  """
  headers:CaseInsensitiveDict[str]= CaseInsensitiveDict()
  headers['Content-Type'] = 'application/json'
  # get arguments if not given
  location = '127.0.0.1'
  if not userName:
    userName = input('Enter local admin username: ').strip()
  if not password:
    password = input('Enter password: ').strip()
  if not path:
    path = input('Enter path to data: ').strip()
  db = SqlLiteDB(basePath=Path(path))
  # use information
  authUser = requests.auth.HTTPBasicAuth(userName, password)
  resp = requests.get(f'http://{location}:5984/_all_dbs', headers=headers, auth=authUser, timeout=10)
  if resp.status_code != 200:
    print('**ERROR response for _all_dbs wrong', resp.text)
    print('Username and password', userName, password)
    return
  databases = resp.json()
  print('Databases:',databases)
  if not database:
    database = input('Enter database: ').strip()
  # big loop over all documents
  resp = requests.get(f'http://{location}:5984/{database}/_all_docs', headers=headers, auth=authUser, timeout=10)
  for item in resp.json()['rows']:
    docID = item['id']
    if docID in ('-dataHierarchy-','-ontology-') or docID.startswith('_design/'):
      continue
    # print(f'DocID: {docID}')
    doc   = requests.get(f'http://{location}:5984/{database}/{docID}', headers=headers, auth=authUser, timeout=10).json()
    doc, attachments = translateDoc(doc)
    db.saveDoc(doc)
    for att in attachments:
      docAttach = requests.get(f'http://{location}:5984/{database}/{docID}/{att}',
                                headers=headers, auth=authUser, timeout=10).json()
      setAll = set(docAttach.keys())
      setImportant  = setAll.difference({'-date','date','-client','image','type','-type','client','-name','-branch','branch'})
      if not setImportant or ('-name' in docAttach and docAttach['-name']=='new folder'):
        continue
      date = docAttach['-date'] if '-date' in docAttach else docAttach['date'] if 'date' in docAttach else att
      if '-client' in docAttach:
        del docAttach['-client']
      db.cursor.execute('INSERT INTO changes VALUES (?,?,?)', [docID, date, json.dumps(docAttach)])
      db.connection.commit()
  return


def translateDoc(doc:dict[str,Any], comment:str='') -> tuple[dict[str,Any],list[Any]]:
  """ translate to new style

  Args:
    doc (dict): input document
    comment (str): comment to add to the output, e.g. offending doc-id

  Returns:
    dict: output document
  """
  from .handleDictionaries import fillDocBeforeCreate
  defaultValues = {'gui':[True,True], 'user':''}
  try:
    doc['id'] = doc.pop('_id')
    for key in ('name','user','type','gui','tags','client','branch','date'):
      if key in doc:      #skip if key is already in correct format
        continue
      if key in defaultValues and f'-{key}' not in doc:
        doc[key] = defaultValues[key]
        continue
      doc[key] = doc.pop(f'-{key}')
    doc['dateCreated']  = doc['date']
    doc['dateModified'] = doc.pop('date')
    doc['branch'] = doc['branch'][0] | {'op':'c'} if doc['branch'] else \
                    {'stack':[], 'child':9999, 'path':None, 'show':[True], 'op':'c'}
    del doc['_rev']
    attachments = doc.pop('_attachments',[])
    doc = fillDocBeforeCreate(doc, doc['type'])
  except Exception:
    print('Input document has mistakes in: ',comment,'\n',json.dumps(doc, indent=2))
    raise
  return doc, attachments


def translateV2_V3(path:str='') -> None:
  """ Translate old id files in the file-tree into the new style
  Args:
    path (str): path to file-tree
  """
  if not path:
    path = input('Enter path to data: ').strip()
  for aPath, _, files in os.walk(path):
    if aPath == path or 'StandardOperatingProcedures' in aPath:
      continue
    if '.id_pastaELN.json' not in files:
      print('**ERROR** id file does NOT exist:', aPath,'\n   ',' '.join(files))
    with open(Path(aPath)/'.id_pastaELN.json', encoding='utf-8') as fIn:
      doc = json.load(fIn)
    docNew, _ = translateDoc(doc, aPath)
    del docNew['branch']['op']
    docNew['branch'] = [docNew['branch']]
    with open(Path(aPath)/'.id_pastaELN.json','w', encoding='utf-8') as fOut:
      fOut.write(json.dumps(docNew))
  return

def __returnBackend__(projectGroup:str='') -> Backend:
  """ Internal function: return backend based on project group
  Args:
    projectGroup (str): name of project group
  """
  while not projectGroup:
    with open(Path.home()/CONF_FILE_NAME, encoding='utf-8') as fIn:
      config = json.load(fIn)
      print('Possible project groups:','  '.join(f'{idx+1}-{i}' for idx,i in enumerate(config['projectGroups'].keys())))
    projectGroup = input('  Enter project group [number or name or entire text]: ').strip()
    if re.match(r'^\d+-\w+$', projectGroup):
      projectGroup = projectGroup.split('-')[1]
    if re.match(r'^\d+$', projectGroup):
      projectGroup = list(config['projectGroups'].keys())[int(projectGroup)-1]
    if projectGroup not in config['projectGroups'].keys():
      projectGroup = ''
  return Backend(projectGroup)


def verifyPasta(projectGroup:str='', repair:Union[None,Callable[[str],bool]]=None) -> None:
  """ Do the default verification of PastaELN. Adopted to CLI
    Args:
    projectGroup (str): name of project group
    repair (function): repair
  """
  be = __returnBackend__(projectGroup)
  outputString('print','info', be.checkDB(outputStyle='text', repair=repair, minimal=True))
  return


def createLostAndFound(projectGroup:str='') -> None:
  """ Create a lost and found project that is the target of misc documents
    Args:
      projectGroup (str): name of project group
  """
  be = __returnBackend__(projectGroup)
  be.addData('x0', {'name': 'Lost and Found', 'comment': 'Location of lost database items'})
  return


def scanAllProjects(projectGroup:str='') -> None:
  """ Scan all projects to identify missing items

    Args:
      projectGroup (str): name of project group
  """
  progressBar = DummyProgressBar()
  be = __returnBackend__(projectGroup)
  for projID in be.db.getView('viewDocType/x0')['id'].values:
    be.scanProject(progressBar,projID)
  return


def repairPropertiesDot(projectGroup:str='') -> None:
  """ Repair sqlite database by changing properties table: if key does not have a ., prepend it
  Args:
    projectGroup (str): name of project group
  """
  db = __returnBackend__(projectGroup).db
  key= input('Which key to repair, e.g. "chemistry" will become .chemistry? ')
  db.cursor.execute(f"SELECT id FROM properties where key == '{key}'")
  res = db.cursor.fetchall()
  for idx, docID in enumerate(res):
    docID = docID[0]
    try:
      db.cursor.execute(f"UPDATE properties SET key='.{key}' WHERE id == '{docID}' and  key=='{key}'")
    except Exception:
      print(f"Error, could not change {docID} and {key}. Likely that combination exists already in properties. Repair manually")
      if idx==0:
        print(traceback.format_exc())
  db.connection.commit()
  print('Done')
  return


def purgeLocal(projectGroup:str='') -> None:
  """ Purge entire local storage, remove everything

    Args:
    projectGroup (str): name of project group
  """
  backend = __returnBackend__(projectGroup)
  dirName = backend.basePath
  if dirName.as_posix() != '/home/steffen/FZJ/pasta_misc/testing': #TODO temporary safeguard
    print('DO NOT DELETE THIS')
    return
  backend.exit()
  try:
    shutil.rmtree(dirName)
    os.makedirs(dirName)
    if platform.system()=='Windows':
      print('Try-Except unnecessary')
  except Exception:
    pass
  return


def sync(projectGroup:str='', command:str='') -> None:
  """ synchronize with elab server

    Args:
    projectGroup (str): name of project group
    command (str): 'ss' or 'sg' to send/get data
  """
  backend = __returnBackend__(projectGroup)
  sync = Pasta2Elab(backend, backend.configurationProjectGroup)
  if command:
    _ = QApplication()
    sync.sync('sA' if command=='ss' else 'gA')
  return


def printOrDelete(projectGroup:str='', docID:str='', output:bool=True) -> None:
  """ Print or delete a document
  Args:
    projectGroup (str): from which project group to delete
    docID (str): which ID to delete
    output (bool): print=True or delete=False
  """
  if not projectGroup:
    with open(Path.home()/CONF_FILE_NAME, encoding='utf-8') as fIn:
      config = json.load(fIn)
      print('Possible project groups:','  '.join(config['projectGroups'].keys()))
    projectGroup = input('Enter project group: ').strip()
  be = Backend(projectGroup)
  if not docID:
    docID = input('Enter docID: ').strip()
  if output:
    print(json.dumps(be.db.getDoc(docID), indent=2))
  else:
    be.db.remove(docID)
  return


def userQuestion(errorMessage:str, allYes:bool=False) -> bool:
  """ Ask user if repair should be done

  Args:
    errorMessage (str): error message
    allYes (bool): answer all questions with yes

  Return:
    bool: repair should be done
  """
  print(errorMessage)
  return True if allYes else input('Repair [yN]: ')=='y'


def help() -> None:
  """ Print all commands
  """
  print("""Command line program to troubleshoot and possibly repair Pasta-ELN database
Commands - general:
  - [h]elp: long help
  - [q]uit
  - [p]rint a document
  - [d]elete a document
  - [s]can all projects
Commands - update Version 2 -> Version 3:
  - [c]onvert couchDB to SQLite
  - [t]ranslate disk structure from V2->v3
Commands - database integrity:
  - [v]erify
  - [r]epair
  - [rA]epair: answer always 'yes': WARNING can change too much
  - [cp]-create a lost and found project: helpful for some repair operations
  - [pL]urge local database: REMOVE EVERYTHING
  - [ss]ync SEND ALL
  - [sg]ync GET ALL
Commands - depricated:
  - [rp1] repair properties: add missing '.'
""")
  return


def main() -> None:
  '''
  Main function
  '''
  print('\n-------------------------------------------------------------------------')
  print(  '------------     Manual functions for PASTA-ELN installation    ---------')
  print(  '-------------------------------------------------------------------------')
  while True:
    command = input('\nImportant commands [h]elp; [q]uit; [v]erify; [r]epair: ')
    if command == 'c':
      couchDB2SQLite()
    elif command == 't':
      translateV2_V3()
    elif command == 'v':
      verifyPasta()
    elif command == 'cp':
      createLostAndFound()
    elif command == 'r':
      verifyPasta('', userQuestion)
    elif command == 'rA':
      verifyPasta('', lambda t: userQuestion(t, True))
    elif command == 'rp1':
      repairPropertiesDot()
    elif command == 'p':
      printOrDelete()
    elif command == 's':
      scanAllProjects()
    elif command in ['ss','sg']:
      sync('', command)
    elif command == 'd':
      printOrDelete(projectGroup='', docID='', output=False)
    elif command == 'pL':
      purgeLocal()
    elif command == 'q':
      break
    elif command == 'h':
      help()
    else:
      print('Unknown command or incomplete entries.')


if __name__ ==  '__main__':
  main()
