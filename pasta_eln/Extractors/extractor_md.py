"""extract data from vendor
- Markdown .md for procedures
"""

def use(filePath, recipe='', saveFileName=None):
  """
  Args:
    filePath (string): full path file name
    recipe (string): supplied to guide recipes
                     recipe is / separated hierarchical elements parent->child
    saveFileName (string): if given, save the image to this file-name
  Returns:
    dict: containing image, metaVendor, metaUser, recipe
  """
  with open(filePath,'r', encoding='utf-8') as fIn:
    return {'content':fIn.read(), 'recipe': recipe+'/markdown', 'metaVendor':{}, 'metaUser':{}}

  #other datatypes follow here
  #...

  #final return if nothing successful
  # return {}
