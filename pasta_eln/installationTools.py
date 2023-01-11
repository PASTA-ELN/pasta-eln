'''  Methods that check, repair, the local PASTA-ELN installation '''
import os, platform, sys, json, shutil, random, string, subprocess, logging
import importlib.util
import urllib.request
from pathlib import Path
from cloudant.client import CouchDB

from .backend import Pasta
from .fixedStrings import defaultOntology


def getOS():
  '''
  Get operating system and python environment

  Returns:
    string: os + pythonEnvironment
  '''
  operatingSys = platform.system()
  # Get base/real prefix, or sys.prefix if there is none
  get_base_prefix_compat = getattr(sys, 'base_prefix', None) or getattr(sys, 'real_prefix', None) or sys.prefix
  in_virtualenv = get_base_prefix_compat != sys.prefix
  environment = sys.prefix if in_virtualenv else '_system_'
  return operatingSys+' '+environment


def createDefaultConfiguration(user, password, pathPasta=None):
  '''
  Check configuration file .pastaELN.json for consistencies

  Args:
    user (str): user name (for windows)
    password (str): password (for windows)
    pathPasta (str): place to store pasta data

  Returns:
    dict: dictionary of configuration
  '''
  if user == '':
    user = input('Enter user name: ')
  if password == '':
    password = input('Enter password: ')
  if pathPasta is None:
    if platform.system()=='Windows':
      pathPasta = str(Path.home()/'Documents'/'PASTA_ELN')
    else:
      pathPasta = str(Path.home()/'PASTA_ELN')
  conf = {}
  conf['default']     = 'research'
  conf['links']       = {'research':{\
                          'local':{'user':user, 'password':password, 'database':'research', 'path':pathPasta},
                          'remote':{}  }}
  conf['version']     = 1
  try:
    conf['userID']      = os.getlogin()
  except:   #github action
    conf['userID']      = 'github_user'
  conf['extractors']  = {}
  conf['qrPrinter']   = {}
  conf['magicTags']   = ['P1','P2','P3','TODO','WAIT','DONE']
  return conf


def runAsAdminWindows(cmdLine):
  '''
  Run a command as admin in windows
  - (C) COPYRIGHT © Preston Landers 2010
  - https://stackoverflow.com/questions/19672352/how-to-run-script-with-elevated-privilege-on-windows
  - asks user for approval
  - waits for commands to end

  Args:
    cmdLine (list): list of command line sections runAsAdmin(["c:\\Windows\\notepad.exe"])
  '''
  import win32con, win32event, win32process
  from win32com.shell.shell import ShellExecuteEx
  from win32com.shell import shellcon
  procInfo = ShellExecuteEx(nShow=win32con.SW_SHOWNORMAL,
                            fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                            lpVerb='runas',  # causes UAC elevation prompt.
                            lpFile= '"'+cmdLine[0]+'"',
                            lpParameters=" ".join(cmdLine[1:]))
  procHandle = procInfo['hProcess']
  _ = win32event.WaitForSingleObject(procHandle, win32event.INFINITE)
  _   = win32process.GetExitCodeProcess(procHandle)
  return


def git(command='test'):
  '''
  WINDOWS test git installation or install it

  Args:
    command (string): 'test' or 'install'

  Returns:
    string: '' for success, filled with errors
  '''
  if platform.system()!='Windows':
    return '**ERROR: git can only be tested, etc. on Windows'
  if command == 'test':
    if shutil.which('git') is None:
      return '**ERROR: git not installed'
    return ''
  elif command == 'install':
    logging.info('git starting ...')
    ## Using installer that requires 14-next ;-(
    # url = 'https://github.com/git-for-windows/git/releases/download/v2.39.0.windows.2/Git-2.39.0.2-64-bit.exe'
    # path = Path.home()/'Downloads'/'git-installer.exe'
    # resultFilePath, _ = urllib.request.urlretrieve(url, path)
    # cmd = ['cmd.exe','/K ',str(resultFilePath)]
    # _ = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    ## Winget creates paths if run as admin
    runAsAdminWindows(['winget','install','--id','Git.Git','-e','--source','winget'])
    # os.system('winget install --id Git.Git -e --source winget')    #does not work since in user-mode
    logging.info('git ended')
    return 'Installed git using temporary files in Downloads'

  return '**ERROR: Unknown command'


def gitAnnex(command='test'):
  '''
  test git-annex installation or install it

  Args:
    command (string): 'test' or 'install'

  Returns:
    string: '' for success, filled with errors
  '''
  if command == 'test':
    if platform.system()=='Linux':
      if shutil.which('git-annex') is None:
        return '**ERROR: git-annex not installed'
    elif platform.system()=='Windows':
      if shutil.which('git-annex') is None:
        return '**ERROR: git-annex not installed'
    # found = importlib.util.find_spec('datalad')
    #Has information if global or local installed
    # ModuleSpec(name='datalad', origin='/usr/local/lib/python3.8/dist-packages/datalad/__init__.py')
    return ''

  elif command == 'install':
    if platform.system()=='Linux':
      return '**ERROR: should not be called'
    elif platform.system()=='Windows':
      logging.info('gitannex install starting ...')
      ## Old version with installer
      # url = 'https://downloads.kitenet.net/git-annex/windows/7/current/git-annex-installer.exe'
      # path = Path.home()/'Downloads'/'git-annex-installer.exe'
      # resultFilePath, _ = urllib.request.urlretrieve(url, path)
      # cmd = ['cmd.exe','/K ',str(resultFilePath)]
      ## New version with datalad-installer: Does not ask questions
      cmd = ['datalad-installer','git-annex','-m','datalad/git-annex:release']
      _ = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
      logging.info('gitannex install ended')
      return 'Installed git-annex using temporary files in Downloads'
    return '**ERROR: Unknown operating system '+platform.system()

  return '**ERROR: Unknown command'



def couchdb(command='test'):
  '''
  test couchDB installation or (install it on Windows-only)

  Args:
    command (string): 'test' or 'install'

  Returns:
    string: '' for success, filled with errors
  '''
  if command == 'test':
    try:
      with urllib.request.urlopen('http://127.0.0.1:5984') as package:
        contents = package.read()
        if json.loads(contents)['couchdb'] == 'Welcome':
          return ''
    except:
      pass
    return '**ERROR**'

  elif command == 'install':
    if platform.system()=='Linux':
      return '**ERROR should not be called'
    elif platform.system()=='Windows':
      logging.info('CouchDB starting ...')
      url = 'https://couchdb.neighbourhood.ie/downloads/3.1.1/win/apache-couchdb-3.1.1.msi'
      path = Path.home()/'Downloads'/'apache-couchdb-3.1.1.msi'
      logging.info('Start download of couchdb')
      _, _ = urllib.request.urlretrieve(url, path)
      ## Old version with installer
      # cmd = ['cmd.exe','/K ',str(resultFilePath)]
      # _ = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
      ## New version without questions
      password = ''.join(random.choice(string.ascii_letters) for i in range(12))
      logging.info('PASSWORD: '+password)
      path = str(path).replace('\\','\\\\')
      cmd = ['msiexec','/i',path,'/quiet','COOKIEVALUE=abcdefghijklmo','INSTALLSERVICE=1','ADMINUSER=admin',\
             'ADMINPASSWORD='+password,'/norestart','/l*','log.txt']
      logging.info('COMMAND: '+' '.join(cmd))
      runAsAdminWindows(cmd)
      logging.info('CouchDB ending')
      return 'Installed couchDB with password |'+password+'|'
    return '**ERROR: Unknown operating system '+platform.system()
  return '**ERROR: Unknown command'


def couchdbUserPassword(username, password):
  '''
  test if username and password are correct

  Args:
    username (string): user name
    password (string): password

  Returns:
    bool: True if success, False if failure
  '''
  try:
    _ = CouchDB(username, password, url='http://127.0.0.1:5984', connect=True)
    return True
  except:
    return False


def installLinuxRoot(gitAnnexExists, couchDBExists, pathPasta=''):
  '''
  Install all packages in linux using the root-password

  Args:
    gitAnnexExists (bool): does the git-annex installation exist
    couchDBExists (bool): does the couchDB installation exist
    pathPasta (str): path to install pasta in (Linux)

  Returns:
    string: ''=success, else error messages
  '''
  logging.info('InstallLinuxRoot starting ...')
  bashCommand = []
  password = ''
  if not gitAnnexExists:
    bashCommand += [
      'sudo wget -q http://neuro.debian.net/lists/focal.de-fzj.full -O /etc/apt/sources.list.d/neurodebian.sources.list',
      'sudo apt-key adv --recv-keys --keyserver hkps://keyserver.ubuntu.com 0xA5D32F012649A5A9',
      'sudo apt-get update',
      'sudo apt-get install -y git-annex-standalone',
      'echo DONE',
      'sleep 10']
  if not couchDBExists:
    password = ''.join(random.choice(string.ascii_letters) for i in range(12))
    logging.info('PASSWORD: '+password)
    #create or adopt .pastaELN.json
    path = Path.home()/'.pastaELN.json'
    if path.exists():
      with open(path,'r', encoding='utf-8') as fConf:
        conf = json.load(fConf)
    else:
      conf = createDefaultConfiguration('admin', password, pathPasta)
    with open(path,'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(conf, indent=2) )
    bashCommand += [
      'sudo snap install couchdb',
      'sudo snap set couchdb admin='+password,
      'sudo snap start couchdb',
      'sudo snap connect couchdb:mount-observe',
      'sudo snap connect couchdb:process-control',
      'sleep 5',
      'curl -X PUT http://admin:'+password+'@127.0.0.1:5984/_users',
      'curl -X PUT http://admin:'+password+'@127.0.0.1:5984/_replicator',
      'curl -X PUT http://admin:'+password+'@127.0.0.1:5984/_global_changes',
      'sleep 10',
      'echo DONE-Press-Key',
      'read']  #TODO if successful in Aug2023: remove "echo....read"
  #Try all terminals
  scriptFile = Path.home()/'pastaELN_Install.sh'
  with open(scriptFile,'w', encoding='utf-8') as shell:
    shell.write('\n'.join(bashCommand))
  os.chmod(scriptFile, 0o0777)
  if not (Path.home()/'.gitconfig').exists():
    with open(Path.home()/'.gitconfig','w', encoding='utf-8') as gitConfig:
      gitConfig.write('[user]\n\temail = anonymous@aol.com\n\tname = anonymous\n')
  terminals = ['xterm -e bash -c ','qterminal -e bash -c ','gnome-terminal -- ']
  logging.info('Command: '+str(bashCommand))
  resultString = 'Password: '+password
  for term in terminals:
    # _ = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    res = os.system(term+scriptFile.as_posix())
    logging.info('Linux install terminal '+term+' '+str(res) )
    if res == 0:
      break
    if terminals.index(term)==len(terminals)-1:
      logging.error('**ERROR: Last terminal failed')
      res = os.system('\n'.join(bashCommand[:-2]))
      logging.info('Finished using straight Bash command result='+str(res))
      resultString = '**ERROR: Last terminal failed'
  success = 'CouchDB works' if couchdbUserPassword('admin',password) else 'CouchDB FAILED'
  logging.info('InstallLinuxRoot ending. '+success)
  return resultString


def configuration(command='test', user='', password='', pathPasta=''):
  '''
  Check configuration file .pastaELN.json for consistencies

  Args:
    command (str): 'test' or 'repair'
    user (str): user name (for windows)
    password (str): password (for windows)
    pathPasta (str): path to install pasta in (Windows)

  Returns:
    string: ''=success, else error messages
  '''
  logging.info('Configuration starting ...')
  output = ''
  try:
    with open(Path.home()/'.pastaELN.json','r', encoding='utf-8') as fConf:
      conf = json.load(fConf)
  except:
    output += '**ERROR configuration file does not exist\n'
    conf = {}
    if command == 'repair':
      conf = createDefaultConfiguration(user, password, pathPasta)

  illegalNames = [key for key in conf if key.startswith('-')]
  if not 'userID' in conf:
    if command == 'repair':
      conf['userID'] = os.getlogin()
    else:
      output += '**ERROR: No userID in config file\n'
  if not 'magicTags' in conf:
    if command == 'repair':
      conf['magicTags'] = []
    else:
      output += '**ERROR: No magicTags in config file\n'
  if not 'qrPrinter' in conf:
    if command == 'repair':
      conf['qrPrinter'] = {}
    else:
      output += '**ERROR: No qrPrinter in config file\n'
  if not 'tableFormat' in conf:
    if command == 'repair':
      conf['tableFormat'] = {}
    else:
      output += '**ERROR: No tableFormat in config file\n'
  if not 'extractors' in conf:
    if command == 'repair':
      conf['extractors'] = {}
    else:
      output += '**ERROR: No extractors in config file\n'
  if not 'version' in conf or conf['version']!=1:
    if command == 'repair':
      conf['version'] = 1
    else:
      output += '**ERROR: No or wrong version in config file\n'
  if not 'links' in conf:
    output += '**ERROR: No links in config file; REPAIR MANUALLY\n'

  if not 'default' in conf:
    if command == 'repair' and len(illegalNames)==0:
      conf['default'] = list(conf['links'].keys())[0]
    else:
      output += '**ERROR: No default links in config file\n'
  else:
    if not conf['default'] in conf['links']:
      if command == 'repair':
        conf['default'] = list(conf['links'].keys())[0]
      else:
        output += '**ERROR: default entry '+conf['default']+' not in links\n'
  if len(illegalNames)>0:
    if command == 'repair':
      for key in illegalNames:
        del conf[key]
    else:
      output += '**ERROR: - type entries '+str(illegalNames)+' in config file\n'

  if command == 'repair':
    with open(Path.home()/'.pastaELN.json','w', encoding='utf-8') as f:
      f.write(json.dumps(conf,indent=2))
  logging.info('Configuration ending')
  return output



def ontology(command='test'):
  '''
  Check configuration file .pastaELN.json for consistencies

  Args:
    command (string): 'test' or 'install'

  Returns:
    string: ''=success, else error messages
  '''
  output = ''
  pasta = Pasta()

  if command == 'test':
    output += 'database name:'+pasta.db.db.database_name+'\n'
    designDocuments = pasta.db.db.design_documents()
    output += 'Design documents'+'\n'
    for item in designDocuments:
      numViews = len(item['doc']['views']) if 'views' in item['doc'] else 0
      output += '  '+item['id']+'   Num. of views:'+str(numViews)+'\n'
    try:
      _ = pasta.db.getDoc('-ontology-')
      output += 'Ontology exists on server'+'\n'
    except:
      output += '**ERROR: Ontology does NOT exist on server'+'\n'
    return output

  elif command == 'install':
    logging.info('ontology starting ...')
    doc = json.loads(defaultOntology)
    print(doc)
    logging.info('ontology ending ...')
    # _ = pasta.db.create_document(doc)
    return ''

  return '**ERROR: Unknown command'



def exampleData(force=False, callbackPercent=None):
  '''
  Create example data after installation

  Args:
    force (bool): force creation by removing content before creation
    callbackPercent (function): callback function given to exampleData, such that exampleData can report progress back
  '''
  logging.info('Start example data creation')
  if callbackPercent is not None:
    callbackPercent(0)
  configName = 'research'
  if force:
    pasta = Pasta(configName, initConfig=False)
    dirName = pasta.basePath
    pasta.exit(deleteDB=True)
    shutil.rmtree(dirName)
    os.makedirs(dirName)
  if callbackPercent is not None:
    callbackPercent(1)
  pasta = Pasta(configName, initViews=True, initConfig=False)
  if callbackPercent is not None:
    callbackPercent(2)
  ### CREATE PROJECTS AND SHOW
  print('*** CREATE EXAMPLE PROJECT AND SHOW ***')
  pasta.addData('x0', {'-name': 'PASTAs Example Project', 'objective': 'Test if everything is working as intended.', 'status': 'active', 'comment': '#tag Can be used as reference or deleted'})
  if callbackPercent is not None:
    callbackPercent(3)
  print(pasta.output('x0'))
  if callbackPercent is not None:
    callbackPercent(4)
  logging.info('Finished creating example project')

  ### TEST PROJECT PLANING
  print('*** TEST PROJECT PLANING ***')
  viewProj = pasta.db.getView('viewDocType/x0')
  projID1  = [i['id'] for i in viewProj if 'PASTA' in i['value'][0]][0]
  if callbackPercent is not None:
    callbackPercent(5)
  pasta.changeHierarchy(projID1)
  if callbackPercent is not None:
    callbackPercent(6)
  pasta.addData('x1',    {'comment': 'This is hard! #TODO', '-name': 'This is an example task'})
  if callbackPercent is not None:
    callbackPercent(7)
  pasta.addData('x1',    {'comment': 'This will take a long time. #WAIT', '-name': 'This is another example task'})
  if callbackPercent is not None:
    callbackPercent(8)
  pasta.changeHierarchy(pasta.currentID)
  pasta.addData('x2',    {'-name': 'This is an example subtask',     'comment': 'Random comment 1'})
  if callbackPercent is not None:
    callbackPercent(9)
  pasta.addData('x2',    {'-name': 'This is another example subtask','comment': 'Random comment 2'})
  if callbackPercent is not None:
    callbackPercent(10)
  pasta.changeHierarchy(None)
  pasta.addData('x1',    {'-name': 'Data files'})
  if callbackPercent is not None:
    callbackPercent(11)
  semStepID = pasta.currentID
  pasta.changeHierarchy(semStepID)
  semDirName = pasta.basePath/pasta.cwd
  pasta.changeHierarchy(None)
  print(pasta.outputHierarchy())
  if callbackPercent is not None:
    callbackPercent(12)
  logging.info('Finished project planning')

  ### TEST PROCEDURES
  print('\n*** TEST PROCEDURES ***')
  sopDir = pasta.basePath/'StandardOperatingProcedures'
  os.makedirs(sopDir, exist_ok=True)
  with open(sopDir/'Example_SOP.md','w', encoding='utf-8') as fOut:
    fOut.write('# Put sample in instrument\n# Do something\nDo not forget to\n- not do anything wrong\n- **USE BOLD LETTERS**\n')
  if callbackPercent is not None:
    callbackPercent(13)
  pasta.addData('procedure', {'-name': 'StandardOperatingProcedures/Example_SOP.md', 'comment': '#v1'})
  if callbackPercent is not None:
    callbackPercent(14)
  print(pasta.output('procedure'))
  if callbackPercent is not None:
    callbackPercent(15)
  logging.info('Finished procedures creating')

  ### TEST SAMPLES
  print('*** TEST SAMPLES ***')
  pasta.addData('sample',    {'-name': 'Example sample', 'chemistry': 'A2B2C3', 'qrCode': '13214124 99698708', 'comment': 'can be used as example or removed'})
  if callbackPercent is not None:
    callbackPercent(16)
  print(pasta.output('sample'))
  if callbackPercent is not None:
    callbackPercent(17)
  print(pasta.outputQR())
  if callbackPercent is not None:
    callbackPercent(18)
  logging.info('Finished samples creating')

  ###  TEST MEASUREMENTS AND SCANNING/CURATION
  print('*** TEST MEASUREMENTS AND SCANNING/CURATION ***')
  shutil.copy(Path(__file__).parent/'Resources'/'ExampleMeasurements'/'simple.png', semDirName)
  shutil.copy(Path(__file__).parent/'Resources'/'ExampleMeasurements'/'simple.csv', semDirName)
  if callbackPercent is not None:
    callbackPercent(19)
  logging.info('Finished copy files')
  pasta.scanTree()
  logging.info('Finished scan tree')
  if callbackPercent is not None:
    callbackPercent(20)

  ### USE GLOBAL FILES
  print('*** USE GLOBAL FILES ***')
  pasta.changeHierarchy(semStepID)
  if callbackPercent is not None:
    callbackPercent(21)
  pasta.addData('measurement', {'-name': 'https://developers.google.com/search/mobile-sites/imgs/mobile-seo/separate-urls.png', \
    'comment':'remote image from google. Used for testing and reference. Can be deleted.'})
  if callbackPercent is not None:
    callbackPercent(22)
  print(pasta.output('measurement'))
  if callbackPercent is not None:
    callbackPercent(23)
  logging.info('Finished global files additions')

  ### VERIFY DATABASE INTEGRITY
  print('\n*** VERIFY DATABASE INTEGRITY ***')
  print(pasta.checkDB(verbose=True))
  print('\n*** DONE WITH VERIFY ***')
  if callbackPercent is not None:
    callbackPercent(24)
  logging.info('Finished checking database')
  return


def createShortcut():
  """
  Create shortcut icon depending on operating system
  """
  logging.info('Create shortcut starting')
  if platform.system()=='Linux':
    content ='[Desktop Entry]\nName=PASTA ELN\nComment=PASTA electronic labnotebook\n'
    content+='Exec=pastaELN\n'
    content+='Icon='+ (Path(__file__).parent/'Resources'/'Icons'/'favicon64.png').as_posix() + '\n'
    content+='Terminal=false\nType=Application\nCategories=Utility;Application;\n'
    try:
      with open(Path.home()/'Desktop'/'pastaELN.desktop','w', encoding='utf-8') as fOut:
        fOut.write(content)
        os.chmod(Path.home()/'Desktop'/'pastaELN.desktop', 0o777)
    except:
      pass
    try:
      with open(Path.home()/'.local'/'share'/'applications'/'pastaELN.desktop','w', encoding='utf-8') as fOut:
        fOut.write(content)
        os.chmod(Path.home()/'.local'/'share'/'applications'/'pastaELN.desktop', 0o777)
    except:
      pass
  elif platform.system()=='Windows':
    import winshell
    from win32com.client import Dispatch

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut( os.path.join(winshell.desktop(), "pastaELN.lnk") )
    shortcut.Targetpath = r"pastaELN"
    shortcut.WorkingDirectory = str(Path.home())
    shortcut.IconLocation = str(Path(__file__).parent/'Resources'/'Icons'/'favicon64.ico')
    shortcut.save()
  logging.info('Create shortcut end')
  return


##############
# Main method for testing and installation without GUI
def main():
  ''' Main method and entry point for commands '''
  logPath = Path.home()/'pastaELN.log'
  #old versions of basicConfig do not know "encoding='utf-8'"
  logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')   #TODO this loggingWarning goes into configuration
  for package in ['urllib3', 'requests', 'asyncio', 'datalad', 'PIL', 'matplotlib.font_manager']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start PASTA Install')
  print('---- Test PASTA-ELN installation----')
  print('--   if nothing reported: it is ok.')
  print('getOS        :', getOS())
  if platform.system()=='Windows':
    res = git()
    existsGit = res==''
    print('git        :',res)
  res = gitAnnex()
  existsGitAnnex = res==''
  print('git-annex    :', res)
  res = couchdb()
  existsCouchDB = res==''
  print('chouchDB     :', res)
  res = configuration()
  flagConfiguration = 'ERROR' in res
  print('configuration:', res)
  try:
    res = '\n'+ontology()
  except:
    res = ' **ERROR**'
    #No new 'raise' so that it install-script continues its path
  flagOntology = 'ERROR' in res
  print('ontology     :'+res)

  print('Add "install" argument to install PASTA-ELN.')
  if len(sys.argv)>1 and 'install' in sys.argv:
    if platform.system()=='Linux':
      print('---- Create PASTA-ELN installation Linux ----')
      if (not existsGitAnnex) or (not existsCouchDB):
        print('install with root credentials...')
        dirName = (Path.home()/'pastaELN').as_posix()
        installLinuxRoot(existsGitAnnex, existsCouchDB, dirName)
      if flagConfiguration:
        print('repair  configuration:', configuration('repair'))
      if flagOntology and existsCouchDB:
        print('install ontology     :', ontology('install'))

    elif platform.system()=='Windows':
      print('---- Create PASTA-ELN installation Windows ----')
      if not existsGit:
        print('install git          :', git('install'))
      if not existsGitAnnex:
        print('install git-annex    :', gitAnnex('install'))
      if not existsCouchDB:
        print('install couchDB      :', couchdb('install'))
      if flagConfiguration:
        print('repair  configuration:', configuration('repair'))
      if flagOntology and existsCouchDB:
        print('install ontology     :', ontology('install'))

  print('Add "example" argument to create example data.')
  if len(sys.argv)>1 and 'example' in sys.argv:
    print('---- Create Example data ----')
    print('create example data  :', exampleData())

  logging.info('End PASTA Install')
  return


# called by python3 -m pasta_eln.installTools
if __name__ == '__main__':
  main()
