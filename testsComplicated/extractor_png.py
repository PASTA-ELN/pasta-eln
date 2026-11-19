"""extract data from vendor
- default png file

SAME AS DEFAULT, copied here such that test-21 can succeed
"""
import base64
from io import BytesIO
import numpy as np
from PIL import Image, ImageFilter


def use(filePath, style={'main':''}, saveFileName=None):
  image = Image.open(filePath)
  metaVendor = image.info
  toDelete = [key for key, value in metaVendor.items() if not isinstance(value, (str, int, float, list))]
  for key in toDelete:
    del metaVendor[key]
  if style['main'] == 'measurement/image/crop':    #: Crop 3/4 of the image
    imgArr = np.array(image)
    newHeight = int(imgArr.shape[0]/2)
    newWidth  = int(imgArr.shape[1]/2)
    imgArr = imgArr[:newHeight, :newWidth, :]
    image = Image.fromarray(imgArr)
  elif style['main'] == 'measurement/image/gaussian':    #: Gaussian blur {'blur radius':['r = 1','r = 5','r = 10','r = 100']}
    radius = int(style.get('blur radius','r = 1').split('=')[-1].strip())
    image = image.filter(ImageFilter.GaussianBlur(radius = radius))
  elif True or style['main'] == 'measurement/image': #: Default | uncropped
    style['main'] = 'measurement/image'
  metaUser   = [{'key':'imageWidth',  'value':image.size[0], 'unit':'mm', 'label':'Largeur de l`image', 'PURL':'http://purl.allotrope.org/ontologies/result#AFR_0002468'},
                {'key':'imageHeight', 'value':f'{image.size[1]}+/- 3', 'unit':'mm', 'label':'Höhe des Bildes','PURL':'http://purl.allotrope.org/ontologies/result#AFR_0002467'}
               ]
  if saveFileName is not None:
    image.save(saveFileName)
  maxSize = 400
  if max(image.size)>maxSize:
    scale = max(image.size)/maxSize
    newSize = (int(image.size[0]/scale), int(image.size[1]/scale))
    image = image.resize(newSize)
  figfile = BytesIO()
  image.save(figfile, format='PNG')
  imageB64 = base64.b64encode(figfile.getvalue()).decode()
  imageB64 = f"data:image/png;base64,{imageB64}"
  return {'image':imageB64, 'style':style, 'metaVendor':metaVendor, 'metaUser':metaUser}
