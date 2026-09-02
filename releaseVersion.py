#!/usr/bin/python3
""" Script to run when releasing a new version to pypi """
from __future__ import annotations
import datetime
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tokenize
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
  try:
    headers:CaseInsensitiveDict[str]= CaseInsensitiveDict()
    headers['Content-Type'] = 'application/json'
    resp = requests.get('https://api.github.com/repos/PASTA-ELN/pasta-eln/contributors', headers=headers, timeout=10)
    if not resp.ok:
      print('**ERROR: get not successful',resp.reason)
      return
    with open('CONTRIBUTORS.md', 'w', encoding='utf-8') as fOut:
      fOut.write('# Contributors\n## Code contributors\nThe following people have contributed code to this project:\n')
      fOut.write('<table border="2"><tr>\n')
      for idx, user in enumerate(json.loads(resp.text)):
        userName = user['login']
        link     = user['html_url']
        avatar   = user['avatar_url']
        fOut.write(f'<td style="text-align: center"><a href="{link}"><img src="{avatar}" /><br>{userName}</a></td>')
        if idx%3==2:
          fOut.write('</tr>\n')
      fOut.write('<td></td></tr>\n</table>')
      fOut.write('\n\n## Support contributors\n The following people contributed in the discussions:\n')
      fOut.write('- Hanna Tsybenko\n')
      fOut.write('- Ruth Schwaiger\n')
      fOut.write('\n\n## Software projects\nMost of the file-layout and the integration of webservices follows the example of datalad and datalad-gooey')
      fOut.write('https://github.com/datalad. We thank those developers for their work and contribution to free software.\n')
  except Exception:
    print('**Warning: could not create list of contributors; perhaps no internet connection. Keep old.')
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
  k = min(k, len(releases)+1)
  for i in range(1, k):
    print(f'  {releases[-i]:8s} was released {(datetime.datetime.now()-datetime.datetime.strptime(uploadTimes[-i],"%Y-%m-%dT%H:%M:%S")).days:3d} days ago')
  return


def createChangelog(version: str) -> Path:
  """Write a Git-based changelog draft for the new stable release ``version``.

  - The previous stable release is determined from the merged Git tags and  defines the beginning of the commit range.
  - The current ``HEAD`` defines the release source commit and the end of that range.
  - Beta-version tags are ignored.

  Args:
    version: Release currently being prepared.

  Returns:
    The path to the generated Markdown draft.
  """
  stableTags = [tag for tag in subprocess.run(['git', '--no-pager', 'tag', '--merged', 'HEAD', '--list', 'v*'],
                                                capture_output=True, text=True, check=True).stdout.splitlines()
                if re.fullmatch(r'v\d+\.\d+\.\d+', tag) and tag != f'v{version}']
  stableTags.sort(key=lambda tag: tuple(int(part) for part in tag[1:].split('.')))
  if not stableTags:
    raise RuntimeError('Cannot create a stable changelog without a previous stable tag.')
  previousTag = stableTags[-1]
  previousHash = subprocess.run(['git', 'rev-parse', previousTag], capture_output=True, text=True, check=True).stdout.strip()
  releaseHash = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()

  commitText = subprocess.run(['git', '--no-pager', 'log', '--reverse', '--format=%H%x1f%s%x1f%b%x1e', f'{previousTag}..{releaseHash}'],
                              capture_output=True, text=True, check=True).stdout
  commits = []
  for record in commitText.split('\x1e'):
    if not record.strip():
      continue
    commitHash, subject, body = record.strip().split('\x1f', 2)
    changedFiles = subprocess.run(['git', 'diff-tree', '--no-commit-id', '--name-status', '-r', commitHash],
                                  capture_output=True, text=True, check=True).stdout.strip()
    commits.append(f'- {subject} ([`{commitHash[:8]}`](https://github.com/PASTA-ELN/pasta-eln/commit/{commitHash}))\n'
                   '  Commit body:\n'
                   f'  {body.replace(chr(10), f"{chr(10)}  ")}\n'
                   '  Changed files:\n'
                   f'  {changedFiles.replace(chr(10), f"{chr(10)}  ")}')
  if not commits:
    raise RuntimeError(f'No commits found between {previousTag} and {releaseHash}.')
  draftPath = Path(f'CHANGELOG_DRAFT_v{version}.md')
  draftPath.write_text(
      f'## [v{version}](https://github.com/PASTA-ELN/pasta-eln/tree/v{version}) '
      f'({datetime.date.today().isoformat()})\n\n'
      f'**Release source commit:** `{releaseHash}`\n'
      f'**Previous stable release:** `{previousTag}` (`{previousHash}`)\n\n'
      + '\n'.join(commits) + '\n', encoding='utf-8')
  return draftPath


LLM_INSTRUCTION = """
Rewrite this Git-generated changelog draft into polished release notes.

The draft describes the new PASTA-ELN release. Preserve exactly:

- the release heading and date;
- the “Release source commit” line;
- the “Previous stable release” line;
- the commit link and hash for every change retained in the release notes. Internal-only commits may be omitted.

Improve only the release-note content:

- group related commits under concise headings such as “New features”, “Improvements”, “Bug fixes”, and “Maintenance”;
- rewrite commit subjects into clear, user-facing descriptions;
- combine related commits where appropriate;
- remove purely internal or unhelpful commits if they do not represent a user-visible change;
- do not invent functionality, behavior, or reasons not supported by the commit subjects;
- do not mention GitHub issues unless they are already present in the input;
- retain commit links for all summarized changes;
- treat “Commit body” and “Changed files” as source context only; do not copy those labels into the published release notes;
- return valid Markdown only.

Exclude internal development work from the release notes. Do not mention:

- code-quality improvements, type checking, linting, spelling, formatting, or pre-commit checks;
- CI, test-only, or build-pipeline changes;
- refactoring or application-structure changes;
- removal of obsolete widgets, files, or other internal cleanup.

If a commit contains both internal work and a user-visible change, describe only the user-visible change. Omit a commit entirely when it has no meaningful user-facing effect.

Output the complete replacement file, including the preserved metadata.
"""


def newVersion(level:int=2) -> None:
  """
  Create a new version

  Args:
    level (int): which number of the version to increase 0=mayor,1=minor,2=sub
  """
  print('Create new version...')
  prevVersionsFromPypi()
  #get old version number
  currentVersion = getVersion()[1:]
  # A beta version does not define a release boundary. Its base version is
  # therefore the default stable version proposed by the release script.
  if 'b' in currentVersion:
    version = currentVersion.split('b', 1)[0]
  else:
    versionList = [int(i) for i in currentVersion.split('.')]
    versionList[level] += 1
    for i in range(level+1,3):
      versionList[i] = 0
    version = '.'.join([str(i) for i in versionList])
  reply = input(f'Create version (2.5, 3.1.4b1): [{version}]: ')
  version = version if not reply or len(reply.split('.'))<2 else reply
  print(f'======== Version {version} =======')
  #git commands and update python files
  subprocess.run(['git', 'pull'], check=True)
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
  changeCheck = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--'], check=False)
  if changeCheck.returncode == 1:
    subprocess.run(['git', 'commit', '-a', '-m', 'update version numbers'], check=True)
  elif changeCheck.returncode != 0:
    raise subprocess.CalledProcessError(changeCheck.returncode, changeCheck.args)
  # must not add entries to the changelog.
  if re.fullmatch(r'\d+\.\d+\.\d+', version):
    draftPath = createChangelog(version)
    print(f'Changelog draft written to {draftPath}. Replace it with the reviewed changelog before continuing.')
    print(LLM_INSTRUCTION)
    if input('Insert reviewed changelog draft and continue? [y/N]: ').lower() != 'y':
      raise RuntimeError('Release stopped before changelog publication.')
    changelogPath = Path('CHANGELOG.md')
    reviewedDraft = draftPath.read_text(encoding='utf-8').rstrip()
    requiredMetadata = (f'## [v{version}]', r'\*\*Release source commit:\*\* `[0-9a-f]{40}`',
                        r'\*\*Previous stable release:\*\* `v\d+\.\d+\.\d+` \(`[0-9a-f]{40}`\)')
    if any(re.search(metadata, reviewedDraft) is None for metadata in requiredMetadata):
      raise RuntimeError(f'Reviewed changelog draft {draftPath} is missing required release metadata.')
    changelog = changelogPath.read_text(encoding='utf-8')
    stableHeading = changelog.find('\n## [v')
    insertion = reviewedDraft + '\n\n'
    changelogPath.write_text(changelog[:stableHeading] + '\n' + insertion + changelog[stableHeading + 1:]
                             if stableHeading >= 0 else changelog.rstrip() + '\n\n' + insertion, encoding='utf-8')
    draftPath.unlink()
  addition = input('\n\nWhat do you want to add to the push message (do not use \' or \")? ')
  changeCheck = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--'], check=False)
  if changeCheck.returncode == 1:
    subprocess.run(['git', 'commit', '-a', '-m', f'updated changelog; {addition}'], check=True)
  elif changeCheck.returncode != 0:
    raise subprocess.CalledProcessError(changeCheck.returncode, changeCheck.args)
  subprocess.run(['git', 'tag', '-a', f'v{version}', '-m', f'Version {version}; see CHANGELOG for details'], check=True)
  #push and publish
  print('\n\nWill bypass rule violation\n\n')
  subprocess.run(['git', 'push'], check=True)
  subprocess.run(['git', 'push', 'origin', f'v{version}'], check=True)
  return


def createRequirementsFile() -> None:
  """
  Create a requirements.txt file from the setup.cfg information
  - not done anymore automatically
  - should be manually executed for every 0.1 release, every 6month - 1year
  - go to new versions of all libs
  - do testing of pasta afterwards; use beta versions for that
  - do a diff of the resulting requirements files to ensure that at least the pyside versions are identical

  Commands (requires pip-tools installed via pip):
  - pip-compile --no-annotate -U -o requirements-linuxNew.txt
  - diff requirements-linux.txt requirements-windows.txt to see changes and create those into windows too
  """
  print('Requirements.txt file creation skipped.\n'
        '- manually create Linux an Windows versions for every 0.1 release\n'
        '- read releaseVersion for instructions')
  return


def runTests() -> bool:
  """
  run unit-tests: can only work if all add-ons and dependencies are fulfilled

  Cannot be an action, since dependencies are partly private

  Returns:
    bool: True if all tests passed
  """
  print('Start running tests')
  coverageArgs = [sys.executable, '-m', 'coverage', 'run', '--source=pasta_eln']
  tests = [i for i in os.listdir('tests') if i.endswith('.py') and i.startswith('test_')]
  firstTest = True
  for fileI in sorted(tests):
    coverageOption = [] if firstTest else ['-a']
    result = subprocess.run(coverageArgs + coverageOption + ['-m', 'pytest', '-s', '--no-skip', f'tests/{fileI}'],
                            capture_output=True, check=False)
    firstTest = False
    success = result.stdout.decode('utf-8').count('*** DONE WITH VERIFY ***')
    if success==1:
      success += result.stdout.decode('utf-8').count('**ERROR')
      success -= result.stdout.decode('utf-8').count('**ERROR Red: FAILURE and ERROR')
      for badWord in ['**ERROR got a file','FAILED','ModuleNotFoundError']:
        success += result.stdout.decode('utf-8').count(badWord)
    success += result.stdout.decode('utf-8').count('========= FAILURES =========')
    success += result.stdout.decode('utf-8').count('========== ERRORS ==========')
    if success==0:
      print(f"  success: Python unit test {fileI}")
    else:
      print(f"  FAILED: Python unit test {fileI}")
      print(f"    run: 'pytest -s tests/{fileI}' and check logFile")
      print(f"\n---------------------------\n{result.stdout.decode('utf-8')}\n---------------------------\n")
      return False
  print('Start running complicated tests')
  tests = [i for i in os.listdir('testsComplicated') if i.endswith('.py') and i.startswith('test_')]
  for fileI in sorted(tests):
    result = subprocess.run(coverageArgs + ['-a', '-m', 'pytest', '-s', '--no-skip', f'testsComplicated/{fileI}'],
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
      print(f"    run: 'pytest -s testsComplicated/{fileI}' and check logFile")
      print(f"\n---------------------------\n{result.stdout.decode('utf-8')}\n---------------------------\n")
      return False
  coverageResult = subprocess.run([sys.executable, '-m', 'coverage', 'html'], capture_output=True, check=False)
  reportPath = Path('htmlcov/index.html').resolve()
  if coverageResult.returncode != 0:
    print(f'**ERROR: HTML coverage report was not created at {reportPath}')
    return False
  print(f'HTML coverage report: {reportPath}')
  return True


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


def rightAlignComments() -> None:
  """
  Check if comments are right-aligned to column 110
  """
  print('================ START RIGHT-ALIGNMENT CHECK ================')
  for root, _, files in os.walk('pasta_eln'):
    for file in files:
      if file.endswith('.py') and \
          file not in ['markdown2html.py','html2markdown.py','html2mdConfig.py','html2mdUtils.py','htmlString.py',
                       'gui_communicate.py','worker.py'] and 'Resources/' not in root and '/add_ons' not in root:
        filePath = os.path.join(root, file)
        with open(filePath, encoding='utf-8') as f:
          content = f.read()
        commentColumns = {token.start[0]: token.start[1]
          for token in tokenize.generate_tokens(io.StringIO(content).readline) if token.type == tokenize.COMMENT}
        output = ''                                                                  # sourcery skip: use-join
        for number, line in enumerate(content.splitlines(), start=1):
          commentColumn = commentColumns.get(number)
          hasInlineComment = commentColumn is not None and bool(line[:commentColumn].strip()) and \
            line[commentColumn-1].isspace() and 'import' not in line
          if hasInlineComment and len(line)!=110:
            output += f'{number}: {line.strip()}\n'
        if output and 'Resources/' not in filePath:
          print('Processing file:', filePath)
          print(output)
  print('================ END RIGHT-ALIGNMENT CHECK ================')
  return


def findTasks() -> None:
  """ Find all tasks in the pasta_eln codebase that are emitted by the UI.
  This is used to find discrepancies in keys.
  - information also in guiCommunicate
  """
  target:dict[str,list[str]] = {}
  result1 = subprocess.run(['grep', '-r','uiRequestTask', 'pasta_eln'], capture_output=True, text=True, check=False)
  for line in result1.stdout.split('\n'):
    if len(line)<10:
      continue
    fileName, code = line.split(':', maxsplit=1)
    if 'uiRequestTask.emit(Task.' in code:  # this is how it should be
      task = code.split('emit(Task.')[1].split(',', maxsplit=1)[0]
      data = code.split('emit(Task.')[1].split(',', maxsplit=1)[1][:-1]
      if task not in target:
        target[task] = []
      target[task].append(f'{fileName.strip()}: {data.strip()}')
  print(json.dumps(target, indent=2))



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
           'isort'     : 'isort --ca pasta_eln/',
           'pylint'    : 'pylint pasta_eln/',
           'mypy'      : 'mypy --no-warn-unused-ignores pasta_eln/',
           'sourcery'  : 'sourcery review pasta_eln/',
           'isort2'    : 'isort releaseVersion.py',
           'pylint2'   : 'pylint releaseVersion.py',
           'mypy2'     : 'mypy --no-warn-unused-ignores releaseVersion.py',
           'sourcery2' : 'sourcery review releaseVersion.py',
           'sphinx-doc': 'make -C docs'}
  for label, cmd in tools.items():
    print(f'------------------ start {label} -----------------')
    subprocess.run(shlex.split(cmd), check=False)
    print(f'---------------- end {label} ---------------')
  rightAlignComments()
  return


def getArtifacts() -> None:
  """ Get artifacts from action """
  if not os.path.exists('artifacts'):
    os.makedirs('artifacts')
  owner='PASTA-ELN'
  repo='pasta-eln'
  workflowFile='installLinux.yml'
  url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflowFile}/runs?per_page=1"
  response = requests.get(url, timeout=30)
  response.raise_for_status()
  data = response.json()
  runID = data['workflow_runs'][0]['id'] if data['workflow_runs'] else None

  url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{runID}/artifacts"
  response = requests.get(url, timeout=30)
  response.raise_for_status()
  data = response.json()
  artifactUrl = str(data['artifacts'][0]['archive_download_url']) if data['artifacts'] else None
  if artifactUrl is None:
    print('No artifacts found.')
    return
  print('Download:',artifactUrl,'into artifacts/...')

  with open(Path.home()/'.ssh'/'github.token', encoding='utf-8') as fIn:
    token = fIn.read().strip()
  headers = {'Authorization': f"token {token}"}
  response = requests.get(artifactUrl, headers=headers, stream=True, timeout=60)
  response.raise_for_status()
  with open('artifacts/artifact.zip', 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
      if chunk:
        f.write(chunk)
  subprocess.run(['unzip', '-o', 'artifact.zip'], cwd='artifacts', check=False)
  Path('artifacts/artifact.zip').unlink()
  return


if __name__=='__main__':
  #run tests and create default files
  successTests = runTests()
  if not successTests:
    sys.exit(1)
  #create files automatically
  createContributors()
  runSourceVerification()
  createRequirementsFile()
  versionLevel = 2 if len(sys.argv)==1 else int(sys.argv[1])
  #test if on main branch
  resultMain = subprocess.run(['git','status'], capture_output=True, check=False)
  if resultMain.stdout.decode('utf-8').strip().startswith('On branch main\n'):
    #do update
    print("""You should have done before as ~12 issues are closed in current milestone:
- 'git checkout main'
- 'git merge sb_staging'
- Close milestone on github
""")
    if input('Continue: only "y" continues. ') == 'y':
      newVersion(versionLevel)
      getArtifacts()
      print("""You should do here after:
- 'git checkout sb_staging'
- 'git merge main'
- Open new milestone on github and fill in few issues
""")
    else:
      print('You have to be on main branch to continue.')
