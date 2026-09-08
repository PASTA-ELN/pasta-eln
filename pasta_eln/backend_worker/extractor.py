"""Extractor discovery, execution, timeout handling, and result merging."""
import json
import logging
import multiprocessing
import os
import tempfile
import time
import traceback
from collections.abc import Callable
from datetime import datetime, timezone
from hashlib import sha256
from inspect import signature
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO
from urllib import request
import xml.etree.ElementTree as ET
import matplotlib
import matplotlib.axes as mpaxes
import matplotlib.pyplot as plt
from PIL import Image, PngImagePlugin
from ..addons import loadNamedModule
from ..text_tools.handle_dictionaries import truncateMetadata
from ..text_tools.string_changes import outputString

matplotlib.use('Agg')
matplotlib.rcParams['svg.fonttype'] = 'none'

PROVENANCE_KEY = 'PastaELNProvenance'
TRUNC_WARNING = 'Metadata truncated to configured maximum size.'


class ExtractorManager:
  """Manage extractor jobs independently from database workflows."""
  def __init__(self, basePath:Path, addOnPath:Path, timeout:str, metadataLimit:str,
               dataHierarchy:Callable[[str,str],Any]) -> None:
    """Create an extractor manager for one backend/project-group context.

    Args:
      basePath (Path): Root path of the local project data tree.
      addOnPath (Path): Directory containing extractor_*.py add-ons.
      timeout (str): Maximum extractor runtime, e.g. "10 sec" or "1 min".
      metadataLimit (str): Maximum serialized metadata length, e.g. "80 kB".
      dataHierarchy (Callable): Backend callback for looking up valid document types.
    """
    self.basePath = basePath
    self.addOnPath = addOnPath
    self.timeoutSeconds = int(timeout[:-3]) if timeout.endswith('sec') else int(timeout[:-3])*60
    # Keep the historical user-facing kB unit; each kB means 1024 serialized JSON characters.
    self.metadataLimit = int(metadataLimit[:-3]) * 1024
    self.dataHierarchy = dataHierarchy


  def prepareJob(self, filePath:Path, docType:None | list[str]=None, jobID:Any=None) -> dict[str,Any] | None:
    """Resolve paths/downloads and build one extractor job.

    Args:
      filePath (Path): Local or remote file path to extract.
      docType (None, list): Current document type used as extractor style input.
      jobID (Any): Identifier used to map returned results back to the job list.

    Returns:
      dict, None: Extractor job dictionary, or None if no matching extractor exists or download failed.
    """
    docType = [''] if docType is None else docType
    docName = filePath.relative_to(self.basePath).as_posix() if filePath.is_absolute() else filePath.as_posix()
    doc = {'name':docName, 'type':docType}
    extension = filePath.suffix[1:]                                                 #cut off initial . of .jpg
    if str(filePath).startswith('http'):
      absFilePath = Path(tempfile.gettempdir())/filePath.name
      try:
        req = request.Request(filePath.as_posix().replace(':/','://'), headers={'User-Agent': 'Mozilla/5.0'})
        with request.urlopen(req, timeout=60) as urlRequest:
          with open(absFilePath, 'wb') as f:
            try:
              f.write(urlRequest.read())
            except Exception:
              logging.error('Saving downloaded file to temporary disk', exc_info=True)
              return None
      except Exception:
        logging.error('Could not download file from internet %s', filePath.as_posix())
        return None
    else:
      if filePath.is_absolute():
        filePath = filePath.relative_to(self.basePath)
      absFilePath = self.basePath/filePath
    pyFile = f'extractor_{extension.lower()}.py'
    pyPath = self.addOnPath/pyFile
    if not pyPath.is_file():
      return None
    return {'id':jobID, 'doc':doc, 'addOnPath':self.addOnPath, 'pyFile':pyFile, 'absFilePath':absFilePath,
            'extension':extension, 'style':{'main':'/'.join(docType)}, 'dataHash':sha256File(absFilePath),
            'extractorHash':sha256File(pyPath), 'saveFileName':None}


  def applyResults(self, results:list[dict[str,Any]], jobs:list[dict[str,Any]]) -> list[tuple[dict[str,Any],dict[str,Any]]]:
    """Merge extractor results into their job documents.

    Args:
      results (list): Results returned by runJobs.
      jobs (list): Original extractor jobs, indexed by each result id.

    Returns:
      list: Tuples of job and mutated document for each applied result.
    """
    applied = []
    for result in results:
      job = jobs[result['id']]
      doc = job['doc']
      pyFile = result['pyFile']
      absFilePath = result['absFilePath']
      try:
        if result['status'] == 'ok':
          content = result['content']
          general = content.get('general',[])
          for key in [i for i in content if i not in ['metaVendor','metaUser','image','content','style']]:#only allow accepted keys
            del content[key]
          doc |= content
          for item in general:
            doc[item[0]] = item[1]
          for meta in ['metaVendor','metaUser']:
            if meta not in doc:
              doc[meta] = {}
            if isinstance(doc[meta], dict):                                                   #convenient type
              if meta == 'metaVendor' and 'fileExtension' not in doc[meta]:
                doc[meta]['fileExtension'] = result['extension'].lower()
              for item in doc[meta]:
                if isinstance(doc[meta][item], tuple):
                  doc[meta][item] = list(doc[meta][item])
                try:
                  _ = json.dumps(doc[meta][item], ensure_ascii=False)
                except (ValueError, TypeError):
                  doc[meta][item] = str(doc[meta][item])
                  logging.warning('stringified  %s %s',meta, item)
            else:
              for item in doc[meta]:
                if not (isinstance(item, dict) and 'key' in item and 'value' in item and 'unit' in item):
                  logging.error('Complicated extractor return wrong', exc_info=True)
            doc[meta], truncated, oldSize, newSize = truncateMetadata(doc[meta], self.metadataLimit)
            if truncated:
              logging.warning('%s %s (%d -> %d characters).', TRUNC_WARNING, meta, oldSize, newSize)
          if doc['style']['main'].startswith(doc['type'][0]):
            doc['type'] = doc['style']['main'].split('/')
          else:
            #user has strange wish: trust him/her
            logging.info('user has strange wish: trust him/her: %s  %s','/'.join(doc['type']),'  '+doc['style']['main'])
          del doc['style']
          if 'links' in doc and len(doc['links'])==0:
            del doc['links']
          doc['dataHash'] = job['dataHash']
          doc['extractorHash'] = job['extractorHash']
        else:
          doc['metaUser'] = {'filename':absFilePath.name, 'extension':absFilePath.suffix,
                             'filesize':absFilePath.stat().st_size,
                             'created at':datetime.fromtimestamp(absFilePath.stat().st_ctime, tz=timezone.utc).isoformat(),
                             'modified at':datetime.fromtimestamp(absFilePath.stat().st_mtime, tz=timezone.utc).isoformat()}
          if result['status'] == 'timeout':
            doc['metaUser'] |= {'extractorStatus':'stopped',
                                'extractorError':f"Extractor stopped after {self.timeoutSeconds} seconds."}
            logging.warning('Extractor stopped after timeout %s: %s', self.timeoutSeconds, pyFile)
          else:
            logging.warning('Issue with extractor %s\n %s', pyFile, result.get('traceback',''))
      except Exception:
        logging.warning('Issue with extractor %s\n %s', pyFile, traceback.format_exc())
        doc['metaUser'] = {'filename':absFilePath.name, 'extension':absFilePath.suffix,
                           'filesize':absFilePath.stat().st_size,
                           'created at':datetime.fromtimestamp(absFilePath.stat().st_ctime, tz=timezone.utc).isoformat(),
                           'modified at':datetime.fromtimestamp(absFilePath.stat().st_mtime, tz=timezone.utc).isoformat()}
      doc['dataHash'] = job['dataHash']
      applied.append((job, doc))
    return applied


  def runJobs(self, jobs:list[dict[str,Any]]) -> list[dict[str,Any]]:
    """Run extractor jobs in parallel child processes.

    Args:
      jobs (list): Prepared extractor jobs from prepareJob.

    Returns:
      list: Result dictionaries containing status and extractor metadata.
    """
    if not jobs:
      return []
    maxWorkers = min(4, os.cpu_count() or 1, len(jobs))
    waiting = list(jobs)
    active:list[dict[str,Any]] = []
    results:list[dict[str,Any]] = []

    def startJob(job:dict[str,Any]) -> None:
      """Start one extractor child process and add it to the active job list.

      Args:
        job (dict): Prepared extractor job to start.
      """
      parentConnection, childConnection = multiprocessing.Pipe(duplex=False)
      process = multiprocessing.Process(target=runExtractorInSubprocess, args=(job, childConnection))
      process.start()
      childConnection.close()
      active.append({'job':job, 'connection':parentConnection, 'process':process,
                     'deadline':time.monotonic()+self.timeoutSeconds})

    while waiting or active:
      while waiting and len(active)<maxWorkers:
        startJob(waiting.pop(0))
      for state in active[:]:
        job = state['job']
        connection = state['connection']
        process = state['process']
        if connection.poll():
          result = connection.recv()
          process.join(1)
          if process.is_alive():
            process.terminate()
            process.join(1)
          connection.close()
          result |= {'id':job['id'], 'pyFile':job['pyFile'], 'absFilePath':job['absFilePath'], 'extension':job['extension']}
          results.append(result)
          active.remove(state)
        elif not process.is_alive():
          process.join()
          connection.close()
          results.append({'id':job['id'], 'status':'error', 'traceback':'Extractor process exited without result.',
                          'pyFile':job['pyFile'], 'absFilePath':job['absFilePath'],
                          'extension':job['extension']})
          active.remove(state)
        elif time.monotonic() >= state['deadline']:
          process.terminate()
          process.join(2)
          if process.is_alive():
            process.kill()
            process.join(1)
          connection.close()
          results.append({'id':job['id'], 'status':'timeout', 'pyFile':job['pyFile'],
                          'absFilePath':job['absFilePath'], 'extension':job['extension']})
          active.remove(state)
      if active:
        time.sleep(0.05)
    return results


  def use(self, filePath:Path, dataHash:str, doc:dict[str,Any]) -> None:
    """Run the matching extractor for one document and merge its result.

    Args:
      filePath (Path): Local or remote file path to extract.
      dataHash (str): SHA-256 of the data file to store in the document.
      doc (dict): Document to mutate with extractor output.
    """
    job = self.prepareJob(filePath, doc['type'], 0)
    if job is not None:
      try:
        job['doc'] = doc
        job['dataHash'] = dataHash
        if results := self.runJobs([job]):
          self.applyResults(results, [job])
      except Exception:
        logging.warning('Issue with extractor %s\n %s', job['pyFile'], traceback.format_exc())
        absFilePath = job['absFilePath']
        doc['metaUser'] = {'filename':absFilePath.name, 'extension':absFilePath.suffix,
                           'filesize':absFilePath.stat().st_size,
                           'created at':datetime.fromtimestamp(absFilePath.stat().st_ctime, tz=timezone.utc).isoformat(),
                           'modified at':datetime.fromtimestamp(absFilePath.stat().st_mtime, tz=timezone.utc).isoformat()}
    doc['dataHash'] = dataHash                                 #essential for logic, always save, unlike image


  def test(self, filePath:Path |str, extractorPath:Path | None=None, style:dict[str,Any]={'main':''},
           outputStyle:str='text', saveFig:str='') -> tuple[str, str]:
    """Test one extractor and return a human-readable report.

    Args:
      filePath (Path, str): path to the file to be tested
      extractorPath (Path, None): path to the directory with extractors
      style (dict): style with a main-key that is / separated
      outputStyle (str): report in ['print','text','html'] including show images
      saveFig (str): save figure to...; if given stop testing after generating image

    Returns:
      str, str: short summary or long report and image (as svg or base64 string)
    """
    content = {}
    report = outputString(outputStyle, 'h2', 'Report on extractor test')
    htmlStr= 'Please visit <a href="https://pasta-eln.github.io/pasta-eln/extractors.html#'
    success = True
    if isinstance(filePath, str):
      filePath = Path(filePath)
    if filePath.as_posix().startswith('http'):
      tempFilePath = Path(tempfile.gettempdir())/filePath.name
      try:
        request.urlretrieve(filePath.as_posix().replace(':/','://'), tempFilePath)
      except Exception:
        success = False
        report += outputString(outputStyle, 'error', 'Could not download file from internet')
        report += outputString(outputStyle, 'error', f'{htmlStr}download-error">website</a>')
        return report, ''
      filePath = tempFilePath
    report += outputString(outputStyle, 'info', f'Check file: {str(filePath)}')
    extension = filePath.suffix[1:]
    pyFile = f'extractor_{extension.lower()}.py'
    if extractorPath is None:
      extractorPath = self.addOnPath
    #start testing
    if (extractorPath/pyFile).is_file():
      report += outputString(outputStyle, 'info', f'Use extractor: {str(extractorPath / pyFile)}.')
    else:
      success = False
      report += outputString(outputStyle, 'error', f'No suitable extractor was found: {pyFile}')
    if success:
      try:
        module  = loadNamedModule(extractorPath, pyFile[:-3])
        plt.clf()
        parameters = tuple(signature(module.use).parameters)
        if (getattr(module, 'PASTA_ELN_EXTRACTOR_API', -1) == 2  and parameters == ('filePath','style','saveFigure')):
          dataHash = sha256File(filePath)
          extractorHash = sha256File(extractorPath/pyFile)

          # assemble callback function with known content
          def saveExtractorFigure(image:Image.Image | None=None) -> None:
            """Save an extractor figure with the current export provenance.
            Args:
              image (Image.Image | None): image to save or process
            """
            saveFigure(Path(saveFig) if saveFig else None, dataHash, extractorHash, image)

          content = module.use(filePath, style, saveExtractorFigure)
        else:
          report += outputString(outputStyle, 'warning',
                                 'Legacy extractor: content was extracted, but marked figure export requires API v2.')
          content = module.use(filePath, style)
        if saveFig:
          return report, content.get('image','')
      except Exception:
        success = False
        report += outputString(outputStyle, 'error', 'Python error in extractor')
        report += outputString(outputStyle, 'error', f'{htmlStr}python-error">website</a>')
        report += outputString(outputStyle, 'error', traceback.format_exc(limit=3))
    if success:
      if 'style' in content:
        possibleDocTypes = [] if self.dataHierarchy is None else [i for i in self.dataHierarchy('', '') if i[0]!='x']
        matches = [i for i in possibleDocTypes if content['style']['main'].startswith(i)]
        if matches or content['style']['main'] in {'', '-'}:
          report += outputString(outputStyle, 'info', 'Style is valid: '+content['style']['main']+'.')
          contentLength = len(json.dumps(content, ensure_ascii=False))
          report += outputString(outputStyle, 'info', f'Extracted size: {contentLength // 1024} kB.')
        else:
          report += outputString(outputStyle, 'error', 'Style does not follow doctype in dataHierarchy.')
      else:
        report += outputString(outputStyle,'error','Style not included in extractor.')
    if success:
      try:
        _ = json.dumps(content, ensure_ascii=False)
      except Exception:
        report += outputString(outputStyle,'error','Extractor reply not json dumpable.')
    if success:
      for meta in ['metaVendor', 'metaUser']:
        if meta in content:
          content[meta], truncated, oldSize, newSize = truncateMetadata(content[meta], self.metadataLimit)
          if truncated:
            report += outputString(outputStyle, 'warning', f'{TRUNC_WARNING} {meta}: {oldSize}->{newSize} characters.')
    if success:
      metaVendor = content.get('metaVendor')
      if isinstance(metaVendor, (dict)):
        try:
          _ = json.dumps(metaVendor, ensure_ascii=False)
          report += outputString(outputStyle, 'info', f'Vendor entries: {len(metaVendor)}.')
        except (TypeError, ValueError):
          success = False
          report += outputString(outputStyle, 'error', 'Some JSON format does not fit in metaVendor')
          report += outputString(outputStyle, 'error', f'{htmlStr}metadata-error">website</a>')
          for key, value in metaVendor.items():
            try:
              _ = json.dumps(value, ensure_ascii=False)
            except (TypeError, ValueError):
              report += outputString(outputStyle, 'error', f'FAIL {key}: {value!r} ({type(value).__name__})')
      else:
        success = False
        report += outputString(outputStyle, 'error',
                               f'metaVendor must be a dictionary not {type(metaVendor).__name__}.')
    if success:
      try:
        _ = json.dumps(content['metaUser'], ensure_ascii=False)
        if not isinstance(content['metaUser'], (dict,list)):
          raise TypeError(' Meta user: wrong type')
        report += 'User entries: '+str(len(content['metaUser']))+'.<br>'
      except Exception:
        report += outputString(outputStyle,'error', 'Some JSON format does not fit in metaUser')
        report += outputString(outputStyle, 'error', f'{htmlStr}metadata-error">website</a>')
        #iterate keys
        for key in content['metaUser']:
          try:
            _ = json.dumps(content['metaUser'][key], ensure_ascii=False)
          except Exception:
            report += outputString(outputStyle,'error',f'FAIL {key}:'+str(content['metaUser'][key])+' type:') + str(type(content['metaUser'][key]))
      if 'image' not in content:
        success = False
        report += outputString(outputStyle,'error','Image does not exist')
    if success and isinstance(content.get('image',''),Image.Image):
      success = False
      report += outputString(outputStyle,'error','Image is a PIL image: not a base64 string')
      report += outputString(outputStyle, 'error', f'{htmlStr}pillow-image">website</a>')
      # print('Encode image via the following: pay attention to jpg/png which is encoded twice\n```')
      # print('from io import BytesIO')
      # print('figfile = BytesIO()')
      # print('image.save(figfile, format="PNG")')
      # print('imageData = base64.b64encode(figfile.getvalue()).decode()')
      # print('image = "data:image/jpg;base64," + imageData')
    if success and isinstance(content.get('image',''), mpaxes._axes.Axes):  # pylint: disable=protected-access
      success = False
      report += outputString(outputStyle,'error','Image is a matplotlib axis: not a base64 string')
      report += outputString(outputStyle, 'error', f'{htmlStr}matplotlib">website</a>')
      # print('**Warning: image is a matplotlib axis: not a svg string')
      # print('  figfile = StringIO()')
      # print('plt.savefig(figfile, format="svg")')
      # print('image = figfile.getvalue()')
    if success and isinstance(content.get('image',''), str):#show content
      size = len(content['image'])
      report += outputString(outputStyle, 'info', f'Image size: {str(size // 1024)} kB.')
    if outputStyle=='print':
      logging.info('Identified metadata %s',content)
    return report, content.get('image','')


# OTHER FUNCTIONS
def saveFigure(path:Path | None, dataHash:str, extractorHash:str, image:Any=None) -> None:
  """Save an extractor figure with PASTA-ELN provenance.
    Args:
      path (Path | None): file path to process
      dataHash (str): SHA-256 hash of the extracted data
      extractorHash (str): SHA-256 hash of the extractor source
      image (Any): image to save or process
  """
  if path is None:
    return
  imageType = path.suffix.lower().removeprefix('.')
  imageType = 'jpg' if imageType == 'jpeg' else imageType
  if imageType not in {'png', 'jpg', 'svg'}:
    raise ValueError(f'Unsupported figure format: {path.suffix}')
  output = BytesIO()
  if image is None:
    plt.savefig(output, format=imageType, dpi=150, bbox_inches='tight')
  else:
    image.save(output, format='JPEG' if imageType == 'jpg' else imageType)
  payload = json.dumps({'PastaELNExport':True, 'dataHash':dataHash, 'extractorHash':extractorHash},
                       ensure_ascii=False, separators=(',', ':'))
  if imageType == 'svg':
    root = ET.fromstring(output.getvalue())
    metadata = ET.Element('{http://www.w3.org/2000/svg}metadata', {'id':PROVENANCE_KEY})
    metadata.text = payload
    root.insert(0, metadata)
    path.write_bytes(ET.tostring(root, encoding='utf-8', xml_declaration=True))
    return
  source = Image.open(BytesIO(output.getvalue()))
  marked = BytesIO()
  if imageType == 'png':
    pngInfo = PngImagePlugin.PngInfo()
    pngInfo.add_text(PROVENANCE_KEY, payload)
    source.save(marked, format='PNG', pnginfo=pngInfo)
  else:
    exif = source.getexif()
    exif[37510] = payload.encode('utf-8')
    source.save(marked, format='JPEG', exif=exif.tobytes())
  path.write_bytes(marked.getvalue())


def isPastaExport(path:Path) -> bool:
  """Return whether a file is a legacy-named or metadata-marked PASTA export.
    Args:
      path (Path): file path to process
    Returns:
      bool: Whether the file is a PASTA-ELN export.
  """
  if '_PastaExport' in path.name:
    return True
  try:
    if path.suffix.lower() == '.svg':
      root = ET.fromstring(path.read_bytes())
      element = root.find("{http://www.w3.org/2000/svg}metadata[@id='PastaELNProvenance']")
      payload = '' if element is None or element.text is None else element.text
    else:
      with Image.open(path) as image:
        payload = image.info.get(PROVENANCE_KEY, '') if path.suffix.lower() == '.png' else \
                  image.getexif().get(37510, b'')
        if isinstance(payload, bytes):
          payload = payload.decode('utf-8')
    return json.loads(payload).get('PastaELNExport') is True
  except (ET.ParseError, OSError, ValueError, json.JSONDecodeError):
    return False


def runExtractorInSubprocess(job:dict[str,Any], connection:Any) -> None:
  """Actually run one extractor in a child process and send the result through a pipe.

  Args:
    job (dict): Extractor job with add-on path, extractor file, data file, and style.
    connection (Any): Multiprocessing pipe connection used to send the result to the parent.
  """
  try:
    plt.clf()
    module = loadNamedModule(job['addOnPath'], job['pyFile'][:-3])
    if getattr(module, 'PASTA_ELN_EXTRACTOR_API', None) == 2:
      def saveExtractorFigure(image:Image.Image | None=None) -> None:
        """Save an extractor figure with the subprocess job provenance.
        Args:
          image (Image.Image | None): image to save or process
        """
        saveFigure(job.get('saveFileName'), job['dataHash'], job['extractorHash'], image)
      content = module.use(job['absFilePath'], job['style'], saveExtractorFigure)
      connection.send({'status':'ok', 'content':content})
    else:
      logging.warning('Legacy extractor %s: update to PASTA_ELN_EXTRACTOR_API = 2 for marked exports.', job['pyFile'])
      content = module.use(job['absFilePath'], job['style'])
      connection.send({'status':'ok', 'content':content})
  except Exception:
    connection.send({'status':'error', 'traceback':traceback.format_exc()})
  finally:
    plt.close('all')
    connection.close()


# HASH FUNCTIONS
def sha256File(path:Path) -> str:
  """Return the SHA-256 digest of raw bytes in a reachable file.
    Args:
      path (Path): file path to process
    Returns:
      str: SHA-256 digest of the file contents.
  """
  if str(path).startswith('http'):
    req = request.Request(path.as_posix().replace(':/','://'), headers={'User-Agent': 'Mozilla/5.0'})
    with request.urlopen(req, timeout=60) as stream:
      return _sha256Stream(stream)
  with open(path.resolve(), 'rb') as stream:
    return _sha256Stream(stream)


def _sha256Stream(stream:BinaryIO) -> str:
  """Calculate a SHA-256 digest without loading the complete file.
    Args:
      stream (BinaryIO): binary stream to hash
    Returns:
      str: SHA-256 digest of the stream contents.
  """
  hasher = sha256()
  while chunk := stream.read(65536):
    hasher.update(chunk)
  return hasher.hexdigest()
