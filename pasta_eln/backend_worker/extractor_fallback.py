"""Fallback extractor: used when no extractor_<extension>.py exists, hence the item stays unidentified '-'
- the file type comes from the shipped shared-mime-info database (Resources/mime): name first, then content
- images: preview; text: beginning of the text; other files: type and size
"""
import base64
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any
import xdg.BaseDirectory
from PIL import Image
from xdg import Mime

PASTA_ELN_EXTRACTOR_API = 2
MAX_SIZE = 400                                                           # pixels of the preview's longer side
MAX_CONTENT = 192                                                   # characters of text: Pasta-ELN stores 200
DATABASE = Path(__file__).parent.parent/'Resources'

# only the shipped database, not the system's: the same result on every operating system
xdg.BaseDirectory.xdg_data_home = str(DATABASE)
xdg.BaseDirectory.xdg_data_dirs = [str(DATABASE)]
Mime._cache_uptodate = False                                                # pylint: disable=protected-access


def isText(mimeType:Mime.MIMEtype) -> bool:
  """Whether the type is text: text/* or a subclass of text/plain, e.g. application/json
  Args:
    mimeType (MIMEtype): type to check
  Returns:
    bool: True if text
  """
  return mimeType.media == 'text' or any(isText(parent) for parent in mimeType.inherits_from())


def findExtractor(filePath:Path, addOnPath:Path) -> tuple[Path, str]:
  """Extractor for a file: by its extension, else by the extensions of its file type, else this fallback
  - e.g. 'photo.jpg' -> image/jpeg -> '*.jpeg' -> extractor_jpeg.py; a PNG without extension -> extractor_png.py
  Args:
    filePath (Path): full path file name; the content is read only if the name does not decide the type
    addOnPath (Path): directory with the extractor_*.py add-ons
  Returns:
    tuple: directory and file name of the extractor
  """
  pyFile = f'extractor_{filePath.suffix[1:].lower()}.py'
  if (addOnPath/pyFile).is_file():
    return addOnPath, pyFile
  mimeType = Mime.get_type2(str(filePath))                             # loads the database: before Mime.globs
  globs = sorted(Mime.globs.allglobs.get(mimeType, ()), key=lambda i: (-i[0], i[1]))
  for _, pattern, _ in globs:
    pyFile = f'extractor_{pattern[2:].lower()}.py'
    if pattern.startswith('*.') and (addOnPath/pyFile).is_file():
      return addOnPath, pyFile
  return Path(__file__).parent, 'extractor_fallback.py'


def use(filePath:Path, style:dict[str,Any], saveFigure:Any) -> dict[str,Any]:
  """
  Args:
    filePath (Path): full path file name
    style    (dict): style, not used: the fallback has no recipes
    saveFigure (Any): callback used to save an extracted figure
  Returns:
    dict: containing image or content, metaVendor, metaUser, style
  """
  filePath = Path(filePath)
  # ponytail: pyxdg's checking order skips the longest-glob rule and checks low-priority magic first;
  #   modama's mime.py fixes both, if wrong types show up
  mimeType = Mime.get_type2(str(filePath))
  with open(DATABASE/'mime'/'comments', encoding='utf-8') as fIn:
    names = dict(line.rstrip('\n').split('\t', 1) for line in fIn)
  fileStat = filePath.stat()
  metaVendor = {'MIME type':str(mimeType), 'file type':names.get(str(mimeType), 'unknown'),
                'file size [bytes]':fileStat.st_size,
                'modified at':datetime.fromtimestamp(fileStat.st_mtime, tz=timezone.utc).isoformat()}
  try:
    image: Image.Image|None = Image.open(filePath) if mimeType.media == 'image' else None
  except OSError:                                        # Pillow cannot read all images, e.g. SVG, camera raw
    image = None
  if image is not None:
    metaVendor |= {'width [px]':image.size[0], 'height [px]':image.size[1], 'mode':image.mode,
                   'frames':getattr(image, 'n_frames', 1)}
    metaVendor |= {k:v for k,v in image.info.items() if isinstance(k, str) and isinstance(v, (str, int, float))}
    image = image.convert('RGBA')
    saveFigure(image.convert('RGB'))                                                       # JPEG has no alpha
    image.thumbnail((MAX_SIZE, MAX_SIZE))
    figfile = BytesIO()
    image.save(figfile, format='PNG')
    return {'image':f'data:image/png;base64,{base64.b64encode(figfile.getvalue()).decode()}',
            'style':{'main':'-/image'}, 'metaVendor':metaVendor, 'metaUser':{}}
  # if text
  if isText(mimeType):
    with open(filePath, encoding='utf-8', errors='replace') as fIn:
      content = f'```\n{fIn.read(MAX_CONTENT)}\n```'
    return {'content':content, 'style':{'main':'-/text'}, 'metaVendor':metaVendor, 'metaUser':{}}
  # others
  return {'content':f'{metaVendor["file type"]}, {fileStat.st_size:,} bytes', 'style':{'main':'-/binary'},
          'metaVendor':metaVendor, 'metaUser':{}}
