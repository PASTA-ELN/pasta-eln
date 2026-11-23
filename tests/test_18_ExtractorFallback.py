"""Fallback extractor: files without extractor_<extension>.py stay unidentified '-' but get a preview"""
import zipfile
from pathlib import Path
from PIL import Image
from pasta_eln.addons import loadNamedModule


def test_fallback(tmp_path:Path) -> None:
  """GIF image, text without extension, ZIP without extension"""
  fallback = loadNamedModule(Path(__file__).parent.parent/'pasta_eln'/'backend_worker', 'extractor_fallback')
  frames = [Image.new('RGB', (800, 300), color) for color in ('red', 'green', 'blue')]
  frames[0].save(tmp_path/'anim.gif', save_all=True, append_images=frames[1:])
  (tmp_path/'README').write_text('# Notes\n'*100, encoding='utf-8')
  zipfile.ZipFile(tmp_path/'archive', 'w').writestr('x.txt', 'x')
  saved:list[Image.Image] = []
  result = fallback.use(tmp_path/'anim.gif', {'main':''}, saved.append)
  assert result['style']['main'] == '-/image'
  assert result['image'].startswith('data:image/png;base64,')
  assert result['metaVendor']['file type'] == 'GIF image'
  assert result['metaVendor']['frames'] == 3
  assert saved[0].size == (800, 300)
  result = fallback.use(tmp_path/'README', {'main':''}, None)
  assert result['style']['main'] == '-/text'
  assert len(result['content']) <= 200
  result = fallback.use(tmp_path/'archive', {'main':''}, None)
  assert result['style']['main'] == '-/binary'
  assert result['metaVendor']['MIME type'] == 'application/zip'


def test_findExtractor(tmp_path:Path) -> None:
  """By extension, by the extensions of the file type (name or content), else the fallback"""
  fallback = loadNamedModule(Path(__file__).parent.parent/'pasta_eln'/'backend_worker', 'extractor_fallback')
  for name in ('extractor_jpeg.py', 'extractor_html.py', 'extractor_png.py'):
    (tmp_path/name).write_text('', encoding='utf-8')
  Image.new('RGB', (10, 10)).save(tmp_path/'image', format='PNG')
  (tmp_path/'page.htm').write_text('<html></html>', encoding='utf-8')
  assert fallback.findExtractor(tmp_path/'photo.jpg', tmp_path) == (tmp_path, 'extractor_jpeg.py')
  assert fallback.findExtractor(tmp_path/'page.htm', tmp_path) == (tmp_path, 'extractor_html.py')
  assert fallback.findExtractor(tmp_path/'image', tmp_path) == (tmp_path, 'extractor_png.py')
  assert fallback.findExtractor(tmp_path/'data.weird', tmp_path)[1] == 'extractor_fallback.py'
