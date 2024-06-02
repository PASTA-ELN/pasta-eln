""" Class for interaction with sqlite """
import json, copy, sqlite3
from typing import Any, Optional, Union
from pathlib import Path
from anytree import Node
from .fixedStringsJson import defaultDataHierarchy, defaultDataHierarchyNode

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
DATAHIERARCHY=['IRI','attachments','title','icon','shortcut']

class SqlLiteDB:
  """
  Class for interaction with couchDB
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
    self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [i[0] for i in self.cursor.fetchall()]
    self.connection.commit()
    # check if default documents exist and create
    if 'dataHierarchy' not in tables or resetDataHierarchy:
      if 'dataHierarchy' in tables:
        print('Info: remove old dataHierarchy')
        self.cursor.execute("DROP TABLE dataHierarchy")
      self.cursor.execute(f"CREATE TABLE IF NOT EXISTS dataHierarchy (docType TEXT PRIMARY KEY, iri TEXT, attachments TEXT, title TEXT, icon TEXT, shortcut varchar(1), meta TEXT)")
      for k, v in defaultDataHierarchy.items():
        if k[0] in ('_','-'):
          continue
        self.cursor.execute(f"INSERT INTO dataHierarchy VALUES (?, ?, ?, ?, ?, ?, ?)", [k]+[str(v[i]) for i in DATAHIERARCHY]+[json.dumps(v['meta'])])
      self.initDocTypeViews( configuration['tableColumnsMax'] )
      self.initGeneralViews()
    # refill old-style dictionary
    self.dataHierarchy = {}
    self.cursor.execute("SELECT * FROM dataHierarchy")
    for row in self.cursor.fetchall():
      rowList     = list(row)
      rowList[-1] = json.loads(row[-1])
      self.dataHierarchy[row[0]] = {i:j for i,j in zip(DATAHIERARCHY+['meta'],rowList[1:])}
    patternDB    = list(map(lambda x: x[0], self.cursor.description))[1:-1]  #TODO: do not substract but add for comparison
    patternCode  = [i.lower() for i in DATAHIERARCHY]
    if patternDB!= patternCode:
      print(F"**ERROR wrong dataHierarchy version: {patternDB} {patternCode}")
      raise ValueError(f"Wrong dataHierarchy version {patternDB} {patternCode}")
    # create if not exists, main table and check its colums
    tableString = ', '.join([f'{i[1:]} {j}' for i,j in zip(KEY_ORDER,KEY_TYPE)])+', '+', '.join([f'{i} TEXT' for i in OTHER_ORDER])+', meta TEXT, __history__ TEXT'
    self.cursor.execute(f"CREATE TABLE IF NOT EXISTS main ({tableString})")
    print('TODO: check code vs. data-colums')

    self.dataLabels = {k:v['title'] for k,v in self.dataHierarchy.items() if k[0] not in ['_','-']}
    self.basePath   = basePath
    print('**INFO END INIT')
    return


  def initDocTypeViews(self, tableColumnsMax:int, docTypeChange:str='', columnsChange:list[str]=[]) -> None:
    """
    for the individual docTypes

    Args:
      tableColumnsMax (int): max. number of columns in the docType tables
      docTypeChange (str): if change columns for docType: give docType
      columnsChange (list): change table / view columns to these
    """
    print('**START INITDOCTYPEVIEWS')
    return


  def getColumnNames(self) -> dict[str,str]:
    """ get names of table columns from design documents

    Returns:
      dict: docType and ,-separated list of names as string
    """
    print('**START GETCOLUMNSNAMES')
    return


  def initGeneralViews(self) -> None:
    """
    general views: Hierarchy, Identify
    """
    print('**START INITVIEWSGENERAL')
    return


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
    print('**START GETDOC')
    return


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
    doc['-type'] = '/'.join(doc['-type'])
    doc['-tags'] = ' '.join(doc['-tags'])
    doc['-gui']  = ''.join(['T' if i else 'F' for i in doc['-gui']])
    doc['-branchStack'] = '/'.join(doc['-branch']['stack'])
    doc['-branchChild'] = str(doc['-branch']['child'])
    doc['-branchPath']  = doc['-branch']['path']
    doc['-branchShow']  = ''.join(['T' if j else 'F' for j in doc['-branch']['show']])
    del doc['-branch']
    metadoc = {k:v for k,v in doc.items() if k not in KEY_ORDER+OTHER_ORDER}
    docList = [doc.get(x,'') for x in KEY_ORDER]+[doc.get(i,'') for i in OTHER_ORDER]+[json.dumps(metadoc), '']
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
    print('**START UPDATEDOC')
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
    print('**START UPDATEBRANCH')
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
    print('**START CREATE SHOW FROM STACK')
    return


  def remove(self, docID:str) -> dict[str,Any]:
    """
    remove doc from database: temporary for development and testing

    Args:
      docID (string): id of document to remove

    Returns:
      dict: document that was removed
    """
    print('**START REMOVE')
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
    print('**START ATTACHMENT')
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
    print('**START GETVIEW', thePath.split('/')[1], startKey)
    self.cursor.execute("SELECT * FROM main WHERE type LIKE '"+thePath.split('/')[1]+"%'")
    if startKey is not None or preciseKey is not None:
      print("***TODO: do this 645p.ueoi")
    results = self.cursor.fetchall()
    print(results)
    a = 4/0
    return


  def saveView(self, designName:str, viewCode:dict[str,str]) -> None:
    """
    Adopt the view by defining a new jsCode

    Args:
        designName (string): name of the design
        viewCode (dict): viewName: js-code
    """
    print('**START SAVE VIEW')
    return


  def getHierarchy(self, start:str, allItems:bool=False) -> Node:
    """
    get hierarchy tree for projects, ...

    Args:
      start (str): start of the hierarchy (most parent)
      allItems (bool):  true=show all items, false=only non-hidden

    Returns:
      Node: hierarchy in an anytree
    """
    print('**START GET HIERARCHY')
    return


  def hideShow(self, stack:Union[str,list[str]]) -> None:
    """
    Toggle hide/show indicator of branch

    Args:
      stack (list, str): stack of docID; docID (str)
    """
    print('**START HIDE/SHOW')
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
    print('**START SET GUI')
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
    print('**START REPLICATE')
    return


  def historyDB(self) -> dict[str,Any]:
    """
    Collect last modification days of documents
    """
    print('**START HISTORY')
    return


  def checkDB(self, outputStyle:str='text', repair:bool=False, minimal:bool=False) -> str:
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
    print('**START CHECKDB')
    return
