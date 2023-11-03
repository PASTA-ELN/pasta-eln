""" Class for interaction with couchDB """
import traceback, logging, time, json, os, re
from typing import Any, Optional, Union
from pathlib import Path
from anytree import Node
from anytree.search import find_by_attr
from cloudant.client import CouchDB
from cloudant.replicator import Replicator
from PySide6.QtWidgets import QProgressBar  # pylint: disable=no-name-in-module
from .fixedStringsJson import defaultOntology, defaultOntologyNode
from .handleDictionaries import ontology_pre_to_V4
from .miscTools import tracebackString, DummyProgressBar

class Database:
  """
  Class for interaction with couchDB
  """
  def __init__(self, user:str, password:str, databaseName:str, configuration:dict[str,Any],
               resetOntology:bool=False, basePath:Path=Path()):
    """
    Args:
      user (string): user name to local database
      password (string): password to local database
      databaseName (string): local database name
      configuration (dict): configuration of GUI elements
      resetOntology (bool): reset ontology
    """
    try:
      self.client = CouchDB(user, password, url='http://127.0.0.1:5984', connect=True)
    except Exception:
      print('**ERROR dit01: Could not connect with username+password to local server')
      return
    self.databaseName = databaseName
    if self.databaseName in self.client.all_dbs():
      self.db = self.client[self.databaseName]
    else:
      self.db = self.client.create_database(self.databaseName)  #tests and initial creation of example data set requires this
    # check if default documents exist and create
    if '-ontology-' not in self.db or resetOntology:
      if '-ontology-' in self.db:
        print('Info: remove old ontology')
        self.db['-ontology-'].delete()
      self.ontology = defaultOntology
      self.db.create_document(self.ontology)
      self.initDocTypeViews( configuration['tableColumnsMax'] )
      self.initGeneralViews()
    self.ontology = dict(self.db['-ontology-'])
    if '-version' in self.ontology and int(self.ontology['-version']) < 4:
      logging.info('Convert ontology to V4.0')
      ontology_pre_to_V4(self.ontology)
      self.db['-ontology-'].delete()
      self.db.create_document(self.ontology)
    if '-version' not in self.ontology or self.ontology['-version'] != 4:
      print(F"**ERROR wrong ontology version: {self.ontology['-version']}")
      raise ValueError(f"Wrong ontology version {self.ontology['-version']}")
    self.dataLabels = {k:v['displayedTitle'] for k,v in self.ontology.items() if k[0] not in ['_','-']}
    self.basePath   = basePath
    return


  def initDocTypeViews(self, tableColumnsMax:int, docTypeChange:str='', columnsChange:list[str]=[]) -> None:
    """
    for the individual docTypes

    Args:
      tableColumnsMax (int): max. number of columns in the docType tables
      docTypeChange (str): if change columns for docType: give docType
      columnsChange (list): change table / view columns to these
    """
    tracebackString(True, 'initDocTypeView')
    # print('SB: initDocViews newColumns',newColumns)
    oldColumnNames = self.getColumnNames()
    jsDefault = 'if ($docType$) {doc["-branch"].forEach(function(branch){emit($key$, [$outputList$]);});}'
    viewCode = {}
    for docType in [i for i in self.ontology if i[0] not in ['_','-']]+['-']:
      if docType=='x0':
        newString = "doc['-type']=='x0' && (doc['-branch'][0].show.every(function(i) {return i;}))"
        js    = jsDefault.replace('$docType$', newString).replace('$key$','doc._id')
        jsAll = jsDefault.replace('$docType$', "doc['-type']=='x0'").replace('$key$','doc._id')
      elif docType[0]=='x':
        continue
      else: #show all doctypes that have the same starting ..
        js = jsDefault.replace('$docType$',
            f"doc['-type'].join('/').substring(0,{len(docType)})=='{docType}"+"' && (doc['-branch'][0].show.every(function(i) {return i;}))",
            ).replace('$key$', 'branch.stack[0]')
        jsAll = jsDefault.replace(
            '$docType$',
            f"doc['-type'].join('/').substring(0, {len(docType)})=='{docType}'",
            ).replace('$key$', 'branch.stack[0]')
      outputList = []
      baseDocType = docType[:-3] if docType.endswith('All') else docType
      if docTypeChange==docType:
        columnNames = columnsChange
      elif baseDocType in oldColumnNames:
        columnNames = oldColumnNames[baseDocType].split(',')
      elif docType == '-':
        columnNames = [i['name'] for i in defaultOntologyNode['default'] if 'name' in i]
      else:
        columnNames = [i['name'] for group in self.ontology[docType]['meta']
                       for i in self.ontology[docType]['meta'][group]]
      columnNames = columnNames[:tableColumnsMax]
      commentString = f'// {docType} : ' + ','.join(columnNames) + '\n'
      for name in columnNames:
        if name == 'image':
          outputList.append('doc.image?doc.image.length>3:false')  #Not as .toString() because that leads to inconsistencies
        elif name == '-tags':
          outputList.append("doc['-tags'].join(' ')")
        elif '#_' in name:
          outputList.append(f'doc["-tags"].indexOf("{name[1:]}")>-1')
        elif name == '-type':
          outputList.append('doc["-type"].slice(1).join("/")')
        elif name == 'content':
          outputList.append('doc.content?doc.content.slice(0, 100):""')
        elif '/' in name:  #stacked requests i.e. metaVendor/date
          parentString = 'doc' + ''.join([f'["{i}"]' for i in name.split('/')[:-1]])
          newString = 'doc' + ''.join([f'["{i}"]' for i in name.split('/')])
          newString = f'{parentString} ? {newString}: ""'
          outputList.append(newString)
        else:
          outputList.append(f'doc["{name}"]')
      outputStr = ','.join(outputList)
      viewCode[docType.replace('/','__')]       = commentString+js.replace('$outputList$', outputStr)
      viewCode[docType.replace('/','__')+'All'] = commentString+jsAll.replace('$outputList$', outputStr)
    self.saveView('viewDocType', viewCode)
    return


  def getColumnNames(self) -> dict[str,str]:
    """ get names of table columns from design documents

    Returns:
      dict: docType and ,-separated list of names as string
    """
    if '_design/viewDocType' not in self.db:
      return {}
    try:
      comments = [v['map'].split('\n// ')[1].split('\n')[0]
                  for v in self.db['_design/viewDocType']['views'].values()]
      return {i.split(' : ')[0]:i.split(' : ')[1] for i in comments}
    except Exception:
      defaultColumnNames = {'-':','.join([i['name'] for i in defaultOntologyNode['default'] if 'name' in i])}
      for docType, docTypeDict in self.ontology.items():
        if docType[0] in ['_','-']:
          continue
        columnNames = [i['name'] for group in docTypeDict['meta'] for i in docTypeDict['meta'][group]]
        defaultColumnNames[docType] = ','.join(columnNames)
      return defaultColumnNames


  def initGeneralViews(self) -> None:
    """
    general views: Hierarchy, Identify
    """
    tracebackString(True, 'initGeneralView')
    jsHierarchy  = '''
      if ('-type' in doc && (doc["-branch"][0].show.every(function(i) {return i;}))) {
        doc['-branch'].forEach(function(branch, idx) {emit(branch.stack.concat([doc._id]).join(' '),[branch.child,doc['-type'],doc['-name'],idx]);});
      }
    '''
    jsHierarchyAll  = '''
      if ('-type' in doc) {
        doc['-branch'].forEach(function(branch, idx) {emit(branch.stack.concat([doc._id]).join(' '),[branch.child,doc['-type'],doc['-name'],idx]);});
      }
    '''
    jsPath = '''
      if ('-type' in doc && '-branch' in doc && (doc["-branch"][0].show.every(function(i) {return i;}))){
        if ('shasum' in doc){doc['-branch'].forEach(function(branch,idx){if(branch.path){emit(branch.path,[branch.stack,doc['-type'],branch.child,doc.shasum,idx]);}});}
        else                {doc['-branch'].forEach(function(branch,idx){if(branch.path){emit(branch.path,[branch.stack,doc['-type'],branch.child,''        ,idx]);}});}
      }
    '''
    jsPathAll = '''
      if ('-type' in doc && '-branch' in doc){
        if ('shasum' in doc){doc['-branch'].forEach(function(branch,idx){if(branch.path){emit(branch.path,[branch.stack,doc['-type'],branch.child,doc.shasum,idx]);}});}
        else                {doc['-branch'].forEach(function(branch,idx){if(branch.path){emit(branch.path,[branch.stack,doc['-type'],branch.child,''        ,idx]);}});}
      }
    '''
    self.saveView('viewHierarchy',{'viewHierarchy':jsHierarchy,'viewPaths':jsPath,\
                                   'viewHierarchyAll':jsHierarchyAll,'viewPathsAll':jsPathAll})
    jsSHA= "if (doc['-type'][0]==='measurement'){emit(doc.shasum, doc['-name']);}"
    jsQR = "if (doc.qrCode.length > 0) {doc.qrCode.forEach(function(thisCode) {emit(thisCode, doc['-name']);});}"
    jsTags="if ('-tags' in doc && (doc['-branch'][0].show.every(function(i) {return i;})))"+\
              "{doc['-tags'].forEach(function(tag){emit(tag,[doc['-name'], doc['-type'].join('/')]);});}"
    jsTagsAll="if ('-tags' in doc){doc['-tags'].forEach(function(tag){emit(tag,[doc['-name'], doc['-type'].join('/')]);});}"
    views = {'viewQR':jsQR, 'viewSHAsum':jsSHA, 'viewTags':jsTags, 'viewTagsAll':jsTagsAll}
    self.saveView('viewIdentify', views)
    return



  def exit(self, deleteDB:bool=False) -> None:
    """
    Shutting down things

    Args:
      deleteDB (bool): remove database
    """
    import warnings
    if deleteDB:
      self.db.client.delete_database(self.databaseName)
    warnings.simplefilter("ignore")  #client disconnect triggers ignored ResourceWarning on socket
    self.client.disconnect()
    return


  def getDoc(self, docID:str) -> dict[str,Any]:
    """
    Wrapper for get from database function

    Args:
        docID (dict): document id

    Returns:
        dict: json representation of document
    """
    return dict(self.db[docID])


  def saveDoc(self, doc:dict[str,Any]) -> dict[str,Any]:
    """
    Wrapper for save to database function

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
    doc['-client'] = tracebackString(False, 'save:'+doc['_id'])
    if '-branch' in doc and 'op' in doc['-branch']:
      del doc['-branch']['op']  #remove operation, saveDoc creates and therefore always the same
      if 'show' not in doc['-branch']:
        doc['-branch']['show'] = self.createShowFromStack(doc['-branch']['stack'])
      doc['-branch'] = [doc['-branch']]
    try:
      res = self.db.create_document(doc)
      logging.debug('successfully saved doc with type and branch '+doc['_id']+' '+'/'.join(doc['-type'])+'  |  '+str(doc['-branch'])+'\n')
    except Exception:
      logging.error('could not save, likely JSON issue; Check logging file')
      logging.error('could not save, likely JSON issue')
      if 'image' in doc:
        del doc['image']
      logging.error(str(doc))
      logging.error(traceback.format_exc())
      res=None
    return res


  def updateDoc(self, change:dict[str,Any], docID:str) -> dict[str,Any]:
    """
    Update document by
    - saving changes to oldDoc (revision document)
    - updating new-document concurrently
    - create a docID for oldDoc
    - Bonus: save '_rev' from newDoc to oldDoc in order to track that updates cannot happen by accident

    Args:
        change (dict): item to update
        docID (string):  id of document to change

    Returns:
        dict: json representation of updated document
    """
    change['-client'] = tracebackString(False, f'updateDoc:{docID}')
    newDoc = self.db[docID]  #this is the document that stays live
    initialDocCopy = dict(newDoc)
    if 'edit' in change:     #if delete
      oldDoc = dict(newDoc)
      for item in oldDoc:
        if item not in ('_id', '_rev', '-branch'):
          del newDoc[item]
      newDoc['-user']   = change['-user']
    else:                    #if update
      oldDoc = {}            #this is an older revision of the document
      # nothingChanged = True
      # handle branch
      if '-branch' in change:# and len(change['-branch']['stack'])>0:
        op = change['-branch'].pop('op')
        oldpath = change['-branch'].pop('oldpath',None)
        if change['-branch']['path'] is None:
          change['-branch']['path']=newDoc['-branch'][0]['path']
        if change['-branch'] not in newDoc['-branch']:       #skip if new branch is already in branch
          oldDoc['-branch'] = newDoc['-branch'].copy()
          for branch in newDoc['-branch']:
            if op=='c' and branch['path']==change['-branch']['path']:
              op='u'
          if op=='c':    #create, append
            change['-branch']['show'] = self.createShowFromStack(change['-branch']['stack'])
            newDoc['-branch'] += [change['-branch']]
            # nothingChanged = False
          elif op=='u':  #update
            if oldpath is not None:
              for branch in newDoc['-branch']:
                if branch['path'].startswith(oldpath):
                  if os.path.basename(branch['path']) == newDoc['-name'] and \
                         os.path.basename(str(change['-branch']['path']))!='':
                    newDoc['-name'] = os.path.basename(str(change['-branch']['path']))
                  branch['path'] = branch['path'].replace(oldpath ,change['-branch']['path'])
                  branch['stack']= change['-branch']['stack']
                  branch['show'] = self.createShowFromStack(change['-branch']['stack'], branch['show'][-1])
                  break
            else:
              newDoc['-branch'][0] = change['-branch'] #change the initial one
            # nothingChanged = False
          elif op=='d':  #delete
            newDoc['-branch'] = [branch for branch in newDoc['-branch'] if branch['path']!=change['-branch']['path']]
            # originalLength = len(newDoc['-branch'])
            # if originalLength!=len(newDoc['-branch']):
            #   nothingChanged = False
          else:
            logging.warning('database.update.1: unknown branch op: '+newDoc['_id']+' '+newDoc['-name'])
            return newDoc
      #handle other items
      # change has to be dict, not Document
      for item in change:
        if item in ['_id','_rev','-branch']:                #skip items cannot do not result in change
          continue
        if item=='-type' and change['-type']==['--']:          #skip non-set type
          continue
        if item=='image' and change['image']=='':          #skip if non-change in image
          continue
        if change[item] is None:
          # DO CHANGE TO EMPTY: if user wants it
          # or (isinstance(change[item], str) and change[item].strip()=='') or \
          #    (isinstance(change[item], list) and len(change[item])==0):      #skip empty entries
          continue
        ## Discussion: What if content only differs by whitespace changes?
        # These changes should occur in the database, the user wanted it so
        # Do these changes justify a new revision?
        # Hence one could update the doc and previous-revision(with the current _rev)
        #  - but that would lead to special cases, more code, chaos
        #  - also not sure how often simple white space changes occur, how important
        # To identify these cases use the following
        # if (isinstance(change[item], str) and " ".join(change[item].split())!=" ".join(newDoc[item].split()) ) or \
        #    (isinstance(change[item], list) and change[item]!=newDoc[item] ):
        # Add to testBasic to test for it:
        #       myString = myString.replace('A long comment','A long   comment')
        if item not in newDoc or change[item]!=newDoc[item]:
          # if item not in ['-date','-client','-user']:      #if only date/client change, no significant change
          #   nothingChanged = False
          if item == 'image':
            oldDoc[item] = 'image changed'       #don't backup images: makes database big and are only thumbnails anyhow
          elif item in newDoc:
            oldDoc[item] = newDoc[item]
          newDoc[item] = change[item]
      # Always update, for some reason single tags are not recognized
      # if nothingChanged:
      #   logging.debug('database.update.2: doc not updated-nothing changed: '+newDoc['_id']+' '+newDoc['-name'])
      #   return newDoc
    #For both cases: delete and update
    if '_curated' not in newDoc['-tags'] and newDoc['-type'][0][0]!='x':
      newDoc['-tags'].append('_curated')
    try:
      newDoc.save()
    except Exception:
      logging.error('database.update: update unsuccessful: '+newDoc['_id']+' '+newDoc['-name'])
      print('**ERROR: could not update document. Likely version conflict. Initial and current version:')
      print(initialDocCopy)
      print(newDoc)
      return {}
    attachmentName = 'v0.json'
    if '_attachments' in newDoc:
      attachmentName = 'v'+str(len(newDoc['_attachments']))+'.json'
    newDoc.put_attachment(attachmentName, 'application/json', json.dumps(oldDoc))
    logging.debug('database.update.3: doc update success: '+newDoc['_id']+' '+newDoc['-name']+'\n')
    return newDoc


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
    doc = self.db[docID]
    doc['-client'] = tracebackString(False, f'updateBranch:{docID}')
    if len(doc['-branch'])<=branch:
      print(f'**ERROR Cannot delete branch that does not exist {branch}in doc {docID}')
      logging.error('**ERROR Cannot delete branch that does not exist %s in doc %s', branch, docID)
    oldPath = doc['-branch'][branch]['path']
    if oldPath is None:
      path = None
    if path=='':
      name = f'{child:03d}_' + '_'.join(oldPath.split('/')[-1].split('_')[1:])
      path = '/'.join(oldPath.split('/')[:-1]+[name])
    # test if path already exists
    if docID[0]=='x' and path is not None:
      if not (self.basePath/path/'.id_pastaELN.json').exists():
        logging.debug('Target folder\'s json does not exist: '+path)
        oldDocID = ''
      else:
        with open(self.basePath/path/'.id_pastaELN.json', 'r', encoding='utf-8') as fIn:
          oldJsonContent = json.load(fIn)
          oldDocID = oldJsonContent['_id']
      if path is not None and (self.basePath/path).exists() and docID!=oldDocID:
        print(f'**ERROR** Target folder already exist: {path}. Try to create a new path name')
        logging.error('Target folder already exist: %s. Try to create a new path name', path)
      while path is not None and (self.basePath/path).exists() and docID!=oldDocID:
        if re.search(r"_\d+$", path) is None:
          path += '_1'
        else:
          path = '_'.join(path.split('_')[:-1])+'_'+str(int(path.split('_')[-1])+1)
    # assemble data
    doc['-branch'][branch]['path']=path
    doc['-branch'][branch]['child']=child
    stackOld = list(doc['-branch'][branch]['stack'])
    if stack is not None:
      doc['-branch'][branch]['stack']=stack
    doc['-branch'][branch]['show'] = self.createShowFromStack(doc['-branch'][branch]['stack'],
                                                              doc['-branch'][branch]['show'][-1])
    doc.save()
    logging.debug('success BRANCH updated with type and branch '+doc['_id']+' '+'/'.join(doc['-type'])+'  |  '+str(doc['-branch'])+'\n')
    # move content: folder and data and write .json to disk
    if oldPath is not None and path is not None and ':/' not in oldPath:
      if not (self.basePath/oldPath).exists() and (self.basePath/path).exists():
        logging.debug('database:updateBranch: dont move since already good')
      else:
        (self.basePath/oldPath).rename(self.basePath/path)
    if docID[0]=='x' and path is not None:
      with open(self.basePath/path/'.id_pastaELN.json', 'w', encoding='utf-8') as fOut:
        fOut.write(json.dumps(self.getDoc(docID)))
      # update children's paths
      children = self.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stackOld+[docID,'']))
      for line in children:
        docLine = self.db[line['id']]
        flagNotChanged = True
        for branchLine in docLine['-branch']:
          if branchLine['path'] is not None and branchLine['path'].startswith(oldPath):
            branchLine['path'] = path+branchLine['path'][len(oldPath):]
            flagNotChanged = False
          if stack is not None and '/'.join(branchLine['stack']).startswith('/'.join(stackOld)):
            branchLine['stack'] = stack+branchLine['stack'][len(stackOld):]
            branchLine['show']  = self.createShowFromStack(branchLine['stack'], branchLine['show'][-1])
            flagNotChanged = False
        if flagNotChanged:
          print(f"**Unsure** Not updated{str(line)}")
        docLine.save()
        # update .json on disk
        for branchLine in docLine['-branch']:
          if line['id'][0]=='x'  and (self.basePath/branchLine['path']).exists():
            with open(self.basePath/branchLine['path']/'.id_pastaELN.json', 'w', encoding='utf-8') as fOut:
              fOut.write(json.dumps(docLine))
    return oldPath, path


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
    show = len(stack)*[True] + [currentShow]
    for idx, docID in enumerate(stack):
      if not self.db[docID]['-branch'][0]['show'][-1]:
        show[idx] = False
    return show


  def remove(self, docID:str) -> dict[str,Any]:
    """
    remove doc from database: temporary for development and testing

    Args:
      docID (string): id of document to remove

    Returns:
      dict: document that was removed
    """
    tracebackString(True, f'remove:{docID}')
    doc = self.db[docID]
    res = dict(doc)
    doc.delete()
    return res


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
    try:
      doc = self.db[docID]
      if '-attachment' not in doc:
        doc['-attachment'] = {}
      if name in doc['-attachment']:
        doc['-attachment'][name] += [content]
      else:
        doc['-attachment'][name] = [content]
      doc.save()
      return True
    except Exception:
      return False


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
    from cloudant.view import View
    designDoc = self.db.get_design_document(thePath.split('/')[0])
    v = View(designDoc, thePath.split('/')[1])
    try:
      if startKey is not None:
        res = v(startkey=startKey, endkey=f'{startKey}zzz')['rows']
      elif preciseKey is not None:
        res = v(key=preciseKey)['rows']
      else:
        res = list(v.result)
    except Exception:
      print('**ERROR dgv01: Database / Network problem for path |', thePath)
      print(traceback.format_exc())
      res = []
    return res


  def saveView(self, designName:str, viewCode:dict[str,str]) -> None:
    """
    Adopt the view by defining a new jsCode

    Args:
        designName (string): name of the design
        viewCode (dict): viewName: js-code
    """
    from cloudant.design_document import DesignDocument
    if f'_design/{designName}' in self.db:
      designDoc = self.db[f'_design/{designName}']
      if '_rev' in designDoc:
        designDoc.delete()
    designDoc = DesignDocument(self.db, designName)
    for view in viewCode:
      thisJsCode = 'function (doc) {\n' + viewCode[view] + '\n}'
      designDoc.add_view(view, thisJsCode)
    try:
      designDoc.save()
    except Exception:
      print('**ERROR dsv01: something unexpected has happened.')
      logging.error('dsv01: something unexpected has happened.')
      logging.error(traceback.format_exc())
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
    if not allItems:
      view = self.getView('viewHierarchy/viewHierarchy',    startKey=start)
    if allItems or len(view)==0:
      view = self.getView('viewHierarchy/viewHierarchyAll', startKey=start)
    # for item in view:
    #   print(item)
    levelNum = 1
    while True:
      level = [i for i in view if len(i['key'].split())==levelNum]
      if levelNum==1:
        if len(level)==1:
          dataTree = Node(id=level[0]['key'], docType=level[0]['value'][1], name=level[0]['value'][2])
        else:
          print(f'**ERROR getHierarchy Did not find corresponding level={levelNum} under docID {start}')
          dataTree = Node(id=None, name='')
      else:
        childList = [i['value'][0] for i in level]   #temporary list to allow sorting for child-number
        # https://stackoverflow.com/questions/6618515/sorting-list-based-on-values-from-another-list
        for node in [x for (_,x) in sorted(zip(childList, level), key=lambda pair: pair[0])]:
          parentID = node['key'].split()[-2]
          parentNode = find_by_attr(dataTree, parentID, name='id')
          _ = Node(id=node['id'], parent=parentNode, docType=node['value'][1], name=node['value'][2])
      if not level: #if len(level)==0
        break
      levelNum += 1
    # print(RenderTree(dataTree, style=AsciiStyle()))
    return dataTree


  def hideShow(self, stack:Union[str,list[str]]) -> None:
    """
    Toggle hide/show indicator of branch

    Args:
      stack (list, str): stack of docID; docID (str)
    """
    flippedOnce = False
    if isinstance(stack, str):
      doc = self.db[stack]
      for idx, _ in enumerate(doc['-branch']):
        doc['-branch'][idx]['show'][-1] = not doc['-branch'][idx]['show'][-1]
        logging.debug('flipped str: %s',str(stack))
      doc.save()
      if stack[0]=='x':
        stack = doc['-branch'][0]['stack']+[stack]
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
    if doc['-type'][0][0]=='x':
      with open(self.basePath/doc['-branch'][0]['path']/'.id_pastaELN.json','w', encoding='utf-8') as fOut:
        fOut.write(json.dumps(doc))
    return


  def replicateDB(self, dbInfo:dict[str,Any], progressBar:Union[QProgressBar,DummyProgressBar], removeAtStart:bool=False) -> str:
    """
    Replication to another instance

    Args:
        dbInfo (dict): info on the remote database
        progressBar (QProgressBar): gui - qt progress bar
        removeAtStart (bool): remove remote DB before starting new

    Returns:
        str: report
    """
    progressBar.show()
    try:
      rep = Replicator(self.client)
      try:
        client2 = CouchDB(dbInfo['user'], dbInfo['password'], url=dbInfo['url'], connect=True)
      except Exception:
        return '<b>ERROR drp01: Could not connect to remote server. Abort replication.</b><br>'+\
                 'user:'+dbInfo['user']+'<br>password:'+dbInfo['password']+'<br>url:'+dbInfo['url']
      db2 = client2[dbInfo['database']]
      replResult = rep.create_replication(self.db, db2, create_target=False, continuous=False)
      logging.info('Start replication '+replResult['_id']+'.')
      progressBar.setValue(10)
      #try every 10sec whether replication success. Do that for max. of 5min
      startTime = time.time()
      while True:
        progressBar.setValue(10+ int((time.time()-startTime)/60./5.*90) )
        if (time.time()-startTime)/60.>5.:
          logging.info('Stop waiting for replication '+replResult['_id']+'.')
          progressBar.hide()
          return "Waited for 5min. No replication success in that time"
        replResult.fetch()        # get updated, latest version from the server
        if '_replication_state' in replResult:
          logging.info('Success replication '+replResult['_id']+'.')
          progressBar.hide()
          reply = f"Replication success state: {replResult['_replication_state']}\n" + \
                  f"  time of reporting: {replResult['_replication_state_time']}\n"
          stats = dict(replResult['_replication_stats'])
          del stats['checkpointed_source_seq']
          return reply+'\n  '.join([f"{k.replace('_',' ')}:{v}" for k,v in stats.items()])
        time.sleep(10)
    except Exception:
      progressBar.hide()
      return "**ERROR drp02: replicate error |\n"+traceback.format_exc()



  def historyDB(self) -> dict[str,Any]:
    """
    Collect last modification days of documents
    """
    from datetime import datetime
    import numpy as np
    collection:dict[str,Any] = {}
    for doc in self.db:
      if doc['_id'][1]=='-' and len(doc['_id'])==34 and '-type' in doc and '-date' in doc:
        docType = doc['-type'][0]
        date = doc['-date'][:-1]
        if len(date)==22:
          date += '0'
        date    = datetime.fromisoformat( date ).timestamp()
        if docType in collection:
          collection[docType] = collection[docType] + [date]
        else:
          collection[docType] = [date]
    #determine bins for histogram
    firstSubmit = datetime.now().timestamp()
    for value in collection.values():
      if np.min(value) < firstSubmit:
        firstSubmit = np.min(value)
    bins = np.linspace(firstSubmit, datetime.now().timestamp(), 100 )
    #calculate histogram and save it
    collectionCopy = dict(collection)
    for key,value in collection.items():
      hist, _ = np.histogram(value, bins)
      collectionCopy[key] = hist
    collectionCopy['-bins-'] = (bins[:-1]+bins[1:])/2
    #calculate score
    bias = np.exp(( collectionCopy['-bins-']-collectionCopy['-bins-'][-1] ) / 1.e7)
    score = {key: np.sum(value*bias) for key, value in collectionCopy.items()}
    #reformat dates into string
    collectionCopy['-bins-'] = [datetime.fromtimestamp(i).isoformat() for i in collectionCopy['-bins-']]
    collectionCopy['-score-']= score
    return collectionCopy


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
    import base64, io
    from PIL import Image
    from .miscTools import outputString
    outstring = ''
    if outputStyle=='html':
      outstring += '<div align="right">'
    outstring+= outputString(outputStyle,'h2','LEGEND')
    if not minimal:
      outstring+= outputString(outputStyle,'ok','Green: perfect and as intended')
      outstring+= outputString(outputStyle,'okish', 'Blue: ok-ish, can happen: empty files for testing, strange path for measurements')
    outstring+= outputString(outputStyle,'unsure','Pink: unsure if bug or desired (e.g. move step to random path-name)')
    outstring+= outputString(outputStyle,'warning','Yellow: WARNING should not happen (e.g. procedures without project)')
    outstring+= outputString(outputStyle,'error',  'Red: FAILURE and ERROR: NOT ALLOWED AT ANY TIME')
    if outputStyle=='html':
      outstring += '</div>'
    outstring+= outputString(outputStyle,'h2','List all database entries')
    if repair:
      print('REPAIR MODE IS ON: afterwards, full-reload and create views')
    ## loop all documents
    for doc in self.db:
      try:
        if '_design' in doc['_id']:
          if not minimal:
            outstring+= outputString(outputStyle,'ok','..info: Design document '+doc['_id'])
          continue
        if doc['_id'] == '-ontology-':
          if repair:
            if '-hierarchy-' in doc:
              del doc['-hierarchy-']
            for old,new in [['project','x0'],['step','x1'],['task','x2']]:
              if new not in doc and old in doc:
                doc[new] = doc[old].copy()
                del doc[old]
            doc.save()
          if not minimal:
            outstring+= outputString(outputStyle,'ok','..info: ontology exists')
          continue
        #only normal documents after this line

        ###custom temporary changes: keep few as examples;
        # BE CAREFUL: PRINT FIRST, delete second run ; RUN ONLY ONCE
        # Version1->Version2 changes
        # if '-branch' in doc:
        #   for b in doc['-branch']:
        #     b['show']=[True]*(len(b['stack'])+1)
        # if '-tags' not in doc:
        #   tags = doc['tags']
        #   del doc['tags']
        #   tags = [i[1:] if i[0]=='#' else i for i in tags]
        #   tags = ['_1' if i=='1' else i for i in tags]
        #   tags = ['_2' if i=='2' else i for i in tags]
        #   tags = ['_3' if i=='3' else i for i in tags]
        #   tags = ['_4' if i=='4' else i for i in tags]
        #   tags = ['_5' if i=='5' else i for i in tags]
        #   if '-curated' in doc:
        #     if doc['-type'][0][0]!='x':
        #       tags.append('_curated')
        #     del doc['-curated']
        #   doc['-tags'] = tags
        #   print(doc['_id'], 'tags' in doc, doc['-tags'], '-curated' in doc)
        #### doc.save()
        # END VERSION 1 -> 2 changes
        #   del doc['revisions']
        #   doc.save()
        # if len(doc['_id'].split('-'))==3:
        #   print('id',doc['_id'])
        #   doc.delete()
        #   continue
        ## output size of document
        # print('Name: {0: <16.16}'.format(doc['-name']),'| id:',doc['_id'],'| len:',len(json.dumps(doc)))
        # if repair:
        #   # print("before",doc.keys(),doc['_id'])
        #   # if doc['_id']== "x-028456be353dd7b5092c48841d6dfec8":
        #   #   print('found')
        #   for item in ['branch','curated','user','type','client','date']:
        #     if '-'+item not in doc and item in doc:
        #       if item in ('branch', 'type'):
        #         doc['-'+item] = doc[item].copy()
        #       else:
        #         doc['-'+item] = doc[item]
        #       del doc[item]
        #   #print(doc.keys())
        #   if not '-type' in doc:
        #     doc['-type'] =[]
        #   if doc['-type'] == ["text","project"]:
        #     doc['-type'] = ["x0"]
        #   if doc['-type'] == ["text","step"]:
        #     doc['-type'] = ["x1"]
        #   if doc['-type'] == ["text","task"]:
        #     doc['-type'] = ["x2"]

        #   Project renaming bug 1)
        # if doc['-branch'][0]['path'].startswith('PastaEln'):
        #   oldPath = doc['-branch'][0]['path']
        #   newPath = oldPath.replace('PastaEln', 'Pasta')
        #   print(oldPath, '->', newPath)
        #   doc['-branch'][0]['path'] = newPath
        #   doc.save()
        #
        #   #   if len(doc['-branch'][0]['stack']) == len(doc['-branch'][0]['path'].split('/'))-1 :
        #   #     doc['-type'] = ["x"+str(len(doc['-branch'][0]['stack'])) ]
        #   # print("after ",doc.keys(),doc['_id'])

        #branch test
        if '-branch' not in doc:
          outstring+= outputString(outputStyle,'error',f"dch01: branch does not exist {doc['_id']}")
          continue
        if len(doc['-branch'])>1 and doc['-type'] =='x':                 #text elements only one branch
          outstring+= outputString(outputStyle,'error',f"dch02: branch length >1 for text {doc['_id']} {str(doc['-type'])}")
        for branch in doc['-branch']:
          for item in branch['stack']:
            if not item.startswith('x-'):
              outstring+= outputString(outputStyle,'error',f"dch03: non-text in stack {doc['_id']}")

          if len(branch['stack'])==0 and doc['-type']!=['x0']: #if no inheritance
            if doc['-type'][0] == 'measurement' or  doc['-type'][0][0] == 'x':
              outstring+= outputString(outputStyle,'warning',f"branch stack length = 0: no parent {doc['_id']}")
            elif not minimal:
              outstring+= outputString(outputStyle,'okish',f"branch stack length = 0: no parent for procedure/sample {doc['_id']} | {doc['-name']}")
          if '-type' not in doc or len(doc['-type'])==0:
            outstring+= outputString(outputStyle,'unsure',f"dch04: no type in (removed data?) {doc['_id']}")
            continue
          if doc['-type'][0][0]=='x':
            try:
              dirNamePrefix = branch['path'].split(os.sep)[-1].split('_')[0]
              if dirNamePrefix.isdigit() and branch['child']!=int(dirNamePrefix): #compare child-number to start of directory name
                outstring+= outputString(outputStyle,'error',f"dch05: child-number and dirName dont match {doc['_id']}")
            except Exception:
              pass  #handled next lines
          if branch['path'] is None:
            if doc['-type'][0][0] == 'x':
              outstring+= outputString(outputStyle,'error',f"dch06: branch path is None {doc['_id']}")
            elif doc['-type'][0] == 'measurement':
              if not minimal:
                outstring+= outputString(outputStyle,'okish','measurement branch path is None=no data '+doc['_id']+' '+doc['-name'])
            elif not minimal:
              outstring+= outputString(outputStyle,'ok',f"procedure/sample with empty path {doc['_id']}")
          else:                                                    #if sensible path
            if len(branch['stack'])+1 != len(branch['path'].split(os.sep)):#check if length of path and stack coincide
              if doc['-type'][0] == 'procedure':
                if not minimal:
                  outstring+= outputString(outputStyle,'ok',f"procedure: branch stack and path lengths not equal: {doc['_id']} | {branch['path'][:30]}")
              else:
                outstring+= outputString(outputStyle,'unsure',f"branch stack and path lengths not equal: {doc['_id']} | {branch['path'][:30]}")
            if branch['child'] != 9999:
              for parentID in branch['stack']:                  #check if all parents in doc have a corresponding path
                parentDoc = self.getDoc(parentID)
                if '-branch' not in parentDoc:
                  outstring += outputString(outputStyle, 'error', f'dch07: branch not in parent with id {parentID}')
                  continue
                parentDocBranches = parentDoc['-branch']
                onePathFound = any(parentBranch['path'] is not None and parentBranch['path'] in branch['path'] for parentBranch in parentDocBranches)
                if not onePathFound:
                  outstring+= outputString(outputStyle,'unsure',f"dch08: parent does not have corresponding path (remote content) {doc['_id']} | parentID {parentID}")
          if 'show' not in branch:
            outstring+= outputString(outputStyle,'error',f"dch08a: branch does not have show: {doc['_id']}")
          elif len(branch['show']) != len(branch['stack'])+1:
            outstring+= outputString(outputStyle,'error',f"dch08b: branch-show not same length as branch-stack: {doc['_id']}")

        #every doc should have these:
        for key in ['-name','-tags','-client','-user','-date']:
          if key not in doc:
            outstring+= outputString(outputStyle,'error',f"dch17: {key} not in (deleted doc?){doc['_id']}")

        #doc-type specific tests
        if '-type' in doc and doc['-type'][0] == 'sample':
          if 'qrCode' not in doc:
            outstring+= outputString(outputStyle,'error',f"dch09: qrCode not in sample {doc['_id']}")
        elif '-type' in doc and doc['-type'][0] == 'measurement':
          if 'shasum' not in doc:
            outstring+= outputString(outputStyle,'error',f"dch10: shasum not in measurement {doc['_id']}")
          if 'image' not in doc:
            outstring+= outputString(outputStyle,'error',f"dch11: image not in measurement {doc['_id']}")
          else:
            if doc['image'].startswith('data:image'):  #for jpg and png
              try:
                imgdata = base64.b64decode(doc['image'][22:])
                Image.open(io.BytesIO(imgdata))  #can convert, that is all that needs to be tested
              except Exception:
                outstring+= outputString(outputStyle,'error',f"dch12: jpg-image not valid {doc['_id']}")
            elif doc['image'].startswith('<?xml'):
              #from https://stackoverflow.com/questions/63419010/check-if-an-image-file-is-a-valid-svg-file-in-python
              SVG_R = r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b'
              SVG_RE = re.compile(SVG_R, re.DOTALL)
              if SVG_RE.match(doc['image']) is None:
                outstring+= outputString(outputStyle,'error',f"dch13: svg-image not valid {doc['_id']}")
            elif doc['image']=='':
              outstring+= outputString(outputStyle,'unsure',f"image not valid {doc['_id']} {doc['image']}")
            else:
              outstring+= outputString(outputStyle,'error',f"dch14: image not valid {doc['_id']} {doc['image']}")

      except Exception:
        outstring+= outputString(outputStyle,'error', f"dch15: critical error in {doc['_id']}\n {traceback.format_exc()}")

    ##TEST views
    outstring+= outputString(outputStyle,'h2','List problematic database tables')
    view = self.getView('viewIdentify/viewSHAsum')
    shasumKeys = []
    for item in view:
      if item['key']=='':
        outstring+= outputString(outputStyle,'error', f"measurement without shasum: {item['id']} {item['value']}")
      else:
        if item['key'] in shasumKeys:
          key = item['key'] or '- empty string -'
          outstring += outputString(outputStyle, 'error', f"dch16: shasum twice in view: {key} {item['id']} {item['value']}")
        shasumKeys.append(item['key'])
    return outstring
