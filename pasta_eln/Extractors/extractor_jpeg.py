"""extract data from a .jpeg file
"""
import base64, json
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
  imgArr = np.array(image)
  recipe = 'image/jpeg'
  metaUser   = {'number pixel': imgArr.size,
                'dimension': imgArr.shape}

  #save to file
  imageData = Image.fromarray(imgArr)
  if saveFileName is not None:
    imageData.save(saveFileName)

  # convert PIL image to base64
  figfile = BytesIO()
  imageData.save(figfile, format="JPEG")
  imageData = base64.b64encode(figfile.getvalue()).decode()
  imageData = "data:image/jpeg;base64," + imageData

  # return everything
  return {'image':imageData, 'recipe':recipe, 'metaVendor':metaVendor, 'metaUser':metaUser}

  #other datatypes could follow here if statements are used
  #...
  #final return if nothing successful
  #return {}
