"""extract data from vendor
- default jpg image
"""
import base64, json, re
from io import BytesIO
import numpy as np
from PIL import Image

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
  # Extractor
  image = Image.open(filePath)
  maxSize = 400
  if max(image.size)>maxSize:
    scale = max(image.size)/maxSize
    image = image.resize( (np.array(image.size)/scale).astype(int) )
  metaVendor = image.info
  if 'exif' in metaVendor:
    metaVendor['exif'] = re.sub(r'[^\x20-\x7F]','', metaVendor['exif'].decode('utf-8', errors='ignore'))
  imgArr = np.array(image)
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
  imageData = "data:image/jpg;base64," + imageData

  # return everything
  return {'image':imageData, 'recipe':'measurement/image', 'metaVendor':metaVendor, 'metaUser':metaUser}

  #other datatypes could follow here if statements are used
  #...
  #final return if nothing successful
  #return {'recipe': '-', 'metaVendor':{}, 'metaUser':{}}
