""" PYTHON MIXIN FOR BACKEND containing all the functions that output to CLI """
# mypy: ignore-errors
from .miscTools import createDirName

class CLI_Mixin:
  """ Python Mixin for backend containing all the functions that output to CLI """

  def output(self, docType, printID=False, **kwargs):
    """
    output view to screen
    - length of output 100 character

    Args:
      docType (string): document type to output
      printID (bool):  include docID in output string
      **kwargs (dict): additional parameter

    Returns:
        string: output incl. \n
    """
    outString = []
    widthArray = [25,25,25,25]
    for idx,item in enumerate(i for group in self.db.ontology[docType]['meta']
                              for i in self.db.ontology[docType]['meta'][group]):
      width = widthArray[idx] if idx<len(widthArray) else 0
      if width!=0:
        formatString = '{0: <'+str(abs(width))+'}'
        outString.append(formatString.format(item['name'].replace('-','')) )
    outString = '|'.join(outString)+'\n'
    outString += '-'*104+'\n'
    for lineItem in self.db.getView(f'viewDocType/{docType}'):
      rowString = []
      for idx, item in enumerate(i for group in self.db.ontology[docType]['meta']
                                 for i in self.db.ontology[docType]['meta'][group]):
        width = widthArray[idx] if idx<len(widthArray) else 0
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
            if lineItem['value'][idx] in ['true', 'false']:
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
      **kwargs (dict): additional parameter

    Returns:
        string: output incl. \n
    """
    outString = [f'{0: <10}'.format('Tags'), f'{0: <60}'.format('Name'), f'{0: <10}'.format('ID')]
    outString = '|'.join(outString)+'\n'
    outString += '-'*106+'\n'
    view = None
    if tag=='':
      view = self.db.getView('viewIdentify/viewTags')
    else:
      view = self.db.getView('viewIdentify/viewTags', preciseKey=f'#{tag}')
    for lineItem in view:
      rowString = [f'{0: <10}'.format(lineItem['key']), f'{0: <60}'.format(lineItem['value']), f'{0: <10}'.format(lineItem['id'])]
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
       **kwargs (dict): additional parameter, i.e. callback

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
      key = item['key'] or '-empty-'
      outString += f"{key[:32]: <32}|{item['value'][:40]: <40}|{item['id']: <25}\n"
    return outString
