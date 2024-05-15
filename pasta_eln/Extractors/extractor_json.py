"""extract data from vendor
- javascript object notion
"""
import json
import os

def use(filePath, recipe='', saveFileName=None):
  """
  Args:
    filePath (Path): full path file name
    recipe (string): supplied to guide recipes
                     recipe is / separated hierarchical elements parent->child
    saveFileName (string): if given, save the image to this file-name

  Returns:
    dict: containing image, metaVendor, metaUser, recipe
  """
  # Extractor for fancy instrument
  content = ''
  fileSize = os.stat(filePath).st_size / (1024*1024)  #in MB
  if fileSize<0.3:
    with open(filePath,'r', encoding='utf-8') as jsonFile:
      jsonContent = jsonFile.read()
      content = json.loads(jsonContent)
      if not isinstance(content, dict):
        content= {'content': json.loads(jsonContent)}
    content= f'```json\n{json.dumps(content, indent=2)}\n```'
  else:
    content= 'Too large json file'
  recipe = 'procedure/json'

  # return everything
  return {'content':content, 'recipe':recipe, 'metaVendor':{}, 'metaUser':{}}

  #other datatypes follow here
  #...
  #final return if nothing successful
  #return {'recipe': '-', 'metaVendor':{}, 'metaUser':{}}
