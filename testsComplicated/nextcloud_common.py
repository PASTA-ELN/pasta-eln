"""Shared functions for Nextcloud pointer files."""
import json
from pathlib import Path
from typing import Any

NLINK_FORMAT = 'pasta-nextcloud-link/1'


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
