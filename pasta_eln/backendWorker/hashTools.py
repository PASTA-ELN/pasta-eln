""" All hash tools for pasta-eln backend worker """
import logging
import os
from io import BufferedReader
from pathlib import Path
from urllib import request


def generic_hash(path:Path, forceFile:bool=False) -> str:
  """
  Hash an object based on its mode

  inspired by:
  https://github.com/chris3torek/scripts/blob/master/githash.py

  Example implementation:
      result = generic_hash(sys.argv[1])
      print('%s: hash = %s' % (sys.argv[1], result))

  Args:
    path (Path): path
    forceFile (bool): force to get shasum of file and not of link (False for gitshasum)

  Returns:
    string: shasum

  Raises:
    ValueError: shasum of directory not supported
  """
  if str(path).startswith('http'):                                                               #Remote file:
    try:
      req = request.Request(path.as_posix().replace(':/','://'), headers={'User-Agent': 'Mozilla/5.0'})
      with request.urlopen(req, timeout=60) as site:
        meta = site.headers
        size = int(meta.get_all('Content-Length')[0])
        return blob_hash(site, size)
    except Exception:
      logging.error('Could not download content / hashing issue %s',path.as_posix().replace(':/','://'), exc_info=True)
      return ''
  if path.is_dir():
    raise ValueError(f'This seems to be a directory {path.as_posix()}')
  if forceFile and path.is_symlink():
    path = path.resolve()
  shasum = ''
  if path.is_symlink():                                                                #if link, hash the link
    shasum = symlink_hash(path)
  elif path.is_file():                                                                             #Local file
    with open(path, 'rb') as stream:
      shasum = blob_hash(stream, path.stat().st_size)
  return shasum


def symlink_hash(path:Path) -> str:
  """
  Return (as hash instance) the hash of a symlink
  Caller must use hexdigest() or digest() as needed on
  the result

  Args:
    path (string): path to symlink

  Returns:
    string: shasum of link, aka short string
  """
  from hashlib import sha1
  hasher = sha1()
  data = os.readlink(path).encode('utf8', 'surrogateescape')
  hasher.update(b'blob {len(data)}\0')
  hasher.update(data)
  return hasher.hexdigest()


def blob_hash(stream:BufferedReader, size:int) -> str:
  """
  Return (as hash instance) the hash of a blob,
  as read from the given stream

  Args:
    stream (string): content to be hashed
    size (int): size of the content

  Returns:
    string: shasum

  Raises:
    ValueError: size given is not the size of the stream
  """
  from hashlib import sha1
  hasher = sha1()
  hasher.update(f'blob {size}\0'.encode('ascii'))
  nRead = 0
  while True:
    data = stream.read(65536)                                    # read 64K at a time for storage requirements
    if data == b'':
      break
    nRead += len(data)
    hasher.update(data)
  if nRead != size:
    raise ValueError(f'{stream.name}: expected {size} bytes, found {nRead} bytes')
  return hasher.hexdigest()
