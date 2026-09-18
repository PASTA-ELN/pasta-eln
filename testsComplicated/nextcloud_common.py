"""Shared functions for Nextcloud pointer files."""
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urljoin
from xml.etree import ElementTree

import requests

NLINK_FORMAT = 'pasta-nextcloud-link/1'
DAV = '{DAV:}'
OC = '{http://owncloud.org/ns}'


def writeNclink(directory:Path, instance:str, targetFile:dict[str,Any]) -> Path:
  """Write a deterministic Nextcloud pointer file.
  Args:
    directory (Path): directory receiving the pointer
    instance (str): alias of the Nextcloud instance
    targetFile (dict[str, Any]): selected file identity and Nextcloud verification metadata
  Returns:
    Path: created pointer path
  """
  name = Path(targetFile['name']).name
  content = {'format':NLINK_FORMAT, 'instance':instance, 'fileId':targetFile['fileId'], 'name':name,
             'nextcloudETag':targetFile['nextcloudETag'],
             'nextcloudContentType':targetFile['nextcloudContentType'],
             'nextcloudSize':targetFile['nextcloudSize']}
  linkPath = directory/f'{name}.nclink'
  linkPath.write_text(json.dumps(content, ensure_ascii=False, sort_keys=True)+'\n', encoding='utf-8')
  return linkPath


def readNclink(linkPath:Path) -> dict[str,Any]:
  """Read and identify a Nextcloud pointer file.
  Args:
    linkPath (Path): pointer file
  Returns:
    dict[str, Any]: pointer content
  """
  content:dict[str,Any] = json.loads(linkPath.read_text(encoding='utf-8'))
  if content.get('format') != NLINK_FORMAT:
    raise ValueError(f'Unsupported Nextcloud pointer format: {content.get("format", "missing")}')
  required = {'instance','fileId','name','nextcloudETag','nextcloudContentType','nextcloudSize'}
  if missing:= required-content.keys():
    raise ValueError(f'Missing Nextcloud pointer fields: {", ".join(sorted(missing))}')
  return content


class NextcloudBrowser:
  """Browse and select files from one authenticated Nextcloud account."""

  def __init__(self, account:dict[str,Any]) -> None:
    """Connect to a Nextcloud account at its root folder.

    Args:
      account (dict[str, Any]): URL, login name, and app password.
    """
    self.session = requests.Session()
    self.session.auth = (account['loginName'], account['appPassword'])
    self.baseURL = account['url'].rstrip('/')
    response = self.session.get(f'{self.baseURL}/ocs/v1.php/cloud/user', params={'format':'json'}, timeout=30,
                                headers={'OCS-APIRequest':'true', 'Accept':'application/json'})
    response.raise_for_status()
    userID = str(response.json()['ocs']['data']['id'])
    self.currentPath = f'/remote.php/dav/files/{quote(userID, safe="")}/'


  def listFolder(self) -> list[dict[str,Any]]:
    """List the files and folders in the current Nextcloud folder.

    Returns:
      list[dict[str, Any]]: child entries with stable file metadata.
    """
    query = ('<?xml version="1.0" encoding="UTF-8"?><d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns">'
             '<d:prop><d:displayname/><d:resourcetype/><d:getcontentlength/><d:getcontenttype/><d:getetag/>'
             '<oc:fileid/></d:prop></d:propfind>')
    response = self.session.request('PROPFIND', urljoin(f'{self.baseURL}/', self.currentPath), data=query.encode('utf-8'),
                                    headers={'Content-Type':'application/xml', 'Depth':'1'}, timeout=60)
    response.raise_for_status()
    entries:list[dict[str,Any]] = []
    for item in ElementTree.fromstring(response.content).findall(f'{DAV}response'):
      href = item.findtext(f'{DAV}href')
      prop = item.find(f'./{DAV}propstat/{DAV}prop')
      if href is None or prop is None:
        continue
      path = unquote(href)
      if path.rstrip('/') == self.currentPath.rstrip('/'):
        continue
      isFolder = prop.find(f'{DAV}resourcetype/{DAV}collection') is not None
      if isFolder:
        path = f'{path.rstrip("/")}/'
      entries.append({'name':prop.findtext(f'{DAV}displayname') or path.rstrip('/').split('/')[-1],
                      'fileId':prop.findtext(f'{OC}fileid') or '', 'path':path,
                      'parentPath':f'{path.rstrip("/").rsplit("/", 1)[0]}/', 'isFolder':isFolder,
                      'nextcloudETag':prop.findtext(f'{DAV}getetag') or '',
                      'nextcloudContentType':prop.findtext(f'{DAV}getcontenttype') or '',
                      'nextcloudSize':int(prop.findtext(f'{DAV}getcontentlength') or -1)})
    return entries


  def openFolder(self, name:str) -> None:
    """Enter one child folder of the current folder.

    Args:
      name (str): displayed folder name.
    """
    folder = next(item for item in self.listFolder() if item['name'] == name and item['isFolder'])
    self.currentPath = folder['path']


  def findFile(self, fileID:str) -> dict[str,Any]:
    """Find one accessible file by stable Nextcloud file ID.

    Args:
      fileID (str): Nextcloud file ID.

    Returns:
      dict[str, Any]: file metadata; its parent becomes the current folder.
    """
    userID = unquote(self.currentPath.split('/')[4])
    query = ('<?xml version="1.0" encoding="UTF-8"?><d:searchrequest xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns">'
             '<d:basicsearch><d:select><d:prop><oc:fileid/><d:displayname/><d:getcontentlength/><d:getcontenttype/>'
             '<d:getetag/></d:prop></d:select><d:from><d:scope><d:href>/files/'
             f'{quote(userID, safe="")}</d:href><d:depth>infinity</d:depth></d:scope></d:from><d:where><d:eq>'
             '<d:prop><oc:fileid/></d:prop><d:literal>'
             f'{fileID}</d:literal></d:eq></d:where></d:basicsearch></d:searchrequest>')
    response = self.session.request('SEARCH', f'{self.baseURL}/remote.php/dav/', data=query.encode('utf-8'),
                                    headers={'Content-Type':'application/xml'}, timeout=60)
    response.raise_for_status()
    for item in ElementTree.fromstring(response.content).findall(f'{DAV}response'):
      href = item.findtext(f'{DAV}href')
      prop = item.find(f'./{DAV}propstat/{DAV}prop')
      if href is None or prop is None or prop.findtext(f'{OC}fileid') != str(fileID):
        continue
      path = unquote(href)
      self.currentPath = f'{path.rsplit("/", 1)[0]}/'
      return {'name':prop.findtext(f'{DAV}displayname') or path.split('/')[-1], 'fileId':str(fileID), 'path':path,
              'parentPath':self.currentPath, 'isFolder':False,
              'nextcloudETag':prop.findtext(f'{DAV}getetag') or '',
              'nextcloudContentType':prop.findtext(f'{DAV}getcontenttype') or '',
              'nextcloudSize':int(prop.findtext(f'{DAV}getcontentlength') or -1)}
    raise FileNotFoundError(f'Nextcloud file ID {fileID} is not accessible')


  def selectFiles(self, names:list[str]) -> list[dict[str,Any]]:
    """Select files from the current folder.

    Args:
      names (list[str]): displayed names of files in the current folder.

    Returns:
      list[dict[str, Any]]: selected file metadata.
    """
    entries = {item['name']:item for item in self.listFolder() if not item['isFolder']}
    return [entries[name] for name in names]


def writeNclinks(directory:Path, instance:str, targetFiles:list[dict[str,Any]]) -> list[Path]:
  """Write one Nextcloud pointer for each selected file.

  Args:
    directory (Path): directory receiving the pointers.
    instance (str): alias of the Nextcloud instance.
    targetFiles (list[dict[str, Any]]): selected file metadata.

  Returns:
    list[Path]: created pointer paths.
  """
  return [writeNclink(directory, instance, targetFile) for targetFile in targetFiles]
