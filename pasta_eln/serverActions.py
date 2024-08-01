#!/usr/bin/python3
"""Commandline utility to admin the remote server"""
import json
from typing import Any
from pathlib import Path
import requests
from requests.structures import CaseInsensitiveDict
from .sqlite import SqlLiteDB
from .handleDictionaries import fillDocBeforeCreate

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
    # translate to new style
    doc['id'] = doc.pop('_id')
    for key in ('name','user','type','gui','tags','client','branch'):
      doc[key] = doc.pop(f'-{key}')
    doc['dateCreated']  = doc['-date']
    doc['dateModified'] = doc.pop('-date')
    doc['branch'] = doc['branch'][0] | {'op':'c'} if doc['branch'] else \
                    {'stack':[], 'child':9999, 'path':None, 'show':[True], 'op':'c'}
    del doc['_rev']
    # save
    doc = fillDocBeforeCreate(doc, doc['type'])
    db.saveDoc(doc)
    if '_attachments' in doc:
      for att in doc['_attachments']:
        docAttach = requests.get(f'http://{location}:5984/{database}/{docID}/{att}',
                                  headers=headers, auth=authUser, timeout=10).json()
        setAll = set(docAttach.keys())
        setImportant  = setAll.difference({'-date','date','-client','image','type','-type','client','-name','-branch','branch'})
        if not setImportant or ('-name' in docAttach and docAttach['-name']=='new folder'):
          continue
        print(setImportant)
        date = docAttach['-date'] if '-date' in docAttach else docAttach['date'] if 'date' in docAttach else att
        if '-client' in docAttach:
          del docAttach['-client']
        db.cursor.execute("INSERT INTO changes VALUES (?,?,?)", [docID, date, json.dumps(docAttach)])
      db.connection.commit()
  return


def main() -> None:
  '''
  Main function
  '''
  print('\n-------------------------------------------------------------------------')
  print(  'Manage users and databases for PASTA-ELN on a local couchDB installation')
  print(  '-------------------------------------------------------------------------')
  while True:
    print('\nCommands: [q]uit; [c]onvert couchDB to SQLite')
    command = input('> ')
    if command == 'c':
      couchDB2SQLite()
    elif command == 'q':
      break
    else:
      print("Unknown command or incomplete entries.")


if __name__ ==  '__main__':
  main()
