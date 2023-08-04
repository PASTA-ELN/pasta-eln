"""extract data from vendor
- default png file
"""
import base64
from io import BytesIO
import numpy as np
from PIL import Image

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
  # Extractor
  image = Image.open(filePath)
  metaVendor = image.info
  toDelete = []
  for key,value in metaVendor.items():
    if not isinstance(value, (str, int, float, list)):
      toDelete.append(key)
  for key in toDelete:
    del metaVendor[key]
  imgArr = np.array(image)
  if recipe == 'measurement/image/crop':    #: Crop 3/4 of the image
    newHeight = int(imgArr.shape[0]/2)
    newWidth  = int(imgArr.shape[1]/2)
    imgArr = imgArr[:newHeight, :newWidth, :]
  elif True or recipe == 'measurement/image': #: Default | uncropped
    recipe = 'measurement/image'
  metaUser   = {'number all pixel': int(np.prod(image.size[:2])) }

  #save to file
  imageData = Image.fromarray(imgArr)
  if saveFileName is not None:
    imageData.save(saveFileName)

  # convert PIL image to base64
  figfile = BytesIO()
  imageData.save(figfile, format="PNG")
  imageData = base64.b64encode(figfile.getvalue()).decode()
  imageData = "data:image/png;base64," + imageData

  # return everything
  return {'image':imageData, 'recipe':recipe, 'metaVendor':metaVendor, 'metaUser':metaUser}

  #other datatypes could follow here if statements are used
  #...
  #final return if nothing successful
  #return {}
