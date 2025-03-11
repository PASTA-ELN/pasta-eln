#!/usr/bin/python3
"""Commandline utility to admin local installation and convert from Pasta-ELN version 2"""
import json
import os
import platform
import re
import shutil
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Union
import requests
from requests.structures import CaseInsensitiveDict
from pasta_eln.backend import Backend
from pasta_eln.elabFTWsync import Pasta2Elab
from pasta_eln.fixedStringsJson import CONF_FILE_NAME
from pasta_eln.textTools.stringChanges import outputString


class Tools:
  """Commandline utility to admin local installation and convert from Pasta-ELN version 2"""
  def __init__(self) -> None:
    self.backend:Backend = Backend()
    self.projectGroup = ''


  def __choice__(self, command:str) -> str:
    """  depending on choice, execute command
    Args:
      command (str): command
    """
    helpString = 'Command line program to troubleshoot and possibly repair Pasta-ELN database\n'\
                'Commands - general:\n'\
                '  [h]elp: long help\n'\
                '  [q]uit\n'
    helpString += '  [p]rint a document\n'
    if command == 'p':
      self.printOrDelete()
    helpString += '  [d]elete a document\n'
    if command == 'd':
      self.printOrDelete(projectGroup='', docID='', output=False)
    helpString += '  [s]can all projects\n'
    if command == 's':
      self.scanAllProjects()

    helpString += 'Commands - update Version 2 -> Version 3:\n'
    helpString += '  [c]onvert couchDB to SQLite\n'
    if command == 'c':
      self.couchDB2SQLite()
    helpString += '  [t]ranslate disk structure from V2->v3\n'
    if command == 't':
      self.translateV2_V3()

    helpString += 'Commands - database integrity:\n'
    helpString += '  [v]erify\n'
    if command == 'v':
      self.verifyPasta()
    helpString += '  [r]epair\n'
    if command == 'r':
      self.verifyPasta('', self.__userQuestion__)
    helpString += '  [rA]epair: answer always "yes": WARNING can change too much\n'
    if command == 'rA':
      self.verifyPasta('', lambda t: self.__userQuestion__(t, True))
    helpString += '  [cp]-create a lost and found project: helpful for some repair operations\n'
    if command == 'cp':
      self.createLostAndFound()

    helpString += 'Commands - clone from / to server:\n'
    helpString += '  [ss]ync SEND ALL\n'
    helpString += '  [sg]ync GET ALL\n'
    if command in {'ss','sg'}:
      self.sync('', command)
    helpString += '  [pL]urge local database: REMOVE EVERYTHING\n'
    if command == 'pL':
      self.purgeLocal()
    helpString += '  [pR]urge remote database: REMOVE EVERYTHING\n'
    if command == 'pR':
      self.purgeRemote()

    helpString += 'Commands - deprecated:\n'
    helpString += '  [rp1] repair properties: add missing "."\n'
    if command == 'rp1':
      self.repairPropertiesDot()
    return helpString if command=='h' else 'Done'


  def __setBackend__(self, projectGroup:str='') -> None:
    """ Internal function: return backend based on project group
    Args:
      projectGroup (str): "name" of project group
    """
    with open(Path.home()/CONF_FILE_NAME, encoding='utf-8') as fIn:
      config = json.load(fIn)
      print('Project groups:','  '.join(f'{idx+1}-{i}' for idx,i in enumerate(config['projectGroups'].keys())))
    while not self.projectGroup:
      projectGroup = projectGroup or input('  Enter project group [number or name or entire text]: ').strip()
      if re.match(r'^\d+-\w+$', projectGroup):
        self.projectGroup = projectGroup.split('-')[1]
      elif re.match(r'^\d+$', projectGroup):
        self.projectGroup = list(config['projectGroups'].keys())[int(projectGroup)-1]
      elif projectGroup in config['projectGroups'].keys():
        self.projectGroup = projectGroup
      else:
        projectGroup = ''
    self.backend = Backend(self.projectGroup)
    return


  def __progressBar__(self, iteration:int, total:int=100, prefix:str='', suffix:str='', decimals:int=1,
                      length:int=100, fill:str='█', printEnd:str='') -> None:
    """
    Call in a loop to create terminal progress bar
    - https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters

    Args:
        iteration (int): current iteration
        total     (int): total iterations
        prefix    (str): prefix string
        suffix    (str): suffix string
        decimals  (int): positive number of decimals in percent complete
        length    (int): character length of bar
        fill      (int): bar fill character
        printEnd  (int): end character (e.g. "\r", "\r\n")
    """
    percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    barString = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{barString}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
      print()
    return


  def __updateProgressBar__(self, dType:str, data:str|int) -> None:
    """ update dialog
    - "text" and "append" will update the text

    Args:
      dType (str): what to update and how "text", "append", "count", "incr"
      data (str): str- or int-value to update with
    """
    if dType in {'text','append'} and isinstance(data, str):
      print(data)
    if dType=='count' and isinstance(data, int):
      self.__progressBar__(data)
    return


  def __userQuestion__(self, errorMessage:str, allYes:bool=False) -> bool:
    """ Ask user if repair should be done

    Args:
      errorMessage (str): error message
      allYes (bool): answer all questions with yes

    Return:
      bool: repair should be done
    """
    print(errorMessage)
    return True if allYes else input('Repair [yN]: ')=='y'


  def run(self, todos:list[str]=[]) -> None:
    """  run the list of given commands, else run while-loop until user ends
    Args:
      todos (list): string-commands
    """
    if todos:
      self.__setBackend__(todos.pop(0))
    while True:
      command = todos.pop(0) if todos else input('\nImportant commands [h]elp; [q]uit; [v]erify; [r]epair: ')
      if command == 'q':
        break
      print(self.__choice__(command))
    return


  def printOrDelete(self, projectGroup:str='', docID:str='', output:bool=True) -> None:
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


  def scanAllProjects(self, projectGroup:str='') -> None:
    """ Scan all projects to identify missing items

      Args:
        projectGroup (str): name of project group
    """
    if not self.projectGroup:
      self.__setBackend__(projectGroup)
    projectGroups = self.backend.db.getView('viewDocType/x0')['id'].values
    for projID in projectGroups:
      self.backend.scanProject(lambda i: self.__updateProgressBar__('count',i), projID)
    return


  def couchDB2SQLite(self, userName:str='', password:str='', database:str='', path:str='') -> None:
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
    db = self.backend.db
    resp = requests.get(f'http://{location}:5984/{database}/_all_docs', headers=headers, auth=authUser, timeout=10)
    for item in resp.json()['rows']:
      docID = item['id']
      if docID in ('-dataHierarchy-','-ontology-') or docID.startswith('_design/'):
        continue
      # print(f'DocID: {docID}')
      doc   = requests.get(f'http://{location}:5984/{database}/{docID}', headers=headers, auth=authUser, timeout=10).json()
      doc, attachments = self.translateDoc(doc)
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


  def translateDoc(self, doc:dict[str,Any], comment:str='') -> tuple[dict[str,Any],list[Any]]:
    """ translate to new style

    Args:
      doc (dict): input document
      comment (str): comment to add to the output, e.g. offending doc-id

    Returns:
      dict: output document
    """
    from .textTools.handleDictionaries import fillDocBeforeCreate
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


  def translateV2_V3(self, path:str='') -> None:
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
      docNew, _ = self.translateDoc(doc, aPath)
      del docNew['branch']['op']
      docNew['branch'] = [docNew['branch']]
      with open(Path(aPath)/'.id_pastaELN.json','w', encoding='utf-8') as fOut:
        fOut.write(json.dumps(docNew))
    return


  def verifyPasta(self, projectGroup:str='', repair:Union[None,Callable[[str],bool]]=None) -> None:
    """ Do the default verification of PastaELN. Adopted to CLI
      Args:
      projectGroup (str): name of project group
      repair (function): repair
    """
    if not self.projectGroup:
      self.__setBackend__(projectGroup)
    outputString('print','info', self.backend.checkDB(outputStyle='text', repair=repair, minimal=False))
    return



  def createLostAndFound(self, projectGroup:str='') -> None:
    """ Create a lost and found project that is the target of misc documents
      Args:
        projectGroup (str): name of project group
    """
    if not self.projectGroup:
      self.__setBackend__(projectGroup)
    self.backend.addData('x0', {'name': 'Lost and Found', 'comment': 'Location of lost database items'})
    return


  def purgeLocal(self, projectGroup:str='') -> None:
    """ Purge entire local storage, remove everything

      Args:
      projectGroup (str): name of project group
    """
    if not self.projectGroup:
      self.__setBackend__(projectGroup)
    dirName = self.backend.basePath
    if dirName.as_posix() != '/home/steffen/FZJ/pasta_misc/testing': #TODO temporary safeguard
      print('DO NOT DELETE THIS')
      return
    self.backend.exit()
    try:
      shutil.rmtree(dirName)
      os.makedirs(dirName)
      if platform.system()=='Windows':
        print('Try-Except unnecessary')
    except Exception:
      pass
    self.__setBackend__(self.projectGroup)
    return


  def purgeRemote(self, projectGroup:str='') -> None:
    """ Purge entire remote storage, remove everything

      Args:
      projectGroup (str): name of project group
    """
    if not self.projectGroup:
      self.__setBackend__(projectGroup)
    Pasta2Elab(self.backend, self.projectGroup, True)
    return



  def sync(self, projectGroup:str='', command:str='') -> None:
    """ synchronize with elab server

      Args:
      projectGroup (str): name of project group
      command (str): 'ss' or 'sg' to send/get data
    """
    if not self.projectGroup:
      self.__setBackend__(projectGroup)
    syncObj = Pasta2Elab(self.backend, self.projectGroup)
    if command:
      syncObj.sync('sA' if command=='ss' else 'gA', progressCallback=self.__updateProgressBar__)
    return


  def repairPropertiesDot(self, projectGroup:str='') -> None:
    """ Repair sqlite database by changing properties table: if key does not have a ., prepend it
    Args:
      projectGroup (str): name of project group
    """
    if not self.projectGroup:
      self.__setBackend__(projectGroup)
    key= input('Which key to repair, e.g. "chemistry" will become .chemistry? ')
    self.backend.db.cursor.execute(f"SELECT id FROM properties where key == '{key}'")
    res = self.backend.db.cursor.fetchall()
    for idx, docID in enumerate(res):
      docID = docID[0]
      try:
        self.backend.db.cursor.execute(f"UPDATE properties SET key='.{key}' WHERE id == '{docID}' and  key=='{key}'")
      except Exception:
        print(f"Error, could not change {docID} and {key}. Likely that combination exists already in properties. Repair manually")
        if idx==0:
          print(traceback.format_exc())
    self.backend.db.connection.commit()
    print('Done')
    return



def main() -> None:
  '''
  Main function
  '''
  print('\n-------------------------------------------------------------------------')
  print(  '------------     Manual functions for PASTA-ELN installation    ---------')
  print(  '-------------------------------------------------------------------------')
  tools = Tools()
  todos = []
  if len(sys.argv)==2:
    todos = sys.argv[1].split()
    if not re.match(r'^\d+$', todos[0]):
      print('** ERROR Malformed todo list (start with a number), exit')
      return
  tools.run(todos)
  return


if __name__ ==  '__main__':
  main()
