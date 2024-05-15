"""extract data from vendor
- javascript object notion
"""
import json

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
  with open(filePath,'r', encoding='utf-8') as jsonFile:
    jsonContent = jsonFile.read()
    content = json.loads(jsonContent)
    if not isinstance(content, dict):
      content= {'content': json.loads(jsonContent)}
  recipe = 'procedure/json'
  content= f'```json\n{json.dumps(content, indent=2)}\n```'

  # return everything
  return {'content':content, 'recipe':recipe, 'metaVendor':{}, 'metaUser':{}}

  #other datatypes follow here
  #...
  #final return if nothing successful
  #return {'recipe': '-', 'metaVendor':{}, 'metaUser':{}}
