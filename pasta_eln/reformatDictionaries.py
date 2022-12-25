"""Change the format of dictionaries"""


def ontology2Labels(ontology, tableFormat):
  """
  Extract labels and create lists of docType,docLabel pair
  - docLabel is the plural human-readable form of the docType
  - docType is the single-case noun
  Args:
     ontology: ontology
     tableFormat: tableFormat branch from .pastaELN.json

  Returns:
     dictionary: dataDict, hierarchyDict
  """
  dataDict = {}
  hierarchyDict = {}
  for key in ontology.keys():
    if key=='_id' or key=='_rev':
      continue
    label = None
    if key in tableFormat and '-label-' in tableFormat[key]:  #use label from tableFormat
      label = tableFormat[key]['-label-']
    elif key[0]=='x':                                         #use default structural elements
      label = ['Projects','Tasks','Subtasks','Subsubtasks'][key[1]]
    else:                                                     #default system  sample->Samples
      label = key[0].upper()+key[1:]+'s'
    if key[0]=='x':
      hierarchyDict[key] = label
    else:
      dataDict[key] = label
  return {'dataDict':dataDict, 'hierarchyDict':hierarchyDict}

