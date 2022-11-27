#!/usr/bin/python3
"""Commandline utility to admin the remote server"""
import sys, json, secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
import requests
import keyring as cred
from PIL import Image, ImageDraw, ImageFont

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#encrypt data
#https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
backend = default_backend()
iterationsGlobal = 100_000
def _derive_key(password: bytes, salt: bytes, iterations: int = iterationsGlobal) -> bytes:
  """
  derive key helper fuction
  """
  kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations, backend=backend)
  return b64e(kdf.derive(password))
def passwordEncrypt(message: bytes, iterations: int = iterationsGlobal) -> bytes:
  """
  encrypt with password
  """
  salt = secrets.token_bytes(16)
  key = _derive_key('pastaDB_2022'.encode(), salt, iterations)
  return b64e(b'%b%b%b' % (salt, iterations.to_bytes(4, 'big'), b64d(Fernet(key).encrypt(message))))
def passwordDecrypt(token: bytes) -> bytes:
  """
  decrypt with pasword
  """
  decoded = b64d(token)
  salt, iterNum, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
  iterations = int.from_bytes(iterNum, 'big')
  key = _derive_key('pastaDB_2022'.encode(), salt, iterations)
  return Fernet(key).decrypt(token)

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
  resp = requests.put(url+'/'+userDB, headers=headers, auth=auth)
  if not resp.ok:
    print("**ERROR 1: put not successful",resp.reason)
    return

  # create user
  data = {"docs":[{"_id":"org.couchdb.user:"+userName,"name": userName,"password":userPW,
    "roles":[userDB+"-W"], "type": "user", "orcid": ""}]}
  data = json.dumps(data)
  resp = requests.post(url+'/_users/_bulk_docs', headers=headers, auth=auth, data=data)
  if not resp.ok:
    print("**ERROR 2: post not successful",resp.reason)
    return

  # create _security in database
  data = {"admins": {"names":[],"roles":[userDB+"-W"]},
          "members":{"names":[],"roles":[userDB+"-R"]}}
  data = json.dumps(data)
  resp = requests.put(url+'/'+userDB+'/_security', headers=headers, auth=auth, data=data)
  if not resp.ok:
    print("**ERROR 3: post not successful",resp.reason)
    return

  # create _design/authentication in database
  data = {"validate_doc_update": "function(newDoc, oldDoc, userCtx) {"+\
    "if (userCtx.roles.indexOf('"+userDB+"-W')!==-1){return;} "+\
    "else {throw({unauthorized:'Only Writers (W) may edit the database'});}}"}
  data = json.dumps(data)
  resp = requests.put(url+'/'+userDB+'/_design/authentication', headers=headers, auth=auth, data=data)
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
  resp = requests.get(url+'/_users/_all_docs', headers=headers, auth=auth)
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
    respI = requests.get(url+'/_users/'+i['id'], headers=headers, auth=auth)
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
  resp = requests.get(url+'/_all_dbs', headers=headers, auth=auth)
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
    respI = requests.get(url+'/'+i+'/_security', headers=headers, auth=auth)
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
    respI = requests.get(url+'/'+i+'/_design/authentication', headers=headers, auth=auth)
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
  resp = requests.get(url, headers=headers)
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
    resp = requests.get(url+'/'+iDB, headers=headers, auth=authUser)
    if resp.ok:
      print("-> Database can be read")
    else:
      print("**ERROR: Database cannot be read")
      break
    #test server with user credentials 2
    resp = requests.get(url+'/'+iDB+'/_design/authentication', headers=headers, auth=authUser)
    if resp.ok:
      print("-> Authentication can be read")
    else:
      print("**ERROR: Authentication  cannot be read")
      break
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
    print('\nCommands: [q]uit; [n]ew user; list [u]ser; list [d]atabases; [t]est user')
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
    elif command == 't' and userName and userPassword and len(userName)>2 and len(userPassword)>2:
      testUser(url, auth, userName, userPassword)
    else:
      print("Unknown command or incomplete entries.")


if __name__ ==  '__main__':
  main()
