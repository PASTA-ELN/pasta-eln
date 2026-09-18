"""Extract data referenced by a Nextcloud pointer file."""
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin
from xml.etree import ElementTree

import requests

from pasta_eln.configuration_file import loadConfiguration
from pasta_eln.misc_tools import loadNamedModule
from testsComplicated.nextcloud_common import readNclink


MAX_AUTOMATIC_SIZE = 100 * 1024 * 1024  #100MB
DAV = '{DAV:}'
OC = '{http://owncloud.org/ns}'


def use(filePath:Path, style:dict[str,Any], saveFileName:str|None=None) -> dict[str,Any]:
  """Resolve a Nextcloud pointer and extract its remote file.
  Args:
    filePath (Path): `.nclink` pointer
    style (dict[str, Any]): extraction recipe
    saveFileName (str | None): optional extracted-image destination
  Returns:
    dict[str, Any]: extractor result and Nextcloud provenance
  """
  # find credentials by iterating upwards in the directory structure
  credentialsPath = next((directory/'.nextcloud_credentials.json' for directory in filePath.parents
                          if (directory/'.nextcloud_credentials.json').is_file()), None)
  if credentialsPath is None:
    raise FileNotFoundError(f'No .nextcloud_credentials.json found for {filePath}')
  credentials = loadConfiguration(credentialsPath)
  # get account
  link = readNclink(filePath)
  account = json.loads(credentials['addOnParameter']['nextcloud'][link['instance']])

  # start a http session and get userID
  session = requests.Session()
  session.auth = (account['loginName'], account['appPassword'])
  baseURL = account['url'].rstrip('/')
  response = session.get(f'{baseURL}/ocs/v1.php/cloud/user', params={'format':'json'}, timeout=30,
                         headers={'OCS-APIRequest':'true', 'Accept':'application/json'})
  response.raise_for_status()
  userID = str(response.json()['ocs']['data']['id'])

  # find all files that have that fileId, but it should only be one
  query = f'{queryStr1}{quote(userID, safe='')}{queryStr2}{link['fileId']}{queryStr3}'
  response = session.request('SEARCH', f'{baseURL}/remote.php/dav/', data=query.encode('utf-8'),
                             headers={'Content-Type':'application/xml'}, timeout=60)
  response.raise_for_status()
  remote:dict[str,Any]|None = None
  for item in ElementTree.fromstring(response.content).findall(f'{DAV}response'):
    prop = item.find(f'.//{DAV}prop')
    href = item.findtext(f'{DAV}href')
    if prop is not None and href and prop.findtext(f'{OC}fileid') == str(link['fileId']):
      size = prop.findtext(f'{DAV}getcontentlength')
      remote = {'path':href, 'url':urljoin(f'{baseURL}/', href),
                'size':int(size) if size is not None else -1,
                'contentType':prop.findtext(f'{DAV}getcontenttype') or '',
                'etag':prop.findtext(f'{DAV}getetag') or ''}
      break
  if remote is None:
    raise FileNotFoundError(f'Nextcloud file ID {link["fileId"]} is not accessible')

  current = {'nextcloudETag':remote['etag'], 'nextcloudContentType':remote['contentType'],
             'nextcloudSize':remote['size']}
  changed = [key for key, value in current.items() if value != link[key]]
  if changed:
    raise ValueError(f'Nextcloud file changed: {", ".join(changed)} to {current}')

  # create metaVendor
  metaVendor = {'nextcloudInstance':link['instance'], 'nextcloudFileId':link['fileId'],
                'nextcloudPath':remote['path'], 'nextcloudETag':remote['etag'],
                'nextcloudContentType':remote['contentType'], 'nextcloudSize':remote['size']}
  result:dict[str,Any] = {'general':[('name',link['name'])], 'style':style,
                          'metaVendor':metaVendor, 'metaUser':{}}
  if remote['size'] < 0 or remote['size'] > MAX_AUTOMATIC_SIZE:
    return result

  # copy local and run extractor.use()
  with tempfile.TemporaryDirectory() as temporaryDirectory:
    localPath = Path(temporaryDirectory)/Path(link['name']).name
    response = session.get(remote['url'], stream=True, timeout=60)
    response.raise_for_status()
    with localPath.open('wb') as stream:
      for chunk in response.iter_content(1024*1024):
        if chunk:
          stream.write(chunk)
    extractorPath = Path(__file__).parent/f'extractor_{localPath.suffix[1:].lower()}.py'
    if extractorPath.is_file() and extractorPath != Path(__file__):
      extractor = loadNamedModule(extractorPath.parent, extractorPath.stem)
      extracted = extractor.use(localPath, style, saveFileName)
      extracted.setdefault('metaVendor', {}).update(result['metaVendor'])
      extracted.setdefault('metaUser', {})
      extracted.setdefault('general', []).append(('name',link['name']))
      result = extracted
  return result


queryStr1=('<?xml version="1.0" encoding="UTF-8"?><d:searchrequest xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns">'
           '<d:basicsearch><d:select><d:prop><oc:fileid/><d:displayname/><d:getcontentlength/><d:getcontenttype/>'
           '<d:getetag/></d:prop></d:select><d:from><d:scope><d:href>/files/')
queryStr2=('</d:href><d:depth>infinity</d:depth></d:scope></d:from><d:where><d:eq><d:prop><oc:fileid/></d:prop>'
           '<d:literal>')
queryStr3='</d:literal></d:eq></d:where></d:basicsearch></d:searchrequest>'
