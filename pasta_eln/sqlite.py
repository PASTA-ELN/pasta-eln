""" Class for interaction with sqlite """
import base64, copy, io, json, logging, os, re, sqlite3
from typing import Any, Optional, Union
from datetime import datetime
from pathlib import Path
from anytree import Node
import pandas as pd
from PIL import Image
from .fixedStringsJson import defaultDataHierarchy, defaultDefinitions
from .miscTools import outputString, hierarchy, camelCase, tracebackString

# DO NOT WORK ON THIS IF THERE IS SOMETHING ON THE TODO LIST
# Notes:
# - try to use sqlite style as much as possible and
#   translate within this file into PASTA-document-style
#   - KEEP THE REST OF THE CODE THE SAME FOR NOW
# - start with first test: run-fix-run-fix
#   - pytest --no-skip --tb=short tests/test_01_3Projects.py
#   - start pasta with pudb
#   - do an unit example for the sin-curve
#   - give an example for attachment in datahierarchy: same table
#   - TODO test and use gui, with now all requirements implemented
#   - pyInstaller for windows
#   - write a better default example
#   - do more tests and more coverage
# - LATER change configuration to sqlite
# - do not work on replicator: use eln file there
# TODO: check branches in db: why are some stacks so short in main project group

# Benefits:
# - easy installation
# - test as github actions
# - read / backup database with many other tools
# - can switch between both databases by changing the config
# - investigate perhaps:
#   redis db: server that is similar to others; save to file is also a general location; not user-space
#   crateDB: server; not user space
# - try ID as uuid4 = integer (see if elabFTW does it too)
#   - see if I use x-4523452345 anywhere
#   - see if I use the first letter of the docID
#   -> such long integers are not supported by sqlite: stay with string/text

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
    self.connection = sqlite3.connect(basePath/"pastaELN.db")
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
    if group not given: return all
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

    # properties
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
    changesDict:dict[str,str]         = {}

    # tags and qrCodes
    tagsNew= set(dataNew.pop('tags'))
    self.cursor.execute(f"SELECT tag FROM tags WHERE id == '{docID}'")
    tagsOld= {i[0] for i in self.cursor.fetchall()}
    for tag in tagsOld.difference(tagsNew):
      self.cursor.execute(f"DELETE FROM tags WHERE id == '{docID}' and tag == '{tag}'")
    tagsNew = tagsNew.difference(tagsOld)
    self.cursor.executemany("INSERT INTO tags VALUES (?, ?);", zip([docID]*len(tagsNew), tagsNew))
    qrCodesNew= set(dataNew.pop('qrCodes', []))
    self.cursor.execute(f"SELECT qrCode FROM qrCodes WHERE id == '{docID}'")
    qrCodesOld= {i[0] for i in self.cursor.fetchall()}
    for qrCode in qrCodesOld.difference(qrCodesNew):
      self.cursor.execute(f"DELETE FROM qrCodes WHERE id == '{docID}' and qrCode == '{qrCode}'")
    qrCodesNew = qrCodesNew.difference(qrCodesOld)
    self.cursor.executemany("INSERT INTO qrCodes VALUES (?, ?);", zip([docID]*len(qrCodesNew), qrCodesNew))
    # separate into main and properties
    mainNew = {key: dataNew.pop(key) for key in KEY_ORDER if key in dataNew}
    # TODO handle properties and branch
    print(dataNew, 'still to implement: handle')
    # handle main
    self.connection.row_factory = sqlite3.Row  #default None
    cursor = self.connection.cursor()
    cursor.execute(f"SELECT * FROM main WHERE id == '{docID}'")
    mainOld = dict(cursor.fetchone())
    mainOld['type']= mainOld['type'].split('/')
    changesDB: dict[str,dict[str,str]] = {'main': {}}
    for key in ('name','user','type','dateModified','client','image','content','comment'):
      if key in mainNew and mainOld[key]!=mainNew[key]:
        changesDB['main'][key] = mainNew[key]
        changesDict[key] = mainOld[key]

    #TODO: do not save changes if name='new folder'
    # change content in database
    if set(changesDict.keys()).difference(('dateModified','client','user')):
      changeString = ', '.join([f"{k}='{v}'" for k,v in changesDB['main'].items()])
      self.cursor.execute(f"UPDATE main SET {changeString} WHERE id = '{docID}'")
      self.cursor.execute("INSERT INTO changes VALUES (?,?,?)", [docID, datetime.now().isoformat(), json.dumps(changesDict)])
      self.connection.commit()

    return mainOld | mainNew


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
    stack = [] if stack is None else stack
    #use
    self.cursor.execute(f"SELECT path FROM branches WHERE id == '{docID}' and idx == {branch}")
    pathOld = self.cursor.fetchone()[0]
    cmd = f"UPDATE branches SET stack='{'/'.join(stack+[docID])}', child={child}, path='{path}' "\
          f"WHERE id = '{docID}' and idx = {branch}"
    self.cursor.execute(cmd)
    self.connection.commit()
    return (None if pathOld=='*' else pathOld, None if path=='*' else path)


  def remove(self, docID:str) -> dict[str,Any]:
    """
    remove doc from database: temporary for development and testing

    Args:
      docID (string): id of document to remove

    Returns:
      dict: document that was removed
    """
    doc = self.getDoc(docID)
    del doc['image']
    del doc['content']
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
    # allFlag = False
    if thePath.endswith('All'):
      thePath = thePath.removesuffix('All')
      # allFlag = True
      #TODO print('**info do something with all flag')
    viewType, docType = thePath.split('/')
    if viewType=='viewDocType':
      viewColumns = self.dataHierarchy(docType, 'view')+['id']
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
            f"FROM branches INNER JOIN main USING(id) WHERE branches.stack LIKE '{startKey}%' ORDER BY branches.stack"
      self.cursor.execute(cmd)
      results = self.cursor.fetchall()
      # value: [child, doc['-type'], doc['.name'], doc['-gui']]
      results = [{'id':i[0], 'key':i[1].replace('/',' '),
                  'value':[i[2], i[3].split('/'), i[4], [j=='T' for j in i[5]]]} for i in results]
    elif thePath=='viewHierarchy/viewPaths':
      # JOIN and get type
      if startKey is not None:
        print('**ERROR NOT IMPLEMENTED')
      elif preciseKey is not None:
        cmd = "SELECT branches.id, branches.path, branches.stack, main.type, branches.child, main.shasum "\
              f"FROM branches INNER JOIN main USING(id) WHERE branches.path LIKE '{preciseKey}'"
        self.cursor.execute(cmd)
      else:
        cmd = "SELECT branches.id, branches.path, branches.stack, main.type, branches.child, main.shasum "\
              "FROM branches INNER JOIN main USING(id)"
        self.cursor.execute(cmd)
      results = self.cursor.fetchall()
      # value: [branch.stack, doc['-type'], branch.child, doc.shasum,idx]
      results = [{'id':i[0], 'key':i[1],
                  'value':[i[2].replace('/',' '), i[3].split('/'), i[4], i[5]]} for i in results if i[1] is not None]
    elif viewType=='viewIdentify' and docType=='viewTags':
      self.cursor.execute("SELECT * FROM tags")
      results = self.cursor.fetchall()
    elif viewType=='viewIdentify':
      if docType=='viewQR':
        if startKey is None:
          cmd = "SELECT qrCodes.id, qrCodes.qrCode, main.name FROM qrCodes INNER JOIN main USING(id)"
          self.cursor.execute(cmd)
        else:
          raise ValueError('Not implemented')
      elif docType=='viewSHAsum':
        if startKey is None:
          self.cursor.execute("SELECT id, shasum, name FROM main")
        else:
          self.cursor.execute(f"SELECT id, shasum, name FROM main WHERE shasum='{startKey}'")
      else:
        raise ValueError('Invalid docType')
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
        parent = item['key'].split()[-2]
        subNode = Node(id=_id, parent=id2Node[parent], docType=docType, name=name, gui=gui, childNum=childNum)
        id2Node[_id] = subNode
    # add non-folders into tree
    # print(len(nonFolders),'length: crop if too long')
    for item in nonFolders:
      _id     = item['id']
      childNum, docType, name, gui = item['value']
      parentId = item['key'].split()[-2]
      Node(id=_id, parent=id2Node[parentId], docType=docType, name=name, gui=gui, childNum=childNum)
    # sort children
    for parentNode in id2Node.values():
      children = parentNode.children
      childNums= [f'{i.childNum}{i.id}' for i in children]
      parentNode.children = [x for _, x in sorted(zip(childNums, children))]
    return dataTree


  def hideShow(self, stack:Union[str,list[str]]) -> None:
    """
    Toggle hide/show indicator of branch

    Args:
      stack (list, str): stack of docID; docID (str)
    """
    #TODO
    """
    flippedOnce = False #prevent forward-backward flipping
    if isinstance(stack, str):  #do first document itself
      doc = self.db[stack]
      for idx, _ in enumerate(doc['-branch']):  #check all branches
        doc['-branch'][idx]['show'][-1] = not doc['-branch'][idx]['show'][-1]
        logging.debug('flipped str: %s',str(stack))
      doc.save()
      if stack[0]=='x':
        stack = doc['-branch'][0]['stack']+[stack]  #create full stack of children
      flippedOnce = True
    if isinstance(stack, list):
      iFlip = len(stack)-1
      logging.debug('  database list %s %s',str(stack),str(iFlip))
      for item in self.getView('viewHierarchy/viewHierarchyAll', startKey=' '.join(stack)):
        logging.debug('  docID: %s',item['id'])
        doc = self.db[item['id']]
        for idx, branch in enumerate(doc['-branch']):
          if not flippedOnce or iFlip!=len(branch['stack']):
            doc['-branch'][idx]['show'][iFlip] = not doc['-branch'][idx]['show'][iFlip]
        doc.save()
    # not sure this is needed anymore
    if doc['-type'][0][0]=='x':
      with open(self.basePath/doc['-branch'][0]['path']/'.id_pastaELN.json','w', encoding='utf-8') as fOut:
        fOut.write(json.dumps(doc))
    """
    raise ValueError('Not implemented HIDE/SHOW')


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
            parentDoc = self.getDoc(parentID)
            parentDocBranches = parentDoc['branch']
            onePathFound = any(path.startswith(parentBranch['path']) for parentBranch in parentDocBranches)
            if not onePathFound and (not docType.startswith('procedure') or not minimal):
              outString+= outputString(outputStyle,'unsure',f"dch08: parent does not have corresponding path (remote) {docID} | parentID {parentID}")

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
