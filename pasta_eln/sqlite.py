""" Class for interaction with sqlite """
import base64, copy, io, json, logging, os, re, sqlite3
from typing import Any, Optional, Union
from pathlib import Path
from anytree import Node
from PIL import Image
from .fixedStringsJson import defaultDataHierarchy
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

KEY_ORDER   = ['_id' ,            '_rev','-name','-user','-type','-branchStack','-branchChild','-branchPath','-branchShow','-date','-gui',      '-tags','-client']
KEY_TYPE    = ['TEXT PRIMARY KEY','TEXT','TEXT', 'TEXT', 'TEXT', 'TEXT',        'TEXT',        'TEXT',       'TEXT',       'TEXT', 'varchar(2)','TEXT', 'TEXT']
OTHER_ORDER = ['image', 'content', 'comment']
DATA_HIERARCHY=['IRI','attachments','title','icon','shortcut','view']

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
    # create if not exists, main table and check its colums
    tableString = ', '.join([f'{i[1:]} {j}' for i,j in zip(KEY_ORDER,KEY_TYPE)])+', '+', '.join([f'{i} TEXT' for i in OTHER_ORDER])+', meta TEXT, __history__ TEXT'
    self.cursor.execute(f"CREATE TABLE IF NOT EXISTS main ({tableString})")
    self.cursor.execute("SELECT * FROM main")
    self.mainColumnNames = list(map(lambda x: x[0], self.cursor.description))
    if self.mainColumnNames != [i[1:] if i[0] in ('_','-') else i for i in KEY_ORDER]+OTHER_ORDER+['meta','__history__']:
      logging.error("Difference in sqlite-table and code")
      logging.error(self.mainColumnNames)
      logging.error([i[1:] if i[0] in ('_','-') else i for i in KEY_ORDER]+OTHER_ORDER+['meta','__history__'])
      raise ValueError('SQLite table difference')
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
      tableString = 'docType TEXT PRIMARY KEY, '+' TEXT, '.join(DATA_HIERARCHY)+' TEXT, meta TEXT'
      self.cursor.execute(f"CREATE TABLE IF NOT EXISTS dataHierarchy ({tableString})")
      for k, v in defaultDataHierarchy.items():
        self.cursor.execute("INSERT INTO dataHierarchy VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [k]+[str(v[i]) for i in DATA_HIERARCHY]+[json.dumps(v['meta'])])
      self.connection.commit()
    # refill old-style dictionary
    self.cursor = self.connection.execute('select * from dataHierarchy')
    patternDB    = list(map(lambda x: x[0], self.cursor.description))
    patternCode  = ['docType']+DATA_HIERARCHY+['meta']
    if patternDB!= patternCode:
      print(F"**ERROR wrong dataHierarchy version: {patternDB} {patternCode}")
      raise ValueError(f"Wrong dataHierarchy version {patternDB} {patternCode}")
    return


  def dataHierarchy(self, docType:str, column:str) -> dict[str,Any]:
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
    self.cursor.execute(f"SELECT * FROM main WHERE id == '{docID}'")
    data = self.cursor.fetchone()
    # CONVERT SQLITE STYLE INTO PASTA-DICT
    if data is None:
      logging.error('Could not find id in database: '+docID)
      return {}
    doc = {'-'+k:v for k,v in zip(self.mainColumnNames,data)}
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
    for idx, stack in enumerate(doc['-branchStack'].split(' ')):
      iPath = doc['-branchPath'].split(' ')[idx]
      doc['-branch'].append({'stack': stack.split('/')[:-1],
                            'child':  int(doc['-branchChild'].split(' ')[idx]),
                            'path':   None if iPath == '*' else iPath,
                            'show':   [i=='T' for i in doc['-branchShow'].split(' ')[idx]]})
    del doc['-branchStack']
    del doc['-branchChild']
    del doc['-branchPath']
    del doc['-branchShow']
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
    if 'content' in doc and len(doc['content'])>200:
      doc['content'] = doc['content'][:200]
    doc['-type'] = '/'.join(doc['-type'])
    doc['-tags'] = ' '.join(doc['-tags'])
    doc['-gui']  = ''.join(['T' if i else 'F' for i in doc['-gui']])
    doc['-branchStack'] = '/'.join(doc['-branch']['stack']+[doc['_id']])
    doc['-branchChild'] = str(doc['-branch']['child'])
    doc['-branchPath']  = '*' if doc['-branch']['path'] is None else doc['-branch']['path']
    doc['-branchShow']  = ''.join(['T' if j else 'F' for j in doc['-branch']['show']])
    del doc['-branch']
    metaDoc = {k:v for k,v in doc.items() if k not in KEY_ORDER+OTHER_ORDER}
    docList = [doc.get(x,'') for x in KEY_ORDER]+[doc.get(i,'') for i in OTHER_ORDER]+[json.dumps(metaDoc), '']
    self.cursor.execute(f"INSERT INTO main VALUES ({', '.join(['?']*len(docList))})", docList)
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
      self.cursor.execute("SELECT id, branchStack, branchChild, type, name, gui FROM main WHERE branchStack LIKE '"+startKey+"%'")
      results = self.cursor.fetchall()
      results = [{'id':i[0], 'key':i[1].replace('/',' '), 'value':[int(i[2]), i[3].split('/'), i[4], [j=='T' for j in i[5]]]} for i in results]
    elif thePath=='viewHierarchy/viewPaths':
      if startKey is not None:
        print('**ERROR NOT IMPLEMENTED')
      elif preciseKey is not None:
        self.cursor.execute("SELECT id, branchPath, branchStack, type, branchChild, JSON_EXTRACT(meta, '$.shasum') FROM main WHERE branchPath LIKE '"+preciseKey+"'")
      else:
        self.cursor.execute("SELECT id, branchPath, branchStack, type, branchChild, JSON_EXTRACT(meta, '$.shasum') FROM main")
      results = self.cursor.fetchall()
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
    self.cursor.execute("SELECT id, type, branchStack, branchPath, branchChild, branchShow FROM main")
    res = self.cursor.fetchall()
    for row in res:
      try:
        id, docType, stack, path, child, show = row[0], row[1], row[2].split(' '), row[3].split(' '), row[4].split(' '), row[5].split(' ')
      except:
        outstring+= outputString(outputStyle,'error',f"dch03a: branch data has strange list {id}")
        continue
      if len(docType.split('/'))==0:
        outstring+= outputString(outputStyle,'unsure',f"dch04: no type in (removed data?) {id}")
        continue
      if  len(stack)>1 and docType.startswith('x'):
        outstring+= outputString(outputStyle,'error',f"dch02: branch length >1 for text id: {id}")
      if not all([all([k.startswith('x-') for k in j.split('/')[:-1]]) for j in stack]):
        outstring+= outputString(outputStyle,'error',f"dch03: non-text in stack in id: {id}")
      if not (len(stack)==len(path)==len(child)==len(show)):
        outstring+= outputString(outputStyle,'error',f"length of branch items not identical id: {id}")
      if any([len(i)==0 for i in stack]) and not docType.startswith('x0'): #if no inheritance
        if docType.startswith(('measurement','x')):
          outstring+= outputString(outputStyle,'warning',f"branch stack length = 0: no parent {id}")
        elif not minimal:
          outstring+= outputString(outputStyle,'okish',f"branch stack length = 0: no parent for procedure/sample {id}")
      for idx in range(len(path)):
        try:
          dirNamePrefix = path[idx].split(os.sep)[-1].split('_')[0]
          if dirNamePrefix.isdigit() and int(child[idx])!=int(dirNamePrefix): #compare child-number to start of directory name
            outstring+= outputString(outputStyle,'error',f"dch05: child-number and dirName dont match {id}")
        except Exception:
          pass  #handled next lines
        if path[idx] is None:
          if docType.startswith('x'):
            outstring+= outputString(outputStyle,'error',f"dch06: branch path is None {id}")
          elif docType.startswith('measurement'):
            if not minimal:
              outstring+= outputString(outputStyle,'okish', f'measurement branch path is None=no data {id}')
          elif not minimal:
            outstring+= outputString(outputStyle,'ok',f"procedure/sample with empty path {id}")
        else:                                                    #if sensible path
          if len(stack[idx].split('/')) != len(path[idx].split(os.sep)) and path[idx]!='*' and not path[idx].startswith('http'): #check if length of path and stack coincide; ignore path=None=*
            if docType.startswith('procedure'):
              if not minimal:
                outstring+= outputString(outputStyle,'ok',f"procedure: branch stack and path lengths not equal: {id}")
            else:
              outstring+= outputString(outputStyle,'unsure',f"branch stack and path lengths not equal: {id}")
          if path[idx]!='*' and not path[idx].startswith('http'):
            for parentID in stack[idx].split('/')[:-1]:            #check if all parents in doc have a corresponding path
              parentDoc = self.getDoc(parentID)
              parentDocBranches = parentDoc['-branch']
              onePathFound = any(path[idx].startswith(parentBranch['path']) for parentBranch in parentDocBranches)
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
