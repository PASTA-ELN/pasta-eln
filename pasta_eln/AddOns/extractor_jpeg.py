"""extract data from vendor
- default jpeg image
For tutorials, see extractor_csv.py and extractor_png.py
"""
import base64, re, json
from io import BytesIO
import numpy as np
from PIL import Image

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
  # Extractor
  image = Image.open(filePath)
  maxSize = 400
  if max(image.size)>maxSize:
    scale = max(image.size)/maxSize
    newSize = (int(image.size[0]/scale), int(image.size[1]/scale))
    image = image.resize(newSize)
  metaVendor = image.info
  # clean meta_data
  if 'exif' in metaVendor:
    metaVendor['exif'] = re.sub(r'[^\x20-\x7F]','', metaVendor['exif'].decode('utf-8', errors='ignore'))
  for k,v in metaVendor.items():
    try:
      _ = json.dumps(v)
    except Exception:
      metaVendor[k] = str(v)
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
  imageData = f"data:image/jpg;base64,{imageData}"

  # return everything
  return {'image':imageData, 'style': {'main':'measurement/image'}, 'metaVendor':metaVendor, 'metaUser':metaUser}
