"""extract data from
- Python source files
"""

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
  # HERE MAIN PART OF EXTRACTOR
  metaVendor = {}
  metaUser   = {}
  recipe     = 'procedure/python'
  content    = ''
  with open(filePath, 'r', encoding='utf-8') as fIn:
    content = '``` python\n'+fIn.read()+'```'
  return {'image':'', 'recipe':recipe, 'metaVendor':metaVendor, 'metaUser':metaUser, 'content':content}
