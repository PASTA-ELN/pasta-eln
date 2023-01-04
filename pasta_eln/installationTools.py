'''  Methods that check, repair, the local PASTA-ELN installation '''
import os, platform, sys, json, shutil, random, string
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
  conf['userID']      = os.getlogin()
  conf['extractors']  = {}
  conf['qrPrinter']   = {}
  conf['magicTags']   = ['P1','P2','P3','TODO','WAIT','DONE']
  return conf


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
    url = 'https://github.com/git-for-windows/git/releases/download/v2.39.0.windows.2/Git-2.39.0.2-64-bit.exe'
    path = Path.home()/'Downloads'/'git-installer.exe'
    resultFilePath, _ = urllib.request.urlretrieve(url, path)
    os.system(str(resultFilePath))
    # Winget does not allow to set PATHs
    # os.system('winget install --id Git.Git -e --source winget')
    # Alternative approach: use winget and set environment at each pastaELN start for
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
    if shutil.which('git-annex') is None:
      return '**ERROR: git-annex not installed'
    # found = importlib.util.find_spec('datalad')
    #Has information if global or local installed
    # ModuleSpec(name='datalad', origin='/usr/local/lib/python3.8/dist-packages/datalad/__init__.py')
    return ''

  elif command == 'install':
    if platform.system()=='Linux':
      bashCommand = [
        'sudo wget -q http://neuro.debian.net/lists/focal.de-fzj.full -O /etc/apt/sources.list.d/neurodebian.sources.list',
        'sudo apt-key adv --recv-keys --keyserver hkps://keyserver.ubuntu.com 0xA5D32F012649A5A9',
        'sudo apt-get update',
        'sudo apt-get install -y git-annex-standalone',
        'echo DONE',
        'sleep 10000']
      os.system('xterm -e "'+'; '.join(bashCommand)+'"')
      return ''
    if platform.system()=='Windows':
      url = 'https://downloads.kitenet.net/git-annex/windows/7/current/git-annex-installer.exe'
      path = Path.home()/'Downloads'/'git-annex-installer.exe'
      resultFilePath, _ = urllib.request.urlretrieve(url, path)
      os.system(str(resultFilePath))
      return 'Installed git-annex using temporary files in Downloads'
    return '**ERROR: Unknown operating system '+platform.system()

  return '**ERROR: Unknown command'



def couchdb(command='test'):
  '''
  test couchDB installation or install it
  - Linux install also creates default configuration file .pastaELN.json
  - Windows not since the password is unknown after installation

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
      password = ''.join(random.choice(string.ascii_letters) for i in range(12))
      bashCommand = [
        'sudo snap install couchdb',
        'sudo snap set couchdb admin='+password,
        'sudo snap start couchdb',
        'sudo snap connect couchdb:mount-observe',
        'sudo snap connect couchdb:process-control',
        'sleep 5',
        'curl -X PUT http://admin:'+password+'@127.0.0.1:5984/_users',
        'curl -X PUT http://admin:'+password+'@127.0.0.1:5984/_replicator',
        'curl -X PUT http://admin:'+password+'@127.0.0.1:5984/_global_changes',
        'echo DONE',
        'sleep 10000']
      os.system('xterm -e "'+'; '.join(bashCommand)+'"')
      #create or adopt .pastaELN.json
      path = Path.home()/'.pastaELN.json'
      if path.exists():
        with open(path,'r', encoding='utf-8') as fConf:
          conf = json.load(fConf)
      else:
        conf = createDefaultConfiguration('admin', password)
      with open(path,'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(conf, indent=2) )
      return 'Password: '+password
    if platform.system()=='Windows':
      url = 'https://couchdb.neighbourhood.ie/downloads/3.1.1/win/apache-couchdb-3.1.1.msi'
      path = Path.home()/'Downloads'/'apache-couchdb-3.1.1.msi'
      resultFilePath, _ = urllib.request.urlretrieve(url, path)
      os.system(str(resultFilePath))
      return 'Installed couchDB'
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


def configuration(command='test', user='', password='', pathPasta=None):
  '''
  Check configuration file .pastaELN.json for consistencies

  Args:
    command (str): 'test' or 'repair'
    user (str): user name (for windows)
    password (str): password (for windows)
    pathPasta (str): path to install pasta in (Windows and Linux)

  Returns:
    string: ''=success, else error messages
  '''
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
  if not 'softwareDir' in conf:
    if command == 'repair':
      conf['softwareDir'] = os.path.dirname(os.path.abspath(__file__))
    else:
      output += '**ERROR: No softwareDir in config file\n'
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
    doc = json.loads(defaultOntology)
    print(doc)
    # _ = pasta.db.create_document(doc)
    return ''

  return '**ERROR: Unknown command'



def exampleData(force=True):
  '''
  Create example data after installation

  Args:
    force (bool): force creation by removing content before creation
  '''
  configName = 'research'
  if force:
    pasta = Pasta(configName, initConfig=False)
    dirName = pasta.basePath
    pasta.exit(deleteDB=True)
    shutil.rmtree(dirName)
    os.makedirs(dirName)
  pasta = Pasta(configName, initViews=True, initConfig=False)
  ### CREATE PROJECTS AND SHOW
  print('*** CREATE EXAMPLE PROJECT AND SHOW ***')
  pasta.addData('x0', {'-name': 'PASTAs Example Project', 'objective': 'Test if everything is working as intended.', 'status': 'active', 'comment': '#tag Can be used as reference or deleted'})
  print(pasta.output('x0'))

  ### TEST PROJECT PLANING
  print('*** TEST PROJECT PLANING ***')
  viewProj = pasta.db.getView('viewDocType/x0')
  projID1  = [i['id'] for i in viewProj if 'PASTA' in i['value'][0]][0]
  pasta.changeHierarchy(projID1)
  pasta.addData('x1',    {'comment': 'This is hard! #TODO', '-name': 'This is an example task'})
  pasta.addData('x1',    {'comment': 'This will take a long time. #WAIT', '-name': 'This is another example task'})
  pasta.changeHierarchy(pasta.currentID)
  pasta.addData('x2',    {'-name': 'This is an example subtask',     'comment': 'Random comment 1'})
  pasta.addData('x2',    {'-name': 'This is another example subtask','comment': 'Random comment 2'})
  pasta.changeHierarchy(None)
  pasta.addData('x1',    {'-name': 'Data files'})
  semStepID = pasta.currentID
  pasta.changeHierarchy(semStepID)
  semDirName = pasta.basePath/pasta.cwd
  pasta.changeHierarchy(None)
  print(pasta.outputHierarchy())

  ### TEST PROCEDURES
  print('\n*** TEST PROCEDURES ***')
  sopDir = pasta.basePath/'StandardOperatingProcedures'
  os.makedirs(sopDir)
  with open(sopDir/'Example_SOP.md','w', encoding='utf-8') as fOut:
    fOut.write('# Put sample in instrument\n# Do something\nDo not forget to\n- not do anything wrong\n- **USE BOLD LETTERS**\n')
  pasta.addData('procedure', {'-name': 'StandardOperatingProcedures/Example_SOP.md', 'comment': '#v1'})
  print(pasta.output('procedure'))

  ### TEST SAMPLES
  print('*** TEST SAMPLES ***')
  pasta.addData('sample',    {'-name': 'Example sample', 'chemistry': 'A2B2C3', 'qrCode': '13214124 99698708', 'comment': 'can be used as example or removed'})
  print(pasta.output('sample'))
  print(pasta.outputQR())

  ###  TEST MEASUREMENTS AND SCANNING/CURATION
  print('*** TEST MEASUREMENTS AND SCANNING/CURATION ***')
  shutil.copy(Path(__file__).parent/'Resources'/'ExampleMeasurements'/'simple.png', semDirName)
  shutil.copy(Path(__file__).parent/'Resources'/'ExampleMeasurements'/'simple.csv', semDirName)
  pasta.scanTree()

  ### USE GLOBAL FILES
  print('*** USE GLOBAL FILES ***')
  pasta.changeHierarchy(semStepID)
  pasta.addData('measurement', {'-name': 'https://developers.google.com/search/mobile-sites/imgs/mobile-seo/separate-urls.png', \
    'comment':'remote image from google. Used for testing and reference. Can be deleted.'})
  print(pasta.output('measurement'))

  ### VERIFY DATABASE INTEGRITY
  print('\n*** VERIFY DATABASE INTEGRITY ***')
  print(pasta.checkDB(verbose=True))
  print('\n*** DONE WITH VERIFY ***')
  return


def createShortcut():
  """
  Create shortcut icon depending on operating system
  """
  if platform.system()=='Windows':
    import winshell
    from win32com.client import Dispatch

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut( os.path.join(winshell.desktop(), "pastaELN.lnk") )
    shortcut.Targetpath = r"pastaELN"
    shortcut.WorkingDirectory = str(Path.home())
    shortcut.IconLocation = str(Path(__file__)/'Resources'/'Icons'/'favicon32.ico')
    shortcut.save()
  else:
    print("not implemented yet")



##############
# Main method for testing and installation without GUI
def main():
  ''' Main method and entry point for commands '''
  print('---- Test PASTA-ELN installation----')
  print('--   if nothing reported: it is ok.')
  print('getOS        :', getOS())
  res = gitAnnex()
  flagGitAnnex = 'ERROR' in res
  print('git-annex    :', res)
  res = couchdb()
  flagCouchdb = 'ERROR' in res
  print('chouchDB     :', res)
  res = configuration()
  flagConfiguration = 'ERROR' in res
  print('configuration:', res)
  try:
    res = '\n'+ontology()
  except:
    res = ' **ERROR**'
    raise
  flagOntology = 'ERROR' in res
  print('ontology     :'+res)

  print('Add "install" argument to install PASTA-ELN.')
  if len(sys.argv)>1 and 'install' in sys.argv:
    print('---- Create PASTA-ELN installation----')
    if flagGitAnnex:
      print('install git-annex    :', gitAnnex('install'))
    if flagCouchdb:
      print('install couchDB      :', couchdb('install'))
    if flagConfiguration:
      print('repair  configuration:', configuration('repair'))
    if flagOntology and not flagCouchdb:
      print('install ontology     :', ontology('install'))

  print('Add "example" argument to create example data.')
  if len(sys.argv)>1 and 'example' in sys.argv:
    print('---- Create Example data ----')
    print('create example data  :', exampleData())

# called by python3 -m pasta_eln.installTools
if __name__ == '__main__':
  main()
