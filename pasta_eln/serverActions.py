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


def backupCouchDB(location:str='', userName:str='', password:str='') -> None:
  """
  Backup everything of the CouchDB installation across all databases and all configurations
  - remote location uses username/password combo in local keystore
  - local location requires username and password

  Args:
    location (str): 'local', 'remote', else: ask user via CLI
    userName (str): username
    password (str): password
  """
  # get username and password
  if not location:
    location = 'remote' if input('Enter location: [r] remote; else local: ')=='r' else 'local'
  if location=='local':
    location = '127.0.0.1'
    if not userName:
      userName = input('Enter local admin username: ').strip()
    if not password:
      password = input('Enter password: ').strip()
  else:
    print('**ERROR: wrong location given.')
    return
  # use information
  authUser = requests.auth.HTTPBasicAuth(userName, password)
  resp = requests.get(f'http://{location}:5984/_all_dbs', headers=headers, auth=authUser, timeout=10)
  if resp.status_code != 200:
    print('**ERROR response for _all_dbs wrong', resp.text)
    print('Username and password', userName, password)
    return
  timestamp = datetime.now().isoformat().split('.')[0].replace('-','').replace(':','')
  zipFileName = 'couchDB_backup_'+location.replace('.','')+'_'+timestamp
  print(f'Create zip-file {zipFileName}.zip')
  databases = resp.json()
  with ZipFile(f'{zipFileName}.zip', 'w', compression=ZIP_DEFLATED) as zipFile:
    for database in databases:
      if database.startswith('_'):
        print('Special database', database, ': Nothing to do')
      else:
        print('Backup normal database ',database)
        resp = requests.get(f'http://{location}:5984/{database}/_all_docs', headers=headers, auth=authUser, timeout=10)
        for item in resp.json()['rows']:
          docID = item['id']
          doc   = requests.get(f'http://{location}:5984/{database}/{docID}', headers=headers, auth=authUser, timeout=10).json()
          zipFile.writestr(f'{zipFileName}/research/{docID}', json.dumps(doc))
          if '_attachments' in doc:
            for att in doc['_attachments']:
              docAttach = requests.get(f'http://{location}:5984/{database}/{docID}/{att}',
                                        headers=headers, auth=authUser, timeout=10).json()
              zipFile.writestr(f'{zipFileName}/{database}/{docID}_attach/{att}', json.dumps(docAttach))
        #_design/authentication is automatically included
        #_security
        doc   = requests.get(f'http://{location}:5984/{database}/_security',
                              headers=headers, auth=authUser, timeout=10).json()
        zipFile.writestr(f'{zipFileName}/{database}/_security', json.dumps(doc))
    with open(Path.home()/'.pastaELN.json', encoding='utf-8') as fIn:
      configuration = json.loads(fIn.read())
      zipFile.writestr(f'{zipFileName}/pastaELN.json', json.dumps(configuration))
  return


def restoreCouchDB(location:str='', userName:str='', password:str='', fileName:str='') -> None:
  """
  restore everything to the CouchDB installation across all databases and all configurations
  - remote location uses username/password combo in local keystore
  - local location requires username and password

  Args:
    location (str): 'local', 'remote', else: ask user via CLI
    userName (str): username
    password (str): password
    fileName (str): file used for restoration
  """
  # get username and password
  if not location:
    location = 'remote' if input('Enter location: [r]emote; else local: ')=='r' else 'local'
  if location=='local':
    location = '127.0.0.1'
    if not userName:
      userName = input('Enter username: ').strip()
    if not password:
      password = input('Enter password: ').strip()
  else:
    print('**ERROR: wrong location given.')
    return
  if not fileName:
    possFiles = [i for i in os.listdir('.') if i.startswith('couchDB') and i.endswith('.zip')]
    for idx, i in enumerate(possFiles):
      print(f'[{str(idx + 1)}] {i}')
    fileChoice = input(f'Which file to use for restored? (1-{len(possFiles)}) ')
    fileName = possFiles[int(fileChoice)-1] if fileChoice else possFiles[0]
  # use information
  authUser = requests.auth.HTTPBasicAuth(userName, password)
  with ZipFile(fileName, 'r', compression=ZIP_DEFLATED) as zipFile:
    files = [i for i in zipFile.namelist() if not i.endswith('/')]  #only files, no folders
    #first run through: create documents and design documents
    for fileI in files:
      fileParts = fileI.split('/')[1:]
      if fileParts==['pastaELN.json']: #do not recreate file, it is only there for manual recovery
        continue
      if len(fileParts)!=2:
        print(f"**ERROR: Cannot process file {fileI}: does not have 1+2 parts")
        continue
      database = fileParts[0]
      docID = fileParts[1]
      if docID.endswith('_attach'):
        continue #Do in second loop
      #test if database is exists: create otherwise
      resp = requests.get(f'http://{location}:5984/{database}/_all_docs', headers=headers, auth=authUser, timeout=10)
      if resp.status_code != 200 and resp.json()['reason']=='Database does not exist.':
        resp = requests.put(f'http://{location}:5984/{database}', headers=headers, auth=authUser, timeout=10)
        if not resp.ok:
          print("**ERROR: could not create database",resp.reason)
          return
      #test if document is exists: create otherwise
      if docID=='_design':
        docID = '/'.join(fileParts[1:])
      resp = requests.get(f'http://{location}:5984/{database}/{docID}', headers=headers, auth=authUser, timeout=10)
      if resp.status_code != 200 and resp.json()['reason']=='missing':
        with zipFile.open(fileI) as dataIn:
          doc = json.loads( dataIn.read() )  #need doc conversion since deleted from it
          del doc['_rev']
          if '_attachments' in doc:
            del doc['_attachments']
          resp = requests.put(f'http://{location}:5984/{database}/{docID}', data=json.dumps(doc), headers=headers, auth=authUser, timeout=10)
          if resp.ok:
            print('Saved document:', database, docID)
          else:
            print("**ERROR: could not save document:",resp.reason, database, docID, '\n', doc)
    #second run through: create attachments
    for fileI in files:
      fileParts = fileI.split('/')[1:]
      if fileParts==['pastaELN.json'] or fileParts[-1]=='' or fileParts[-2]=='_design': #do not recreate file, it is only there for manual recovery
        continue
      if len(fileParts)!=2:
        print(f"**ERROR-Attachment: Cannot process file {fileI}: does not have 1+2 parts")
        continue
      database = fileParts[0]
      docID = fileParts[1]
      if not docID.endswith('_attach'):
        continue #Did already in the first loop
      #test if attachment exists: create otherwise
      attachPath = f'{docID[:-7]}/{fileParts[-1]}'
      resp = requests.get(f'http://{location}:5984/{database}/{attachPath}', headers=headers, auth=authUser, timeout=10)
      if resp.status_code == 404 and 'missing' in resp.json()['reason']:
        with zipFile.open(fileI) as dataIn:
          attachDoc = dataIn.read()
          resp = requests.get(f'http://{location}:5984/{database}/{docID[:-7]}', headers=headers, auth=authUser, timeout=10)
          headers['If-Match'] = resp.json()['_rev'] #will be overwritten each time
          resp = requests.put(f'http://{location}:5984/{database}/{attachPath}', data=attachDoc, headers=headers, auth=authUser, timeout=10)
          if resp.ok:
            print('Saved attachment:', database, attachPath)
          else:
            print('\n**ERROR: could not save attachment:',resp.reason, database, attachPath,'\n', doc)
  return


def main() -> None:
  '''
  Main function
  '''
  print("Could not get credentials for the remote server from keyring.")
  ## URL
  url = input('Enter the URL without http and without port: ')
  if len(url)<2:
    print('* No legit URL entered: exit')
    sys.exit(1)
  ## User-name, password
  administrator = input('Enter the administrator username: ')
  password =      input('Enter the administrator password: ')
  #assemble information
  url = f'http://{url}:5984'
  auth = requests.auth.HTTPBasicAuth(administrator, password)

  print('\n-------------------------------------------------------------------------')
  print(  'Manage users and databases for PASTA-ELN on a local couchDB installation')
  print(  '-------------------------------------------------------------------------')
  while True:
    print('\nCommands: [q]uit; [b]ackup data; [r]estore data')
    command = input('> ')
    userName, userPassword = '', ''
    if command == 'q':
      break
    # ask questions for parameters
    if command in ['n', 't', 'l']:
      userName =      input('Enter the user-name, e.g. m.miller: ')
    if command in ['t', 'l']:
      userPassword =  input('Enter the user-password: ')
    # execute command
    elif command == 'b':
      backupCouchDB()
    elif command == 'r':
      restoreCouchDB()
    else:
      print("Unknown command or incomplete entries.")


if __name__ ==  '__main__':
  main()
