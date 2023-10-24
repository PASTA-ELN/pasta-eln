'''  Methods that check, repair, the local PASTA-ELN installation '''
import os, platform, sys, json, shutil, random, string, logging
from typing import Optional, Any, Callable
import urllib.request
from pathlib import Path
from cloudant.client import CouchDB

from .backend import Backend
from .fixedStringsJson import defaultOntology, defaultConfiguration, configurationGUI
from .miscTools import outputString, DummyProgressBar


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
  return f'{operatingSys} {environment}'


def createDefaultConfiguration(user:str, password:str, pathPasta:Optional[Path]=None) -> dict[str,Any]:
  '''
  Create base of configuration file .pastaELN.json
  - basic project group
  - defaultProjectGroup
  - userID

  Args:
    user (str): user name (for windows)
    password (str): password (for windows)
    pathPasta (Path): place to store pasta data

  Returns:
    dict: dictionary of configuration
  '''
  if not user:
    user = input('Enter user name: ')
  if not password:
    password = input('Enter password: ')
  if pathPasta is None:
    if platform.system()=='Windows':
      pathPasta = Path.home()/'Documents'/'PASTA_ELN'
    else:
      pathPasta = Path.home()/'PASTA_ELN'
  conf: dict[str, Any] = {
      'defaultProjectGroup': 'research',
      'projectGroups': {
          'research': {
              'local': {'user': user, 'password': password, 'database': 'research', 'path': str(pathPasta)},
              'remote': {},
          }}, 'version': 2}
  try:
    conf['userID']      = os.getlogin()
  except Exception:   #github action
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
                            lpFile= f'"{cmdLine[0]}"',
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
    except Exception:
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
      password = ''.join(random.choice(string.ascii_letters) for _ in range(12))
      logging.info('PASSWORD: %s',password)
      pathS = str(path).replace('\\','\\\\')
      cmd = ['msiexec','/i',pathS,'/quiet','COOKIEVALUE=abcdefghijklmo','INSTALLSERVICE=1','ADMINUSER=admin',\
             f'ADMINPASSWORD={password}','/norestart','/l*','log.txt']
      logging.info('COMMAND: '+' '.join(cmd))
      runAsAdminWindows(cmd)
      logging.info('CouchDB ending')
      return f'Installed couchDB with password |{password}|'
    return f'**ERROR: Unknown operating system {platform.system()}'
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
  except Exception:
    return False


def installLinuxRoot(couchDBExists:bool, pathPasta:Path=Path(''), password:str='') -> str:
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
    if not password:
      password = ''.join(random.choice(string.ascii_letters) for _ in range(12))
      logging.info('PASSWORD: %s',password)
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
    bashCommand = [
      'sudo snap install couchdb',
      f'sudo snap set couchdb admin={password}',
      'sudo snap start couchdb',
      'sudo snap connect couchdb:mount-observe',
      'sudo snap connect couchdb:process-control',
      'sleep 5',
      f'curl -X PUT http://admin:{password}@127.0.0.1:5984/_users',
      f'curl -X PUT http://admin:{password}@127.0.0.1:5984/_replicator',
      f'curl -X PUT http://admin:{password}@127.0.0.1:5984/_global_changes',
      f'curl -X PUT http://admin:{password}@127.0.0.1:5984/_node/_local/_config/couch_httpd_auth/timeout/ -d \'"60000"\'',
      'sleep 10']
  #Try all terminals
  scriptFile = Path.home()/'pastaELN_Install.sh'
  with open(scriptFile,'w', encoding='utf-8') as shell:
    shell.write('\n'.join(bashCommand))
  os.chmod(scriptFile, 0o0777)
  terminals = ['xterm -e bash -c ','qterminal -e bash -c ','gnome-terminal -- ']
  logging.info('Command: %s',str(bashCommand))
  resultString = f'Password: {password}'
  for term in terminals:
    # _ = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    res = os.system(term+scriptFile.as_posix())
    logging.info('Linux install terminal %s  %s',term,str(res))
    if res == 0:
      break
    if terminals.index(term)==len(terminals)-1:
      logging.error('**ERROR: Last terminal failed')
      res = os.system('\n'.join(bashCommand[:-2]))
      logging.info('Finished using straight Bash command result=%s',str(res))
      resultString = '**ERROR: Last terminal failed'
  success = 'CouchDB works' if couchdbUserPassword('admin',password) else 'CouchDB FAILED'
  logging.info('InstallLinuxRoot ending. %s',success)
  return resultString


def configuration(command:str='test', user:str='', password:str='', pathPasta:Path=Path('')) -> str:
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
  except Exception:
    output += '**ERROR configuration file does not exist\n'
    conf = {}
    if command == 'repair':
      conf = createDefaultConfiguration(user, password, pathPasta)
  logging.info(json.dumps(conf, indent=2))

  #check normal items
  for k,v in defaultConfiguration.items():
    if k not in conf:
      if command == 'repair':
        if isinstance(v,str) and v.startswith('$') and v.startswith('$'):
          v = eval(v[1:-1]) # pylint: disable=eval-used
        conf[k] = v
      else:
        output += outputString('text','error', f'No {k} in config file')
  #GUI items
  if 'GUI' not in conf:
    if command == 'repair':
      conf['GUI'] = {}
    else:
      output += outputString('text','error', 'No GUI in config file')
  for _, items in configurationGUI.items():
    for k,v in items.items():
      if 'GUI' in conf and k not in conf['GUI']:
        if command == 'repair':
          conf['GUI'][k] = v[1]
        else:
          output += outputString('text','error', f'No {k} in GUI part of config file')
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
  backend = Backend()
  if command == 'test':
    if not hasattr(backend.db, 'db'):
      return '**ERROR: couchDB not initialized'
    output = 'database name: {backend.db.db.database_name}\nDesign documents\n'
    for item in backend.db.db.design_documents():
      numViews = len(item['doc']['views']) if 'views' in item['doc'] else 0
      output += '  '+item['id']+'   Num. of views:'+str(numViews)+'\n'
    try:
      _ = backend.db.getDoc('-ontology-')
      output += 'Ontology exists on server'+'\n'
    except Exception:
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
  outputFormat = 'print'
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
  outputString(outputFormat,'h2','CREATE EXAMPLE PROJECT AND SHOW')
  backend.addData('x0', {'-name': 'PASTAs Example Project', 'objective': 'Test if everything is working as intended.', 'status': 'active', 'comment': '#Important Can be used as reference or deleted'})
  if callbackPercent is not None:
    callbackPercent(3)
  outputString(outputFormat,'info', backend.output('x0'))
  if callbackPercent is not None:
    callbackPercent(4)
  logging.info('Finished creating example project')

  ### TEST PROJECT PLANING
  outputString(outputFormat,'h2','TEST PROJECT PLANING')
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
  if backend.cwd is not None:
    semDirName = backend.basePath/backend.cwd
  backend.changeHierarchy(None)
  outputString(outputFormat,'info',backend.outputHierarchy())
  if callbackPercent is not None:
    callbackPercent(12)
  logging.info('Finished project planning')

  ### TEST PROCEDURES
  outputString(outputFormat,'h2','TEST PROCEDURES')
  sopDir = backend.basePath/'StandardOperatingProcedures'
  os.makedirs(sopDir, exist_ok=True)
  with open(sopDir/'Example_SOP.md','w', encoding='utf-8') as fOut:
    fOut.write('# Put sample in instrument\n# Do something\nDo not forget to\n- not do anything wrong\n- **USE BOLD LETTERS**\n')
  if callbackPercent is not None:
    callbackPercent(13)
  backend.addData('procedure', {'-name': 'StandardOperatingProcedures/Example_SOP.md', 'comment': '#v1'})
  if callbackPercent is not None:
    callbackPercent(14)
  outputString(outputFormat,'info',backend.output('procedure'))
  if callbackPercent is not None:
    callbackPercent(15)
  logging.info('Finished procedures creating')

  ### TEST SAMPLES
  outputString(outputFormat,'h2','TEST SAMPLES')
  backend.addData('sample',    {'-name': 'Example sample', 'chemistry': 'A2B2C3', 'qrCode': '13214124 99698708', 'comment': 'can be used as example or removed'})
  if callbackPercent is not None:
    callbackPercent(16)
  outputString(outputFormat,'info',backend.output('sample'))
  if callbackPercent is not None:
    callbackPercent(17)
  outputString(outputFormat,'info',backend.outputQR())
  if callbackPercent is not None:
    callbackPercent(18)
  logging.info('Finished samples creating')

  ###  TEST MEASUREMENTS AND SCANNING/CURATION
  outputString(outputFormat,'h2','TEST MEASUREMENTS AND SCANNING')
  shutil.copy(Path(__file__).parent/'Resources'/'ExampleMeasurements'/'simple.png', semDirName)
  shutil.copy(Path(__file__).parent/'Resources'/'ExampleMeasurements'/'simple.csv', semDirName)
  if callbackPercent is not None:
    callbackPercent(19)
  logging.info('Finished copy files')
  progressBar = DummyProgressBar()
  backend.scanProject(progressBar, projID1)
  logging.info('Finished scan tree')
  if callbackPercent is not None:
    callbackPercent(20)

  ### USE GLOBAL FILES
  outputString(outputFormat,'h2','USE GLOBAL FILES')
  backend.changeHierarchy(semStepID)
  if callbackPercent is not None:
    callbackPercent(21)
  backend.addData('measurement', {
    '-name': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Misc_pollen.jpg/315px-Misc_pollen.jpg',\
    'comment':'remote image from wikipedia. Used for testing and reference. Can be deleted.'})
  if callbackPercent is not None:
    callbackPercent(22)
  outputString(outputFormat,'info',backend.output('measurement'))
  if callbackPercent is not None:
    callbackPercent(23)
  logging.info('Finished global files additions')

  ### VERIFY DATABASE INTEGRITY
  outputString(outputFormat,'h2','VERIFY DATABASE INTEGRITY')
  outputString(outputFormat,'info',backend.checkDB(outputStyle='text'))
  outputString(outputFormat,'h2','DONE WITH VERIFY')
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
        alias = f"alias pastaELN='{sys.prefix}/bin/python3 -m pasta_eln.gui'"
        logging.info(alias)
        fOut.write(f'{alias}\n')
      content += f'Exec={sys.prefix}/bin/python3 -m pasta_eln.gui\n'
    content+='Icon='+ (Path(__file__).parent/'Resources'/'Icons'/'favicon64.png').as_posix() + '\n'
    content+='Terminal=false\nType=Application\nCategories=Science;Application;\n'
    try:
      linkString = (Path.home()/'Desktop'/'pastaELN.desktop').as_posix()
      with open(linkString,'w', encoding='utf-8') as fOut:
        fOut.write(content)
        os.system(f'gio set {linkString} metadata::trusted true') #for ubuntu systems
        os.chmod(Path.home()/'Desktop'/'pastaELN.desktop', 0o775)
    except Exception:
      pass
    try:
      with open(Path.home()/'.local'/'share'/'applications'/'pastaELN.desktop','w', encoding='utf-8') as fOut:
        fOut.write(content)
        os.chmod(Path.home()/'.local'/'share'/'applications'/'pastaELN.desktop', 0o777)
    except Exception:
      pass
  elif platform.system()=='Windows':
    import winshell
    from win32com.client import Dispatch
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut( os.path.join(winshell.desktop(), "pastaELN.lnk") )
    env = os.environ['CONDA_PREFIX'] if 'CONDA_PREFIX' in os.environ else ''  #full path of env
    if env:
      env = env.split('\\')[-1]  #just the env name
      user = os.getlogin()
      batContent = f"cmd.exe /c \"C:\\Users\\{user}\\anaconda3\\Scripts\\activate {env} && python -m pasta_eln.gui\""
      batLocation= f"C:\\Users\\{user}\\startPastaELN.bat"
      with open(batLocation, 'w', encoding='utf-8') as fBat:
        fBat.write(batContent)
      shortcut.Targetpath = batLocation
    else:
      shortcut.Targetpath = r"python -m pasta_eln.gui"
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
  except Exception:
    res = ' **ERROR**'
    #No new 'raise' so that it install-script continues its path
  flagOntology = 'ERROR' in res
  print(f'ontology     :{res}')

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
