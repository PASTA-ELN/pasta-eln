#!/usr/bin/python3
""" Script to run when releasing a new version to pypi """
from __future__ import annotations
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

try:
  import requests
  from requests.structures import CaseInsensitiveDict
except Exception:
  pass


def getVersion() -> str:
  """
  Get current version number from git-tag

  Returns:
    string: v0.0.0
  """
  result = subprocess.run(['git','tag'], capture_output=True, check=False)
  versionStr = result.stdout.decode('utf-8').strip()
  versionList= [i[1:].replace('b','.') for i in versionStr.split('\n')]
  if versionList == ['']:  #default
    return 'v0.0.1'
  versionList.sort(key=lambda s: list(map(int, s.split('.'))))
  lastVersion = versionList[-1]
  if lastVersion.count('.')==3:
    lastVersion = '.'.join(lastVersion.split('.')[:3]) + f'b{lastVersion.split(".")[-1]}'
  return f'v{lastVersion}'

def createContributors() -> None:
  """
  curl -L -H "Accept: application/vnd.github+json"  -H "X-GitHub-Api-Version: 2022-11-28"   https://api.github.com/repos/PASTA-ELN/pasta-eln/contributors
  """
  headers:CaseInsensitiveDict[str]= CaseInsensitiveDict()
  headers['Content-Type'] = 'application/json'
  resp = requests.get('https://api.github.com/repos/PASTA-ELN/pasta-eln/contributors', headers=headers, timeout=10)
  if not resp.ok:
    print('**ERROR: get not successful',resp.reason)
    return
  with open('CONTRIBUTORS.md', 'w', encoding='utf-8') as fOut:
    fOut.write('# Contributors \n## Code contributors\nThe following people have contributed code to this project:\n')
    fOut.write('<table border="2"><tr>\n')
    for idx, user in enumerate(json.loads(resp.text)):
      userName = user['login']
      link     = user['html_url']
      avatar   = user['avatar_url']
      fOut.write(f'<td style="text-align: center"><a href="{link}"><img src="{avatar}" /><br>{userName}</a></td>')
      if idx%3==2:
        fOut.write('</tr>\n')
    fOut.write('<td></td></tr>\n</table>')
    fOut.write('\n\n## Support contributors \n The following people contributed in the discussions:\n')
    fOut.write('- Hanna Tsybenko\n')
    fOut.write('- Ruth Schwaiger\n')
    fOut.write('\n\n## Software projects\nMost of the file-layout and the integration of webservices follows the example of datalad and datalad-gooey')
    fOut.write('https://github.com/datalad. We thank those developers for their work and contribution to free software.')
  return


def prevVersionsFromPypi(k:int=15) -> None:
  """ Get and print the information of the last k versions on pypi

  Args:
    k (int): number of information
  """
  url = 'https://pypi.org/pypi/pasta-eln/json'
  with urlopen(url) as response:
    data = json.loads(response.read())
  releases = list(data['releases'].keys())
  uploadTimes = [i[0]['upload_time'] for i in data['releases'].values()]
  releases = [x for _, x in sorted(zip(uploadTimes, releases))]
  uploadTimes = sorted(uploadTimes)
  print('Version information from pypi')
  for i in range(1, k):
    print(f'  {releases[-i]:8s} was released {(datetime.datetime.now()-datetime.datetime.strptime(uploadTimes[-i],"%Y-%m-%dT%H:%M:%S")).days:3d} days ago')
  return


def newVersion(level:int=2) -> None:
  """
  Create a new version

  Args:
    level (int): which number of the version to increase 0=mayor,1=minor,2=sub
  """
  # last 10 releases from pypi
  url = 'https://pypi.python.org/pypi/pasta-eln/json'
  with urlopen(url) as response:
    data_json = json.loads(response.read())
  labels, dates = [], []
  for release in data_json['releases']:
    labels.append(release)
    dates.append(data_json['releases'][release][0]['upload_time'])
  print('Latest versions on Pypi')
  print('  '+', '.join([x for _, x in sorted(zip(dates, labels))][-10:]))
  print('Create new version...')
  prevVersionsFromPypi()
  #get old version number
  versionList = [int(i) for i in getVersion()[1:].replace('b','.').split('.')]
  #create new version number
  versionList[level] += 1
  for i in range(level+1,3):
    versionList[i] = 0
  version = '.'.join([str(i) for i in versionList])
  reply = input(f'Create version (2.5, 3.1.4b1): [{version}]: ')
  version = version if not reply or len(reply.split('.'))<2 else reply
  print(f'======== Version {version} =======')
  #update python files
  filesToUpdate = {'pasta_eln/__init__.py':'__version__ = ',
                   'docs/source/conf.py':'version = '}
  for path,text in filesToUpdate.items():
    with open(path, encoding='utf-8') as fIn:
      fileOld = fIn.readlines()
    fileNew = []
    for line in fileOld:
      line = line[:-1]  #only remove last char, keeping front part
      if line.startswith(text):
        line = f"{text}'{version}'"
      fileNew.append(line)
    with open(path,'w', encoding='utf-8') as fOut:
      fOut.write('\n'.join(fileNew)+'\n')
  #execute git commands
  os.system('git pull')
  os.system(f'git tag -a v{version} -m "Version {version}; see CHANGELOG for details"')
  #create CHANGELOG / Contributor-list
  with open(Path.home()/'.ssh'/'github.token', encoding='utf-8') as fIn:
    token = fIn.read().strip()
  os.system(f'github_changelog_generator -u PASTA-ELN -p pasta-eln -t {token}')
  createContributors()
  addition = input('\n\nWhat do you want to add to the push message (do not use \' or \")? ')
  os.system(f'git commit -a -m "updated changelog; {addition}"')
  #push and publish
  print('\n\nWill bypass rule violation\n\n')
  os.system('git push')
  os.system(f'git push origin v{version}')
  return


def createRequirementsFile() -> None:
  """
  Create a requirements.txt file from the setup.cfg information
  - not done anymore automatically
  - should be manually executed for every 0.1 release, every 6month - 1year
  - go to new versions of all libs
  - do testing of pasta afterwards; use beta versions for that
  - do a diff of the resulting requirements files to ensure that at least the pyside versions are identical

  Commands:
  - pip-compile -o requirements-linux.txt
  - copy files together
  - diff requirements-linux.txt requirements-windows.txt
  """
  print('Requirements.txt file creation skipped.\n'
        '- manually create Linux an Windows versions for every 0.1 release\n'
        '- read releaseVersion for instructions')
  # print('Start creating requirement file for linux')
  # os.system('pip-compile -o requirements-linux.txt')
  # print('Start creating requirement file for windows')
  # config = configparser.ConfigParser()
  # config.read('setup.cfg')
  # requirements = config['options']['install_requires'].split('\n')
  # requirements = [i.replace(' ==','==') if '==' in i else i for i in requirements]
  # # Linux
  # requirementsLinux = [i for i in requirements if i!='' and 'Windows' not in i]
  # with open('requirements-linux.txt','w', encoding='utf-8') as req:
  #   req.write('#This file is autogenerated by commit.py from setup.cfg. Change content there\n')
  #   req.write('\n'.join(requirementsLinux))
  # # Windows
  # requirementsWindows = [i for i in requirements if i!='']
  # requirementsWindows = [i.split(';')[0] if 'Windows' in i else i for i in requirementsWindows]
  # with open('requirements-windows.txt','w', encoding='utf-8') as req:
  #   req.write('#This file is autogenerated by commit.py from setup.cfg. Change content there\n')
  #   req.write('\n'.join(requirementsWindows))
  return


def runTests() -> None:
  """
  run unit-tests: can only work if all add-ons and dependencies are fulfilled

  Cannot be an action, since dependencies are partly private
  """
  print('Start running tests')
  tests = [i for i in os.listdir('tests') if i.endswith('.py') and i.startswith('test_')]
  for fileI in sorted(tests):
    result = subprocess.run(['pytest','-s','--no-skip',f'tests/{fileI}'],
                            capture_output=True, check=False)
    success = result.stdout.decode('utf-8').count('*** DONE WITH VERIFY ***')
    if success==1:
      success += result.stdout.decode('utf-8').count('**ERROR')
      success -= result.stdout.decode('utf-8').count('**ERROR Red: FAILURE and ERROR')
      for badWord in ['**ERROR got a file','FAILED','ModuleNotFoundError']:
        success += result.stdout.decode('utf-8').count(badWord)
    if success==0:
      print(f"  success: Python unit test {fileI}")
    else:
      print(f"  FAILED: Python unit test {fileI}")
      print(f"    run: 'pytest -s tests/{fileI}' and check logFile")
      print(f"\n---------------------------\n{result.stdout.decode('utf-8')}\n---------------------------\n")
  print('**WARNING Start running complicated tests: SKIP FOR NOW')
  # tests = [i for i in os.listdir('testsComplicated') if i.endswith('.py') and i.startswith('test_')]
  # for fileI in sorted(tests):
  #   result = subprocess.run(['pytest','-s','--no-skip','testsComplicated/'+fileI],
  #                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
  #   success = result.stdout.decode('utf-8').count('*** DONE WITH VERIFY ***')
  #   if success==1:
  #     success += result.stdout.decode('utf-8').count('**ERROR')
  #     success -= result.stdout.decode('utf-8').count('**ERROR Red: FAILURE and ERROR')
  #     for badWord in ['**ERROR got a file','FAILED','ModuleNotFoundError']:
  #       success += result.stdout.decode('utf-8').count(badWord)
  #   if success==1:
  #     print("  success: Python unit test "+fileI)
  #   else:
  #     print("  FAILED: Python unit test "+fileI)
  #     print(f"    run: 'pytest -s testsComplicated/{fileI}' and check logFile")
  #     print(f"\n---------------------------\n{result.stdout.decode('utf-8')}\n---------------------------\n")
  return


def copyAddOns() -> None:
  """
  Copy add-ons from main location to distribution
  """
  print('Start copying add-ons')
  basePath = 'pasta_eln/AddOns'
  skipFiles= ['extractor_csv.py', 'extractor_jpg.py']
  for fileI in os.listdir(basePath):
    if fileI in skipFiles or not fileI.endswith('.py'):
      continue
    shutil.copy(f'../AddOns/{fileI}', f'{basePath}/{fileI}')
  return


def runSourceVerification() -> None:
  """ Verify code with a number of tools:
  Order: first those that change code automatically, then those that require manual inspection
  - pre-commit (which has a number of submodules included)
  - isort
  - pylint
  - mypy
  - sourcery
  """
  tools = {'pre-commit': 'pre-commit run --all-files',
           'isort'     : 'isort pasta_eln/',
           'pylint'    : 'pylint pasta_eln/',
           'mypy'      : 'mypy --no-warn-unused-ignores pasta_eln/',
           'sourcery'  : 'sourcery review pasta_eln/',
           'isort2'    : 'isort releaseVersion.py',
           'pylint2'   : 'pylint releaseVersion.py',
           'mypy2'     : 'mypy --no-warn-unused-ignores releaseVersion.py',
           'sourcery2' : 'sourcery review releaseVersion.py'}
  for label, cmd in tools.items():
    print(f'------------------ start {label} -----------------')
    os.system(cmd)
    print(f'---------------- end {label} ---------------')
  return


if __name__=='__main__':
  #run tests
  runTests()
  runSourceVerification()
  createRequirementsFile()
  versionLevel = 2 if len(sys.argv)==1 else int(sys.argv[1])
  #do update
  if input('Continue: only "y" continues. ') == 'y':
    newVersion(versionLevel)
