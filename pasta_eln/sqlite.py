""" Class for interaction with sqlite """
import base64, copy, io, json, logging, os, re, sqlite3
from typing import Any, Optional, Union
from pathlib import Path
from anytree import Node
from PIL import Image
from .fixedStringsJson import defaultDataHierarchy, defaultDefinitions
from .miscTools import outputString

"""
DO NOT WORK ON THIS IF THERE IS SOMETHING ON THE TODO LIST

Notes:
- try to use sqlite style as much as possible and
  translate within this file into PASTA-document-style
  - KEEP THE REST OF THE CODE THE SAME
- start with first test: run-fix-run-fix
  pytest --no-skip --tb=short tests/test_01_3Projects.py
- do not work on replicator
- at the end: create a translator

Benefits:
- easy installation
- test as github actions
- read / backup database with many other tools
- can switch between both databases by changing the config
- investigate perhaps:
  redis db: server that is similar to others; save to file is also a general location; not user-space
  crateDB: server; not user space
- try ID as uuid4 = integer (see if elabFTW does it too)
  - see if I use x-4523452345 anywhere
  - see if I use the first letter of the docID
  -> such long integers are not supported by sqlite: stay with string/text
"""

KEY_ORDER   =    ['_id' , '-name','-user','-type','-dateCreated','-gui',      '-client']
KEY_TYPE    =    ['TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT',        'varchar(2)', 'TEXT']
OTHER_ORDER =    ['image', 'content', 'comment']
DATA_HIERARCHY = ['docType', 'IRI','attachments','title','icon','shortcut','view']
DEFINITIONS =    ['docType','class','idx', 'name', 'query', 'unit', 'IRI', 'mandatory', 'list']


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
    self.createSQLTable('main',    [i[1:] if i[0] in ('-','_') else i for i in KEY_ORDER]+OTHER_ORDER,                    'id', KEY_TYPE+['TEXT']*len(OTHER_ORDER))
    # branches table
    self.createSQLTable('branches',    ['id','stack','child','path','show','dateChanged'],  'id, stack', ['TEXT']*2+['INTEGER']+["TEXT"]*3)
    # metadata table
    # - contains metadata of specific item
    # - key is generally not shown to user
    # - flattened key
    # - can be adopted by adv. user
    self.createSQLTable('metadata',    ['id','key','value','unit'],                    'id, key')
    # definitions table (see below)
    # tags of items
    self.createSQLTable('tags',        ['id','tag'],                                   'id, tag')
    # list of changes to attachments
    self.createSQLTable('attachments', ['id','attachment','date','doc','description'], 'id, attachment, date')
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


  def createSQLTable(self, name, columns, primary, colTypes=None):
    if colTypes is None:
      colTypes = ['TEXT']*len(columns)
    colText = ', '.join(f'{i} {j}' for i,j in zip(columns, colTypes))
    self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} ({colText}, PRIMARY KEY ({primary}))")
    self.cursor.execute(f"SELECT * FROM {name}")
    columnNames = list(map(lambda x: x[0], self.cursor.description))
    if columnNames != columns:
      logging.error(f"Difference in sqlite table: {name}")
      logging.error(columnNames)
      logging.error(columns)
      raise ValueError('SQLite table difference')
    return columnNames


  def dataHierarchy(self, docType:str, column:str, group:str='') -> dict[str,Any]:
    """
    """
    ### return column information
    if docType=='': #if all docTypes
      column = f', {column}' if column else ''
      self.cursor.execute(f"SELECT docType {column} FROM dataHierarchy")
      results = self.cursor.fetchall()
      if column=='':
        return [i[0] for i in results]
      resultsDict = {i[0]:i[1] for i in results}
      if column!=', title':
        raise ValueError('Not tested')
        #   resultsDict = {k:json.loads(v) for k,v in resultsDict.items()}
        #   resultsDict = {k:v.split(',') for k,v in resultsDict.items()}
      return resultsDict
    ### if metadata = definitions of data
    if column == 'meta':
      self.connection.row_factory = sqlite3.Row  #default None
      cursor = self.connection.cursor()
      if group == '':
        cursor.execute(f"SELECT * FROM definitions WHERE docType == '{docType}'")
      else:
        cursor.execute(f"SELECT * FROM definitions WHERE docType == '{docType}' and class == '{group}'")
      return cursor.fetchall()
    if column == 'metaColumns':
      self.cursor.execute(f"SELECT DISTINCT class FROM definitions WHERE docType == '{docType}'")
      result = [i[0] for i in self.cursor.fetchall()]
      return result
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
    self.cursor.execute(f"SELECT * FROM main INNER JOIN branches USING(id) WHERE main.id == '{docID}'")
    data = self.cursor.fetchall()
    # CONVERT SQLITE STYLE INTO PASTA-DICT
    if data is None:
      logging.error('Could not find id in database: '+docID)
      return {}
    doc = {'-'+k:v for k,v in zip(self.mainColumnNames,data[0])}
    doc['_id'] = doc.pop('-id')
    doc['_rev'] = doc.pop('-rev')
    doc['comment']= doc.pop('-comment')
    image = doc.pop('-image')
    if len(image)>3:
      doc['image'] = image
    content = doc.pop('-content')
    if len(content)>3:
      doc['content'] = content
    doc['-type']= doc['-type'].split('/')
    doc['-tags']= doc['-tags'].split(' ') if doc['-tags'] else []
    doc['-gui'] = [i=='T' for i in doc['-gui']]
    doc['-branch'] = []
    # data ends with ... 'stack', 'child', 'path', 'show', 'dateChanged'
    for dataI in data:
      doc['-branch'].append({'stack': dataI[-5].split('/')[:-1],
                             'child': dataI[-4],
                             'path':  None if dataI[-3] == '*' else dataI[-3],
                             'show':   [i=='T' for i in dataI[-2]]})
    del doc['-__history__']
    meta = json.loads(doc.pop('-meta'))
    doc |= meta
    return doc


  def saveDoc(self, doc:dict[str,Any]) -> dict[str,Any]:
    """
    Wrapper for save to database function
    - not helpful to convert _id to int since sqlite does not digest such long integer
      doc['_id']  = int(doc['_id'][2:], 16)

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
    docOrg = copy.deepcopy(doc)
    self.cursor.execute(f"INSERT INTO branches VALUES ({', '.join(['?']*6)})",
                        [doc['_id'],
                         '/'.join(doc['-branch']['stack']+[doc['_id']]),
                         str(doc['-branch']['child']),
                         '*' if doc['-branch']['path'] is None else doc['-branch']['path'],
                         ''.join(['T' if j else 'F' for j in doc['-branch']['show']]),
                         doc['-date']])
    del doc['-branch']
    self.cursor.executemany(f"INSERT INTO tags VALUES (?, ?);", zip([doc['_id']]*len(doc['-tags']), doc['-tags']))
    del doc['-tags']
    if 'content' in doc and len(doc['content'])>200:
      doc['content'] = doc['content'][:200]
    doc['-type'] = '/'.join(doc['-type'])
    doc['-gui']  = ''.join(['T' if i else 'F' for i in doc['-gui']])
    doc['-dateCreated'] = doc.pop('-date')
    metaDoc = {k:v for k,v in doc.items() if k not in KEY_ORDER+OTHER_ORDER}
    docList = [doc.get(x,'') for x in KEY_ORDER]+[doc.get(i,'') for i in OTHER_ORDER]
    self.cursor.execute(f"INSERT INTO main VALUES ({', '.join(['?']*len(docList))})", docList)
    self.cursor.executemany(f"INSERT INTO metadata VALUES (?, ?, ?, ?);", zip([doc['_id']]*len(metaDoc),
                                                                              [i.split('_')[0] for i in metaDoc.keys()],
                                                                              metaDoc.values(),
                                                                              [i.split('_')[1] if '_' in i else '' for i in metaDoc.keys()]))
    self.connection.commit()
    branch = copy.deepcopy(docOrg['-branch'])
    del branch['op']
    docOrg['-branch'] = [branch]
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
    return


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
    return


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
    return


  def remove(self, docID:str) -> dict[str,Any]:
    """
    remove doc from database: temporary for development and testing

    Args:
      docID (string): id of document to remove

    Returns:
      dict: document that was removed
    """
    raise ValueError('Not implemented REMOVE')
    return


  def addAttachment(self, docID:str, name:str, content:dict[str,Any]) -> bool:
    """
    Update document by adding attachment (no new revision)

    Args:
        docID (string):  id of document to change
        name (string): attachment name to add to
        content (dict): dictionary of content to be added (should include user,date,docID,remark)

    Returns:
        bool: success of method
    """
    print('Not implemented ATTACHMENT')
    return


  def getView(self, thePath:str, startKey:Optional[str]=None, preciseKey:Optional[str]=None) -> list[dict[str,Any]]:
    """
    Wrapper for getting view function

    Args:
        thePath (string): path to view
        startKey (string): if given, use to filter output, everything that starts with this key
        preciseKey (string): if given, use to filter output. Match precisely

    Returns:
        list: list of documents in this view
    """
    allFlag = False
    if thePath.endswith('All'):
        thePath = thePath[:-3]
        allFlag = True
        print('**info do something with all flag')
    viewType, docType = thePath.split('/')
    if viewType=='viewDocType':
      viewColumns = self.dataHierarchy(docType, 'view')
      columns = ', '.join(['id'] + [i[1:] if i[0] in ('-','_')   else
                                    i     if i    in OTHER_ORDER else
                                    f"JSON_EXTRACT(meta, '$.{i}')"    for i in viewColumns])
      self.cursor.execute("SELECT "+columns+" FROM main WHERE type LIKE '"+docType+"%'")
      if startKey is not None or preciseKey is not None:
        print("***TODO: do this 645p.ueoi")
      results = self.cursor.fetchall()
      results = [{'id':i[0], 'key':i[0], 'value':list(i[1:])} for i in results]
    elif thePath=='viewHierarchy/viewHierarchy':
      self.cursor.execute("SELECT branches.id, branches.stack, branches.child, main.type, main.name, main.gui FROM branches INNER JOIN main USING(id) WHERE branches.stack LIKE '"+startKey+"%'")
      results = self.cursor.fetchall()
      # value: [child, doc['-type'], doc['-name'], doc['-gui']]
      results = [{'id':i[0], 'key':i[1].replace('/',' '), 'value':[i[2], i[3].split('/'), i[4], [j=='T' for j in i[5]]]} for i in results]
    elif thePath=='viewHierarchy/viewPaths':
      # JOIN and get type
      if startKey is not None:
        print('**ERROR NOT IMPLEMENTED')
      elif preciseKey is not None:
        self.cursor.execute("SELECT branches.id, branches.path, branches.stack, main.type, branches.child, JSON_EXTRACT(main.meta, '$.shasum') FROM branches INNER JOIN main USING(id) WHERE branches.path LIKE '"+preciseKey+"'")
      else:
        self.cursor.execute("SELECT branches.id, branches.path, branches.stack, main.type, branches.child, JSON_EXTRACT(main.meta, '$.shasum') FROM branches INNER JOIN main USING(id)")
      results = self.cursor.fetchall()
      # value: [branch.stack, doc['-type'], branch.child, doc.shasum,idx]
      results = [{'id':i[0], 'key':i[1], 'value':[i[2].replace('/',' '), i[3].split('/'), i[4], i[5]]} for i in results if i[1] is not None]
    elif viewType=='viewIdentify':
      key = 'qrCode' if docType=='viewQR' else 'shasum'
      if startKey is None:
        self.cursor.execute(f"SELECT id, JSON_EXTRACT(meta, '$.{key}'), name FROM main")
      else:
        self.cursor.execute(f"SELECT id, JSON_EXTRACT(meta, '$.{key}'), name FROM main WHERE JSON_EXTRACT(meta, '$.{key}')='{startKey}'")
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
    raise ValueError('Not implemented SET GUI')
    return


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
    return


  def historyDB(self) -> dict[str,Any]:
    """
    Collect last modification days of documents
    """
    raise ValueError('Not implemented HISTORY')
    return


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
        id, docType, stack, path, child, show = row[0], row[1], row[2], row[3], row[4], row[5]
      except:
        outstring+= outputString(outputStyle,'error',f"dch03a: branch data has strange list {id}")
        continue
      if len(docType.split('/'))==0:
        outstring+= outputString(outputStyle,'unsure',f"dch04: no type in (removed data?) {id}")
        continue
      if not all([k.startswith('x-') for k in stack.split('/')[:-1]]):
        outstring+= outputString(outputStyle,'error',f"dch03: non-text in stack in id: {id}")
      if any([len(i)==0 for i in stack]) and not docType.startswith('x0'): #if no inheritance
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
            parentDocBranches = parentDoc['-branch']
            onePathFound = any(path.startswith(parentBranch['path']) for parentBranch in parentDocBranches)
            if not onePathFound and (not docType.startswith('procedure') or not minimal):
              outstring+= outputString(outputStyle,'unsure',f"dch08: parent does not have corresponding path (remote content) {id} | parentID {parentID}")

    #doc-type specific tests
    self.cursor.execute("SELECT id, JSON_EXTRACT(meta, '$.qrCode') FROM main WHERE  type LIKE 'sample%'")
    res = [i[0] for i in self.cursor.fetchall() if i[1] is None]
    if res:
      outstring+= outputString(outputStyle,'warning',f"dch09: qrCode not in samples {res}")
    self.cursor.execute("SELECT id, JSON_EXTRACT(meta, '$.shasum'), image FROM main WHERE  type LIKE 'measurement%'")
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
