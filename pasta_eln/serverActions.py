#!/usr/bin/python3
"""Commandline utility to admin the remote server"""
import sys, json, base64, os
from typing import Any
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import requests
from requests.structures import CaseInsensitiveDict

def passwordEncrypt(message:str) -> bytes:
  """
  obfuscate message
  """
  return base64.b64encode(bytearray(message, encoding='utf-8'))
def passwordDecrypt(message:bytes) -> str:
  """
  de-obfuscate message
  """
  return base64.b64decode(message).decode('utf-8')

#global variables
headers:CaseInsensitiveDict[str]= CaseInsensitiveDict()
headers["Content-Type"] = "application/json"


def couchDB2SQLite(userName:str='', password:str='', database:str='', path:str='') -> None:
  """
  Backup everything of the CouchDB installation across all databases and all configurations
  - remote location uses username/password combo in local keystore
  - local location requires username and password

  Args:
    userName (str): username
    password (str): password
  """
  from .sqlite import SqlLiteDB
  from .handleDictionaries import fillDocBeforeCreate
  # get username and password
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
    print(f'DocID: {docID}')
    doc   = requests.get(f'http://{location}:5984/{database}/{docID}', headers=headers, auth=authUser, timeout=10).json()
    # translate to new style
    doc['id'] = doc.pop('_id')
    for key in ('name','user','type','gui','tags','client'):
      doc[key] = doc.pop(f'-{key}')
    doc['dateCreated']  = doc['-date']
    doc['dateModified'] = doc.pop('-date')
    doc['branch'] = doc.pop('-branch')[0] | {'op':'c'}
    del doc['_rev']

    doc = fillDocBeforeCreate(doc, doc['type'])
    db.saveDoc(doc)
    if '_attachments' in doc:
      for att in doc['_attachments']:
        docAttach = requests.get(f'http://{location}:5984/{database}/{docID}/{att}',
                                  headers=headers, auth=authUser, timeout=10).json()
        print(docAttach)
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
    if command == 'q':
      break
    else:
      print("Unknown command or incomplete entries.")


if __name__ ==  '__main__':
  main()
