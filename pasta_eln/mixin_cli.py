""" PYTHON MIXIN FOR BACKEND containing all the functions that output to CLI """
import re, platform
from pathlib import Path
try:
  import datalad.api as datalad
except:
  print('**ERROR: Could not start datalad')
from .miscTools import createDirName

class Bcolors:
  """
  Colors for Command-Line-Interface and output
  """
  if platform.system()=='Windows':
    HEADER = ''
    OKBLUE = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''
    BOLD = ''
    UNDERLINE = ''
  else:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CLI_Mixin:
  """ Python Mixin for backend containing all the functions that output to CLI """

  def output(self, docType, printID=False, **kwargs):
    """
    output view to screen
    - length of output 100 character

    Args:
      docType (string): document type to output
      printID (bool):  include docID in output string
      kwargs (dict): additional parameter

    Returns:
        string: output incl. \n
    """
    outString = []
    widthArray = [25,25,25,25]
    if docType in self.tableFormat and '-default-' in self.tableFormat[docType]:
      widthArray = self.tableFormat[docType]['-default-']
    for idx,item in enumerate(self.db.ontology[docType]):
      if not '-name' in item:    #heading
        continue
      if idx<len(widthArray):
        width = widthArray[idx]
      else:
        width = 0
      if width!=0:
        formatString = '{0: <'+str(abs(width))+'}'
        outString.append(formatString.format(item['-name']) )
    outString = '|'.join(outString)+'\n'
    outString += '-'*104+'\n'
    for lineItem in self.db.getView('viewDocType/'+docType):
      rowString = []
      for idx, item in enumerate(self.db.ontology[docType]):
        if idx<len(widthArray):
          width = widthArray[idx]
        else:
          width = 0
        if width!=0:
          formatString = '{0: <'+str(abs(width))+'}'
          if isinstance(lineItem['value'][idx], str ):
            contentString = lineItem['value'][idx]
          elif isinstance(lineItem['value'][idx], (bool,int)):
            contentString = str(lineItem['value'][idx])
          elif lineItem['value'][idx] is None:
            contentString = '--'
          else: #list
            contentString = ' '.join(lineItem['value'][idx])
          contentString = contentString.replace('\n',' ')
          if width<0:  #test if value as non-trivial length
            if lineItem['value'][idx]=='true' or lineItem['value'][idx]=='false':
              contentString = lineItem['value'][idx]
            elif isinstance(lineItem['value'][idx], bool ) or lineItem['value'][idx] is None:
              contentString = str(lineItem['value'][idx])
            elif len(lineItem['value'][idx])>1 and len(lineItem['value'][idx][0])>3:
              contentString = 'true'
            else:
              contentString = 'false'
            # contentString = True if contentString=='true' else False
          rowString.append(formatString.format(contentString)[:abs(width)] )
      if printID:
        rowString.append(' '+lineItem['id'])
      outString += '|'.join(rowString)+'\n'
    return outString


  def outputTags(self, tag='', **kwargs):
    """
    output view to screen
    - length of output 100 character

    Args:
      tag (string): tag to be listed, if empty: print all
      kwargs (dict): additional parameter

    Returns:
        string: output incl. \n
    """
    outString = []
    outString.append(f'{0: <10}'.format('Tags') )
    outString.append(f'{0: <60}'.format('Name') )
    outString.append(f'{0: <10}'.format('ID') )
    outString = '|'.join(outString)+'\n'
    outString += '-'*106+'\n'
    view = None
    if tag=='':
      view = self.db.getView('viewIdentify/viewTags')
    else:
      view = self.db.getView('viewIdentify/viewTags',preciseKey='#'+tag)
    for lineItem in view:
      rowString = []
      rowString.append(f'{0: <10}'.format(lineItem['key']))
      rowString.append(f'{0: <60}'.format(lineItem['value']))
      rowString.append(f'{0: <10}'.format(lineItem['id']))
      outString += '|'.join(rowString)+'\n'
    return outString


  def outputHierarchy(self, onlyHierarchy=True, addID=False, addTags=None, **kwargs):
    """
    output hierarchical structure in database
    - convert view into native dictionary
    - ignore key since it is always the same

    Args:
       onlyHierarchy (bool): only print project,steps,tasks or print all (incl. measurements...)[default print all]
       addID (bool): add docID to output
       addTags (string): add tags, comments, objective to output ['all','tags',None]
       kwargs (dict): additional parameter, i.e. callback

    Returns:
        string: output incl. \n
    """
    from anytree import PreOrderIter
    if len(self.hierStack) == 0:
      return 'Warning: pasta.outputHierarchy No project selected'
    hierString = ' '.join(self.hierStack)
    hierarchy = self.db.getHierarchy(hierString)
    output = ""
    for node in PreOrderIter(hierarchy):
      output +='  '*node.depth+node.name+' | '+'/'.join(node.docType)+' | '+node.id+'\n'
    return output


  def getEditString(self):
    """
    Return org-mode markdown string of hierarchy tree
      complicated style: this document and all its children and grandchildren...

    Returns:
        string: output incl. \n
    """
    return self.outputHierarchy(True,True,'tags')


  def setEditString(self, text, callback=None):
    """
    Using Org-Mode string, replay the steps to update the database

    Args:
       text (string): org-mode structured text
       callback (function): function to verify database change

    Returns:
       success of function: true/false
    """
    # write backup
    verbose = False #debugging only of this function
    if verbose:
      print('===============START SAVE HIERARCHY===============')
      print(text)
      print('---------------End reprint input   ---------------')
    dlDataset = datalad.Dataset(self.basePath/self.cwd.parts[0])
    # add the prefix to org-mode structure lines
    prefix = '*'*len(self.hierStack)
    startLine = r'^\*+\ '
    newText = ''
    for line in text.split('\n'):
      if len(re.findall(startLine,line))>0:  #structure line
        newText += prefix+line+'\n'
      else:                                  #other lines, incl. first
        newText += line+'\n'
    newText = prefix+' '+newText
    docList = [] #TODO not required anymore cT.editString2Docs(newText, self.magicTags)
    del newText; del text
    # initialize iteration
    levelOld = None
    path      = None
    deletedDocs= []
    for doc in docList:  #iterate through all entries

      # deleted items
      if doc['edit'] == '-delete-':
        doc['-user']   = self.userID
        doc = self.db.updateDoc(doc,doc['_id'])
        deletedDocs.append(doc['_id'])
        thisStack = ' '.join(doc['-branch'][0]['stack']+[doc['_id']])
        view = self.db.getView('viewHierarchy/viewHierarchy', startKey=thisStack)
        for item in view:
          subDoc = {'-user':self.userID, 'edit':'-delete-'}
          _ = self.db.updateDoc(subDoc, item['id'])
          deletedDocs.append(item['id'])
        oldPath = doc['-branch'][0]['path']
        newPath = oldPath.parent/('trash_'+oldPath.name)
        print('Deleted doc: Path',oldPath,newPath)
        _ = self.basePath/oldPath.rename(self.basePath/newPath)
        continue

      # deleted parents
      if doc['_id'] in deletedDocs:
        continue

      # All non-deleted items: identify docType
      docDB    = self.db.getDoc(doc['_id']) if doc['_id']!='' else None
      levelNew = doc['-type']
      if levelOld is None:   #first run-through
        children  = [0]
      else:                   #after first entry
        if levelNew<levelOld:                               #UNCLE, aka SIBLING OF PARENT
          for _ in range(levelOld-levelNew):
            children.pop()
          children[-1] += 1
        elif levelNew>levelOld:                             #CHILD
          children.append(0)
        else:                                               #SIBLING
          children[-1] += 1
      if '_id' not in doc or docDB is None or docDB['-type'][0][0]=='x':
        doc['-type'] = 'x'+str(levelNew)
      else:
        doc['-type'] = docDB['-type']

      # for all non-text types: change children and  childNum in database
      #   and continue with next doc. This makes subsequent code easier
      if doc['-type'][0][0]!='x':
        docDB = dict(docDB)
        docDB.update(doc)
        doc = docDB
        doc['childNum'] = children[-1]
        del doc['edit']
        self.addData('-edit-', doc, self.hierStack)
        levelOld     = levelNew
        continue

      # ONLY TEXT DOCUMENTS
      if doc['edit'] == "-edit-":
        edit = "-edit-"
      else:
        edit = doc['-type']
      del doc['edit']
      # change directories: downward
      if levelOld is None:   #first run-through
        doc['childNum'] = docDB['-branch'][0]['child']
      else:                   #after first entry
        lenPath = len(self.cwd.parts)-1 if len(self.cwd.parts[-1])==0 else len(self.cwd.parts)
        for _ in range(lenPath-levelNew):
          self.changeHierarchy(None)                        #'cd ..'
        #check if directory exists on disk
        #move directory; this is the first point where the non-existence of the folder is seen and can be corrected
        dirName = self.basePath/self.cwd/createDirName(doc['-name'],doc['-type'][0],children[-1])
        if not dirName.exists():                     #if move, deletion or because new
          if doc['_id']=='' or doc['_id']=='undefined':     #if new data
            dirName.mkdir()
          else:                                             #if move
            path = Path(docDB['-branch'][0]['path'])
            if not (self.basePath/path).exists():      #parent was moved: get 'path' from knowledge of parent
              parentID = docDB['-branch'][0]['stack'][-1]
              pathParent = Path(self.db.getDoc(parentID)['-branch'][0]['path'])
              path = pathParent/path.name
            if not (self.basePath/path).exists():        #if still does not exist
              print("**ERROR bse01: doc path was not found and parent path was not found |"+str(doc))
              return False
            if self.confirm is None or self.confirm(None,"Move directory "+path+" -> "+self.cwd+dirName):
              (self.basePath/path).rename(self.basePath/self.cwd/dirName)
              dlDataset.save(path=self.basePath/path, message='SetEditString move directory: origin')
              dlDataset.save(path=self.basePath/self.cwd/dirName, message='SetEditString move dir: target')
        if edit=='-edit-':
          self.changeHierarchy(doc['_id'], dirName)   #'cd directory'
          if path is not None:
            #adopt measurements, samples, etc: change / update path by supplying old path
            view = self.db.getView('viewHierarchy/viewPaths', startKey=path.as_posix())
            for item in view:
              if item['value'][1][0][0]=='x':
                continue  #skip since moved by itself
              self.db.updateDoc( {'-branch':{'path':self.cwd.as_posix(), 'oldpath':path.as_posix(),\
                                            'stack':self.hierStack,\
                                            'child':item['value'][2],\
                                            'op':'u'}},item['id'])
        doc['childNum'] = children[-1]
      ## FOR DEBUGGING:
      if verbose:
        print(doc['-name'].strip()+'|'+str(doc['-type'])+'||'+doc['_id']+' #:',doc['childNum'])
        print('  children:',children,'   levelNew, levelOld',levelNew,levelOld,'   cwd:',self.cwd,'\n')
      # write change to database
      if edit=='-edit-':
        docDB = dict(docDB)
        docDB.update(doc)
        doc = docDB
      self.addData(edit, doc, self.hierStack)
      #update variables for next iteration
      if edit!="-edit-" and levelOld is not None:
        self.changeHierarchy(self.currentID)   #'cd directory'
      levelOld     = levelNew

    #----------------------------------------------------
    #at end, go down ('cd  ..') number of children-length
    if '-type' in doc and doc['-type'][0][0]!='x':  #remove one child, if last was not an x-element, e.g. a measurement
      children.pop()
    for _ in range(len(children)-1):
      self.changeHierarchy(None)
    dataset = datalad.Dataset(self.basePath/self.cwd.parts[0])
    dataset.save(message='set-edit-string: update the project structure')
    return True


  def getChildren(self, docID):
    """
    Get children from this parent using outputHierarchy

    Args:
        docID (string): id parent document

    Returns:
        list: list of names, list of document-ids
    """
    ## CREATE NEW AS VERSION OF ANYTREE
    print(self, docID)
    # hierTree = self.outputHierarchy(True,True,False)
    # if hierTree is None:
    #   print('**ERROR bgc01: No hierarchy tree')
    #   return None, None
    # result = cT.getChildren(hierTree,docID)
    # return result['names'], result['ids']
    return []


  def outputQR(self):
    """
    output list of sample qr-codes

    Returns:
        string: output incl. \n
    """
    outString = f"{'QR': <36}|{'Name': <36}|{'ID': <36}\n"
    outString += '-'*110+'\n'
    for item in self.db.getView('viewIdentify/viewQR'):
      outString += f"{item['key'][:36]: <36}|{item['value'][:36]: <36}|{item['id'][:36]: <36}\n"
    return outString


  def outputSHAsum(self):
    """
    output list of measurement SHA-sums of files

    Returns:
        string: output incl. \n
    """
    outString = f"{'SHAsum': <32}|{'Name': <40}|{'ID': <25}\n"
    outString += '-'*110+'\n'
    for item in self.db.getView('viewIdentify/viewSHAsum'):
      key = item['key'] if item['key'] else '-empty-'
      outString += f"{key[:32]: <32}|{item['value'][:40]: <40}|{item['id']: <25}\n"
    return outString
