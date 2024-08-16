""" Class for interaction with sqlite """
import base64, copy, io, json, logging, os, re, sqlite3
from typing import Any, Optional
from datetime import datetime
from pathlib import Path
from anytree import Node
import pandas as pd
from PIL import Image
from .fixedStringsJson import defaultDataHierarchy, defaultDefinitions, SQLiteTranslation
from .miscTools import outputString, hierarchy, camelCase, tracebackString

KEY_ORDER=['id'  ,'name','user','type','dateCreated','dateModified','gui',      'client','shasum','image','content','comment','externalId']
KEY_TYPE =['TEXT','TEXT','TEXT','TEXT','TEXT',       'TEXT',        'varchar(2)','TEXT',  'TEXT',  'TEXT', 'TEXT',   'TEXT',   'TEXT']
DATA_HIERARCHY = ['docType', 'IRI','title','icon','shortcut','view']
DEFINITIONS =    ['docType','class','idx', 'name', 'query', 'unit', 'IRI', 'mandatory', 'list']

class SqlLiteDB:
  """
  Class for interaction with sqlite
  """
  def __init__(self, resetDataHierarchy:bool=False, basePath:Path=Path()):
    """
    Args:
      configuration (dict): configuration of GUI elements
      resetDataHierarchy (bool): reset dataHierarchy
      basePath (Path): path of project group
    """
    self.connection = sqlite3.connect(basePath/"pastaELN.db", check_same_thread=False)
    self.basePath   = basePath
    self.cursor     = self.connection.cursor()
    self.dataHierarchyInit(resetDataHierarchy)
    # main table
    self.createSQLTable('main',            KEY_ORDER,                                  'id', KEY_TYPE)
    # branches table
    self.createSQLTable('branches', ['id','idx','stack','child','path','show'],'id, idx', ['TEXT','INTEGER']*2+["TEXT"]*2)
    # metadata table
    # - contains metadata of specific item
    # - key is generally not shown to user
    # - flattened key
    # - can be adopted by adv. user
    self.createSQLTable('properties',      ['id','key','value','unit'],                'id, key')
    self.createSQLTable('propDefinitions', ['key','long','IRI'],                       'key')
    # tables: each item can have multiple of these: tags, qrCodes
    self.createSQLTable('tags',            ['id','tag'],                               'id, tag')
    self.createSQLTable('qrCodes',         ['id','qrCode'],                            'id, qrCode')
    # list of changes to attachments
    self.createSQLTable('attachments',     ['id','location','date','guest','remark','user'], 'id, location, date')
    # list of changes to all documents: gives history
    self.createSQLTable('changes',         ['id','date','change'],                     'id, date')
    return


  def dataHierarchyInit(self, resetDataHierarchy:bool=False) -> None:
    """
    prepare / return data hierarchy

    Args:
    """
    self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [i[0] for i in self.cursor.fetchall()] # all tables
    self.connection.commit()
    # check if default documents exist and create
    if 'dataHierarchy' not in tables or resetDataHierarchy:
      if 'dataHierarchy' in tables:
        print('Info: remove old dataHierarchy')
        self.cursor.execute("DROP TABLE dataHierarchy")
      self.createSQLTable('dataHierarchy',  DATA_HIERARCHY,    'docType')
      command = f"INSERT INTO dataHierarchy ({', '.join(DATA_HIERARCHY)}) VALUES ({', '.join(['?']*len(DATA_HIERARCHY))});"
      self.cursor.executemany(command, defaultDataHierarchy)
      # definitions table (see below)
      # - define the key of the metadata table, give long description, IRI, ...
      self.createSQLTable('definitions', DEFINITIONS,  'docType, class, idx')
      command = f"INSERT INTO definitions ({', '.join(DEFINITIONS)}) VALUES ({', '.join(['?']*len(DEFINITIONS))});"
      self.cursor.executemany(command, defaultDefinitions)
      self.connection.commit()
    return


  def createSQLTable(self, name:str, columns:list[str], primary:str, colTypes:Optional[list[Any]]=None) -> list[str]:
    """
    Create a table in the sqlite system

    Args:
      name (str): name of table
      columns (list): list of column names
      primary (str): primary keys as comma-separated
      colTypes (list): optional list of data-types of the columns
    """
    if colTypes is None:
      colTypes = ['TEXT']*len(columns)
    colText = ', '.join(f'{i} {j}' for i,j in zip(columns, colTypes))
    self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} ({colText}, PRIMARY KEY ({primary}))")
    self.cursor.execute(f"SELECT * FROM {name}")
    columnNames = list(map(lambda x: x[0], self.cursor.description))
    if columnNames != columns:
      logging.error("Difference in sqlite table: %s", name)
      logging.error(columnNames)
      logging.error(columns)
      raise ValueError('SQLite table difference')
    return columnNames


  def dataHierarchy(self, docType:str, column:str, group:str='') -> list[Any]:
    """
    get data hierarchy information, old name 'ontology', from database

    Args:
      docType (str): document typ
      column (str): column name as in meta, label, shortcut, ...
      group (str): group of metadata rows; if group not given: return all
    Returns:
      list: information inquired
    """
    ### return column information
    if not docType: #if all docTypes
      column = f', {column}' if column else ''
      self.cursor.execute(f"SELECT docType {column} FROM dataHierarchy")
      results = self.cursor.fetchall()
      return [i[0] for i in results] if column=='' else results
    ### if metadata = definitions of data
    if column == 'meta':
      self.connection.row_factory = sqlite3.Row  #default None
      cursor = self.connection.cursor()
      if group:
        cursor.execute(f"SELECT * FROM definitions WHERE docType == '{docType}' and class == '{group}'")
      else:
        cursor.execute(f"SELECT * FROM definitions WHERE docType == '{docType}'")
      return cursor.fetchall()
    if column == 'metaColumns':
      self.cursor.execute(f"SELECT DISTINCT class FROM definitions WHERE docType == '{docType}'")
      return [i[0] for i in self.cursor.fetchall()]
    # if specific docType
    self.cursor.execute(f"SELECT {column} FROM dataHierarchy WHERE docType == '{docType}'")
    result = self.cursor.fetchone()
    if result is None:
      return []
    if column=='meta':
      return json.loads(result[0])
    elif column=='view':
      return result[0].split(',')
    return result


  def exit(self, deleteDB:bool=False) -> None:
    """
    Shutting down things

    Args:
      deleteDB (bool): remove database
    """
    self.connection.close()
    return


  def getDoc(self, docID:str) -> dict[str,Any]:
    """
    Wrapper for get from database function

    Args:
        docID (dict): document id

    Returns:
        dict: json representation of document
    """
    self.connection.row_factory = sqlite3.Row  #default None
    cursor = self.connection.cursor()
    cursor.execute(f"SELECT * FROM main WHERE id == '{docID}'")
    doc = dict(cursor.fetchone())
    self.cursor.execute(f"SELECT tag FROM tags WHERE id == '{docID}'")
    doc['tags'] = [i[0] for i in self.cursor.fetchall()]
    self.cursor.execute(f"SELECT qrCode FROM qrCodes WHERE id == '{docID}'")
    doc['qrCodes'] = [i[0] for i in self.cursor.fetchall()]
    for key in ['image', 'content','shasum','client','qrCodes']:
      if len(doc[key])==0:
        del doc[key]
    doc['type']= doc['type'].split('/')
    doc['gui'] = [i=='T' for i in doc['gui']]
    doc['branch'] = []
    # data ends with 'id' 'stack', 'child', 'path', 'show', 'dateModified'
    self.cursor.execute(f"SELECT * FROM branches WHERE id == '{docID}'")
    for dataI in self.cursor.fetchall():
      doc['branch'].append({'stack': dataI[2].split('/')[:-1],
                             'child': dataI[3],
                             'path':  None if dataI[4] == '*' else dataI[4],
                             'show':   [i=='T' for i in dataI[5]]})
    cmd = "SELECT properties.key, properties.value, properties.unit, propDefinitions.long, propDefinitions.IRI, " \
          "definitions.unit, definitions.query, definitions.IRI FROM properties LEFT JOIN propDefinitions USING(key) "\
          "LEFT JOIN definitions ON properties.key = (definitions.class || '.' || definitions.name) "\
          f"WHERE properties.id == '{docID}'"
    self.cursor.execute(cmd)
    res = self.cursor.fetchall()
    metadataFlat:dict[str, tuple[str,str,str,str]] = {i[0]:(i[1],
                          ('' if i[2] is None else i[2])+('' if i[5] is None else i[5]),
                          ('' if i[3] is None else i[3])+('' if i[6] is None else i[6]),
                          ('' if i[4] is None else i[4])+('' if i[7] is None else i[7])) for i in res}
    doc |= hierarchy(metadataFlat)
    return doc

  def saveDoc(self, doc:dict[str,Any]) -> dict[str,Any]:
    """
    Save to database
    - not helpful to convert _id to int since sqlite does not digest such long integer
      doc['id']  = int(doc['id'][2:], 16)
    - Example{
        'name': 'G200X',
        'user': 'somebody',
        'type': ['instrument'],
        'branch': {'stack': ['x-9f74f79c96754d4c9065435ddd466c56', 'x-04b5e323d3ae4364bcd310a3e5fd653e'],
                  'child': 9999, 'path': None, 'show': [True, True, True], 'op': 'c'},
        'id': 'i-180212be6c7d4365ac647f266c5698f1',
        'externalId': '',
        'dateCreated': '2024-07-31T22:03:39.530666',
        'dateModified': '2024-07-31T22:03:39.530727',
        'gui': [True, True],
        'comment': '',
        '.vendor': 'KLA',
        '.model': 'KLA G200X',
        'metaVendor': {'j': 258},
        'tags': []}

    Discussion on -branch['path']:
    - full path (from basePath) allows to easily create a view of all paths and search through them
      during each scan, which happens rather often
    - just the incremental path (file-name, folder-name) allows to easily change that if the user wants
      and not change all the children paths, too. However, the renaming of the folder is likely occurring
      less often.

    Args:
        doc (dict): document to save

    Returns:
        dict: json representation of submitted document
    """
    # print('\nsave\n'+'\n'.join([f'{k}: {v}' for k,v in doc.items()]))
    docOrg = copy.deepcopy(doc)
    # save into branch table
    self.cursor.execute(f"INSERT INTO branches VALUES ({', '.join(['?']*6)})",
                        [doc['id'],
                         0,
                         '/'.join(doc['branch']['stack']+[doc['id']]),
                         str(doc['branch']['child']),
                         '*' if doc['branch']['path'] is None else doc['branch']['path'],
                         ''.join(['T' if j else 'F' for j in doc['branch']['show']])])
    del doc['branch']
    # save into tags table
    self.cursor.executemany("INSERT INTO tags VALUES (?, ?);", zip([doc['id']]*len(doc['tags']), doc['tags']))
    del doc['tags']
    if 'qrCode' in doc:
      cmd = "INSERT INTO qrCodes VALUES (?, ?);"
      self.cursor.executemany(cmd, zip([doc['id']]*len(doc['qrCode']), doc['qrCode']))
      del doc['qrCode']
    if 'content' in doc and len(doc['content'])>200:
      doc['content'] = doc['content'][:200]
    doc['type'] = '/'.join(doc['type'])
    doc['gui']  = ''.join(['T' if i else 'F' for i in doc['gui']])
    doc['client'] = tracebackString(False, 'save:'+doc['id'])
    docList = [doc[x] if x in doc else doc.get(f'.{x}','') for x in KEY_ORDER]
    self.cursor.execute(f"INSERT INTO main VALUES ({', '.join(['?']*len(docList))})", docList)
    doc = {k:v for k,v in doc.items() if (k not in KEY_ORDER and k[1:] not in KEY_ORDER) or k == 'id'}

    def insertMetadata(data:dict[str,Any], parentKeys:str) -> None:
      parentKeys = f'{parentKeys}.' if parentKeys else ''
      for key,value in data.items():
        if isinstance(value, dict):
          insertMetadata(value, f'{parentKeys}{key}')
        elif key.endswith(']') and ('[') in key:
          unit   = re.findall(r'\[\S+\]', key)[-1][1:-1]
          label  = key[:-len(unit)-2].strip()
          key    = camelCase(label)
          key    = key[0].lower()+key[1:]
          cmd = "INSERT INTO properties VALUES (?, ?, ?, ?);"
          self.cursor.execute(cmd, [doc['id'], parentKeys+key, str(value), unit])
          cmd = "INSERT INTO propDefinitions VALUES (?, ?, ?);"
          self.cursor.execute(cmd, [parentKeys+key, label, ''])
        elif isinstance(value, list) and isinstance(value[0], dict) and value[0].keys() >= {"key", "value", "unit"}:
          cmd = "INSERT INTO properties VALUES (?, ?, ?, ?);"
          self.cursor.executemany(cmd, zip([doc['id']]*len(value),      [parentKeys+key+'.'+i['key'] for i in value],
                                            [i['value'] for i in value], [i['unit'] for i in value]  ))
          cmd = "INSERT INTO propDefinitions VALUES (?, ?, ?);"
          self.cursor.executemany(cmd, zip([parentKeys+key+'.'+i['key'] for i in value],
                                            [i['label'] for i in value], [i['IRI'] for i in value]  ))
        else:
          cmd = "INSERT INTO properties VALUES (?, ?, ?, ?);"
          self.cursor.execute(cmd, [doc['id'], parentKeys+key, str(value), ''])
      return
    # properties
    metaDoc = {k:v for k,v in doc.items() if k not in KEY_ORDER}
    insertMetadata(metaDoc, '')
    # save changes
    self.connection.commit()
    branch = copy.deepcopy(docOrg['branch'])
    del branch['op']
    docOrg['branch'] = [branch]
    return docOrg


  def updateDoc(self, dataNew:dict[str,Any], docID:str) -> dict[str,Any]:
    """
    Update document by
    - saving changes to oldDoc (revision document)
    - updating new-document concurrently
    - create a docID for oldDoc

    Key:Value
    - if value is None: do not change it;
    - if key does not exist: change it to empty, aka remove it

    Args:
        dataNew (dict): item to update
        docID (string):  id of document to change

    Returns:
        dict: json representation of updated document
    """
    dataNew['client'] = tracebackString(False, f'updateDoc:{docID}')
    if 'edit' in dataNew:     #if delete
      dataNew = {'id':dataNew['id'], 'branch':dataNew['branch'], 'user':dataNew['user'], 'externalId':dataNew['externalId'], 'name':''}
    changesDict:dict[str,str]         = {}
    self.connection.row_factory = sqlite3.Row  #default None
    cursor = self.connection.cursor()

    # tags and qrCodes
    tagsNew= set(dataNew.pop('tags'))
    self.cursor.execute(f"SELECT tag FROM tags WHERE id == '{docID}'")
    tagsOld= {i[0] for i in self.cursor.fetchall()}
    if tagsOld.difference(tagsNew):
      cmd = f"DELETE FROM tags WHERE id == '{docID}' and tag == ?"
      self.cursor.executemany(cmd, tagsOld.difference(tagsNew))
      changesDict['tags'] = ','.join(tagsOld)
    if tagsNew.difference(tagsOld):
      change = tagsNew.difference(tagsOld)
      self.cursor.executemany("INSERT INTO tags VALUES (?, ?);", zip([docID]*len(change), change))
      changesDict['tags'] = ','.join(tagsOld)
    qrCodesNew= set(dataNew.pop('qrCodes', []))
    self.cursor.execute(f"SELECT qrCode FROM qrCodes WHERE id == '{docID}'")
    qrCodesOld= {i[0] for i in self.cursor.fetchall()}
    if qrCodesOld.difference(qrCodesNew):
      cmd = f"DELETE FROM qrCodes WHERE id == '{docID}' and qrCode == ?"
      self.cursor.executemany(cmd, qrCodesOld.difference(qrCodesNew))
      changesDict['qrCodes'] = ','.join(qrCodesOld)
    if qrCodesNew.difference(qrCodesOld):
      change = qrCodesNew.difference(qrCodesOld)
      self.cursor.executemany("INSERT INTO qrCodes VALUES (?, ?);", zip([docID]*len(change), change))
      changesDict['qrCodes'] = ','.join(qrCodesOld)
    # separate into main and properties
    mainNew    = {key: dataNew.pop(key) for key in KEY_ORDER if key in dataNew}
    branchNew  = dataNew.pop('branch',{})
    # read branches and identify changes
    cursor.execute(f"SELECT * FROM branches WHERE id == '{docID}'")
    branchOld = [dict(i) for i in cursor.fetchall()]
    branchOld[0]['show'] = [i=='T' for i in branchOld[0]['show']]
    branchOld[0]['stack'] = branchOld[0]['stack'].split('/')[:-1]
    # print(f'do something with branch: \nnew {branchNew} \nold: {branchOld}')
    if branchNew:
      op      = branchNew.pop('op')             #operation
      oldPath = branchNew.pop('oldPath',None)   #TODO more functions use this ability: backend.py and table.py, which are called by other functions
      if not branchNew['path']:
        branchNew['path'] = branchOld[0]['path']
      if branchNew not in branchOld:            #only do things if the newBranch is not already in oldBranch
        changesDict['branch'] = branchOld.copy()
        idx = None
        for branch in branchOld:                #check if the path is already exist, then it is only an update
          if op=='c' and branch['path']==branchNew['path']:
            op='u'
        if op=='c':    #create, append
          branchNew['show'] = self.createShowFromStack(branchNew['stack'].split('/'))
          branchOld += [branchNew]
        elif op=='u':  #update
          if oldPath is not None:              # search by using old path
            for branch in branchOld:
              if branch['path'].startswith(oldPath):
                if   os.path.basename(branch['path']) == mainNew['name'] and \
                     os.path.basename(str(branchNew['path']))!='':
                  mainNew['name'] = os.path.basename(str(branchNew['path']))
                branch['path'] = branch['path'].replace(oldPath ,branchNew['path'])
                branch['stack']= branchNew['stack']
                branch['show'] = self.createShowFromStack(branchNew['stack'], branch['show'][-1])
                break
          else:
            idx = 0
            branchOld[idx] = branchNew           #change branch 0 aka the default
        elif op=='d':  #delete
          branchOld = [branch for branch in branchOld if branch['path']!=branchNew['path']]
        else:
          raise ValueError(f'sqlite.1: unknown branch op: {mainNew["id"]} {mainNew["name"]}')
        if idx is None:
          raise ValueError(f'sqlite.2: idx unset: {mainNew["id"]} {mainNew["name"]}')
        self.cursor.execute(f"UPDATE branches SET stack='{'/'.join(branchOld[idx]['stack']+[docID])}', "
                            f"path='{branchOld[idx]['path']}', child='{branchOld[idx]['child']}', "
                            f"show='{''.join(['T' if j else 'F' for j in branchOld[idx]['show']])}' "
                            f"WHERE id = '{docID}' and idx = {idx}")
    #TODO: use example with two branches

    # read properties and identify changes
    self.cursor.execute(f"SELECT key, value FROM properties WHERE id == '{docID}'")
    dataOld = {i[0]:i[1] for i in self.cursor.fetchall()}
    for key,value in dataNew.items():
      if isinstance(value, dict):
        for subKey, subValue in value.items():
          longKey = f'{key}.{subKey}'
          if longKey in dataOld and subValue!=dataOld[longKey]:
            self.cursor.execute(f"UPDATE properties SET value='{subValue}' WHERE id = '{docID}' and key = '{longKey}'")
            changesDict[longKey] = dataOld[longKey]
          elif longKey not in dataOld:
            cmd = "INSERT INTO properties VALUES (?, ?, ?, ?);"
            self.cursor.execute(cmd ,[docID, longKey, subValue, ''])
          if longKey in dataOld:
            del dataOld[longKey]
      else:
        logging.error('Property is not a dict, ERROR')
    if set(dataOld.keys()).difference(dataNew.keys()):
      cmd = f"DELETE FROM properties WHERE id == '{docID}' and key == ?"
      self.cursor.executemany(cmd, set(dataOld.keys()).difference(dataNew.keys()))
      changesDict |= dataOld
    # read main and identify if something changed
    cursor.execute(f"SELECT * FROM main WHERE id == '{docID}'")
    mainOld = dict(cursor.fetchone())
    mainOld['type']= mainOld['type'].split('/')
    changesDB: dict[str,dict[str,str]] = {'main': {}}
    for key in ('name','user','type','dateModified','client','image','content','comment'):
      if key in mainNew and mainOld[key]!=mainNew[key]:
        changesDB['main'][key] = '/'.join(mainNew[key]) if key=='type' else mainNew[key].translate(SQLiteTranslation)
        changesDict[key] = mainOld[key]
    # save change content in database: main and changes are updated
    if set(changesDict.keys()).difference(('dateModified','client','user')):
      changeString = ', '.join([f"{k}='{v}'" for k,v in changesDB['main'].items()])
      self.cursor.execute(f"UPDATE main SET {changeString} WHERE id = '{docID}'")
      if 'name' not in changesDict or changesDict['name']!='new item':  #do not save initial change from new item
        self.cursor.execute("INSERT INTO changes VALUES (?,?,?)", [docID, datetime.now().isoformat(), json.dumps(changesDict)])
      self.connection.commit()
    return mainOld | mainNew | {'branch':branchOld, '__version__':'short'}


  def updateBranch(self, docID:str, branch:int, child:int, stack:Optional[list[str]]=None,
                   path:Optional[str]='') -> tuple[Optional[str], Optional[str]]:
    """
    Update document by updating the branch

    Args:
      docID (string):  id of document to change
      branch (int):  index of branch to change
      child (int):  new number of child
      stack (list):  new list of ids
      path (str): new path; None is acceptable

    Returns:
      str, str: old path, new path
    """
    #convert into db style
    path = '*' if path is None else path
    #use
    self.cursor.execute(f"SELECT path, stack, show FROM branches WHERE id == '{docID}' and idx == {branch}")
    pathOld, stackOld, showOld = self.cursor.fetchone()
    stack = stack if stack is not None else stackOld.split('/')[:-1]  # stack without current id
    show  = self.createShowFromStack(stack, showOld[-1])
    cmd = f"UPDATE branches SET stack='{'/'.join(stack+[docID])}', child={child}, path='{path}', show='{show}' "\
          f"WHERE id = '{docID}' and idx = {branch}"
    self.cursor.execute(cmd)
    self.connection.commit()
    # move content: folder and data and write .json to disk
    if pathOld!='*' and path!='*' and ':/' not in pathOld:
      if not (self.basePath/pathOld).exists() and (self.basePath/path).exists():
        logging.debug('sqlite:updateBranch: dont move since already good')
      else:
        (self.basePath/pathOld).rename(self.basePath/path)
    if docID[0]=='x' and path is not None:
      with open(self.basePath/path/'.id_pastaELN.json', 'w', encoding='utf-8') as fOut:
        fOut.write(json.dumps(self.getDoc(docID)))
      self.updateChildrenOfParentsChanges(pathOld,path,  stackOld,'/'.join(stack+[docID]))
    return (None if pathOld=='*' else pathOld, None if path=='*' else path)


  def updateChildrenOfParentsChanges(self, pathOld:str, pathNew:str, stackOld:str, stackNew:str) -> None:
    """
    update children's paths

    Args:
      pathOld (str): old path of parent
      pathNew (str): new path of parent
      stackOld (str): old stack of parent
      stackNew (str): new stack of parent
    """
    cmd = f"SELECT path, stack, show, id, idx FROM branches WHERE stack LIKE '{stackOld}/%'"
    self.cursor.execute(cmd)
    children = self.cursor.fetchall()
    updatedInfo = []
    for (pathIOld, stackIOld, showIOld, docID, idx) in children:
      pathINew  = pathNew+pathIOld[len(pathOld):] if pathIOld!='*' and pathIOld.startswith(pathOld) else pathIOld
      stackINew = stackNew+stackIOld[len(stackOld):]                           if stackNew else stackIOld
      showINew  = self.createShowFromStack(stackIOld.split('/'), showIOld[-1]) if stackNew else showIOld
      updatedInfo.append((pathINew, stackINew, showINew, docID, idx))
      # update .json on disk
      if stackINew.split('/')[-1][0]=='x' and (self.basePath/pathINew).is_dir():
        with open(self.basePath/pathINew/'.id_pastaELN.json', 'r', encoding='utf-8') as fIn:
          doc = json.load(fIn)
        doc['branch'] = [{'stack':stackINew.split('/')[:-1],
                          'show':[i=='T' for i in showINew],
                          'path':pathINew,
                          'child':i['child']}
                         for i in doc['branch'] if i['stack']==stackIOld.split('/')[:-1]]
        with open(self.basePath/pathINew/'.id_pastaELN.json', 'w', encoding='utf-8') as fOut:
          fOut.write(json.dumps(doc))
    cmd = "UPDATE branches SET path=?, stack=?, show=? WHERE id == ? and idx == ?"
    self.cursor.executemany(cmd, updatedInfo)
    self.connection.commit()
    return


  def createShowFromStack(self, stack:list[str], currentShow:str='T') -> str:
    """
    For branches: create show entry in the branches by using the stack
    - should be 1 longer than stack
    - check parents if hidden, then this child is hidden too

    Args:
      stack (list): list of ancestor docIDs '/' separated
      currentShow (str): current show-indicator of this item

    Returns:
      list: list of show = list of bool
    """
    show = len(stack)*['T'] + [currentShow]
    for idx, docID in enumerate(stack):
      self.cursor.execute(f"SELECT show FROM branches WHERE id == '{docID}'")
      if self.cursor.fetchone()[0][-1] == 'F':
        show[idx] = 'F'
    return ''.join(show)

  def remove(self, docID:str) -> dict[str,Any]:
    """
    remove doc from database: temporary for development and testing

    Args:
      docID (string): id of document to remove

    Returns:
      dict: document that was removed
    """
    doc = self.getDoc(docID)
    doc.pop('image','')
    doc.pop('content','')
    self.cursor.execute(f"DELETE FROM main WHERE id == '{docID}'")
    self.cursor.execute(f"DELETE FROM branches WHERE id == '{docID}'")
    self.cursor.execute(f"DELETE FROM properties WHERE id == '{docID}'")
    self.cursor.execute(f"DELETE FROM tags WHERE id == '{docID}'")
    self.cursor.execute(f"DELETE FROM qrCodes WHERE id == '{docID}'")
    self.cursor.execute(f"DELETE FROM attachments WHERE id == '{docID}'")
    self.cursor.execute("INSERT INTO changes VALUES (?,?,?)", [docID, datetime.now().isoformat(), json.dumps(doc)])
    self.connection.commit()
    return doc


  def initAttachment(self, docID:str, name:str, docType:str) -> None:
    """ initialize an attachment by defining its name and type

    Args:
      docID (str): document / instrument on which attachments are installed
      name (str): description of attachment location
      docType (str): document type what can be attached. Use empty string if these are remarks, i.e. no items are attached
    """
    cmd = "INSERT INTO attachments VALUES (?,?,?,?,?,?)"
    self.cursor.execute(cmd, [docID, name, '', docType, '', ''])
    self.connection.commit()
    return


  def addAttachment(self, docID:str, name:str, content:dict[str,Any]) -> None:
    """
    Update document by adding attachment (no new revision)

    Args:
        docID (string):  id of document to change
        name (string): attachment name to add to
        content (dict): dictionary of content to be added (should include user,date,docID,remark)

    """
    cmd = "INSERT INTO attachments VALUES (?,?,?,?,?,?)"
    self.cursor.execute(cmd, [docID, name, content['date'], content['docID'], content['remark'], content['user']])
    self.connection.commit()
    return


  def getView(self, thePath:str, startKey:Optional[str]=None, preciseKey:Optional[str]=None) -> pd.DataFrame:
    """
    Wrapper for getting view function

    Args:
        thePath (string): path to view
        startKey (string): if given, use to filter output, everything that starts with this key
        preciseKey (string): if given, use to filter output. Match precisely

    Returns:
        df: data-frame with human-readable column names
    """
    allFlag = False
    if thePath.endswith('All'):
      thePath = thePath.removesuffix('All')
      allFlag = True
    viewType, docType = thePath.split('/')
    if viewType=='viewDocType':
      viewColumns = self.dataHierarchy(docType, 'view')
      viewColumns = viewColumns+['id'] if viewColumns else ['name','tags','comment','id']
      textSelect = ', '.join([f'main.{i}' for i in viewColumns if i in KEY_ORDER or i[1:] in KEY_ORDER])
      if 'tags' in viewColumns:
        textSelect += ', tags.tag'
      if 'qrCodes' in viewColumns:
        textSelect += ', qrCodes.qrCode'
      metadataKeys  = [f'properties.key == "{i}"' for i in viewColumns if i not in KEY_ORDER+['tags']]
      if metadataKeys:
        textSelect += ', properties.key, properties.value'
      cmd = f"SELECT {textSelect} FROM main LEFT JOIN tags USING(id) LEFT JOIN qrCodes USING(id) "\
              f"INNER JOIN branches USING(id) LEFT JOIN properties USING(id) WHERE main.type LIKE '{docType}%'"
      if not allFlag:
        cmd += r" and NOT branches.show LIKE '%F%'"
      if startKey:
        cmd += f" and branches.stack LIKE '{startKey}%'"
      df      = pd.read_sql_query(cmd, self.connection)
      allCols = list(df.columns)
      if 'image' in viewColumns:
        df['image'] = str(len(df['image'])>1)
      if 'tags' in viewColumns:
        allCols.remove('tag')
        df   = df.groupby(allCols)['tag'].apply(lambda x: ', '.join(x.astype(str))).reset_index()
      if 'qrCodes' in viewColumns:
        allCols.remove('qrCode')
        df   = df.groupby(allCols)['qrCode'].apply(lambda x: ', '.join(x.astype(str))).reset_index()
      if metadataKeys:
        columnNames = [i for i in df.columns if i not in ('key','value')]
        df = df.pivot(index=columnNames, columns='key', values='value').reset_index()  # Pivot the DataFrame
        df.columns.name = None                                                         # Flatten the columns
      columnOrder = ['tag' if i=='tags' else 'qrCode' if i=='qrCodes'
                     else i[1:] if i.startswith('.') and i[1:] in KEY_ORDER else i for i in viewColumns]
      df = df.reindex(columnOrder, axis=1)
      df = df.rename(columns={i:i[1:] for i in columnOrder if i.startswith('.') })
      df = df.astype('str').fillna('')
      return df
    elif thePath=='viewHierarchy/viewHierarchy':
      cmd = "SELECT branches.id, branches.stack, branches.child, main.type, main.name, main.gui "\
            f"FROM branches INNER JOIN main USING(id) WHERE branches.stack LIKE '{startKey}%'"
      if not allFlag:
        cmd += r" and NOT branches.show LIKE '%F%'"
      cmd += " ORDER BY branches.stack"
      self.cursor.execute(cmd)
      results = self.cursor.fetchall()
      # value: [child, doc['-type'], doc['.name'], doc['-gui']]
      results = [{'id':i[0], 'key':i[1],
                  'value':[i[2], i[3].split('/'), i[4], [j=='T' for j in i[5]]]} for i in results]
    elif thePath=='viewHierarchy/viewPaths':
      cmd = "SELECT branches.id, branches.path, branches.stack, main.type, branches.child, main.shasum, branches.idx "\
            "FROM branches INNER JOIN main USING(id)"
      # JOIN and get type
      if startKey is not None:
        if startKey.endswith('/'):
          startKey = startKey.removesuffix('/')
        cmd += f" WHERE branches.path LIKE '{startKey}%'"
      elif preciseKey is not None:
        cmd += f" WHERE branches.path LIKE '{preciseKey}'"
      if not allFlag:
        if "WHERE" in cmd:
          cmd += r" AND NOT branches.show LIKE '%F%'"
        else:
          cmd += r" WHERE NOT branches.show LIKE '%F%'"
      self.cursor.execute(cmd)
      results = self.cursor.fetchall()
      # value: [branch.stack, doc['-type'], branch.child, doc.shasum, idx]
      results = [{'id':i[0], 'key':i[1],
                  'value':[i[2], i[3].split('/')]+list(i[4:])} for i in results if i[1] is not None]
    elif viewType=='viewIdentify' and docType=='viewTags':
      self.cursor.execute("SELECT * FROM tags")
      results = self.cursor.fetchall()
    elif viewType=='viewIdentify':
      if docType=='viewQR':
        if startKey is None:
          cmd = "SELECT qrCodes.id, qrCodes.qrCode, main.name FROM qrCodes INNER JOIN main USING(id)"
          if not allFlag:
            cmd += r" INNER JOIN branches USING(id) WHERE NOT branches.show LIKE '%F%'"
        else:
          raise ValueError('Not implemented sqlite l 599')
      elif docType=='viewSHAsum':
        if startKey is None:
          cmd = "SELECT main.id, main.shasum, main.name FROM main"
          if not allFlag:
            cmd += r" INNER JOIN branches USING(id) WHERE NOT branches.show LIKE '%F%'"
        else:
          cmd = f"SELECT main.id, main.shasum, main.name FROM main INNER JOIN branches USING(id) WHERE shasum='{startKey}'"
          if not allFlag:
            cmd += r" and NOT branches.show LIKE '%F%'"
      else:
        raise ValueError('Invalid docType')
      self.cursor.execute(cmd)
      results = self.cursor.fetchall()
      results = [{'id':i[0], 'key':i[1].replace('/',' '), 'value':i[2]} for i in results if i[1] is not None]
    else:
      print('continue here with view', thePath, startKey, preciseKey)
      raise ValueError('Not implemented')
    return results


  def getHierarchy(self, start:str, allItems:bool=False) -> Node:
    """
    get hierarchy tree for projects, ...

    Args:
      start (str): start of the hierarchy (most parent)
      allItems (bool):  true=show all items, false=only non-hidden

    Returns:
      Node: hierarchy in an anytree
    """
    view = self.getView('viewHierarchy/viewHierarchy',    startKey=start)
    # create tree of folders: these are the only ones that have children
    dataTree = None
    nonFolders = []
    id2Node = {}
    for item in view:
      docType = item['value'][1]
      if docType[0][0] != 'x':
        nonFolders.append(item)
        continue
      _id     = item['id']
      childNum, docType, name, gui = item['value']
      if dataTree is None:
        dataTree = Node(id=_id, docType=docType, name=name, gui=gui, childNum=childNum)
        id2Node[_id] = dataTree
      else:
        parent = item['key'].split('/')[-2]
        subNode = Node(id=_id, parent=id2Node[parent], docType=docType, name=name, gui=gui, childNum=childNum)
        id2Node[_id] = subNode
    # add non-folders into tree
    # print(len(nonFolders),'length: crop if too long')
    for item in nonFolders:
      _id     = item['id']
      childNum, docType, name, gui = item['value']
      parentId = item['key'].split('/')[-2]
      Node(id=_id, parent=id2Node[parentId], docType=docType, name=name, gui=gui, childNum=childNum)
    # sort children
    for parentNode in id2Node.values():
      children = parentNode.children
      childNums= [f'{i.childNum}{i.id}' for i in children]
      parentNode.children = [x for _, x in sorted(zip(childNums, children))]
    return dataTree


  def hideShow(self, docID:str) -> None:
    """
    Toggle hide/show indicator of branch

    Args:
      docID (str): document id
    """
    def adoptShow(item:tuple[str,str,str,str]) -> tuple[str,str,str]:
      """ Adopt show string, internal mapping function

      Args:
        item (tuple): id, idx, stack, show

      Returns:
        tuple: show, id, idx
      """
      docID, idx, stack, show = item
      j = stack.split('/').index(docID)
      showL = list(show)
      showL[j] = 'T' if showL[j]=='F' else 'F'
      return (''.join(showL), docID, idx)
    cmd = f"SELECT id, idx, stack, show FROM branches WHERE stack LIKE '%{docID}%'"
    self.cursor.execute(cmd)
    changed = map(adoptShow, self.cursor.fetchall())
    cmd = "UPDATE branches SET show=? WHERE id = ? and idx= ?"
    self.cursor.executemany(cmd, changed)
    self.connection.commit()
    return


  def setGUI(self, docID:str, guiState:list[bool]) -> None:
    """
    Set the gui state
    - 0: true=show details; false=hide details
    - 1: true=show children; false=hide children; only makes sense for folders: doctype = x1

    Args:
      docID (str): docID
      guiState (list): list of bool that show if document is shown
    """
    guiList = ''.join(['T' if i else 'F' for i in guiState])
    cmd = f"UPDATE main SET gui='{guiList}' WHERE id = '{docID}'"
    self.cursor.execute(cmd)
    self.connection.commit()
    return


  def checkDB(self, outputStyle:str='text', minimal:bool=False) -> str:
    """
    Check database for consistencies by iterating through all documents
    - only reporting, no repair
    - custom changes are possible with normal scan
    - no interaction with hard disk

    Args:
        outputStyle (str): output using a given style: see outputString
        minimal (bool): true=only show warnings and errors; else=also show information

    Returns:
        str: output
    """
    outString = ''
    if outputStyle=='html':
      outString += '<div align="right">'
    outString+= outputString(outputStyle,'h2','LEGEND')
    if not minimal:
      outString+= outputString(outputStyle,'perfect','Green: perfect and as intended')
      outString+= outputString(outputStyle,'ok', 'Blue: ok, can happen: empty files for testing, strange path for measurements')
    outString+= outputString(outputStyle,'unsure', 'Dark magenta: unsure if bug or desired (e.g. move step to random path-name)')
    outString+= outputString(outputStyle,'warning','Orange-red: WARNING should not happen (e.g. procedures without project)')
    outString+= outputString(outputStyle,'error',  'Red: FAILURE and ERROR: NOT ALLOWED AT ANY TIME')
    if outputStyle=='html':
      outString += '</div>'
    outString+= outputString(outputStyle,'h2','List all database entries')
    # tests
    cmd = "SELECT id, main.type, branches.stack, branches.path, branches.child, branches.show "\
          "FROM branches INNER JOIN main USING(id)"
    self.cursor.execute(cmd)
    res = self.cursor.fetchall()
    for row in res:
      try:
        docID, docType, stack, path, child, _ = row[0], row[1], row[2], row[3], row[4], row[5]
      except ValueError:
        outString+= outputString(outputStyle,'error',f"dch03a: branch data has strange list {docID}")
        continue
      if len(docType.split('/'))==0:
        outString+= outputString(outputStyle,'unsure',f"dch04: no type in (removed data?) {docID}")
        continue
      if not all(k.startswith('x-') for k in stack.split('/')[:-1]):
        outString+= outputString(outputStyle,'error',f"dch03: non-text in stack in id: {docID}")
      if any(len(i)==0 for i in stack) and not docType.startswith('x0'): #if no inheritance
        if docType.startswith(('measurement','x')):
          outString+= outputString(outputStyle,'warning',f"branch stack length = 0: no parent {docID}")
        elif not minimal:
          outString+= outputString(outputStyle,'ok',f"branch stack length = 0: no parent for procedure/sample {docID}")
      try:
        dirNamePrefix = path.split(os.sep)[-1].split('_')[0]
        if dirNamePrefix.isdigit() and child!=int(dirNamePrefix): #compare child-number to start of directory name
          outString+= outputString(outputStyle,'error',f"dch05: child-number and dirName dont match {docID}")
      except Exception:
        pass  #handled next lines
      if path is None:
        if docType.startswith('x'):
          outString+= outputString(outputStyle,'error',f"dch06: branch path is None {docID}")
        elif docType.startswith('measurement'):
          if not minimal:
            outString+= outputString(outputStyle,'ok', f'measurement branch path is None=no data {docID}')
        elif not minimal:
          outString+= outputString(outputStyle,'perfect',f"procedure/sample with empty path {docID}")
      else:                                                    #if sensible path
        if len(stack.split('/')) != len(path.split(os.sep)) and path!='*' and not path.startswith('http'):
          #check if length of path and stack coincide; ignore path=None=*
          if docType.startswith('procedure'):
            if not minimal:
              outString+= outputString(outputStyle,'perfect',f"procedure: branch stack and path lengths not equal: {docID}")
          else:
            outString+= outputString(outputStyle,'unsure',f"branch stack and path lengths not equal: {docID}")
        if path!='*' and not path.startswith('http'):
          for parentID in stack.split('/')[:-1]:            #check if all parents in doc have a corresponding path
            try:
              parentDoc = self.getDoc(parentID)
            except Exception:
              outString+= outputString(outputStyle,'error',f"branch stack parent is bad: {docID}")
              continue
            parentDocBranches = parentDoc['branch']
            onePathFound = any(path.startswith(parentBranch['path']) for parentBranch in parentDocBranches)
            if not onePathFound:
              if docType.startswith('procedure') and not minimal:
                outString+= outputString(outputStyle,'perfect',f"dch08: parent of procedure does not have corresponding path {docID} | parentID {parentID}")
              else:
                outString+= outputString(outputStyle,'unsure',f"dch08: parent does not have corresponding path {docID} | parentID {parentID}")


    #doc-type specific tests
    self.cursor.execute("SELECT qrCodes.id, qrCodes.qrCode FROM qrCodes JOIN main USING(id) WHERE  main.type LIKE 'sample%'")
    if res:= [i[0] for i in self.cursor.fetchall() if i[1] is None]:
      outString+= outputString(outputStyle,'warning',f"dch09: qrCode not in samples {res}")
    self.cursor.execute("SELECT id, shasum, image FROM main WHERE  type LIKE 'measurement%'")
    for row in self.cursor.fetchall():
      docID, shasum, image = row
      if shasum is None:
        outString+= outputString(outputStyle,'warning',f"dch10: shasum not in measurement {docID}")
      if image.startswith('data:image'):  #for jpg and png
        try:
          imgData = base64.b64decode(image[22:])
          Image.open(io.BytesIO(imgData))  #can convert, that is all that needs to be tested
        except Exception:
          outString+= outputString(outputStyle,'error',f"dch12: jpg-image not valid {docID}")
      elif image.startswith('<?xml'):
        #from https://stackoverflow.com/questions/63419010/check-if-an-image-file-is-a-valid-svg-file-in-python
        SVG_R = r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b'
        SVG_RE = re.compile(SVG_R, re.DOTALL)
        if SVG_RE.match(image) is None:
          outString+= outputString(outputStyle,'error',f"dch13: svg-image not valid {docID}")
      elif image in ('', None):
        outString+= outputString(outputStyle,'unsure',f"image not valid {docID} {image}")
      else:
        outString+= outputString(outputStyle,'error',f"dch14: image not valid {docID} {image}")
    return outString
