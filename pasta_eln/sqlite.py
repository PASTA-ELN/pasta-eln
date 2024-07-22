""" Class for interaction with sqlite """
import base64, copy, io, json, logging, os, re, sqlite3
from typing import Any, Optional, Union
from datetime import datetime
from pathlib import Path
from anytree import Node
import pandas as pd
from PIL import Image
from .fixedStringsJson import defaultDataHierarchy, defaultDefinitions
from .miscTools import outputString, hierarchy, camelCase

# DO NOT WORK ON THIS IF THERE IS SOMETHING ON THE TODO LIST
# Notes:
# - try to use sqlite style as much as possible and
#   translate within this file into PASTA-document-style
#   - KEEP THE REST OF THE CODE THE SAME FOR NOW
#   - ONCE WE ARE GETTING TO BETA: change _id, -name, ...
# - start with first test: run-fix-run-fix
#   - pytest --no-skip --tb=short tests/test_01_3Projects.py
#   - start pasta with pudb
#   - do an unit example for the sin-curve
#   - give an example for attachment in datahierarchy: same table
#   - TODO test gui, with now all requirements implemented
#   -   if required extend functions in this file
# - LATER change configuration to sqlite
# - do not work on replicator: use eln file there
# - at the end: create a translator: old save doc

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

KEY_ORDER   =    ['id' , 'name','user','type','dateCreated','dateModified','gui',       'client','shasum','image','content','comment']
KEY_TYPE    =    ['TEXT','TEXT','TEXT','TEXT','TEXT',       'TExT',       'varchar(2)','TEXT',  'TEXT',  'TEXT', 'TEXT',   'TEXT']
DATA_HIERARCHY = ['docType', 'IRI','title','icon','shortcut','view']
DEFINITIONS =    ['docType','class','idx', 'name', 'query', 'unit', 'IRI', 'mandatory', 'list']
VALUE_UNIT_SEP = '__'


class SqlLiteDB:
  """
  Class for interaction with sqlite
  """
  def __init__(self, configuration:dict[str,Any], resetDataHierarchy:bool=False, basePath:Path=Path()):
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
    self.createSQLTable('main',     KEY_ORDER,                                         'id',        KEY_TYPE)
    # branches table
    self.createSQLTable('branches', ['id','stack','child','path','show'],'id, stack', ['TEXT']*2+['INTEGER']+["TEXT"]*2)
    # metadata table
    # - contains metadata of specific item
    # - key is generally not shown to user
    # - flattened key
    # - can be adopted by adv. user
    self.createSQLTable('properties',      ['id','key','value','unit'],                'id, key')
    self.createSQLTable('propDefinitions', ['key','long','IRI'],                       'key')
    # tables: each item can have multiple of these: tags, qrCodes
    self.createSQLTable('tags',        ['id','tag'],                                   'id, tag')
    self.createSQLTable('qrCodes',     ['id','qrCode'],                                'id, qrCode')
    # list of changes to attachments
    self.createSQLTable('attachments', ['id','location','date','guest','remark','user'], 'id, location, date')
    # list of changes to all documents: gives history
    self.createSQLTable('changes',     ['id','date','change'],                         'id, date')
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


  def dataHierarchy(self, docType:str, column:str, group:str='') -> dict[str,Any]:
    """
    if group not given: return all
    """
    ### return column information
    if not docType: #if all docTypes
      column = f', {column}' if column else ''
      self.cursor.execute(f"SELECT docType {column} FROM dataHierarchy")
      results = self.cursor.fetchall()
      if column=='':
        return [i[0] for i in results]
      return {i[0]:i[1] for i in results}
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
    return result[0]


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
      doc['branch'].append({'stack': dataI[1].split('/')[:-1],
                             'child': dataI[2],
                             'path':  None if dataI[3] == '*' else dataI[3],
                             'show':   [i=='T' for i in dataI[4]]})
    self.cursor.execute(f"SELECT properties.key, properties.value, properties.unit, propDefinitions.long, propDefinitions.IRI, "
                        f"definitions.unit, definitions.query, definitions.IRI FROM properties LEFT JOIN propDefinitions USING(key) "
                        f"LEFT JOIN definitions ON properties.key = (concat(definitions.class,'.',definitions.name)) "
                        f"WHERE properties.id == '{docID}'")
    res = self.cursor.fetchall()
    metadataFlat:dict[str, tuple[str,str,str,str]] = {i[0]:(i[1],
                          ('' if i[2] is None else i[2])+('' if i[5] is None else i[5]),
                          ('' if i[3] is None else i[3])+('' if i[6] is None else i[6]),
                          ('' if i[4] is None else i[4])+('' if i[7] is None else i[7])) for i in res}
    doc |= hierarchy(metadataFlat)
    return doc


  def saveDoc(self, doc:dict[str,Any]) -> dict[str,Any]:
    """
    Wrapper for save to database function
    - not helpful to convert _id to int since sqlite does not digest such long integer
      doc['id']  = int(doc['id'][2:], 16)

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
    self.cursor.execute(f"INSERT INTO branches VALUES ({', '.join(['?']*5)})",
                        [doc['id'],
                         '/'.join(doc['branch']['stack']+[doc['id']]),
                         str(doc['branch']['child']),
                         '*' if doc['branch']['path'] is None else doc['branch']['path'],
                         ''.join(['T' if j else 'F' for j in doc['branch']['show']])])
    del doc['branch']
    # save into tags table
    self.cursor.executemany("INSERT INTO tags VALUES (?, ?);", zip([doc['id']]*len(doc['tags']), doc['tags']))
    del doc['tags']
    if 'qrCode' in doc:
      self.cursor.executemany("INSERT INTO qrCodes VALUES (?, ?);", zip([doc['id']]*len(doc['qrCode']), doc['qrCode']))
      del doc['qrCode']
    if 'content' in doc and len(doc['content'])>200:
      doc['content'] = doc['content'][:200]
    doc['type'] = '/'.join(doc['type'])
    doc['gui']  = ''.join(['T' if i else 'F' for i in doc['gui']])
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
          self.cursor.execute("INSERT INTO properties VALUES (?, ?, ?, ?);", [doc['id'], parentKeys+key, str(value), unit])
          self.cursor.execute("INSERT INTO propDefinitions VALUES (?, ?, ?);", [parentKeys+key, label, ''])
        elif isinstance(value, list) and isinstance(value[0], dict) and value[0].keys() >= {"key", "value", "unit"}:
          self.cursor.executemany("INSERT INTO properties VALUES (?, ?, ?, ?);", zip([doc['id']]*len(value),
                                                                                   [parentKeys+key+'.'+i['key'] for i in value],
                                                                                   [i['value'] for i in value],
                                                                                   [i['unit'] for i in value]  ))
          self.cursor.executemany("INSERT INTO propDefinitions VALUES (?, ?, ?);", zip([parentKeys+key+'.'+i['key'] for i in value],
                                                                                   [i['label'] for i in value],
                                                                                   [i['IRI'] for i in value]  ))
        else:
          self.cursor.execute("INSERT INTO properties VALUES (?, ?, ?, ?);", [doc['id'], parentKeys+key, str(value), ''])
      return
    metaDoc = {k:v for k,v in doc.items() if k not in KEY_ORDER}
    insertMetadata(metaDoc, '')
    # save changes
    self.connection.commit()
    branch = copy.deepcopy(docOrg['branch'])
    del branch['op']
    docOrg['branch'] = [branch]
    return docOrg


  def updateDoc(self, change:dict[str,Any], docID:str) -> dict[str,Any]:
    """
    Update document by
    - saving changes to oldDoc (revision document)
    - updating new-document concurrently
    - create a docID for oldDoc
    - Bonus: save '_rev' from newDoc to oldDoc in order to track that updates cannot happen by accident

    Key:Value
    - if value is None: do not change it;
    - if key does not exist: change it to empty, aka remove it

    Args:
        change (dict): item to update
        docID (string):  id of document to change

    Returns:
        dict: json representation of updated document
    """
    raise ValueError('Not implemented UPDATEDOC')


  def updateBranch(self, docID:str, branch:int, child:int, stack:Optional[list[str]]=None,
                   path:Optional[str]='') -> tuple[str, Optional[str]]:
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
    raise ValueError('Not implemented UPDATEBRANCH')


  def createShowFromStack(self, stack:list[str], currentShow:bool=True) -> list[bool]:
    """
    For branches: create show entry in the branches by using the stack
    - should be 1 longer than stack
    - check parents if hidden, then this child is hidden too

    Args:
      stack (list): list of ancestor docIDs
      currentShow (bool): current show-indicator of this item

    Returns:
      list: list of show = list of bool
    """
    raise ValueError('Not implemented CREATE SHOW FROM STACK')


  def remove(self, docID:str) -> dict[str,Any]:
    """
    remove doc from database: temporary for development and testing

    Args:
      docID (string): id of document to remove

    Returns:
      dict: document that was removed
    """
    doc = self.getDoc(docID)
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
    self.cursor.execute("INSERT INTO attachments VALUES (?,?,?,?,?,?)", [docID, name, '', docType, '', ''])
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
    self.cursor.execute("INSERT INTO attachments VALUES (?,?,?,?,?,?)", [docID, name, content['date'], content['docID'], content['remark'], content['user']])
    self.connection.commit()
    return


  def getView(self, thePath:str, startKey:Optional[str]=None, preciseKey:Optional[str]=None) -> list[dict[str,Any]]:
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
      thePath = thePath[:-3]
      allFlag = True
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
      text    = f'SELECT {textSelect} FROM main LEFT JOIN tags USING(id) LEFT JOIN qrCodes USING(id) '\
                f'INNER JOIN branches USING(id) LEFT JOIN properties USING(id) '\
                f'WHERE main.type LIKE "{docType}%"'
      df      = pd.read_sql_query(text, self.connection)
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
      columnOrder = ['tag' if i=='tags' else 'qrCode' if i=='qrCodes' else i[1:] if i.startswith('.') and i[1:] in KEY_ORDER else i for i in viewColumns]
      df = df.reindex(columnOrder, axis=1)
      df = df.rename(columns={i:i[1:] for i in columnOrder if i.startswith('.') })
      df = df.astype('str').fillna('')
      return df
    elif thePath=='viewHierarchy/viewHierarchy':
      self.cursor.execute(f"SELECT branches.id, branches.stack, branches.child, main.type, main.name, main.gui "\
                          f"FROM branches INNER JOIN main USING(id) WHERE branches.stack LIKE '{startKey}%'")
      results = self.cursor.fetchall()
      # value: [child, doc['-type'], doc['.name'], doc['-gui']]
      results = [{'id':i[0], 'key':i[1].replace('/',' '), 'value':[i[2], i[3].split('/'), i[4], [j=='T' for j in i[5]]]} for i in results]
    elif thePath=='viewHierarchy/viewPaths':
      # JOIN and get type
      if startKey is not None:
        print('**ERROR NOT IMPLEMENTED')
      elif preciseKey is not None:
        self.cursor.execute(f"SELECT branches.id, branches.path, branches.stack, main.type, branches.child, main.shasum "\
                            f"FROM branches INNER JOIN main USING(id) WHERE branches.path LIKE '{preciseKey}'")
      else:
        self.cursor.execute(f"SELECT branches.id, branches.path, branches.stack, main.type, branches.child, main.shasum "\
                            f"FROM branches INNER JOIN main USING(id)")
      results = self.cursor.fetchall()
      # value: [branch.stack, doc['-type'], branch.child, doc.shasum,idx]
      results = [{'id':i[0], 'key':i[1], 'value':[i[2].replace('/',' '), i[3].split('/'), i[4], i[5]]} for i in results if i[1] is not None]
    elif viewType=='viewIdentify':
      if docType=='viewQR':
        if startKey is None:
          self.cursor.execute("SELECT qrCodes.id, qrCodes.qrCode, main.name FROM qrCodes INNER JOIN main USING(id)")
        else:
          print("HHEUOEUOU")
          a = 77/0
      elif startKey is None:
        self.cursor.execute("SELECT id, shasum, name FROM main")
      else:
        self.cursor.execute(f"SELECT id, shasum, name FROM main WHERE shasum='{startKey}'")
      results = self.cursor.fetchall()
      results = [{'id':i[0], 'key':i[1].replace('/',' '), 'value':i[2]} for i in results if i[1] is not None]
    else:
      print('continue here with view', thePath, startKey, preciseKey)
      a = 4/0
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
    raise ValueError('Not implemented SET GUI')


  def replicateDB(self, dbInfo:dict[str,Any], progressBar:Any, removeAtStart:bool=False) -> str:
    """
    Replication to another instance

    One cannot simply create the document no the other server...
    - because then the _rev do not match and will never sync
    - issues arise if the documents in a database are deleted. Better remove the entire database and recreate it

    Args:
        dbInfo (dict): info on the remote database
        progressBar (QProgressBar): gui - qt progress bar
        removeAtStart (bool): remove remote DB before starting new

    Returns:
        str: report
    """
    raise ValueError('Not implemented REPLICATE')


  def historyDB(self) -> dict[str,Any]:
    """
    Collect last modification days of documents
    """
    raise ValueError('Not implemented HISTORY')


  def checkDB(self, outputStyle:str='text', minimal:bool=False) -> str:
    """
    Check database for consistencies by iterating through all documents
    - slow since no views used
    - check views
    - only reporting, no repair
    - custom changes are possible with normal scan
    - no interaction with harddisk

    Args:
        outputStyle (str): output using a given style: see outputString
        repair (bool): repair database
        minimal (bool): true=only show warnings and errors; else=also show information

    Returns:
        str: output
    """
    outstring = ''
    if outputStyle=='html':
      outstring += '<div align="right">'
    outstring+= outputString(outputStyle,'h2','LEGEND')
    if not minimal:
      outstring+= outputString(outputStyle,'ok','Green: perfect and as intended')
      outstring+= outputString(outputStyle,'okish', 'Blue: ok-ish, can happen: empty files for testing, strange path for measurements')
    outstring+= outputString(outputStyle,'unsure', 'Dark magenta: unsure if bug or desired (e.g. move step to random path-name)')
    outstring+= outputString(outputStyle,'warning','Orange-red: WARNING should not happen (e.g. procedures without project)')
    outstring+= outputString(outputStyle,'error',  'Red: FAILURE and ERROR: NOT ALLOWED AT ANY TIME')
    if outputStyle=='html':
      outstring += '</div>'
    outstring+= outputString(outputStyle,'h2','List all database entries')
    # tests
    self.cursor.execute("SELECT id, main.type, branches.stack, branches.path, branches.child, branches.show FROM branches INNER JOIN main USING(id)")
    res = self.cursor.fetchall()
    for row in res:
      try:
        id, docType, stack, path, child, _ = row[0], row[1], row[2], row[3], row[4], row[5]
      except ValueError:
        outstring+= outputString(outputStyle,'error',f"dch03a: branch data has strange list {id}")
        continue
      if len(docType.split('/'))==0:
        outstring+= outputString(outputStyle,'unsure',f"dch04: no type in (removed data?) {id}")
        continue
      if not all(k.startswith('x-') for k in stack.split('/')[:-1]):
        outstring+= outputString(outputStyle,'error',f"dch03: non-text in stack in id: {id}")
      if any(len(i)==0 for i in stack) and not docType.startswith('x0'): #if no inheritance
        if docType.startswith(('measurement','x')):
          outstring+= outputString(outputStyle,'warning',f"branch stack length = 0: no parent {id}")
        elif not minimal:
          outstring+= outputString(outputStyle,'okish',f"branch stack length = 0: no parent for procedure/sample {id}")
      try:
        dirNamePrefix = path.split(os.sep)[-1].split('_')[0]
        if dirNamePrefix.isdigit() and child!=int(dirNamePrefix): #compare child-number to start of directory name
          outstring+= outputString(outputStyle,'error',f"dch05: child-number and dirName dont match {id}")
      except Exception:
        pass  #handled next lines
      if path is None:
        if docType.startswith('x'):
          outstring+= outputString(outputStyle,'error',f"dch06: branch path is None {id}")
        elif docType.startswith('measurement'):
          if not minimal:
            outstring+= outputString(outputStyle,'okish', f'measurement branch path is None=no data {id}')
        elif not minimal:
          outstring+= outputString(outputStyle,'ok',f"procedure/sample with empty path {id}")
      else:                                                    #if sensible path
        if len(stack.split('/')) != len(path.split(os.sep)) and path!='*' and not path.startswith('http'): #check if length of path and stack coincide; ignore path=None=*
          if docType.startswith('procedure'):
            if not minimal:
              outstring+= outputString(outputStyle,'ok',f"procedure: branch stack and path lengths not equal: {id}")
          else:
            outstring+= outputString(outputStyle,'unsure',f"branch stack and path lengths not equal: {id}")
        if path!='*' and not path.startswith('http'):
          for parentID in stack.split('/')[:-1]:            #check if all parents in doc have a corresponding path
            parentDoc = self.getDoc(parentID)
            parentDocBranches = parentDoc['branch']
            onePathFound = any(path.startswith(parentBranch['path']) for parentBranch in parentDocBranches)
            if not onePathFound and (not docType.startswith('procedure') or not minimal):
              outstring+= outputString(outputStyle,'unsure',f"dch08: parent does not have corresponding path (remote content) {id} | parentID {parentID}")

    #doc-type specific tests
    self.cursor.execute("SELECT qrCodes.id, qrCodes.qrCode FROM qrCodes JOIN main USING(id) WHERE  main.type LIKE 'sample%'")
    if res:= [i[0] for i in self.cursor.fetchall() if i[1] is None]:
      outstring+= outputString(outputStyle,'warning',f"dch09: qrCode not in samples {res}")
    self.cursor.execute("SELECT id, shasum, image FROM main WHERE  type LIKE 'measurement%'")
    for row in self.cursor.fetchall():
      id, shasum, image = row
      if shasum is None:
        outstring+= outputString(outputStyle,'warning',f"dch10: shasum not in measurement {id}")
      if image.startswith('data:image'):  #for jpg and png
        try:
          imgdata = base64.b64decode(image[22:])
          Image.open(io.BytesIO(imgdata))  #can convert, that is all that needs to be tested
        except Exception:
          outstring+= outputString(outputStyle,'error',f"dch12: jpg-image not valid {id}")
      elif image.startswith('<?xml'):
        #from https://stackoverflow.com/questions/63419010/check-if-an-image-file-is-a-valid-svg-file-in-python
        SVG_R = r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b'
        SVG_RE = re.compile(SVG_R, re.DOTALL)
        if SVG_RE.match(image) is None:
          outstring+= outputString(outputStyle,'error',f"dch13: svg-image not valid {id}")
      elif image in ('', None):
        outstring+= outputString(outputStyle,'unsure',f"image not valid {id} {image}")
      else:
        outstring+= outputString(outputStyle,'error',f"dch14: image not valid {id} {image}")
    return outstring
