#!/usr/bin/python3
import sys, os, subprocess, shutil, json
from pathlib import Path
from unittest import main as mainTest
from urllib.request import urlopen
import configparser
try:
  import requests
  from requests.structures import CaseInsensitiveDict
except:
  pass


def getVersion():
  """
  Get current version number from git-tag

  Returns:
    string: v0.0.0
  """
  result = subprocess.run(['git','tag'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
  versionList= result.stdout.decode('utf-8').strip()
  versionList= [i[1:].replace('b','.') for i in versionList.split('\n')]
  if versionList == ['']:  #default
    return 'v0.0.1'
  versionList.sort(key=lambda s: list(map(int, s.split('.'))))
  lastVersion = versionList[-1]
  if lastVersion.count('.')==3:
    lastVersion = '.'.join(lastVersion.split('.')[:3]) + f'b{lastVersion.split(".")[-1]}'
  return f'v{lastVersion}'

def createContributors():
  """
  curl -L -H "Accept: application/vnd.github+json"  -H "X-GitHub-Api-Version: 2022-11-28"   https://api.github.com/repos/PASTA-ELN/pasta-eln/contributors
  """
  headers:CaseInsensitiveDict[str]= CaseInsensitiveDict()
  headers["Content-Type"] = "application/json"
  resp = requests.get('https://api.github.com/repos/PASTA-ELN/pasta-eln/contributors', headers=headers, timeout=10)
  if not resp.ok:
    print("**ERROR: get not successful",resp.reason)
    return {}
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


def prevVersionsFromPypi(k=15):
  """ Get and print the information of the last k versions on pypi

  Args:
    k (int): number of information
  """
  from urllib.request import urlopen
  import datetime
  import json
  url = "https://pypi.org/pypi/pasta-eln/json"
  response = urlopen(url)
  data = json.loads(response.read())
  releases = list(data['releases'].keys())
  uploadTimes = [i[0]['upload_time'] for i in data['releases'].values()]
  releases = [x for _, x in sorted(zip(uploadTimes, releases))]
  uploadTimes = sorted(uploadTimes)
  print('Version information from pypi')
  for i in range(1, k):
    print(f'  {releases[-i]:8s} was released {(datetime.datetime.now()-datetime.datetime.strptime(uploadTimes[-i],"%Y-%m-%dT%H:%M:%S")).days:3d} days ago')
  return


def newVersion(level=2):
  """
  Create a new version

  Args:
    level (int): which number of the version to increase 0=mayor,1=minor,2=sub
  """
  # last 10 releases from pypi
  url = 'https://pypi.python.org/pypi/pasta-eln/json'
  response = urlopen(url)
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
  version = [int(i) for i in getVersion()[1:].replace('b','.').split('.')]
  #create new version number
  version[level] += 1
  for i in range(level+1,3):
    version[i] = 0
  version = '.'.join([str(i) for i in version])
  reply = input(f'Create version (2.5, 3.1.4b1): [{version}]: ')
  version = version if not reply or len(reply.split('.'))<2 else reply
  print('======== Version '+version+' =======')
  #update python files
  filesToUpdate = {'pasta_eln/__init__.py':'__version__ = ',
                   'docs/source/conf.py':'version = '}
  for path in filesToUpdate:
    with open(path, encoding='utf-8') as fIn:
      fileOld = fIn.readlines()
    fileNew = []
    for line in fileOld:
      line = line[:-1]  #only remove last char, keeping front part
      if line.startswith(filesToUpdate[path]):
        line = filesToUpdate[path]+'"'+version+'"'
      fileNew.append(line)
    with open(path,'w', encoding='utf-8') as fOut:
      fOut.write('\n'.join(fileNew)+'\n')
  #execute git commands
  os.system(f'git pull')
  os.system(f'git tag -a v{version} -m "Version {version}; see CHANGELOG for details"')
  #create CHANGELOG / Contributor-list
  with open(Path.home()/'.ssh'/'github.token', 'r', encoding='utf-8') as fIn:
    token = fIn.read().strip()
  os.system("github_changelog_generator -u PASTA-ELN -p pasta-eln -t "+token)
  createContributors()
  addition = input('\n\nWhat do you want to add to the push message (do not use \' or \")? ')
  os.system(f'git commit -a -m "updated changelog; {addition}"')
  #push and publish
  print('\n\nWill bypass rule violation\n\n')
  os.system(f'git push')
  os.system(f'git push origin v{version}')
  return


def createRequirementsFile():
  """
  Create a requirements.txt file from the setup.cfg information
  """
  print('Start creating requirement files')
  config = configparser.ConfigParser()
  config.read('setup.cfg')
  requirements = config['options']['install_requires'].split('\n')
  requirements = [i.replace(' ==','==') if '==' in i else i for i in requirements]
  # Linux
  requirementsLinux = [i for i in requirements if i!='' and 'Windows' not in i]
  with open('requirements-linux.txt','w', encoding='utf-8') as req:
    req.write('#This file is autogenerated by commit.py from setup.cfg. Change content there\n')
    req.write('\n'.join(requirementsLinux))
  # Windows
  requirementsWindows = [i for i in requirements if i!='']
  requirementsWindows = [i.split(';')[0] if 'Windows' in i else i for i in requirementsWindows]
  with open('requirements-windows.txt','w', encoding='utf-8') as req:
    req.write('#This file is autogenerated by commit.py from setup.cfg. Change content there\n')
    req.write('\n'.join(requirementsWindows))
  return


def runTests():
  """
  run unit-tests: can only work if all add-ons and dependencies are fulfilled

  Cannot be an action, since dependencies are partly private
  """
  print('Start running tests')
  tests = [i for i in os.listdir('tests') if i.endswith('.py') and i.startswith('test_')]
  for fileI in sorted(tests):
    result = subprocess.run(['pytest','-s','--no-skip',f'tests/{fileI}'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
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


def copyAddOns():
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


def sourcery():
  """ Verify code with sourcery """
  print('------------------ Sourcery -----------------')
  os.system('sourcery review pasta_eln/')
  print('---------------- end sourcery ---------------')
  return


if __name__=='__main__':
  runTests()
  sourcery
  copyAddOns()
  createRequirementsFile()
  #do update
  level = 2 if len(sys.argv)==1 else int(sys.argv[1])
  if input('Continue: only "y" continues. ') == 'y':
    newVersion(level)
  print("\n================================\nPush this and publish add-ons\n================================")
