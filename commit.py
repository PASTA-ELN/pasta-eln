#!/usr/bin/python3
import sys, os
from git import Repo

repo = Repo()
lastTag = repo.tags[-1].name

def get_version():
  return lastTag

def newVersion(level=2, message=''):
  version = [int(i) for i in lastTag[1:].split('.')]
  version[level] += 1
  for i in range(level+1,3):
    version[i] = 0
  version = '.'.join([str(i) for i in version])
  os.system('git commit -a -m "'+message+'"')
  tag = repo.create_tag('v'+version, message='Version '+version)
  print('======== Version '+version+' =======')
  remote = repo.remote('origin')
  remote.push(tag)
  return

if __name__=='__main__':
  if len(sys.argv)==1:
    print("**Require more arguments for creating new version 'message' 'level (optionally)' ")
    level = None
  elif len(sys.argv)==2:
    level=2
  else:
    level = int(sys.argv[2])
  if level is not None:
    message = sys.argv[1]
    newVersion(level, message)
