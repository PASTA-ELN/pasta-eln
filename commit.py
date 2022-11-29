#!/usr/bin/python3
import sys, os, subprocess

def get_version():
  result = subprocess.run(['git','tag'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
  versionList= result.stdout.decode('utf-8').strip()
  versionList= [i[1:] for i in versionList.split('\n')]
  versionList.sort(key=lambda s: list(map(int, s.split('.'))))
  return 'v'+versionList[-1]

def newVersion(level=2, message=''):
  #get old version number
  version = [int(i) for i in get_version()[1:].split('.')]
  #create new version number
  version[level] += 1
  for i in range(level+1,3):
    version[i] = 0
  version = '.'.join([str(i) for i in version])
  print('======== Version '+version+' =======')
  #update __init__.py
  with open('pasta_eln/__init__.py', encoding='utf-8') as fIn:
    fileOld = fIn.readlines()
  fileNew = []
  for line in fileOld:
    line = line[:-1]  #only remove last char, keeping front part
    if line.startswith('__version__ = '):
      line = '__version__ = "'+version+'"'
    fileNew.append(line)
  with open('pasta_eln/__init__.py','w', encoding='utf-8') as fOut:
    fOut.write('\n'.join(fileNew)+'\n')
  #execute git commands
  os.system('git commit -a -m "'+message+'"')
  os.system('git tag -a v'+version+' -m "Version '+version+'"')
  os.system('git push origin v'+version)
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
