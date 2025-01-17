""" PYTHON MIXIN FOR BACKEND containing all the functions that output to CLI """
# mypy: ignore-errors

class CLI_Mixin:
  """ Python Mixin for backend containing all the functions that output to CLI """

  def output(self, docType, printID=False):
    """
    output view to screen
    - length of output 100 character

    Args:
      docType (string): document type to output
      printID (bool):  include docID in output string

    Returns:
        string: output incl. \n
    """
    df = self.db.getView(f'viewDocType/{docType}')
    if not printID:
      df.drop('id', axis=1)
    output = df.to_string(index=False, justify='left', max_colwidth=40)
    outputList = output.split('\n')
    for colName in df.columns[1:]:
      idx = outputList[0].find(colName)
      outputList = [f'{i[:idx]}| {i[idx:]}' for i in outputList]
    outputList.insert(1, '-'*len(max(outputList, key = len)) )
    output = '\n'.join(outputList)
    return output


  def outputHierarchy(self, onlyHierarchy=True, addID=False):
    """
    output hierarchical structure in database
    - convert view into native dictionary
    - ignore key since it is always the same

    Args:
       onlyHierarchy (bool): only print project,steps,tasks or print all (incl. measurements...)[default print all]
       addID (bool): add docID to output

    Returns:
        string: output incl. \n
    """
    from anytree import PreOrderIter
    if len(self.hierStack) == 0:
      return 'Warning: pasta.outputHierarchy No project selected'
    hierString = ' '.join(self.hierStack)
    hierarchy, _ = self.db.getHierarchy(hierString)
    return ''.join('  '*node.depth + node.name + ' | ' + '/'.join(node.docType) + (f' | {node.id}' if addID else '') +'\n'
                   for node in PreOrderIter(hierarchy) if node.docType[0].startswith('x') or not onlyHierarchy)


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
