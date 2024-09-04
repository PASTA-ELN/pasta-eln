#!/usr/bin/python3
"""Commandline utility to admin the remote server"""
import json, os
from typing import Any
from pathlib import Path
import requests
from requests.structures import CaseInsensitiveDict
from .sqlite import SqlLiteDB

#global variables
headers:CaseInsensitiveDict[str]= CaseInsensitiveDict()
headers["Content-Type"] = "application/json"

def couchDB2SQLite(userName:str='', password:str='', database:str='', path:str='') -> None:
  """
  Backup everything of the CouchDB installation (local couchdb instance)

  Args:
    userName (str): username
    password (str): password
    database (str): database
    path     (str): path to location of sqlite file
  """
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
    if docID in ('-dataHierarchy-') or docID.startswith('_design/'):
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
      db.cursor.execute("INSERT INTO changes VALUES (?,?,?)", [docID, date, json.dumps(docAttach)])
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
      print("**ERROR** id file does NOT exist:", aPath,'\n   ',' '.join(files))
    with open(Path(aPath)/'.id_pastaELN.json','r', encoding='utf-8') as fIn:
      doc = json.load(fIn)
    docNew, _ = translateDoc(doc, aPath)
    del docNew['branch']['op']
    docNew['branch'] = [docNew['branch']]
    with open(Path(aPath)/'.id_pastaELN.json','w', encoding='utf-8') as fOut:
      fOut.write(json.dumps(docNew))
  return


def verifyPasta(projectGroup:str='', repair:bool=False) -> None:
  """ Do the default verification of PastaELN. Adopted to CLI """
  from pasta_eln.backend import Backend
  from pasta_eln.miscTools import outputString
  if not projectGroup:
    with open(Path.home()/'.pastaELN.json','r', encoding='utf-8') as fIn:
      config = json.load(fIn)
      print('Possible project groups:','  '.join(config['projectGroups'].keys()))
    projectGroup = input('Enter project group: ').strip()
  be = Backend(projectGroup)
  print('\n\nOUTPUT:')
  outputString('print','info', be.checkDB(outputStyle='text', repair=repair))
  return

def delete(projectGroup:str='', docID:str='') -> None:
  """ Delete a document
  Args:
    projectGroup (str): from which project group to delete
    docID (str): which ID to delete
  """
  from pasta_eln.backend import Backend
  if not projectGroup:
    with open(Path.home()/'.pastaELN.json','r', encoding='utf-8') as fIn:
      config = json.load(fIn)
      print('Possible project groups:','  '.join(config['projectGroups'].keys()))
    projectGroup = input('Enter project group: ').strip()
  be = Backend(projectGroup)
  if not docID:
    docID = input('Enter docID: ').strip()
  be.db.remove(docID)
  return


def main() -> None:
  '''
  Main function
  '''
  print('\n-------------------------------------------------------------------------')
  print(  'Manage users and databases for PASTA-ELN on a local couchDB installation')
  print(  '-------------------------------------------------------------------------')
  while True:
    print('\nCommands - general: [q]uit; [d]elete a document\n - update: [c]onvert couchDB to SQLite; [t]ranslate disk structure from V2->v3\n - database integrity: [v]erify; [r]epair')
    command = input('> ')
    if command == 'c':
      couchDB2SQLite()
    elif command == 't':
      translateV2_V3()
    elif command == 'v':
      verifyPasta()
    elif command == 'r':
      verifyPasta(repair=True)
    elif command == 'd':
      delete()
    elif command == 'q':
      break
    else:
      print("Unknown command or incomplete entries.")


if __name__ ==  '__main__':
  main()
