"""extract data from
- Python source files
For tutorials, see extractor_csv.py and extractor_png.py
"""

def use(filePath, style={'main':''}, saveFileName=None):
  """
  Args:
    filePath (Path): full path file name
    style    (dict): supplied to guide the display / extraction style = recipe
                     main is / separated hierarchical elements parent->child
                     can contain more elements
    saveFileName (string): if given, save the image to this file-name
  Returns:
    dict: containing image, metaVendor, metaUser, recipe
  """
  # HERE MAIN PART OF EXTRACTOR
  metaVendor = {}
  metaUser   = {}
  style      = {'main':'workflow/procedure/python'}
  content    = ''
  with open(filePath, encoding='utf-8') as fIn:
    content = '``` python\n'+fIn.read()+'```'
  if 'common_workflow_description.common_workflow_description import Workflow' in content:
    style      = {'main':'workflow/workplan'}
  return {'image':'', 'style':style, 'metaVendor':metaVendor, 'metaUser':metaUser, 'content':content}
