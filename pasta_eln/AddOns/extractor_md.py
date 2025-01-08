"""extract data from vendor
- Markdown .md for procedures
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
  with open(filePath, encoding='utf-8') as fIn:
    return {'content':fIn.read(), 'style': {'main':'procedure/markdown'}, 'metaVendor':{}, 'metaUser':{}}
