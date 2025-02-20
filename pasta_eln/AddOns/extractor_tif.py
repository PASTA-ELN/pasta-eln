"""extract data from vendor
- default tif file
"""
import base64
from io import BytesIO
import numpy as np
from PIL import Image, ImageFilter


def use(filePath, style={'main':''}, saveFileName=None):
  """
  Args:
    filePath (Path): full path file name
    style    (dict): supplied to guide the display / extraction style = recipe
                     main is / separated hierarchical elements parent->child
                     can contain more elements
    saveFileName (string): if given, save the image to this file-name

  Returns:
    dict: containing image, metaVendor, metaUser, style
  """
  image = Image.open(filePath)
  metaVendor = image.info
  toDelete = [key for key, value in metaVendor.items() if not isinstance(value, (str, int, float, list))]
  for key in toDelete:
    del metaVendor[key]
  style['main'] = 'measurement/image'
  metaUser   = []

  # save to file: this is the high quality image
  if saveFileName is not None:
    image.save(saveFileName)

  # convert PIL image to base64: here one should downscale
  maxSize = 400
  if max(image.size)>maxSize:
    scale = max(image.size)/maxSize
    newSize = (int(image.size[0]/scale), int(image.size[1]/scale))
    image = image.resize(newSize)

  figfile = BytesIO()
  imageData.save(figfile, format='JPEG')
  imageData = base64.b64encode(figfile.getvalue()).decode()
  imageData = f"data:image/jpg;base64,{imageData}"

  # return everything
  return {'image':imageData, 'style':style, 'metaVendor':metaVendor, 'metaUser':metaUser}
