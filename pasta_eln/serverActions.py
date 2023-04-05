#!/usr/bin/python3
"""Commandline utility to admin the remote server"""
import sys, json, secrets, base64, os
import requests
from datetime import datetime
import keyring as cred
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont

#TODO_P5 serverConfiguration: this should become a GUI and CLI and separate into three-files: functions, CLI, GUI
# add: delete all documents, backup database, backup server (incl. all small things)

def passwordEncrypt(message):
  """
  obfuscate message
  """
  return base64.b64encode(bytearray(message, encoding='utf-8'))
def passwordDecrypt(message):
  """
  de-obfuscate message
  """
  return base64.b64decode(message).decode('utf-8')

#global variables
headers = requests.structures.CaseInsensitiveDict()
headers["Content-Type"] = "application/json"


def createUserDatabase(url, auth, userName):
  '''
  create a new user and database

  Args:
    url (string): url incl. http and port
    auth (object): HTTPBasicAuth object
    userName (string): user name, e.g. m.miller
  '''
  userPW = secrets.token_urlsafe(13)
  userDB = userName.replace('.','_')

  # create database
  resp = requests.put(url+'/'+userDB, headers=headers, auth=auth, timeout=10)
  if not resp.ok:
    print("**ERROR 1: put not successful",resp.reason)
    return

  # create user
  data = {"docs":[{"_id":"org.couchdb.user:"+userName,"name": userName,"password":userPW,
    "roles":[userDB+"-W"], "type": "user", "orcid": ""}]}
  data = json.dumps(data)
  resp = requests.post(url+'/_users/_bulk_docs', headers=headers, auth=auth, data=data, timeout=10)
  if not resp.ok:
    print("**ERROR 2: post not successful",resp.reason)
    return

  # create _security in database
  data = {"admins": {"names":[],"roles":[userDB+"-W"]},
          "members":{"names":[],"roles":[userDB+"-R"]}}
  data = json.dumps(data)
  resp = requests.put(url+'/'+userDB+'/_security', headers=headers, auth=auth, data=data, timeout=10)
  if not resp.ok:
    print("**ERROR 3: post not successful",resp.reason)
    return

  # create _design/authentication in database
  data = {"validate_doc_update": "function(newDoc, oldDoc, userCtx) {"+\
    "if (userCtx.roles.indexOf('"+userDB+"-W')!==-1){return;} "+\
    "else {throw({unauthorized:'Only Writers (W) may edit the database'});}}"}
  data = json.dumps(data)
  resp = requests.put(url+'/'+userDB+'/_design/authentication',headers=headers,auth=auth,data=data,timeout=10)
  if not resp.ok:
    print("**ERROR 4: post not successful",resp.reason)
    return

  print('SUCCESS: Server interaction')
  #create image
  img = Image. new('RGB', (500, 500), color = (0, 65, 118))
  d = ImageDraw. Draw(img)
  font = ImageFont.truetype("arial.ttf", 24)
  d.text((30, 30),  "configuration name: remote", fill=(240,240,240), font=font)
  d.text((30, 70),  "user-name: "+userName, fill=(240,240,240), font=font)
  d.text((30,110),  "password: " +userPW,   fill=(240,240,240), font=font)
  d.text((30,150),  "database: " +userDB,   fill=(240,240,240), font=font)
  d.text((30,190),  "Remote configuration", fill=(240,240,240), font=font)
  d.text((30,230),  "Server:   " +url, fill=(240,240,240), font=font)
  img.save(userDB+'.png')
  #create key file
  data = {"configuration name":"remote","user-name":userName,"password":userPW,"database":userDB,\
    "Remote configuration":"true","Server":url}
  data = passwordEncrypt(json.dumps(data).encode())
  with open(userDB+'.key','bw') as fOut:
    fOut.write(data)
  return


def listUsers(url, auth, verbose=True):
  '''
  list (and test) all users

  Args:
    url (string): url incl. http and port
    auth (object): HTTPBasicAuth object
    verbose (bool): verbose output

  Returns:
    dict: user information
  '''
  resp = requests.get(url+'/_users/_all_docs', headers=headers, auth=auth, timeout=10)
  if not resp.ok:
    print("**ERROR: get not successful",resp.reason)
    return {}
  if verbose:
    print("List of users:")
  results = {}
  for i in json.loads(resp.text)['rows']:
    if i['id']=='_design/_auth':
      continue
    if verbose:
      print(i['id'][17:]+'       key:'+i['key'][17:])
    respI = requests.get(url+'/_users/'+i['id'], headers=headers, auth=auth, timeout=10)
    respI = json.loads(respI.text)
    results[respI['name']] = respI['roles']
    if verbose:
      print('  Roles',respI['roles'])
      print('  Name ',respI['name'])
      if respI['name'].replace('.','_')+'-W' in respI['roles']:
        print('  -> corresponds to role-name convention')
      else:
        print('  -> DOES NOT correspond to role-name convention:',respI['name'])
      if i['id'].endswith(respI['name']):
        print('  -> corresponds to id-name convention')
      else:
        print('  -> DOES NOT correspond to id-name convention:',respI['name'])
      print('  Orcid',respI['orcid'])
  if verbose:
    return {}
  return results


def listDB(url, auth, verbose):
  '''
  list (and test) all databases

  Args:
    url (string): url incl. http and port
    auth (object): HTTPBasicAuth object
    verbose (bool): verbose output

  Returns:
    dict: database information
  '''
  resp = requests.get(url+'/_all_dbs', headers=headers, auth=auth, timeout=10)
  if not resp.ok:
    print("**ERROR: get not successful",resp.reason)
    return {}
  if verbose:
    print("List of databases:")
  results = {}
  for i in json.loads(resp.text):
    if i in ['_replicator','_users']:
      continue
    if verbose:
      print(i)
    # test security
    respI = requests.get(url+'/'+i+'/_security', headers=headers, auth=auth, timeout=10)
    respI = json.loads(respI.text)
    security = [respI['admins']['roles'], respI['members']['roles']]
    if verbose:
      print('  Write',respI['admins']['roles'])
      print('  Read ',respI['members']['roles'])
      if (respI['admins']['roles'][0].endswith('-W') and
          respI['members']['roles'][0].endswith('-R') and
          respI['admins']['roles'][0].split('-')[0] == respI['members']['roles'][0].split('-')[0]):
        print('  -> everything ok')
      else:
        print('  -> **ERROR** security')
    # test authentication
    respI = requests.get(url+'/'+i+'/_design/authentication', headers=headers, auth=auth, timeout=10)
    respI = json.loads(respI.text)['validate_doc_update']
    respI = respI.split('indexOf')[1].split('!==')[0].strip()[2:-2]
    results[i] = security+[respI]
    if verbose:
      if respI == i+'-W':
        print('  -> everything ok')
      else:
        print('  -> **ERROR** authentication',respI)
  if verbose:
    return {}
  return results


def testUser(url, auth, userName, userPassword):
  '''
  test if configuration for this user is correct
  '''
  # Test if server exists
  resp = requests.get(url, headers=headers, timeout=10)
  if resp.ok:
    print("-> Server exists")
  else:
    print("**ERROR: Server cannot be reached")
    return
  authUser = requests.auth.HTTPBasicAuth(userName, userPassword)
  if auth is None:
    userDB = [userName.replace('.','_')]
  else:
    # test if configuration corresponds to naming convention
    users     = listUsers(url, auth, False)
    userDB    = [i[:-2] for i in users[userName]]  #list
    databases = listDB(url, auth, False)
  for iDB in userDB:
    if auth is not None:
      write = databases[iDB][0][0]
      read  = databases[iDB][1][0]
      authen= databases[iDB][2]
      if write.endswith('-W') and read.endswith('-R') and authen.endswith('-W') and \
        write[:-2] == read[:-2] and write[:-2] == authen[:-2]:
        print("-> User database and user-name correct")
      else:
        print("**ERROR: ",write,read,authen,iDB)
        break
    #test server with user credentials 1
    resp = requests.get(url+'/'+iDB, headers=headers, auth=authUser, timeout=10)
    if resp.ok:
      print("-> Database can be read")
    else:
      print("**ERROR: Database cannot be read")
      break
    #test server with user credentials 2
    resp = requests.get(url+'/'+iDB+'/_design/authentication', headers=headers, auth=authUser, timeout=10)
    if resp.ok:
      print("-> Authentication can be read")
    else:
      print("**ERROR: Authentication  cannot be read")
      break
  return


def testLocal(userName, password, database=''):
  """
  test local server

  Args:
    userName (str): user name at local server
    password (str): password at local server
    database (str): couchdb database

  Returns:
    str: success and errors in '\n'-string
  """
  answer = ''
  resp = requests.get('http://127.0.0.1:5984', headers=headers, timeout=10)
  if resp.ok:
    answer += 'success: Local server exists\n'
  else:
    answer += 'ERROR: Local server is not working\n'
  authUser = requests.auth.HTTPBasicAuth(userName, password)
  resp = requests.get('http://127.0.0.1:5984/_all_dbs', headers=headers, auth=authUser, timeout=10)
  if resp.ok:
    answer += 'success: Local username and password ok\n'
  else:
    answer += 'ERROR: Local username or password incorrect\n'
  if database!='':
    resp = requests.get('http://127.0.0.1:5984/'+database, headers=headers, auth=authUser, timeout=10)
    if resp.ok:
      answer += 'success: Local database exists\n'
    else:
      answer += 'Warning: Local database does not exist\n'
  return answer


def testRemote(url, userName, password, database):
  """
  test remote server

  Args:
    url (str): url of remote server
    userName (str): user name at remote server
    password (str): password at remote server
    database (str): couchdb database

  Returns:
    str: success and errors in '\n'-string
  """
  answer = ''
  resp = requests.get(url, headers=headers, timeout=10)
  if resp.ok:
    answer += 'success: Remote server exists\n'
  else:
    answer += 'ERROR: Remote server is not working\n'
  authUser = requests.auth.HTTPBasicAuth(userName, password)
  resp = requests.get(url+'/'+database, headers=headers, auth=authUser, timeout=10)
  if resp.ok:
    answer += 'success: Remote database exists\n'
  else:
    answer += 'ERROR: Remote username, password, database incorrect\n'
  return answer


def backupCouchDB(location='', userName='', password=''):
  """
  Backup everything of the CouchDB installation accross all databases and all configurations
  - remote location uses username/password combo in local keystore
  - local location requires username and password

  Args:
    location (str): 'local', 'remote', else: ask user via CLI
    userName (str): username
    password (str): password
  """
  # get username and password
  if location=='':
    location = 'remote' if input('Enter location: [r] remote; else local: ')=='r' else 'local'
  if location=='local':
    location = '127.0.0.1'
    if userName=='':
      userName = input('Enter username: ').strip()
    if password=='':
      password = input('Enter password: ').strip()
  elif location=='remote':
    try:
      myString = cred.get_password('pastaDB','admin')
      location, userName, password = myString.split(':')
      print("URL and credentials successfully read from keyring")
    except:
      print("**ERROR Could not get credentials from keyring. Please create manually.")
      return
  else:
    print('**ERROR: wrong location given.')
    return
  # use information
  authUser = requests.auth.HTTPBasicAuth(userName, password)
  kwargs   = {'headers':headers, 'auth':authUser, 'timeout':10}
  resp = requests.get('http://'+location+':5984/_all_dbs', **kwargs)
  if resp.status_code != 200:
    print('**ERROR response for _all_dbs wrong', resp.text)
    print('Username and password', userName, password)
    return
  timestamp = datetime.now().isoformat().split('.')[0].replace('-','').replace(':','')
  zipFileName = 'couchDB_backup_'+location.replace('.','')+'_'+timestamp
  print('Create zip-file '+zipFileName+'.zip')
  databases = resp.json()
  with ZipFile(zipFileName+'.zip', 'w', compression=ZIP_DEFLATED) as zipFile:
    for database in databases:
      if database.startswith('_'):
        print('Special database', database, ': Nothing to do')
      else:
        print('Backup normal database ',database)
        resp = requests.get('http://'+location+':5984/'+database+'/_all_docs', **kwargs)
        for item in resp.json()['rows']:
          docID = item['id']
          doc   = requests.get('http://'+location+':5984/'+database+'/'+docID, **kwargs).json()
          zipFile.writestr(zipFileName+'/'+database+'/'+docID, json.dumps(doc))
          if '_attachments' in doc:
            for att in doc['_attachments']:
              docAttach = requests.get('http://'+location+':5984/'+database+'/'+docID+'/'+att,**kwargs).json()
              zipFile.writestr(zipFileName+'/'+database+'/'+docID+'_attach/'+att, json.dumps(docAttach))
        #_design/authentication is automatically included
        #_security
        doc   = requests.get('http://'+location+':5984/'+database+'/_security', **kwargs).json()
        zipFile.writestr(zipFileName+'/'+database+'/_security', json.dumps(doc))
    return


def restoreCouchDB(location='', userName='', password='', fileName=''):
  """
  restore everything to the CouchDB installation accross all databases and all configurations
  - remote location uses username/password combo in local keystore
  - local location requires username and password

  Args:
    location (str): 'local', 'remote', else: ask user via CLI
    userName (str): username
    password (str): password
    fileName (str): file used for restoration
  """
  # get username and password
  if location=='':
    location = 'remote' if input('Enter location: [r]emote; else local: ')=='r' else 'local'
  if location=='local':
    location = '127.0.0.1'
    if userName=='':
      userName = input('Enter username: ').strip()
    if password=='':
      password = input('Enter password: ').strip()
  elif location=='remote':
    try:
      myString = cred.get_password('pastaDB','admin')
      location, userName, password = myString.split(':')
      print("URL and credentials successfully read from keyring")
    except:
      print("**ERROR Could not get credentials from keyring. Please create manually.")
      return
  else:
    print('**ERROR: wrong location given.')
    return
  if fileName=='':
    possFiles = [i for i in os.listdir('.') if i.startswith('couchDB') and i.endswith('.zip')]
    for idx, i in enumerate(possFiles):
      print('['+str(idx+1)+'] '+i)
    fileName = input('Which file to use for restored? (1-'+str(len(possFiles))+') ')
    fileName = possFiles[int(fileName)-1]
  # use information
  authUser = requests.auth.HTTPBasicAuth(userName, password)
  kwargs   = {'headers':headers, 'auth':authUser, 'timeout':10}
  with ZipFile(fileName, 'r', compression=ZIP_DEFLATED) as zipFile:
    files = zipFile.namelist()
    #first run through: create documents and design documents
    for fileI in files:
      fileParts = fileI.split('/')[1:]
      database = fileParts[0]
      docID = fileParts[1]
      if docID.endswith('_attach'):
        continue #Do in second loop
      #test if database is exists: create otherwise
      resp = requests.get('http://'+location+':5984/'+database+'/_all_docs', **kwargs)
      if resp.status_code != 200 and resp.json()['reason']=='Database does not exist.':
        resp = requests.put('http://'+location+':5984/'+database, **kwargs)
        if not resp.ok:
          print("**ERROR: could not create database",resp.reason)
          return
      #test if document is exists: create otherwise
      if docID=='_design':
        docID = '/'.join(fileParts[1:])
      resp = requests.get('http://'+location+':5984/'+database+'/'+docID, **kwargs)
      if resp.status_code != 200 and resp.json()['reason']=='missing':
        doc = json.loads( zipFile.open(fileI).read() )  #need doc conversion since deleted from it
        del doc['_rev']
        if '_attachments' in doc:
          del doc['_attachments']
        resp = requests.put('http://'+location+':5984/'+database+'/'+docID, **kwargs,data=json.dumps(doc) )
        if resp.ok:
          print('Saved document:', database, docID)
        else:
          print("**ERROR: could not save document:",resp.reason, database, docID, '\n', doc)
    #second run through: create attachments
    for fileI in files:
      fileParts = fileI.split('/')[1:]
      database = fileParts[0]
      docID = fileParts[1]
      if not docID.endswith('_attach'):
        continue #Did already in the first loop
      #test if attachement exists: create otherwise
      attachPath =docID[:-7]+'/'+fileParts[-1]
      resp = requests.get('http://'+location+':5984/'+database+'/'+attachPath, **kwargs)
      if resp.status_code == 404 and 'missing' in resp.json()['reason']:
        attachDoc = zipFile.open(fileI).read()
        resp = requests.get('http://'+location+':5984/'+database+'/'+docID[:-7],**kwargs)
        headers['If-Match'] = resp.json()['_rev'] #will be overwritten each time
        kwargs   = {'headers':headers, 'auth':authUser, 'timeout':10}
        resp = requests.put('http://'+location+':5984/'+database+'/'+attachPath,**kwargs, data=attachDoc)
        if resp.ok:
          print('Saved attachment:', database, attachPath)
        else:
          print('\n**ERROR: could not save attachment:',resp.reason, database, attachPath,'\n', doc)
  return


def main():
  '''
  Main function
  '''
  #set information once in keyring
  #  myString = url+':'+adminUserName+':'+adminPassword
  #  url without http and port
  #  cred.set_password('pastaDB','admin',myString)
  try:
    myString = cred.get_password('pastaDB','admin')
    url, administrator, password = myString.split(':')
    print("URL and credentials successfully read from keyring")
  except:
    print("Could not get credentials from keyring.")
    ## URL
    url = input('Enter the URL without http and without port: ')
    if len(url)<2:
      print('* No legit URL entered: exit')
      sys.exit(1)
    ## User-name, password
    administrator = input('Enter the administrator username: ')
    password =      input('Enter the administrator password: ')
  #assemble information
  url = 'http://'+url+':5984'
  auth = requests.auth.HTTPBasicAuth(administrator, password)

  while True:
    print('\nAdopt a server to PASTA-ELN\nCommands: [q]uit; [n]ew user; list [u]ser; list [d]atabases; '+\
          '[t]est user; [b]ackup data; [r]estore data')
    command = input('> ')
    userName, userPassword = '', ''
    if command == 'q':
      break
    # ask questions for parameters
    if command in ['n', 't']:
      userName =      input('Enter the user-name, e.g. m.miller: ')
    if command in ['t']:
      userPassword =      input('Enter the user-password: ')
    # execute command
    if command == 'n' and userName and len(userName)>2:
      createUserDatabase(url, auth, userName)
    elif command == 'u':
      listUsers(url, auth)
    elif command == 'd':
      listDB(url, auth, True)
    elif command == 'b':
      backupCouchDB()
    elif command == 'r':
      restoreCouchDB()
    elif command == 't' and userName and userPassword and len(userName)>2 and len(userPassword)>2:
      testUser(url, auth, userName, userPassword)
    else:
      print("Unknown command or incomplete entries.")


if __name__ ==  '__main__':
  main()
