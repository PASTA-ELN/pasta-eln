'''  Methods that check, repair, the local PASTA-ELN installation '''
import os, platform, sys, json, shutil, random, string, logging
from typing import Optional, Any, Callable
import urllib.request
from pathlib import Path
from cloudant.client import CouchDB

from .backend import Backend
from .fixedStrings import defaultOntology


def getOS() -> str:
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


def createDefaultConfiguration(user:str, password:str, pathPasta:Optional[Path]=None) -> dict[str,Any]:
  '''
  Check configuration file .pastaELN.json for consistencies

  Args:
    user (str): user name (for windows)
    password (str): password (for windows)
    pathPasta (Path): place to store pasta data

  Returns:
    dict: dictionary of configuration
  '''
  if user == '':
    user = input('Enter user name: ')
  if password == '':
    password = input('Enter password: ')
  if pathPasta is None:
    if platform.system()=='Windows':
      pathPasta = Path.home()/'Documents'/'PASTA_ELN'
    else:
      pathPasta = Path.home()/'PASTA_ELN'
  conf:dict[str,Any] = {}
  conf['defaultProjectGroup']     = 'research'
  conf['projectGroups']       = {'research':{\
                          'local':{'user':user, 'password':password, 'database':'research',
                                   'path':str(pathPasta)},
                          'remote':{}  }}
  conf['version']     = 2
  try:
    conf['userID']      = os.getlogin()
  except:   #github action
    conf['userID']      = 'github_user'
  #create pastaDir if it does not exist
  if not pathPasta.exists():
    pathPasta.mkdir()
  return conf


def runAsAdminWindows(cmdLine:list[str]) -> None:
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


def couchdb(command:str='test') -> str:
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
      pathS = str(path).replace('\\','\\\\')
      cmd = ['msiexec','/i',pathS,'/quiet','COOKIEVALUE=abcdefghijklmo','INSTALLSERVICE=1','ADMINUSER=admin',\
             'ADMINPASSWORD='+password,'/norestart','/l*','log.txt']
      logging.info('COMMAND: '+' '.join(cmd))
      runAsAdminWindows(cmd)
      logging.info('CouchDB ending')
      return 'Installed couchDB with password |'+password+'|'
    return '**ERROR: Unknown operating system '+platform.system()
  return '**ERROR: Unknown command'


def couchdbUserPassword(username:str, password:str) -> bool:
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


def installLinuxRoot(couchDBExists:bool, pathPasta:Path='', password:str='') -> str:
  '''
  Install all packages in linux using the root-password

  Args:
    couchDBExists (bool): does the couchDB installation exist
    pathPasta (Path): path to install pasta in (Linux)
    password (str): password for couchDB installation

  Returns:
    string: ''=success, else error messages
  '''
  logging.info('InstallLinuxRoot starting ...')
  bashCommand = []
  password = ''
  if not couchDBExists:
    if password=='':
      password = ''.join(random.choice(string.ascii_letters) for i in range(12))
      logging.info('PASSWORD: '+password)
    #create or adopt .pastaELN.json
    path = Path.home()/'.pastaELN.json'
    if path.exists():
      with open(path,'r', encoding='utf-8') as fConf:
        conf = json.load(fConf)
      logging.info('.pastaELN.json exists, do not change it')
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
      'curl -X PUT http://admin:'+password+'@127.0.0.1:5984/_node/_local/_config/couch_httpd_auth/timeout/ -d \'"60000"\'',
      'sleep 10',
      'echo DONE-Press-Key',
      'read']  #TODO_P5 if successful in Aug2023: remove "echo....read"
  #Try all terminals
  scriptFile = Path.home()/'pastaELN_Install.sh'
  with open(scriptFile,'w', encoding='utf-8') as shell:
    shell.write('\n'.join(bashCommand))
  os.chmod(scriptFile, 0o0777)
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


def configuration(command:str='test', user:str='', password:str='', pathPasta:Path='') -> str:
  '''
  Check configuration file .pastaELN.json for consistencies

  Args:
    command (str): 'test' or 'repair'
    user (str): user name (for windows)
    password (str): password (for windows)
    pathPasta (Path): path to install pasta in (Windows)

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
  logging.info(json.dumps(conf, indent=2))

  if 'version' not in conf or conf['version']!=2:
    if command == 'repair':
      conf['version'] = 2
    else:
      output += '**ERROR: No or wrong version in config file\n'
  if 'userID' not in conf:
    if command == 'repair':
      conf['userID'] = os.getlogin()
    else:
      output += '**ERROR: No userID in config file\n'
  if 'defaultTags' not in conf:
    if command == 'repair':
      conf['defaultTags'] = ["P1", "P2", "P3", "TODO", "DOING", "WAIT", "DONE"]
    else:
      output += '**ERROR: No defaultTags in config file\n'
  if 'tableColumnsMax' not in conf:
    if command == 'repair':
      conf['tableColumnsMax'] = 16
    else:
      output += '**ERROR: No tableColumnsMax in config file\n'
  if 'tableHeaders' not in conf:
    if command == 'repair':
      conf['tableHeaders'] = {}
    else:
      output += '**ERROR: No tableHeaders in config file\n'
  if 'qrPrinter' not in conf:
    if command == 'repair':
      conf['qrPrinter'] = {}
    else:
      output += '**ERROR: No qrPrinter in config file\n'
  if 'extractorDir' not in conf:
    if command == 'repair':
      conf['extractorDir'] = (Path(__file__).parent/'Extractors').as_posix()
    else:
      output += '**ERROR: No extractorDir in config file\n'
  if 'extractors' not in conf:
    if command == 'repair':
      conf['extractors'] = {}
    else:
      output += '**ERROR: No extractors in config file\n'
  if 'projectGroups' not in conf:
    output += '**ERROR: No project-groups in config file; REPAIR MANUALLY\n'
  if 'defaultProjectGroup' not in conf:
    if command == 'repair':
      conf['defaultProjectGroup'] = list(conf['projectGroups'].keys())[0]
    else:
      output += '**ERROR: No default projectGroups in config file\n'
  else:
    if conf['defaultProjectGroup'] not in conf['projectGroups']:
      if command == 'repair':
        conf['defaultProjectGroup'] = list(conf['projectGroups'].keys())[0]
      else:
        output += '**ERROR: default entry '+conf['defaultProjectGroup']+' not in projectGroup\n'
  #GUI items
  if 'GUI' not in conf:
    if command == 'repair':
      conf['GUI'] = {}
    else:
      output += '**ERROR: No GUI in config file\n'
  guiItems = {"theme": "light_blue",
    "imageWidthProject": 300,
    "imageWidthDetails": 600,
    "sidebarWidth": 280,
    "loggingLevel": "INFO",
    "tableColumns": {}}
  for key, value in guiItems.items():
    if 'GUI' in conf and key not in conf['GUI']:
      if command == 'repair':
        conf['GUI'][key] = value
      else:
        output += '**ERROR: key: '+key+' not in GUI configuration\n'

  if command == 'repair':
    with open(Path.home()/'.pastaELN.json','w', encoding='utf-8') as f:
      f.write(json.dumps(conf,indent=2))
  logging.info('Configuration ending')
  return output



def ontology(command:str='test') -> str:
  '''
  Check configuration file .pastaELN.json for consistencies

  Args:
    command (string): 'test' or 'install'

  Returns:
    string: ''=success, else error messages
  '''
  output = ''
  backend = Backend()

  if command == 'test':
    if not hasattr(backend.db, 'db'):
      return '**ERROR: couchDB not initialized'
    output += 'database name:'+backend.db.db.database_name+'\n'
    designDocuments = backend.db.db.design_documents()
    output += 'Design documents'+'\n'
    for item in designDocuments:
      numViews = len(item['doc']['views']) if 'views' in item['doc'] else 0
      output += '  '+item['id']+'   Num. of views:'+str(numViews)+'\n'
    try:
      _ = backend.db.getDoc('-ontology-')
      output += 'Ontology exists on server'+'\n'
    except:
      output += '**ERROR: Ontology does NOT exist on server'+'\n'
    return output

  elif command == 'install':
    logging.info('ontology starting ...')
    doc = defaultOntology
    logging.info(str(doc))
    logging.info('ontology ending ...')
    # _ = backend.db.create_document(doc)
    return ''

  return '**ERROR: Unknown command'



def exampleData(force:bool=False, callbackPercent:Optional[Callable[[int],None]]=None) -> str:
  '''
  Create example data after installation

  Args:
    force (bool): force creation by removing content before creation
    callbackPercent (function): callback function given to exampleData, such that exampleData can report progress back
  '''
  logging.info('Start example data creation')
  if callbackPercent is not None:
    callbackPercent(0)
  if force:
    backend = Backend(initConfig=False)
    dirName = backend.basePath
    backend.exit(deleteDB=True)
    shutil.rmtree(dirName)
    os.makedirs(dirName)
  if callbackPercent is not None:
    callbackPercent(1)
  backend = Backend(initViews=True, initConfig=False)
  if callbackPercent is not None:
    callbackPercent(2)
  ### CREATE PROJECTS AND SHOW
  print('*** CREATE EXAMPLE PROJECT AND SHOW ***')
  backend.addData('x0', {'-name': 'PASTAs Example Project', 'objective': 'Test if everything is working as intended.', 'status': 'active', 'comment': '#Important Can be used as reference or deleted'})
  if callbackPercent is not None:
    callbackPercent(3)
  print(backend.output('x0'))
  if callbackPercent is not None:
    callbackPercent(4)
  logging.info('Finished creating example project')

  ### TEST PROJECT PLANING
  print('*** TEST PROJECT PLANING ***')
  viewProj = backend.db.getView('viewDocType/x0')
  projID1  = [i['id'] for i in viewProj if 'PASTA' in i['value'][0]][0]
  if callbackPercent is not None:
    callbackPercent(5)
  backend.changeHierarchy(projID1)
  if callbackPercent is not None:
    callbackPercent(6)
  backend.addData('x1',    {'comment': 'This is hard! #TODO', '-name': 'This is an example task'})
  if callbackPercent is not None:
    callbackPercent(7)
  currentID = backend.addData('x1',    {'comment': 'This will take a long time. #WAIT', '-name': 'This is another example task'})
  if callbackPercent is not None:
    callbackPercent(8)
  backend.changeHierarchy(currentID)
  backend.addData('x2',    {'-name': 'This is an example subtask',     'comment': 'Random comment 1'})
  if callbackPercent is not None:
    callbackPercent(9)
  backend.addData('x2',    {'-name': 'This is another example subtask','comment': 'Random comment 2'})
  if callbackPercent is not None:
    callbackPercent(10)
  backend.changeHierarchy(None)
  semStepID = backend.addData('x1',    {'-name': 'Data files'})
  if callbackPercent is not None:
    callbackPercent(11)
  backend.changeHierarchy(semStepID)
  semDirName = backend.basePath/backend.cwd
  backend.changeHierarchy(None)
  print(backend.outputHierarchy())
  if callbackPercent is not None:
    callbackPercent(12)
  logging.info('Finished project planning')

  ### TEST PROCEDURES
  print('\n*** TEST PROCEDURES ***')
  sopDir = backend.basePath/'StandardOperatingProcedures'
  os.makedirs(sopDir, exist_ok=True)
  with open(sopDir/'Example_SOP.md','w', encoding='utf-8') as fOut:
    fOut.write('# Put sample in instrument\n# Do something\nDo not forget to\n- not do anything wrong\n- **USE BOLD LETTERS**\n')
  if callbackPercent is not None:
    callbackPercent(13)
  backend.addData('procedure', {'-name': 'StandardOperatingProcedures/Example_SOP.md', 'comment': '#v1'})
  if callbackPercent is not None:
    callbackPercent(14)
  print(backend.output('procedure'))
  if callbackPercent is not None:
    callbackPercent(15)
  logging.info('Finished procedures creating')

  ### TEST SAMPLES
  print('*** TEST SAMPLES ***')
  backend.addData('sample',    {'-name': 'Example sample', 'chemistry': 'A2B2C3', 'qrCode': '13214124 99698708', 'comment': 'can be used as example or removed'})
  if callbackPercent is not None:
    callbackPercent(16)
  print(backend.output('sample'))
  if callbackPercent is not None:
    callbackPercent(17)
  print(backend.outputQR())
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
  backend.scanProject(projID1)
  logging.info('Finished scan tree')
  if callbackPercent is not None:
    callbackPercent(20)

  ### USE GLOBAL FILES
  print('*** USE GLOBAL FILES ***')
  backend.changeHierarchy(semStepID)
  if callbackPercent is not None:
    callbackPercent(21)
  backend.addData('measurement', {'-name': 'https://upload.wikimedia.org/wikipedia/commons/a/a4/Misc_pollen.jpg', \
    'comment':'remote image from wikipedia. Used for testing and reference. Can be deleted.'})
  if callbackPercent is not None:
    callbackPercent(22)
  print(backend.output('measurement'))
  if callbackPercent is not None:
    callbackPercent(23)
  logging.info('Finished global files additions')

  ### VERIFY DATABASE INTEGRITY
  print('\n*** VERIFY DATABASE INTEGRITY ***')
  print(backend.checkDB(verbose=True))
  print('\n*** DONE WITH VERIFY ***')
  if callbackPercent is not None:
    callbackPercent(24)
  logging.info('Finished checking database')
  return 'Finished checking database'


def createShortcut() -> None:
  """
  Create alias and shortcut icon depending on operating system
  """
  logging.info('Create shortcut starting')
  if platform.system()=='Linux':
    content ='[Desktop Entry]\nName=PASTA ELN\nComment=PASTA electronic labnotebook\n'
    if sys.prefix==sys.base_prefix:   #normal installation into user-space
      content+='Exec=pastaELN\n'
    else:                             #installation in a virtual environment
      logging.info('In virtual environment, create an alias')
      with open(Path.home()/'.bashrc','a', encoding='utf-8') as fOut:
        alias = "alias pastaELN='"+sys.prefix+"bin/python3 -m pasta_eln.gui'"
        logging.info(alias)
        fOut.write(alias+'\n')
      content+='Exec='+sys.prefix+'bin/python3 -m pasta_eln.gui\n'
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
def main() -> None:
  ''' Main method and entry point for commands '''
  logPath = Path.home()/'pastaELN.log'
  #old versions of basicConfig do not know "encoding='utf-8'"
  logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')   #This logging is always info, since for installation only
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib.font_manager']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start PASTA Install')
  print('---- Test PASTA-ELN installation----')
  print('--   if nothing reported: it is ok.')
  print('getOS        :', getOS())
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
      if not existsCouchDB:
        print('install with root credentials...')
        installLinuxRoot(existsCouchDB, Path.home()/'pastaELN')
      if flagConfiguration:
        print('repair  configuration:', configuration('repair'))
      if flagOntology and existsCouchDB:
        print('install ontology     :', ontology('install'))

    elif platform.system()=='Windows':
      print('---- Create PASTA-ELN installation Windows ----')
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
